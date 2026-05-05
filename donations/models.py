from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# NGO can request food from restaurants
class NGOFoodRequest(models.Model):
    ngo = models.ForeignKey('NGOProfile', on_delete=models.CASCADE)
    food_type = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)
    accepted_by = models.ForeignKey('RestaurantProfile', null=True, blank=True, on_delete=models.SET_NULL, related_name='accepted_ngo_requests')

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.ngo.name} requests {self.quantity} {self.food_type}"

# ===========================================
# USER PROFILES & ROLES
# ===========================================

class RestaurantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, unique=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)  # keep
    pincode = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.business_name


class VolunteerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    area = models.CharField(max_length=150)
    is_available = models.BooleanField(default=True)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='volunteer_photos/', blank=True, null=True)
    aadhar_card = models.CharField(max_length=12, unique=True)
    aadhar_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class NGOProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    ROLE_CHOICES = (
        ("restaurant", "Restaurant"),
        ("volunteer", "Volunteer"),
        ("ngo", "NGO"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} — {self.role}"


# ===========================================
# OPERATIONAL MODELS
# ===========================================

class SurplusFoodRequest(models.Model):
    STORAGE_CHOICES = (
        ("hot", "Hot"),
        ("cold", "Cold"),
        ("room_temp", "Room Temperature"),
    )

    STATUS_CHOICES = (
        ('posted', 'Posted'),
        ('notifying', 'Notifying NGOs'),
        ('accepted', 'Accepted by NGO'),
        ('picked', 'Picked Up'),
        ('expired', 'Expired'),
        ('archived', 'Archived'),
    )

    EXPIRY_REASON_CHOICES = (
        ('manual_delete', 'Manually Deleted by Restaurant'),
        ('auto_expired', 'Auto-Expired - No Acceptance'),
        ('picked_up', 'Successfully Picked Up'),
    )

    # link to RestaurantProfile, not old Restaurant
    restaurant = models.ForeignKey(RestaurantProfile, on_delete=models.CASCADE)
    food_type = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField(auto_now_add=True, null=True)
    cooked_at = models.DateTimeField(null=True, blank=True)
    expiry_at = models.DateTimeField(null=True, blank=True)
    storage_type = models.CharField(max_length=20, choices=STORAGE_CHOICES, default="room_temp")
    safety_notes = models.TextField(blank=True)
    is_picked = models.BooleanField(default=False)
    
    # Geolocation
    restaurant_lat = models.FloatField(null=True, blank=True)
    restaurant_lng = models.FloatField(null=True, blank=True)
    
    # Expiry management
    donation_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='posted'
    )
    
    # Notification tracking
    current_radius_km = models.IntegerField(default=5)
    ngos_notified_at = models.DateTimeField(null=True, blank=True)
    last_radius_expansion_at = models.DateTimeField(null=True, blank=True)
    notified_ngo_ids = models.JSONField(default=list)
    
    # Archival info
    expiry_reason = models.CharField(
        max_length=50,
        choices=EXPIRY_REASON_CHOICES,
        null=True,
        blank=True
    )
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=['donation_status', 'expiry_at']),
            models.Index(fields=['restaurant', 'donation_status']),
        ]

    def __str__(self):
        return f"{self.restaurant.business_name} - {self.quantity} meals"

    @property
    def time_remaining_seconds(self):
        """Returns seconds until expiry, or None if no expiry time set"""
        if not self.expiry_at:
            return None
        now = timezone.now()
        remaining = (self.expiry_at - now).total_seconds()
        return max(0, remaining)

    @property
    def time_remaining_readable(self):
        """Returns human-readable time (e.g., '45 mins', '2 hours 30 mins')"""
        seconds = self.time_remaining_seconds
        if seconds is None:
            return "Unknown"
        if seconds <= 0:
            return "Expired"
        
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{mins}m"

    @property
    def percent_time_remaining(self):
        """Returns percentage of original time remaining (0-100)"""
        if not self.cooked_at or not self.expiry_at:
            return None
        
        total_duration = (self.expiry_at - self.cooked_at).total_seconds()
        time_left = self.time_remaining_seconds
        
        if total_duration <= 0:
            return 0
        
        percent = (time_left / total_duration) * 100
        return max(0, min(100, percent))

    @property
    def urgency_level(self):
        """Returns urgency: 'SAFE', 'EXPIRING_SOON', 'CRITICAL', 'EXPIRED'"""
        seconds_left = self.time_remaining_seconds
        
        if seconds_left is None:
            return "UNKNOWN"
        if seconds_left <= 0:
            return "EXPIRED"
        if seconds_left < 1800:  # < 30 mins
            return "CRITICAL"
        if seconds_left < 7200:  # < 2 hours
            return "EXPIRING_SOON"
        return "SAFE"

    @property
    def urgency_color(self):
        """Returns color code for UI display"""
        urgency_map = {
            'SAFE': 'green',
            'EXPIRING_SOON': 'orange',
            'CRITICAL': 'red',
            'EXPIRED': 'dark-red',
            'UNKNOWN': 'gray',
        }
        return urgency_map.get(self.urgency_level, 'gray')

    @property
    def can_be_accepted_now(self):
        """Checks if donation can still be accepted"""
        return self.urgency_level != "EXPIRED" and self.donation_status in ['posted', 'notifying']

    @property
    def safety_status(self):
        if not self.expiry_at:
            return "Unknown"

        now = timezone.now()
        if self.expiry_at <= now:
            return "Expired"
        if self.expiry_at <= now + timedelta(hours=2):
            return "Expiring Soon"
        return "Safe"

    @property
    def safety_status_class(self):
        status = self.safety_status
        if status == "Safe":
            return "status-complete"
        if status == "Expiring Soon":
            return "status-pending"
        if status == "Expired":
            return "status-danger"
        return "status-neutral"

    @property
    def is_safe_to_accept(self):
        return self.safety_status != "Expired"

    def mark_as_expired(self, reason='auto_expired'):
        """Archive donation as expired"""
        self.donation_status = 'archived'
        self.expiry_reason = reason
        self.archived_at = timezone.now()
        self.save(update_fields=['donation_status', 'expiry_reason', 'archived_at'])


