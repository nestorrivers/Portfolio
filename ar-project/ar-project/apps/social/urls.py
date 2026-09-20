from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from .views import *


urlpatterns = [


    path('social/send_friend_request/', send_friend_request, name='send_friend_request'),
    path('social/accept_friend_request/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('social/decline_friend_request/<int:request_id>/', decline_friend_request, name='decline_friend_request'),
    path('social/friend_list/', friend_list, name='friend_list'),
    path('social/remove_friend/<int:friend_id>/', remove_friend, name='remove_friend'),
    path('social/cancel_friend_request/<int:request_id>/', cancel_friend_request, name='cancel_friend_request'),
    path('social/block_user/<int:user_id>/', block_user, name='block_user'),
    path('social/unblock_user/<int:user_id>/', unblock_user, name='unblock_user'),
    path('social/blocked_list/', blocked_list, name='blocked_list'),
    path('social/friend_requests_sent/', friend_requests_sent, name='friend_requests_sent'),
    path('social/friend_requests_received/', friend_requests_received, name='friend_requests_received'),
]
