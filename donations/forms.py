from django import forms
from .models import (
    RestaurantProfile,
    VolunteerProfile,
    NGOProfile,
    SurplusFoodRequest,
    PickupTask,
    Donation,
)

# ============ RESTAURANT PROFILE FORM ============
class RestaurantForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = ["business_name", "contact_person", "phone", "city", "address"]


# ============ VOLUNTEER PROFILE FORM ============
class VolunteerForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = ["full_name", "phone", "area"]


# ============ NGO PROFILE FORM ============
class NGOForm(forms.ModelForm):
    class Meta:
        model = NGOProfile
        fields = ["name", "contact_person", "phone", "address", "city"]


# ============ OLD DONATION FORM ============
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["restaurant_name", "food_type", "quantity", "city"]


# ============ SURPLUS FOOD REQUEST FORM ============
class SurplusFoodRequestForm(forms.ModelForm):
    class Meta:
        model = SurplusFoodRequest
        fields = ["food_type", "quantity"]
