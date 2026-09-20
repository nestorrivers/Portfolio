
from os import name
from django import forms
from .models import TextObjectReport




class TextObjectReportForm(forms.ModelForm):
    ACTION_CHOICES = [
        ('No Action', 'No Action'),
        ('Warn User', 'Warn User'),
        ('Remove Object', 'Remove Object'),
        ('Ban User', 'Ban User'),
    ]

    action_taken = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    ban_expiration = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}), required=False)
    message_to_reporter = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    message_to_user = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = TextObjectReport
        fields = ['action_taken']


class BanUserForm(forms.Form):
    ban_expiration = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}), required=True)
    ban_reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    message_to_user = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)


class UnbanUserForm(forms.Form):
    message_to_user = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    