from os import name
from django import forms
from .models import ARChannel



CHANNEL_TYPE_CHOICES = [
        ('Public', 'Public'),
        ('Verified', 'Verified Creators'),
        ('Seasonal', 'Seasonal/Event'),
        ('Private', 'Private'),
    ]

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


class ARChannelForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, label="Channel Name")
    description = forms.CharField(widget=forms.Textarea, required=False, label="Description")
    channel_type = forms.ChoiceField(choices=CHANNEL_TYPE_CHOICES, required=True, label="Channel Type")
    theme = forms.ChoiceField(choices=CHANNEL_THEMES, required=False, label="Theme")
    start_date = forms.DateTimeField(required=False, label="Start Date")
    end_date = forms.DateTimeField(required=False, label="End Date")

    is_active = forms.BooleanField(required=False, initial=True, label="Is Active")

    class Meta:
        model = ARChannel
        fields = ['name', 'description', 'channel_type', 'start_date', 'end_date', 'is_active']



