from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import *


urlpatterns = [


    path('notification/view/<int:notification_id>/', notification_view, name='notification_view'),
]
