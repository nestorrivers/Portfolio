from os import name
from django import forms
from .models import FriendRequest




class FriendRequestForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Optional Message')
    class Meta:
        model = FriendRequest
        fields = ['receiver', 'message']