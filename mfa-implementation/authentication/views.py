from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

import googlemaps
from datetime import datetime, date
from .forms import NewAuthorisedLocationForm
from .models import AuthorisedLocation



@login_required(login_url="login")
def new_authorised_location(request):

    user = request.user

    location_form = NewAuthorisedLocationForm()

    if request.method == "POST":
        location_form = NewAuthorisedLocationForm(request.POST)

        if location_form.is_valid():
            location_form = location_form.save(commit=False)

            if location_form.user_specific == True:
                location_form.user = user

            gmaps = googlemaps.Client(key="")

            address = (
                location_form.name
                + location_form.address_line_1
                + location_form.address_line_2
                + location_form.town_city
                + location_form.county
                + location_form.postcode
                + location_form.country
            )
            geocode_results = gmaps.geocode(address)
            lat = geocode_results[0]["geometry"]["location"]["lat"]
            long = geocode_results[0]["geometry"]["location"]["lng"]
            location_form.coordinates = str((lat, long))

            location_form.save()


        else:
            print("Form is not valid")
            print(location_form.errors)
            print(location_form.non_field_errors())


    context = {"location_form": location_form}
    return render(request, "", context)


@login_required(login_url="login")
def edit_authorised_location(request, pk):

    location_form = NewAuthorisedLocationForm()

    if request.method == "POST":
        location_form = NewAuthorisedLocationForm(request.POST)

        if location_form.is_valid():
            location_form = location_form.save(commit=False)

            if location_form.user_specific == True:
                location_form.user = request.user

            gmaps = googlemaps.Client(key="")

            address = (
                location_form.name
                + location_form.address_line_1
                + location_form.address_line_2
                + location_form.town_city
                + location_form.county
                + location_form.postcode
                + location_form.country
            )
            geocode_results = gmaps.geocode(address)
            lat = geocode_results[0]["geometry"]["location"]["lat"]
            long = geocode_results[0]["geometry"]["location"]["lng"]
            location_form.coordinates = str((lat, long))

            location_form.save()

            return redirect(reverse_lazy("authorised_location_list"))

        else:
            print("Form is not valid")
            print(location_form.errors)
            print(location_form.non_field_errors())

    context = {"location_form": location_form}
    return render(request, "", context)


@login_required(login_url="login")
def authorise_pending_user(request, pk):

    pending_user = User.objects.get(pk=pk)

    if request.method == "POST":

        pending_user.is_authorised = True


        return redirect(reverse_lazy("users_pending_authentication_list"))


    context = {"item": pending_user}
    return render(request, "", context)
