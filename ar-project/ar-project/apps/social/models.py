
# Create your models here.
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.conf import settings


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

from django.utils.text import slugify


class Friendship(models.Model):
    FRIENDSHIP_STATUSES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('blocked', 'Blocked'),
    ]

    user_1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_initiated')
    user_1_status = models.CharField(max_length=10, choices=FRIENDSHIP_STATUSES, default='pending')

    user_2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_received')
    user_2_status = models.CharField(max_length=10, choices=FRIENDSHIP_STATUSES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('user_1', 'user_2')

    def __str__(self):
        return f"Friendship between {self.user_1.username} and {self.user_2.username} - Status: {self.user_1_status}/{self.user_2_status}"


class FriendRequest(models.Model):
    FRIEND_REQUEST_STATUSES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_requests_sent')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_requests_received')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=FRIEND_REQUEST_STATUSES, default='pending')

    def __str__(self):
        return f"Friend Request from {self.sender.username} to {self.receiver.username} - Status: {self.status}"