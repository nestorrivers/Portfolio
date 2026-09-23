import sys
from django.urls import path
from .views import *

sys.path.append("..")


urlpatterns = [
    path("login", login, name="login",),
    path("mfa_verify", mfa_verify, name="mfa_verify",),
    path("logout", logout, name="logout",),
]



