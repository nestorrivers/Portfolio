from django.db import models
from django.conf import settings
from django.utils import timezone

from django.contrib.postgres.fields import ArrayField


class TextObjectReport(models.Model):
    REASON_CHOICES = [
        ('Inappropriate Content', 'Inappropriate Content'),
        ('Spam', 'Spam'),
        ('Harassment', 'Harassment'),
        ('Other', 'Other'),
    ]

    ar_object = models.ForeignKey('objects.ARTextObject', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='object_reports')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    additional_info = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    action_taken = models.TextField(blank=True)

    message_to_reporter = models.TextField(blank=True)
    message_to_user = models.TextField(blank=True)

    system_notes = ArrayField(models.TextField(), default=list, blank=True)
    user_notes = ArrayField(models.TextField(), default=list, blank=True)

    def mark_reviewed(self, action_taken):
        self.reviewed = True
        self.reviewed_at = timezone.now()
        self.action_taken = action_taken
        self.save()


class RestrictedArea(models.Model): 

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True) 

    # List of [latitude, longitude] points defining the boundary
    boundary = models.JSONField()    


    # Allows different types of restrictions
    RESTRICTION_TYPES = ( 
                        ("safety", "Safety"), 
                        ("privacy", "Privacy"), 
                        ("legal", "Legal"), 
                        ("sensitive", "Sensitive Location"), 
                        )
    
    restriction_type = models.CharField( max_length=20, choices=RESTRICTION_TYPES )
    
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self): return self.name

    def contains_point(self, latitude, longitude):
        inside = False
        j = len(self.boundary) - 1

        for i in range(len(self.boundary)):
            lat_i, lon_i = self.boundary[i]
            lat_j, lon_j = self.boundary[j]

            if (
                (lat_i > latitude) != (lat_j > latitude)
                and longitude <
                (lon_j - lon_i)
                * (latitude - lat_i)
                / (lat_j - lat_i)
                + lon_i
            ):
                inside = not inside

            j = i

        return inside