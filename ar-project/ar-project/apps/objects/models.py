from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


from datetime import datetime
from urllib.parse import urlparse

from wordfilter import Wordfilter
from django.contrib import messages


from apps.notifications.models import Notification
from apps.moderation.models import RestrictedArea


class ARTextObjectTemplate(models.Model):
    # Identity
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Shape / Geometry
    SHAPE_CHOICES = [
        ('plane', 'Plane'),
        ('box', 'Box'),
        ('circle', 'Circle'),
    ]


    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES)

    width = models.FloatField(default=1.0)
    height = models.FloatField(default=1.0)
    depth = models.FloatField(default=0.1)
    radius = models.FloatField(default=1.0)
    radius_top = models.FloatField(default=1.0)
    radius_bottom = models.FloatField(default=1.0)

    rotation_x = models.FloatField(default=0.0)
    rotation_y = models.FloatField(default=0.0)
    rotation_z = models.FloatField(default=0.0)
    billboard = models.BooleanField(default=False)

    # Material
    material_opacity = models.FloatField(default=1.0)
    material_transparent = models.BooleanField(default=False)
    material_metalness = models.FloatField(default=0.0)
    material_roughness = models.FloatField(default=1.0)

    texture_url = models.URLField(blank=True, null=True)
    texture_repeat_x = models.FloatField(default=1.0)
    texture_repeat_y = models.FloatField(default=1.0)

    cast_shadow = models.BooleanField(default=False)
    receive_shadow = models.BooleanField(default=False)

    # Interaction / Behaviour
    clickable = models.BooleanField(default=True)
    hover_enabled = models.BooleanField(default=False)
    dwell_time_ms = models.IntegerField(default=800)
    scale_on_hover = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ARTextObject(models.Model):
    VISIBILITY_CHOICES = [
        ('Public', 'Public'),
        ('Draft', 'Draft'),
        ('Private', 'Private'),
        ('Suspended', 'Suspended'),
    ]

    # Basic info
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    text_content = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ar_text_objects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    channel = models.ForeignKey(
        'channels.ARChannel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ar_text_objects'
    )



    COLOURS = [
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Green', 'Green'),
        ('Blue', 'Blue'),
        ('Yellow', 'Yellow'),
        ('Purple', 'Purple'),
        ('Orange', 'Orange'),
        ('Gray', 'Gray'),
    ]

    FONT_CHOICES = [
        ('Default', 'Default'),
        ('MozillaVR', 'Mozilla VR'),
        ('AileronSemibold', 'Aileron Semibold'),
    ]

    material_colour = models.CharField(max_length=20, choices=COLOURS, default="white")

    # Text Styling
    font = models.CharField(max_length=255, choices=FONT_CHOICES, default="default")
    font_size = models.FloatField(default=1.0)
    text_wrap_count = models.IntegerField(default=40)
    text_align = models.CharField(
        max_length=20,
        choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')],
        default='center'
    )
    text_baseline = models.CharField(
        max_length=20,
        choices=[('Top', 'Top'), ('Centre', 'Centre'), ('Bottom', 'Bottom')],
        default='Centre'
    )
    text_width = models.FloatField(default=4.0)
    text_opacity = models.FloatField(default=1.0)
    text_colour = models.CharField(max_length=20, choices=COLOURS, default="black")
    object_colour = models.CharField(max_length=20, choices=COLOURS, blank=True, default="black")

    text_offset_x = models.FloatField(default=0.0)
    text_offset_y = models.FloatField(default=0.0)
    text_offset_z = models.FloatField(default=0.0)

    # Shape / Geometry
    SHAPE_CHOICES = [
        ('plane', 'Plane'),
        ('box', 'Box'),
        ('circle', 'Circle'),
    ]

    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES)

    width = models.FloatField(default=1.0)
    height = models.FloatField(default=1.0)
    depth = models.FloatField(default=0.1)
    radius = models.FloatField(default=1.0)
    radius_top = models.FloatField(default=1.0)
    radius_bottom = models.FloatField(default=1.0)

    rotation_x = models.FloatField(default=0.0)
    rotation_y = models.FloatField(default=0.0)
    rotation_z = models.FloatField(default=0.0)
    billboard = models.BooleanField(default=False)

    # Material
    material_opacity = models.FloatField(default=1.0)
    material_transparent = models.BooleanField(default=False)
    material_metalness = models.FloatField(default=0.0)
    material_roughness = models.FloatField(default=1.0)

    texture_url = models.URLField(blank=True, null=True)
    texture_repeat_x = models.FloatField(default=1.0)
    texture_repeat_y = models.FloatField(default=1.0)

    cast_shadow = models.BooleanField(default=False)
    receive_shadow = models.BooleanField(default=False)

    # Interaction / Behaviour
    clickable = models.BooleanField(default=True)
    hover_enabled = models.BooleanField(default=False)
    dwell_time_ms = models.IntegerField(default=800)
    scale_on_hover = models.BooleanField(default=False)


    # Location
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)

    # Visibility and sharing
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='Public'
    )

    # Engagement
    view_count = models.IntegerField(default=0)

    system_notes = ArrayField(
        models.TextField(),
        blank=True,
        default=list
    )

    # Tags
    tags = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )



    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.title} by {self.creator.username}"
    

    @property
    def like_count(self):
        likes_count = TextObjectInteraction.objects.filter(text_object=self, liked=True).count()
        return likes_count

    def is_in_restricted_area(self):
        for area in RestrictedArea.objects.filter(active=True):
            if area.contains_point(
                self.latitude,
                self.longitude
            ):
                return True

        return False

    wf = Wordfilter()
    def moderate_text(self):

        location_passes = True
        if self.is_in_restricted_area():
            location_passes = False

        title_passes = True
        if self.wf.blacklisted(self.title):
            title_passes = False

        description_passes = True
        if self.wf.blacklisted(self.description):
            description_passes = False

        text_passes = True
        if self.wf.blacklisted(self.text_content):
            text_passes = False
        
        if not (title_passes and description_passes and text_passes and location_passes):
            
            reasons = []
            if not title_passes:
                reasons.append('Inappropriate Title')
                self.visibility = "Suspended"
            if not description_passes:
                reasons.append('Inappropriate Description')
                self.visibility = "Suspended"
            if not text_passes:
                reasons.append('Inappropriate Content')
                self.visibility = "Suspended"   
            if not location_passes:
                reasons.append('Restricted area')
                self.visibility = "Suspended"
            
            notification = Notification(
                recipient=self.creator,
                title="Content Moderation Alert",
                message=f"""Dear {self.creator.username},
                
    Your recent AR Text Object content has been flagged by our moderation system.

    Title: {self.title}
    Description: {self.description}
    Content: {self.text_content}

    Your post has been flagged due to:
    {', '.join(reasons)}

    Your post status has been set to 'Suspended'. Please review our community guidelines and make necessary adjustments."""
            )
            notification.save()
            try:
                self.save(update_fields=["visibility"])
            except:
                self.save()
            if self.creator.receive_email_notifications == True:
                subject = "AR Project - Content Moderation Alert for Your AR Text Object"
                body = f"""
                Dear {self.creator.username},
                Your recent AR Text Object content has been flagged by our moderation system.
                Title: {self.title}
                Description: {self.description}
                Content: {self.text_content}
                Your post has been flagged due to:
                {'Inappropriate Title' if not title_passes else ''}
                {'Inappropriate Description' if not description_passes else ''}
                {'Inappropriate Content' if not text_passes else ''}
            """
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if title_passes == False:
                self.system_notes.append(f"{timestamp}: Title flagged as inappropriate.")
            if description_passes == False:
                self.system_notes.append(f"{timestamp}: Description flagged as inappropriate.")
            if text_passes == False:
                self.system_notes.append(f"{timestamp}: Text content flagged as inappropriate.")


    def save_and_moderate(self, *args, **kwargs):
        # Auto-moderate on creation and edit
        text_moderation = self.moderate_text()

        super().save(*args, **kwargs)


class TextObjectInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text_object = models.ForeignKey(ARTextObject, on_delete=models.CASCADE, related_name='text_interactions')

    liked = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    last_updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'text_object')

    def __str__(self):
        return f"{self.user.username} likes {self.text_object.title}"





class ArImageObjectTemplate(models.Model):
    # Identity
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Shape / Geometry
    SHAPE_CHOICES = [
        ('plane', 'Plane'),
        ('box', 'Box'),
        ('circle', 'Circle'),
    ]

    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES)

    width = models.FloatField(default=1.0)
    height = models.FloatField(default=1.0)
    depth = models.FloatField(default=0.1)
    radius = models.FloatField(default=1.0)
    radius_top = models.FloatField(default=1.0)
    radius_bottom = models.FloatField(default=1.0)

    rotation_x = models.FloatField(default=0.0)
    rotation_y = models.FloatField(default=0.0)
    rotation_z = models.FloatField(default=0.0)
    billboard = models.BooleanField(default=False)

    # Material
    material_opacity = models.FloatField(default=1.0)
    material_transparent = models.BooleanField(default=False)
    material_metalness = models.FloatField(default=0.0)
    material_roughness = models.FloatField(default=1.0)

    texture_url = models.URLField(blank=True, null=True)
    texture_repeat_x = models.FloatField(default=1.0)
    texture_repeat_y = models.FloatField(default=1.0)

    cast_shadow = models.BooleanField(default=False)
    receive_shadow = models.BooleanField(default=False)

    # Interaction / Behaviour
    clickable = models.BooleanField(default=True)
    hover_enabled = models.BooleanField(default=False)
    dwell_time_ms = models.IntegerField(default=800)
    scale_on_hover = models.BooleanField(default=False)
    animation_enabled = models.BooleanField(default=False)
    animation_type = models.CharField(max_length=50, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ARImageObject(models.Model):


    VISIBILITY_CHOICES = [
        ('Public', 'Public'),
        ('Draft', 'Draft'),
        ('Private', 'Private'),
        ('Suspended', 'Suspended'),
    ]

    # Basic info
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ar_image_objects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    channel = models.ForeignKey(
        'channels.ARChannel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ar_image_objects'
    )


    COLOURS = [
        ('Black', 'Black'),
        ('White', 'White'),
        ('Red', 'Red'),
        ('Green', 'Green'),
        ('Blue', 'Blue'),
        ('Yellow', 'Yellow'),
        ('Purple', 'Purple'),
        ('Orange', 'Orange'),
        ('Gray', 'Gray'),
    ]


    material_colour = models.CharField(max_length=20, choices=COLOURS, default="white")

    # Shape / Geometry
    SHAPE_CHOICES = [
        ('plane', 'Plane'),
        ('box', 'Box'),
        ('circle', 'Circle'),
    ]

    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES)

    width = models.FloatField(default=1.0)
    height = models.FloatField(default=1.0)
    depth = models.FloatField(default=0.1)
    radius = models.FloatField(default=1.0)
    radius_top = models.FloatField(default=1.0)
    radius_bottom = models.FloatField(default=1.0)

    rotation_x = models.FloatField(default=0.0)
    rotation_y = models.FloatField(default=0.0)
    rotation_z = models.FloatField(default=0.0)
    billboard = models.BooleanField(default=False)

    # Material
    material_opacity = models.FloatField(default=1.0)
    material_transparent = models.BooleanField(default=False)
    material_metalness = models.FloatField(default=0.0)
    material_roughness = models.FloatField(default=1.0)

    texture_url = models.URLField(blank=True, null=True)
    texture_repeat_x = models.FloatField(default=1.0)
    texture_repeat_y = models.FloatField(default=1.0)

    cast_shadow = models.BooleanField(default=False)
    receive_shadow = models.BooleanField(default=False)

    # Interaction / Behaviour
    clickable = models.BooleanField(default=True)
    hover_enabled = models.BooleanField(default=False)
    dwell_time_ms = models.IntegerField(default=800)
    scale_on_hover = models.BooleanField(default=False)
    animation_enabled = models.BooleanField(default=False)
    animation_type = models.CharField(max_length=50, blank=True, default="")


    # Location
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True, blank=True)

    # Visibility and sharing
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='Public'
    )

    # Engagement
    view_count = models.IntegerField(default=0)

    system_notes = ArrayField(
        models.TextField(),
        blank=True,
        default=list
    )

    # Tags
    tags = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )



    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.title} by {self.creator.username}"
    

    @property
    def like_count(self):
        likes_count = TextObjectLike.objects.filter(text_object=self).count()
        return likes_count


    def moderate_url(self):
        ACCEPTABLE_IMAGE_HOSTS = {
            "postimg.cc",
            "ibb.co",
            "imgbox.com",
            "flickr.com",
            "imageshack.com",
            "cloudinary.com",
            "imgpile.com",
            "smugmug.com",
            "photobucket.com",
            "googleusercontent.com",
            "staticflickr.com",
            "githubusercontent.com",
        }

        moderation_passed = True
        failure_reasons = []

        urls_to_check = [
            {"type": "model", "url": self.model_url},
            {"type": "texture", "url": self.texture_url},
        ]

        for entry in urls_to_check:
            if not entry["url"]:
                continue  # Skip blank URLs

            parsed = urlparse(entry["url"])
            domain = parsed.netloc.split(":")[0].lower()

            # Special Imgur rule for UK objects
            if domain == "imgur.com" and (
                49.9 <= self.latitude <= 60.9 and -8.2 <= self.longitude <= 1.8
            ):
                failure_reasons.append(
                    f"Imgur links are not allowed for UK-based objects ({entry['type']})."
                )
                moderation_passed = False
                continue  # No point running whitelist check after this

            # Strict whitelist check
            if domain not in ACCEPTABLE_IMAGE_HOSTS:
                failure_reasons.append(
                    f"Host '{domain}' is not approved ({entry['type']})."
                )
                moderation_passed = False

        if not moderation_passed:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for reason in failure_reasons:
                self.system_notes.append(f"{timestamp}: Failed for reason: {reason}")

            self.visibility = "Suspended"
            self.save(update_fields=["visibility"])


    def save(self, *args, **kwargs):
        # Auto-moderate on creation and edit
        text_moderation = self.moderate_text()
        url_moderation = self.moderate_url()

        super().save(*args, **kwargs)


class ImageObjectInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text_object = models.ForeignKey(ARTextObject, on_delete=models.CASCADE, related_name='image_interactions')
    created_at = models.DateTimeField(auto_now_add=True)

    liked = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'text_object')

    def __str__(self):
        return f"{self.user.username} likes {self.text_object.title}"


