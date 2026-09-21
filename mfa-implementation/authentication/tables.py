from django.shortcuts import render
from django.views.generic import TemplateView

from django.contrib.auth.models import User

from .models import *
from .forms import *



class AuthorisedLocationList(TemplateView):
    template_name = ""

    def get(self, request):

        authorisedLocations = AuthorisedLocation.objects.get()


        context = {
            "authorisedLocations": authorisedLocations,
        }

        return render(
            request,
            "common/authentication/authorisedLocationList.html",
            context,
        )

class UsersPendingAuthenticationList(TemplateView):
    template_name = ""

    def get(self, request):

        pending_users = User.objects.get()


        context = {"pending_users": pending_users}

        return render(
            request,
            "common/authentication/usersPendingAuthenticationList.html",
            context,
        )
