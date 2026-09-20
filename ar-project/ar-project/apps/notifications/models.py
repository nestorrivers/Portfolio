
# Create your models here.
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.conf import settings


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

from django.utils.text import slugify


class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    content = models.TextField()
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_posts')
    def save(self, *args, **kwargs):
        if not self.slug:
            slug_text = f"{self.title} {self.created_at.strftime('%Y%m%d')}"
            base_slug = slugify(slug_text)
            slug = base_slug
            counter = 1
            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Notification(models.Model):

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()

    action_url = models.URLField(null=True, blank=True)
    action_button_text = models.CharField(max_length=100, null=True, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"