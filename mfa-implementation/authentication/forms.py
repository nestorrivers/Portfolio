from django import forms
from .models import *


class NewAuthorisedLocationForm(forms.ModelForm):
    name = forms.CharField(label="Name", max_length=100, required=True)
    address_line_1 = forms.CharField(
        label="Address Line 1", max_length=100, required=True
    )
    address_line_2 = forms.CharField(
        label="Address Line 2", max_length=100, required=False
    )
    town_city = forms.CharField(label="Town/City", max_length=100, required=True)
    county = forms.CharField(label="County", max_length=100, required=False)
    postcode = forms.CharField(label="Postcode", max_length=100, required=True)
    country = forms.CharField(label="Country", max_length=100, required=True)

    radius = forms.DecimalField(
        label="Radius (miles)",
        max_digits=5,
        decimal_places=2,
        required=True,
        min_value=0.00,
        max_value=5.00,
    )

    user_specific = forms.BooleanField(label="User Specific", required=False)

    class Meta:
        model = AuthorisedLocation
        fields = [
            "name",
            "address_line_1",
            "address_line_2",
            "town_city",
            "county",
            "postcode",
            "country",
            "radius",
            "user_specific",
        ]
