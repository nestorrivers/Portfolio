

from decimal import *

from django.contrib import auth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login

import random
from datetime import timedelta

from .models import *
from .utils import authorised_location_haversine, send_user_authorisation_request, get_user_ip






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
                session = LoginSession.objects.get(user=user, sessionStatus="Active")
            except:
                session = None

            # if there is an existing session that hasn't yet closed, close and save it before opening a new one
            if session != None:
                session.session_closed_date = timezone.now()
                session.sessionStatus = "Closed"
                session.save()

            session = LoginSession.objects.create(
                user=user,
                session_created_date=timezone.now(),
                session_coords=user_location,
                session_status="Active",
                session_ip_address=get_user_ip(request),
            )


            if profile.time_restricted_access == True:
                if profile.shift_start_time and profile.shift_end_time:
                    now = timezone.now()
                    if now > profile.shift_start_time or now < profile.shift_end_time:
                        time_authentication = "Granted"
                    else:
                        time_authentication = "Denied"
                else:
                    time_authentication = "Granted"
            else:
                time_authentication = "Granted"

            authorised_locations = authorised_location.objects.get()

            if authorised_locations:
                if user_location:
                    for authorised_location in authorised_locations:
                        distance = authorised_location_haversine(
                            authorised_location, user_location
                        )

                        if distance < authorised_location.radius:
                            geo_authentication = "Granted"
                            break
                        else:
                            geo_authentication = "Denied"

                else:
                    geo_authentication = "Granted"
            else:
                geo_authentication = "Granted"


            if geo_authentication == "Granted" and time_authentication == "Granted":
                user.profile.current_session_authorisation = "Granted"
                profile.save()

                if getattr(user, 'mfa_enabled', False):
                    send_mfa_token(user)
                    return redirect('mfa_verify', user=user.pk)
                else:
                    login(request, user)
                    return redirect('')
            
            else:
                fail_reasons = []
                if geo_authentication == "Denied":
                    fail_reasons.append("Geo Authentication Failed")

                if time_authentication == "Denied":
                    fail_reasons.append("Time Authentication Failed")

                send_user_authorisation_request(request, user, fail_reasons)


        else:
            messages.error(request, "Sorry, your username or password is incorrect.")

    context = {}
    return render(request, "", context)



def send_mfa_token(user):
    """Generate and email a 6-digit MFA token to the user."""
    token = random.randint(100000, 999999)
    user.mfa_secret = str(token)
    user.mfa_token_expires = timezone.now() + timedelta(minutes=5)
    user.save(update_fields=['mfa_secret', 'mfa_token_expires'])

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
        send_mail(subject, plain_message, from_email, [user.email], html_message=html_message)
    except BadHeaderError:
        pass
    except Exception:
        pass


def mfa_verify(request, user):
    """Verify the MFA token and complete login."""
    auth_user = get_object_or_404(User, pk=user)

    if request.method == 'POST':
        token = request.POST.get('mfa_token', '').strip()

        # Ensure expiry is timezone-aware
        expiry = auth_user.mfa_token_expires
        if expiry and expiry.tzinfo is None:
            expiry = timezone.make_aware(expiry)

        if token == str(auth_user.mfa_secret) and expiry and expiry > timezone.now():
            auth_user.mfa_secret = None
            auth_user.mfa_token_expires = None
            auth_user.save(update_fields=['mfa_secret', 'mfa_token_expires'])
            login(request, auth_user)
            return redirect('')
        else:
            messages.error(request, 'Invalid or expired token. Please try again.')
            return redirect('mfa_verify', user=auth_user.pk)

    return render(request, '', {
        'mfa_user': auth_user,
    })







def logout(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        profile.current_session_authorisation = "Logged Out"
        profile.save()

        session = LoginSession.objects.get(user=request.user, sessionStatus="Active")

        session.session_closed_date = timezone.now()
        session.sessionStatus = "Closed"
        session.save()

        auth.logout(request)
        return redirect("login")

    else:
        return redirect("login")
