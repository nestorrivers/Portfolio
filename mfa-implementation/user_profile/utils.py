from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.conf import settings


import hashlib, hmac, secrets

from datetime import timedelta
from haversine import haversine, Unit

from .models import Profile


MFA_MAX_ATTEMPTS = 5

def generate_mfa_token():
    """A random 6-digit code, zero-padded, from a CSPRNG."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_mfa_token(token):
    return hashlib.sha256(f"{settings.SECRET_KEY}:{token}".encode()).hexdigest()


def mfa_token_matches(token, stored_hash):
    if not stored_hash:
        return False
    return hmac.compare_digest(hash_mfa_token(token), stored_hash)


def approval_window():
    return timedelta(minutes=getattr(settings, "LOGIN_APPROVAL_WINDOW_MINUTES", 30))


def request_login_approval(profile):
    profile.login_approval_requested_at = timezone.now()
    profile.save(update_fields=["login_approval_requested_at"])


def grant_login_approval(profile):
    profile.login_approved_until = timezone.now() + approval_window()
    profile.login_approval_requested_at = None
    profile.save(update_fields=["login_approved_until", "login_approval_requested_at"])


def consume_login_approval(profile):
    """Atomically use up a still-valid approval. Returns True if one was used."""
    updated = Profile.objects.filter(
        pk=profile.pk, login_approved_until__gt=timezone.now()
    ).update(login_approved_until=None)
    return updated == 1

def parse_coordinates(value):
    """Parse "lat,lng" (optionally in brackets) into a (float, float) tuple, or None."""
    try:
        lat, lng = (float(part) for part in str(value).strip("() ").split(","))
    except (TypeError, ValueError):
        return None
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None
    return lat, lng


def authorised_location_haversine(authorised_location, user_location):
    """Distance in miles between a stored location and the user's reported
    position, or None if either set of coordinates can't be read."""
    stored = parse_coordinates(authorised_location.coordinates)
    reported = parse_coordinates(user_location)
    if stored is None or reported is None:
        return None
    return haversine(stored, reported, unit=Unit.MILES)


def authorised_location_haversine(authorised_location, user_location):
    authorised_location = authorised_location.coordinates.split(",")
    authorised_location_lat_long = (
        float(authorised_location[0]),
        float(authorised_location[1]),
    )

    user_location = user_location.split(",")

    user_location_lat_long = (float(user_location[0]), float(user_location[1]))

    distance = haversine(
        authorised_location_lat_long, user_location_lat_long, unit=Unit.MILES
    )
    return distance


def send_user_authorisation_request(request, user, reason):
    recipient_list = []


    recipient_list.extend(
        list(
            Profile.objects.filter(
                authorised_to_authenticate_users=True
            ).values_list("user__email", flat=True)
        )
    )
    subject = f"User: {str(user.first_name)} {str(user.last_name)} requires login authorisation."

    approval_link = request.build_absolute_uri(
        reverse("authorise_pending_user", args=[user.pk])
    )
    full_name = f"{user.first_name} {user.last_name}".strip() or user.get_username()
    message = (
        "Hello,\n\n"
        "A login attempt needs your approval.\n\n"
        f"User ID: {user.pk}\n"
        f"Name: {full_name}\n"
        f"Reason: {', '.join(reason)}\n\n"
        f"To approve, go to: {approval_link}\n\n"
        "This is an automated message."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email="",
        recipient_list=recipient_list,
    )


def get_user_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def current_local_time():
    """Current time of day in the project's timezone."""
    now = timezone.now()
    if timezone.is_aware(now):
        now = timezone.localtime(now)
    return now.time()


def is_within_shift(start, end, now):
    """True if `now` falls inside the shift window. Handles overnight shifts."""
    if start <= end:
        return start <= now <= end
    return now >= start or now <= end