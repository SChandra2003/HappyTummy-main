from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.messages import get_messages
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from happytummy.middleware import get_server_boot_time
from donations.models import NGOProfile, RestaurantProfile, SurplusFoodRequest, UserRole
from donations.services import (
    _normalize_msg91_mobile,
    build_surplus_sms_variables,
    get_nearby_ngos_for_surplus,
    send_sms,
)


class SurplusSmsNotificationTests(TestCase):
    def setUp(self):
        self.restaurant_user = User.objects.create_user(
            username="restaurant1",
            password="pass1234",
        )
        UserRole.objects.create(user=self.restaurant_user, role="restaurant")
        self.restaurant = RestaurantProfile.objects.create(
            user=self.restaurant_user,
            business_name="Fresh Kitchen",
            contact_person="Riya",
            phone="9000000001",
            city="Kolkata",
            address="12 Park Street",
        )

        ngo_user = User.objects.create_user(username="ngo1", password="pass1234")
        UserRole.objects.create(user=ngo_user, role="ngo")
        self.nearby_ngo = NGOProfile.objects.create(
            user=ngo_user,
            name="Care Shelter",
            contact_person="Aman",
            phone="9000000002",
            address="1 Mission Road",
            city="Kolkata",
        )

        far_ngo_user = User.objects.create_user(username="ngo2", password="pass1234")
        UserRole.objects.create(user=far_ngo_user, role="ngo")
        NGOProfile.objects.create(
            user=far_ngo_user,
            name="Far Trust",
            contact_person="Sara",
            phone="9000000003",
            address="22 MG Road",
            city="Delhi",
        )

    def test_get_nearby_ngos_for_surplus_matches_same_city(self):
        surplus = SurplusFoodRequest.objects.create(
            restaurant=self.restaurant,
            food_type="Rice",
            quantity=30,
        )

        ngos = list(get_nearby_ngos_for_surplus(surplus))

        self.assertEqual([ngo.id for ngo in ngos], [self.nearby_ngo.id])

    def test_build_surplus_sms_variables_matches_expected_flow_fields(self):
        surplus = SurplusFoodRequest.objects.create(
            restaurant=self.restaurant,
            food_type="Rice",
            quantity=30,
        )

        variables = build_surplus_sms_variables(surplus)

        self.assertEqual(
            variables,
            {
                "restaurant_name": "Fresh Kitchen",
                "quantity": "30",
                "food_type": "Rice",
                "address": "12 Park Street",
                "city": "Kolkata",
            },
        )

    def test_normalize_msg91_mobile_converts_indian_numbers(self):
        self.assertEqual(_normalize_msg91_mobile("9000000002"), "919000000002")
        self.assertEqual(_normalize_msg91_mobile("+91 90000 00002"), "919000000002")

    @override_settings(
        SMS_BACKEND="msg91",
        MSG91_AUTH_KEY="abc123xyz789exampleauthkey",
        MSG91_FLOW_ID="67f8a1b2c3d4e5f678901234",
        MSG91_SENDER_ID="HAPPTY",
    )
    def test_send_sms_skips_placeholder_msg91_configuration(self):
        result = send_sms(
            "+919000000002",
            "Test message",
            template_data={
                "restaurant_name": "Fresh Kitchen",
                "quantity": "30",
                "food_type": "Rice",
                "address": "12 Park Street",
                "city": "Kolkata",
            },
        )

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason"], "placeholder-msg91-config")

    @patch("donations.dashboard_views.notify_nearby_ngos_about_surplus")
    def test_restaurant_dashboard_add_donation_triggers_sms_notification(self, mock_notify):
        self.client.force_login(self.restaurant_user)
        session = self.client.session
        session["server_boot"] = get_server_boot_time()
        session.save()

        response = self.client.post(
            reverse("restaurant_dashboard"),
            data={
                "action": "add_donation",
                "food_type": "Veg Biryani",
                "quantity": "40",
                "cooked_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "expiry_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "storage_type": "hot",
                "safety_notes": "Packed and sealed",
            },
        )

        self.assertEqual(response.status_code, 302)
        donation = SurplusFoodRequest.objects.get(restaurant=self.restaurant)
        mock_notify.assert_called_once_with(donation)

    @override_settings(SMS_BACKEND="console")
    def test_restaurant_dashboard_shows_demo_sms_phone_numbers_in_console_mode(self):
        self.client.force_login(self.restaurant_user)
        session = self.client.session
        session["server_boot"] = get_server_boot_time()
        session.save()

        response = self.client.post(
            reverse("restaurant_dashboard"),
            data={
                "action": "add_donation",
                "food_type": "Veg Biryani",
                "quantity": "40",
                "cooked_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "expiry_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
                "storage_type": "hot",
                "safety_notes": "Packed and sealed",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        message_texts = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any("9000000002" in message for message in message_texts))
        self.assertTrue(any("demo SMS mode" in message for message in message_texts))

    def test_restaurant_can_delete_own_unaccepted_donation(self):
        donation = SurplusFoodRequest.objects.create(
            restaurant=self.restaurant,
            food_type="Rice",
            quantity=30,
        )
        self.client.force_login(self.restaurant_user)
        session = self.client.session
        session["server_boot"] = get_server_boot_time()
        session.save()

        response = self.client.post(
            reverse("restaurant_dashboard"),
            data={
                "action": "delete_donation",
                "donation_id": donation.id,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(SurplusFoodRequest.objects.filter(id=donation.id).exists())
        message_texts = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any("Donation deleted successfully." in message for message in message_texts))

    def test_restaurant_cannot_delete_donation_after_ngo_accepts_it(self):
        donation = SurplusFoodRequest.objects.create(
            restaurant=self.restaurant,
            food_type="Rice",
            quantity=30,
            is_picked=True,
        )
        self.client.force_login(self.restaurant_user)
        session = self.client.session
        session["server_boot"] = get_server_boot_time()
        session.save()

        response = self.client.post(
            reverse("restaurant_dashboard"),
            data={
                "action": "delete_donation",
                "donation_id": donation.id,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(SurplusFoodRequest.objects.filter(id=donation.id).exists())
        message_texts = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any("can no longer be deleted" in message for message in message_texts))

    @override_settings(
        SMS_BACKEND="msg91",
        MSG91_AUTH_KEY="abc123xyz789exampleauthkey",
        MSG91_FLOW_ID="67f8a1b2c3d4e5f678901234",
        MSG91_SENDER_ID="HAPPTY",
    )
    def test_send_test_sms_command_fails_when_provider_not_usable(self):
        with self.assertRaises(CommandError):
            call_command("send_test_sms", "+919000000002")
