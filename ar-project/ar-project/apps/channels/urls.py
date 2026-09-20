from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import *
from .utils import get_channel_objects


urlpatterns = [


    path('channel/create/', create_channel, name='create_channel'),
    path('channel/view/<str:slug>/', channel_detail, name='channel_detail'),
    path('channel/edit/<str:slug>/', edit_channel, name='edit_channel'),
    path('channel/delete/<str:slug>/', delete_channel, name='delete_channel'),
    path('channel/deactivate/<str:slug>/', deactivate_channel, name='deactivate_channel'),
    path('channel/activate/<str:slug>/', activate_channel, name='activate_channel'),

    path('channels/', channel_list_user, name='channel_list_user'),
    path('channels/admin/', channel_list_admin, name='channel_list_admin'),

    path('channel/ar-viewer/<str:slug>/', channel_ar_viewer, name='channel_ar_viewer'),

    path('api/channels/objects/', get_channel_objects, name='get_channel_objects')
]
