import logging
from urllib.parse import quote

import requests
from django.conf import settings

from .models import NGOProfile


logger = logging.getLogger(__name__)


def _normalize_city(city):
    return (city or "").strip().lower()


def get_nearby_ngos_for_surplus(surplus_request):
    city = _normalize_city(getattr(surplus_request.restaurant, "city", ""))
    if not city:
        return NGOProfile.objects.none()

    return NGOProfile.objects.filter(
        city__iexact=surplus_request.restaurant.city,
    ).exclude(phone__isnull=True).exclude(phone__exact="")


def build_surplus_sms_message(surplus_request):
    restaurant = surplus_request.restaurant
    food_type = surplus_request.food_type
    quantity = surplus_request.quantity
    address = restaurant.address
    city = restaurant.city
    return (
        f"HappyTummy alert: {restaurant.business_name} has posted {quantity} "
        f"surplus {food_type} meals near {address}, {city}. "
        f"Log in to claim this donation."
    )


def build_surplus_sms_variables(surplus_request):
    restaurant = surplus_request.restaurant
    return {
        "restaurant_name": restaurant.business_name,
        "quantity": str(surplus_request.quantity),
        "food_type": surplus_request.food_type,
        "address": restaurant.address,
        "city": restaurant.city,
    }


def _normalize_msg91_mobile(phone_number):
    digits = "".join(ch for ch in str(phone_number or "") if ch.isdigit())
    if digits.startswith("91") and len(digits) == 12:
        return digits
    if len(digits) == 10:
        return f"91{digits}"
    return digits


def _looks_like_placeholder(value):
    normalized = (value or "").strip().lower()
    if not normalized:
        return True

    placeholder_markers = (
        "your_",
        "example",
        "abc123",
        "changeme",
        "replace",
    )
    return any(marker in normalized for marker in placeholder_markers)


def _send_twilio_sms(phone_number, message):
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_number = getattr(settings, "TWILIO_FROM_NUMBER", "")

    if not account_sid or not auth_token or not from_number:
        logger.warning("Twilio SMS is not fully configured; skipping SMS send.")
        return {"status": "skipped", "reason": "missing-twilio-config"}
    if any(_looks_like_placeholder(value) for value in (account_sid, auth_token, from_number)):
        logger.warning("Twilio SMS contains placeholder credentials; skipping SMS send.")
        return {"status": "skipped", "reason": "placeholder-twilio-config"}

    response = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{quote(account_sid, safe='')}/Messages.json",
        auth=(account_sid, auth_token),
        data={
            "From": from_number,
            "To": phone_number,
            "Body": message,
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    return {
        "status": "accepted",
        "sid": payload.get("sid"),
        "provider": "twilio",
    }


def _send_msg91_sms(phone_number, template_data):
    auth_key = getattr(settings, "MSG91_AUTH_KEY", "")
    flow_id = getattr(settings, "MSG91_FLOW_ID", "")
    sender_id = getattr(settings, "MSG91_SENDER_ID", "")

    if not auth_key or not flow_id or not sender_id:
        logger.warning("MSG91 SMS is not fully configured; skipping SMS send.")
        return {"status": "skipped", "reason": "missing-msg91-config"}
    if any(_looks_like_placeholder(value) for value in (auth_key, flow_id, sender_id)):
        logger.warning("MSG91 SMS contains placeholder credentials; skipping SMS send.")
        return {"status": "skipped", "reason": "placeholder-msg91-config"}

    mobile = _normalize_msg91_mobile(phone_number)
    if not mobile:
        return {"status": "failed", "reason": "invalid-phone-number"}

    payload = {
        "flow_id": flow_id,
        "sender": sender_id,
        "recipients": [
            {
                "mobiles": mobile,
                **(template_data or {}),
            }
        ],
    }

    response = requests.post(
        "https://api.msg91.com/api/v5/flow/",
        headers={
            "authkey": auth_key,
            "content-type": "application/json",
        },
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    body = response.json()
    if body.get("type") == "error":
        return {
            "status": "failed",
            "reason": body.get("message") or "msg91-error",
            "provider": "msg91",
            "raw_response": body,
        }
    return {
        "status": "accepted",
        "sid": body.get("message"),
        "provider": "msg91",
        "raw_response": body,
    }


def send_sms(phone_number, message, template_data=None):
    backend = getattr(settings, "SMS_BACKEND", "console")

    if backend == "console":
        logger.info("SMS to %s: %s", phone_number, message)
        return {"status": "skipped", "reason": "console-backend"}

    if backend == "twilio":
        return _send_twilio_sms(phone_number, message)

    if backend == "msg91":
        return _send_msg91_sms(phone_number, template_data)

    logger.warning("Unsupported SMS backend configured: %s", backend)
    return {"status": "skipped", "reason": "unsupported-backend"}


def notify_nearby_ngos_about_surplus(surplus_request):
    ngos = list(get_nearby_ngos_for_surplus(surplus_request))
    if not ngos:
        return []

    message = build_surplus_sms_message(surplus_request)
    template_data = build_surplus_sms_variables(surplus_request)
    results = []

    for ngo in ngos:
        try:
            result = send_sms(ngo.phone, message, template_data=template_data)
        except requests.RequestException:
            logger.exception(
                "Failed to send surplus SMS for surplus request %s to NGO %s",
                surplus_request.id,
                ngo.id,
            )
            result = {"status": "failed", "reason": "request-error"}

        results.append(
            {
                "ngo_id": ngo.id,
                "phone": ngo.phone,
                **result,
            }
        )

    return results
