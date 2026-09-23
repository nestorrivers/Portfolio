

from decimal import *

from django.contrib import auth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate
from django.db.models import Q
import random
from datetime import timedelta

from .authentication.models import AuthorisedLocation

from .models import *
from .utils import *


def complete_login(request, user, backend=None):
    """Mark the session as authorised and log the user in."""
    profile = user.profile
    profile.current_session_authorisation = "Granted"
    profile.save(update_fields=["current_session_authorisation"])
    auth.login(request, user, backend=backend)


def login(request):

    if request.method == "POST":
        time_authentication = ""
        geo_authentication = ""

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            profile = user.profile

            # requires a hidden form input on login form that receives user's coordinates upon page load
            user_location = request.POST.get("user_location")

            try:
                session = LoginSession.objects.get(user=user, session_status="Active")
            except:
                session = None

            # if there is an existing session that hasn't yet closed, close and save it before opening a new one
            if session != None:
                session.session_closed_date = timezone.now()
                session.session_status = "Closed"
                session.save()

            session = LoginSession.objects.create(
                user=user,
                session_created_date=timezone.now(),
                session_coords=user_location,
                session_status="Active",
                session_ip_address=get_user_ip(request),
            )


            time_authentication = "Granted"

            if (
                profile.time_restricted_access
                and profile.shift_start_time is not None
                and profile.shift_end_time is not None
                and not is_within_shift(
                    profile.shift_start_time,
                    profile.shift_end_time,
                    current_local_time(),
                )
            ):
                time_authentication = "Denied"


            # locations that apply to this user: global ones plus their own
            authorised_locations = AuthorisedLocation.objects.filter(
                Q(user_specific=False) | Q(user_specific=True, user=user),
                approved_by_manager=True,
            )

            if authorised_locations:
                geo_authentication = "Denied"
                for location in authorised_locations:
                    distance = authorised_location_haversine(location, user_location)
                    if distance is not None and distance < location.radius:
                        geo_authentication = "Granted"
                        break
            else:
                geo_authentication = "Granted"



            if geo_authentication == "Granted" and time_authentication == "Granted":
                if profile.mfa_enabled:
                    send_mfa_token(user)
                    request.session["pending_mfa_user_id"] = str(user.pk)
                    request.session["pending_mfa_backend"] = user.backend
                    return redirect("mfa_verify")

                complete_login(request, user)
                return redirect('')
            
            
            else:
                if consume_login_approval(profile):
                    complete_login(request, user)
                    return redirect("")

                fail_reasons = []
                if geo_authentication == "Denied":
                    fail_reasons.append("Geo Authentication Failed")
                if time_authentication == "Denied":
                    fail_reasons.append("Time Authentication Failed")

                request_login_approval(profile)
                send_user_authorisation_request(request, user, fail_reasons)
                messages.info(request, "Your login needs manager approval. You'll be notified once it's granted.")

        else:
            messages.error(request, "Sorry, your username or password is incorrect.")


    context = {}
    return render(request, "", context)


def send_mfa_token(user):
    """Generate and email a 6-digit MFA token to the user."""
    token = generate_mfa_token()
    user.profile.mfa_secret = hash_mfa_token(token)
    user.profile.mfa_token_expires = timezone.now() + timedelta(minutes=5)
    user.profile.mfa_attempts = 0
    user.profile.save(update_fields=['mfa_secret', 'mfa_token_expires', 'mfa_attempts'])

    subject = 'Your Login Token'
    plain_message = (
        f"Hi,\n\nYour login token is: {token}\n\n"
        f"It expires in 5 minutes.\n\n"
        f"If you didn't request this, please ignore it."
    )

    html_message = (
        f"<h2>Your Login Token</h2>"
        f"<p>Your token is: <strong>{token}</strong></p>"
        f"<p>It expires in 5 minutes.</p>"
        f"<p>If you didn't request this, please ignore it.</p>"
    )
    from_email = settings.EMAIL_HOST_USER or ''

    try:
        send_mail(subject, plain_message, from_email, [user.email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        pass
    except Exception:
        pass


def mfa_verify(request):
    """Verify the MFA token and complete login."""
    user_id = request.session.get("pending_mfa_user_id")
    if not user_id:
        return redirect("login")

    auth_user = get_object_or_404(User, pk=user_id)
    profile = auth_user.profile

    if request.method == "POST":
        token = request.POST.get("mfa_token", "").strip()

        if profile.mfa_attempts >= MFA_MAX_ATTEMPTS:
            messages.error(request, "Too many attempts. Please log in again to get a new code.")
            request.session.pop("pending_mfa_user_id", None)
            request.session.pop("pending_mfa_backend", None)
            return redirect("login")

        expiry = profile.mfa_token_expires
        if expiry and expiry.tzinfo is None:
            expiry = timezone.make_aware(expiry)

        if mfa_token_matches(token, profile.mfa_secret) and expiry and expiry > timezone.now():
            profile.mfa_secret = None
            profile.mfa_token_expires = None
            profile.mfa_attempts = 0
            profile.save(update_fields=['mfa_secret', 'mfa_token_expires', 'mfa_attempts'])

            backend = request.session.pop("pending_mfa_backend", None)
            request.session.pop("pending_mfa_user_id", None)
            complete_login(request, auth_user, backend=backend)
            return redirect("")
        else:
            profile.mfa_attempts += 1
            profile.save(update_fields=['mfa_attempts'])
            messages.error(request, 'Invalid or expired token. Please try again.')
            return redirect("mfa_verify")

    return render(request, "", {"mfa_user": auth_user})


def logout(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        profile.current_session_authorisation = "Logged Out"
        profile.save()

        session = LoginSession.objects.get(user=request.user, session_status="Active")

        session.session_closed_date = timezone.now()
        session.session_status = "Closed"
        session.save()

        auth.logout(request)
        return redirect("login")

    else:
        return redirect("login")
