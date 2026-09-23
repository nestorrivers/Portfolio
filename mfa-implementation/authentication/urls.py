import sys
from django.urls import path
from .views import *
from .tables import *

sys.path.append("..")


urlpatterns = [
    path("authentication/new-authorised-location", new_authorised_location, name="new_authorised_location",),

    path("authentication/edit-authorised-location/<str:pk>", edit_authorised_location, name="edit_authorised_location",),

    path("authentication/authorised-location-list/", AuthorisedLocationList.as_view(), name="authorised_location_list",),
    path("authentication/approve-authorised-location/<str:pk>", approve_authorised_location, name="approve_authorised_location",),

    path("authentication/authorise-pending-user/<str:pk>", authorise_pending_user, name="authorise_pending_user",),
    path("authentication/users-pending-authentication-list/", UsersPendingAuthenticationList.as_view(), name="users_pending_authentication_list",),
]
