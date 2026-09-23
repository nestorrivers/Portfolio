from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .models import *
from .forms import *



class AuthorisedLocationList(LoginRequiredMixin, TemplateView):
    template_name = ""

    def get(self, request):

        authorisedLocations = AuthorisedLocation.objects.all()


        context = {
            "authorisedLocations": authorisedLocations,
        }

        return render(
            request,
            "common/authentication/authorisedLocationList.html",
            context,
        )


class UsersPendingAuthenticationList(LoginRequiredMixin, TemplateView):
    template_name = ""

    def get(self, request):

        pending_users = User.objects.filter(profile__login_approval_requested_at__isnull=False)


        context = {"pending_users": pending_users}

        return render(
            request,
            "common/authentication/usersPendingAuthenticationList.html",
            context,
        )
