import sys
from django.urls import path
from .views import *

sys.path.append("..")


urlpatterns = [
    path("login", login, name="login",),
    path("send_mfa_token", logout, name="logout",),
    path("mfa_verify", logout, name="logout",),
    path("logout", logout, name="logout",),
]



