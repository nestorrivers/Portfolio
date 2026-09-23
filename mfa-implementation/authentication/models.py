from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class AuthorisedLocation(models.Model):

    name = models.CharField(
        max_length=100, blank=True, null=True
    )

    address_line_1 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Address Line 1"
    )

    address_line_2 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Address Line 2"
    )

    town_city = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Town or City"
    )

    county = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="County"
    )

    postcode = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Postcode"
    )

    country = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Country"
    )

    coordinates = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Coordinates"
    )


    radius = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        null=False,
        blank=False,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        verbose_name="Radius",
    )


    user_specific = models.BooleanField(default=False, verbose_name="User Specific"
    )


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="authorised_locations",
    )

    approved_by_manager = models.BooleanField(
        default=False, verbose_name="Approved By Manager"
    )

    approving_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="approved_locations",
    )
