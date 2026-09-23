from django.db import models
from django.contrib.auth.models import User



SESSION_AUTHORISATION_CHOICES = (
    ("Granted", "Granted"),
    ("Pending", "Pending"),
    ("Logged Out", "Logged Out"),
)


class Profile(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Profile"
    )

    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=128, blank=True, null=True)
    mfa_token_expires = models.DateTimeField(blank=True, null=True)
    mfa_attempts = models.PositiveSmallIntegerField(default=0)

    current_session_authorisation = models.CharField(
        max_length=25,
        choices=SESSION_AUTHORISATION_CHOICES,
        default="Pending",
        verbose_name="Current Session Authorisation",
    )

    login_approval_requested_at = models.DateTimeField(blank=True, null=True)
    login_approved_until = models.DateTimeField(blank=True, null=True)

    is_authorised = models.BooleanField(
        default=False, verbose_name="Is Authorised to Use System"
    )

    custom_authorised_location_set = models.BooleanField(
        default=False, verbose_name="Custom Authorised Location Set"
    )


    shift_start_time = models.TimeField(blank=True, null=True, verbose_name="Shift Starts")
    shift_end_time = models.TimeField(blank=True, null=True, verbose_name="Shift Ends")
    time_restricted_access = models.BooleanField(
        default=False, verbose_name="Time Restricted Access"
    )


    password_last_changed = models.DateTimeField(
        auto_now_add=True, verbose_name="Password Last Changed"
    )

    authorised_to_authenticate_users = models.BooleanField(
        default=False, verbose_name="Authorised to Authenticate Users"
    )

    authorised_to_approve_authorised_locations = models.BooleanField(
        default=False, verbose_name="Authorised to Authorise Approved Locations"
    )



SESSION_STATUSES = (
    ("Active", "Active"),
    ("Closed", "Closed"),
)


class LoginSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="User")
    session_id = models.AutoField(primary_key=True, verbose_name="ID")

    session_created_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Session Created Date"
    )
    session_closed_date = models.DateTimeField(
        blank=True, null=True, verbose_name="Session Closed Date"
    )

    session_status = models.CharField(
        max_length=25,
        choices=SESSION_STATUSES,
        default="Active",
        verbose_name="Session Status",
    )

    session_coords = models.CharField(
        max_length=100, blank=True, verbose_name="Session Coords"
    )

    session_ip_address = models.CharField(
        max_length=100, blank=True, verbose_name="Session IP Address"
    )


    class Meta:
        verbose_name_plural = "Login Sessions"


