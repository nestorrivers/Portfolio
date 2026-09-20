from os import name
from django import forms
from .models import NewsPost




class NewsPostForm(forms.ModelForm):

    title = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated tags'}))

    class Meta:
        model = NewsPost
        fields = ['title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated tags'}),
        }


