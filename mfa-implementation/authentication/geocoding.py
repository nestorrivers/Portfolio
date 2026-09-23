import googlemaps
from googlemaps import exceptions as gm_exceptions
from django.conf import settings

ADDRESS_FIELDS = (
    "address_line_1",
    "address_line_2",
    "town_city",
    "county",
    "postcode",
    "country",
)


class GeocodingError(Exception):
    """Raised when a location cannot be geocoded."""


def build_address(location):
    """Join the non-empty address fields with commas."""
    parts = (getattr(location, field) for field in ADDRESS_FIELDS)
    return ", ".join(part for part in parts if part)


def geocode_location(location):
    """Return "lat,lng" for the location's address, or raise GeocodingError."""
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        raise GeocodingError("Google Maps API key is not configured.")

    try:
        results = googlemaps.Client(key=api_key).geocode(build_address(location))
    except (
        ValueError,
        gm_exceptions.ApiError,
        gm_exceptions.HTTPError,
        gm_exceptions.Timeout,
        gm_exceptions.TransportError,
    ) as exc:
        raise GeocodingError("The address could not be checked. Please try again.") from exc

    if not results:
        raise GeocodingError("No results found for that address.")

    point = results[0]["geometry"]["location"]
    return f"{point['lat']},{point['lng']}"