class DonationNotificationLog(models.Model):
    """Tracks notification attempts for each donation"""
    
    NOTIFICATION_STATUS = (
        ('sent', 'SMS Sent'),
        ('pending', 'Awaiting Response'),
        ('accepted', 'Accepted'),
        ('rejected', 'Not Interested'),
        ('failed', 'Send Failed'),
    )
    
    donation = models.ForeignKey(
        SurplusFoodRequest,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    ngo = models.ForeignKey(
        NGOProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=NOTIFICATION_STATUS,
        default='pending'
    )
    
    radius_km = models.IntegerField()
    notified_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    response_time_seconds = models.IntegerField(null=True, blank=True)
    
    sms_provider_response = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-notified_at']
        indexes = [
            models.Index(fields=['donation', 'status']),
            models.Index(fields=['ngo', 'status']),
        ]
    
    def __str__(self):
        return f"Notification {self.donation.id} to {self.ngo.name if self.ngo else 'Unknown'} - {self.status}"


class PickupTask(models.Model):
    # For surplus food: request is SurplusFoodRequest, ngo_request is null
    # For NGO food request: ngo_request is NGOFoodRequest, request is null
    request = models.ForeignKey(SurplusFoodRequest, on_delete=models.CASCADE, null=True, blank=True)
    ngo_request = models.ForeignKey(NGOFoodRequest, on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey(VolunteerProfile, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivery_otp = models.CharField(max_length=6, blank=True)
    otp_verified = models.BooleanField(default=False)
    delivered_to_ngo = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self):
        if self.request:
            return f"Pickup for: {self.request.restaurant.business_name} (Surplus)"
        elif self.ngo_request:
            return f"Pickup for: {self.ngo_request.accepted_by.business_name if self.ngo_request.accepted_by else 'Unassigned'} (NGO Request)"
        return "Pickup Task"

    @property
    def source_address(self):
        if self.request:
            return self.request.restaurant.address
        elif self.ngo_request and self.ngo_request.accepted_by:
            return self.ngo_request.accepted_by.address
        return "-"

    @property
    def destination_address(self):
        if self.request:
            # Surplus food always goes to the NGO that accepted
            return getattr(self.request, 'accepted_by_ngo_address', '-')
        elif self.ngo_request and self.ngo_request.ngo:
            return self.ngo_request.ngo.address
        return "-"


class Donation(models.Model):
    restaurant_name = models.CharField(max_length=200)
    food_type = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField()
    city = models.CharField(max_length=120)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.restaurant_name} - {self.quantity} meals"
