# from django.contrib import admin
# from .models import (
#     Restaurant,
#     NGO,
#     Volunteer,
#     SurplusFoodRequest,
#     PickupTask,
#     Donation,
# )

# @admin.register(Restaurant)
# class RestaurantAdmin(admin.ModelAdmin):
#     list_display = ("name", "contact_person", "email", "phone", "city", "created_at")
#     search_fields = ("name", "email", "phone", "city")
#     list_filter = ("city",)
#     ordering = ("-created_at",)


# @admin.register(NGO)
# class NGOAdmin(admin.ModelAdmin):
#     list_display = ("name", "contact_person", "email", "phone", "city", "created_at")
#     search_fields = ("name", "email", "phone", "city")
#     list_filter = ("city",)
#     ordering = ("-created_at",)


# @admin.register(Volunteer)
# class VolunteerAdmin(admin.ModelAdmin):
#     list_display = ("full_name", "email", "phone", "area", "created_at")
#     search_fields = ("full_name", "email", "phone", "area")
#     list_filter = ("area",)
#     ordering = ("-created_at",)


# @admin.register(SurplusFoodRequest)
# class SurplusFoodRequestAdmin(admin.ModelAdmin):
#     list_display = ("restaurant", "food_type", "quantity", "timestamp", "is_picked")
#     search_fields = ("restaurant__name", "food_type")
#     list_filter = ("is_picked", "timestamp")
#     ordering = ("-timestamp",)


# @admin.register(PickupTask)
# class PickupTaskAdmin(admin.ModelAdmin):
#     list_display = ("request", "assigned_to", "assigned_at", "completed")
#     search_fields = ("request__restaurant__name", "assigned_to__full_name")
#     list_filter = ("completed",)
#     ordering = ("-assigned_at",)


# @admin.register(Donation)
# class DonationAdmin(admin.ModelAdmin):
#     list_display = ("restaurant_name", "food_type", "quantity", "city", "date")
#     search_fields = ("restaurant_name", "food_type", "city")
#     list_filter = ("city", "food_type")
#     ordering = ("-date",)
# from django.contrib import admin
# from .models import (
#     RestaurantProfile,
#     VolunteerProfile,
#     NGOProfile,
#     UserRole,
#     SurplusFoodRequest,
#     PickupTask,
#     Donation,
# )

# @admin.register(RestaurantProfile)
# class RestaurantProfileAdmin(admin.ModelAdmin):
#     list_display = ("business_name", "contact_person", "phone", "city", "user")
#     search_fields = ("business_name", "user__username", "city")
#     list_filter = ("city",)


# @admin.register(VolunteerProfile)
# class VolunteerProfileAdmin(admin.ModelAdmin):
#     list_display = ("full_name", "phone", "area", "is_available", "user")
#     search_fields = ("full_name", "user__username", "area")
#     list_filter = ("area", "is_available")


# @admin.register(NGOProfile)
# class NGOProfileAdmin(admin.ModelAdmin):
#     list_display = ("name", "contact_person", "phone", "city", "user")
#     search_fields = ("name", "city", "user__username")
#     list_filter = ("city",)


# @admin.register(UserRole)
# class UserRoleAdmin(admin.ModelAdmin):
#     list_display = ("user", "role")
#     list_filter = ("role",)
#     search_fields = ("user__username",)


# @admin.register(SurplusFoodRequest)
# class SurplusFoodRequestAdmin(admin.ModelAdmin):
#     list_display = ("restaurant", "food_type", "quantity", "is_picked", "timestamp")
#     search_fields = ("restaurant__business_name", "food_type")
#     list_filter = ("is_picked", "timestamp")


# @admin.register(PickupTask)
# class PickupTaskAdmin(admin.ModelAdmin):
#     list_display = ("request", "assigned_to", "completed", "assigned_at")
#     search_fields = ("assigned_to__full_name", "request__restaurant__business_name")
#     list_filter = ("completed",)


# @admin.register(Donation)
# class DonationAdmin(admin.ModelAdmin):
#     list_display = ("restaurant_name", "food_type", "quantity", "city", "date")
#     list_filter = ("city", "food_type")
#     search_fields = ("restaurant_name", "city")
from django.contrib import admin
from .models import (
    RestaurantProfile,
    VolunteerProfile,
    NGOProfile,
    UserRole,
    SurplusFoodRequest,
    PickupTask,
    Donation,
)

@admin.register(RestaurantProfile)
class RestaurantProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "contact_person", "phone", "city", "user")
    search_fields = ("business_name", "user__username", "city")
    list_filter = ("city",)


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "area", "is_available", "user")
    search_fields = ("full_name", "user__username", "area")
    list_filter = ("area", "is_available")


@admin.register(NGOProfile)
class NGOProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "city", "user")
    search_fields = ("name", "city", "user__username")
    list_filter = ("city",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username",)


@admin.register(SurplusFoodRequest)
class SurplusFoodRequestAdmin(admin.ModelAdmin):
    list_display = ("restaurant", "food_type", "quantity", "is_picked", "timestamp")
    search_fields = ("restaurant__business_name", "food_type")
    list_filter = ("is_picked", "timestamp")


@admin.register(PickupTask)
class PickupTaskAdmin(admin.ModelAdmin):
    list_display = ("request", "assigned_to", "completed", "assigned_at")
    search_fields = ("assigned_to__full_name", "request__restaurant__business_name")
    list_filter = ("completed",)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("restaurant_name", "food_type", "quantity", "city", "date")
    list_filter = ("city", "food_type")
    search_fields = ("restaurant_name", "city")
