from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .permissions import can_authenticate_users, can_approve_locations

from .models import AuthorisedLocation
from .geocoding import ADDRESS_FIELDS, GeocodingError, geocode_location
from .permissions import can_authenticate_users, can_approve_locations
from .forms import NewAuthorisedLocationForm


def _process_location_form(request, location_form):
    """Validate, geocode if needed, and save. Returns True on success."""
    if not location_form.is_valid():
        return False

    location = location_form.save(commit=False)

    if not location.user_specific:
        location.user = None
    elif location.user is None:
        location.user = request.user

    address_changed = bool(set(ADDRESS_FIELDS) & set(location_form.changed_data))
    if address_changed or not location.coordinates:
        try:
            location.coordinates = geocode_location(location)
        except GeocodingError as exc:
            location_form.add_error(None, str(exc))
            return False

    location.save()
    return True


@login_required(login_url="login")
def new_authorised_location(request):
    location_form = NewAuthorisedLocationForm(request.POST or None)

    if request.method == "POST" and _process_location_form(request, location_form):
        return redirect("authorised_location_list")

    return render(request, "", {"location_form": location_form})


@login_required(login_url="login")
def edit_authorised_location(request, pk):
    location = get_object_or_404(AuthorisedLocation, pk=pk)
    location_form = NewAuthorisedLocationForm(request.POST or None, instance=location)

    if request.method == "POST" and _process_location_form(request, location_form):
        return redirect("authorised_location_list")

    return render(request, "", {"location_form": location_form})


@login_required(login_url="login")
def approve_authorised_location(request, pk):

    if not can_approve_locations(request.user):
        messages.error(request, 'Unauthorised to approve authorised locations.')
        return redirect('')

    pending_location = get_object_or_404(AuthorisedLocation, pk=pk)

    if request.method == "POST":
        pending_location.approved_by_manager = True
        pending_location.approving_manager = request.user
        pending_location.save(update_fields=["approved_by_manager", "approving_manager"])

        return redirect(reverse_lazy("approved_locations_pending_authorisation_list"))

    context = {"location": pending_location}
    return render(request, "", context)


@login_required(login_url="login")
def authorise_pending_user(request, pk):

    if not can_authenticate_users(request.user):
        messages.error(request, 'Unauthorised to authenticate users.')
        return redirect('')

    pending_user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        grant_login_approval(pending_user.profile)
        return redirect(reverse_lazy("users_pending_authentication_list"))

    context = {"item": pending_user}
    return render(request, "", context)