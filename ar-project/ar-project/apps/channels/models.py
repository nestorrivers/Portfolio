
# Create your models here.
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify

from datetime import timedelta

from apps.objects.models import ARTextObject  # , ARImageObject
from apps.users.models import CustomUser



class ARChannel(models.Model):
    CHANNEL_TYPE_CHOICES = [
        ('Public', 'Public'),
        ('Verified', 'Verified Creators'),
        ('Seasonal', 'Seasonal/Event'),
        ('Private', 'Private'),
    ]

    CHANNEL_STATUSES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Suspended', 'Suspended'),
    )

    CHANNEL_THEMES = ( 
        ('Christmas', 'Christmas'),
        ('Halloween', 'Halloween'),
        ('Easter', 'Easter'),
        ('Summer', 'Summer'),
        ('Winter', 'Winter'),
        ('SciFi', 'Sci-Fi'),
        ('Fantasy', 'Fantasy'),
        ('Nature', 'Nature'),
        ('Urban', 'Urban'),
        ('Spooky', 'Spooky'),
        ('Art Showcase', 'Art Showcase'),
        ('Education', 'Education'),
        ('Self-Guided Tour', 'Self-Guided Tour'),
        ('General', 'General'),
        ('Other', 'Other'),
    )

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=CHANNEL_STATUSES, default='Active')
    theme = models.CharField(max_length=50, choices=CHANNEL_THEMES, default='General')

    VISIBILITY_CHOICES = [  
        ('Public', 'Public'),
        ('Private', 'Private'),
        ('Draft', 'Draft'),
    ]


    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='Public')

    # Optional seasonal/event support
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    # Optional AR viewer metadata
    viewer_style = models.JSONField(default=dict, blank=True)

    system_notes = ArrayField(models.TextField(), default=list, blank=True)


    class Meta:
        ordering = ['-created_at']


    @property
    def number_of_objects(self):
        text_objects = ARTextObject.objects.filter(channel=self).count()
        # image_objects = ARImageObject.objects.filter(channel=self).count()
        object_count = text_objects  # + image_objects  # + other object types
        return object_count
        

    @property
    def number_of_creators(self):
        text_object_creators = CustomUser.objects.filter(ar_text_objects__channel=self).distinct()
        # image_object_creators = CustomUser.objects.filter(arimageobject__channel=self).distinct()
        # all_creators = text_object_creators.union(image_object_creators)
        return text_object_creators.count()

    @property
    def number_of_views(self):
        text_object_views = sum(ar_object.view_count for ar_object in ARTextObject.objects.filter(channel=self))
        # image_object_views = sum(ar_object.view_count for ar_object in ARImageObject.objects.filter(channel=self))
        total_views = text_object_views  # + image_object_views  # + other object types
        return total_views

    @property
    def number_of_likes(self):
        text_object_likes = sum(ar_object.like_count for ar_object in ARTextObject.objects.filter(channel=self))
        # image_object_likes = sum(ar_object.like_count for ar_object in ARImageObject.objects.filter(channel=self))
        total_likes = text_object_likes  # + image_object_likes  # + other object types
        return total_likes

    def generate_slug(self):
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        while ARChannel.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.generate_slug()
        super().save(*args, **kwargs)



class CreatorChannelLink(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel = models.ForeignKey(ARChannel, on_delete=models.CASCADE)
    linked_at = models.DateTimeField(auto_now_add=True)

    CONTENT_TYPE_CHOICES = [
        ('Text', 'Text'),
        ('Image', 'Image'),
        ('Audio', 'Audio'),
        # ('3DModel', '3D Model'),
        # ('Video', 'Video'),
    ]


    approved_for_text = models.BooleanField(default=False)
    approved_for_image = models.BooleanField(default=False)
    approved_for_audio = models.BooleanField(default=False)
    # approved_for_3dmodel = models.BooleanField(default=False)
    # approved_for_video = models.BooleanField(default=False)


    class Meta:
        unique_together = ('creator', 'channel')