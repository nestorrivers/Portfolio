# views.py
from django.http import JsonResponse
from math import radians, sin, cos, sqrt, atan2
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum, F
from datetime import timedelta


from .models import ARChannel
from apps.objects.models import ARTextObject

from .models import ARTextObject


def get_channel_objects(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse([], safe=False)

    try:
        user_lat = float(request.GET.get("latitude"))
        user_lon = float(request.GET.get("longitude"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid coordinates"}, status=400)
    

    print(f"Fetching AR objects near ({user_lat}, {user_lon}) for user {user.username}")

    # ------------------
    # BOUNDING BOX CALC
    # ------------------
    lat_delta = 0.00045
    abs_lat = abs(user_lat)

    if abs_lat >= 80:
        lon_delta = 0.005
    elif abs_lat >= 60:
        lon_delta = 0.00090 / cos(radians(user_lat))
    elif abs_lat >= 23.5:
        lon_delta = 0.00045 / cos(radians(user_lat))
    else:
        lon_delta = 0.00045 / max(cos(radians(user_lat)), 0.1)

    # ------------------ 
    # INITIAL QUERY
    # Only load fields used in the API
    # ------------------
    # Use meter-based deltas to reliably get a bounding box ~50m around the user
    radius_m = 50.0
    meters_per_deg_lat = 111320.0
    lat_delta = radius_m / meters_per_deg_lat
    cos_lat = max(cos(radians(user_lat)), 1e-6)
    lon_delta = radius_m / (meters_per_deg_lat * cos_lat)

    qs = (
        ARTextObject.objects
        .filter(
            latitude__gte=user_lat - lat_delta,
            latitude__lte=user_lat + lat_delta,
            longitude__gte=user_lon - lon_delta,
            longitude__lte=user_lon + lon_delta,
        )
        .only(
            "id", "latitude", "longitude", "text_content", 
            "font", "font_size", "text_align", "text_colour",
            "object_colour", "shape", "width", "height", "depth",
            "rotation_x", "rotation_y", "rotation_z"
        )
    )

    # ------------------
    # HAVERSINE FUNCTION
    # ------------------
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = map(radians, (lat1, lat2))
        dphi = radians(lat2 - lat1)
        dlambda = radians(lon2 - lon1)

        a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*(sin(dlambda/2)**2)
        return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    # ------------------
    # PROCESS RESULTS
    # ------------------
    results = []
    updated_ids = []

    for obj in qs:
        if haversine(user_lat, user_lon, obj.latitude, obj.longitude) <= 50:
            results.append({
                "id": obj.id,
                "text": obj.text_content,
                "shape": obj.shape,
                "width": obj.width,
                "height": obj.height,
                "depth": obj.depth,
                "rotation": [obj.rotation_x, obj.rotation_y, obj.rotation_z],
                "latitude": obj.latitude,
                "longitude": obj.longitude,
            })
            updated_ids.append(obj.id)

    # ------------------
    # BULK UPDATE VIEWS
    # ------------------
    if updated_ids:
        ARTextObject.objects.filter(id__in=updated_ids).update(
            view_count=F("view_count") + 1
        )

    print(f"Returned {len(results)} AR objects for user at ({user_lat}, {user_lon})")
    for res in results:
        print(f" - AR Object ID {res['id']} at ({res['latitude']}, {res['longitude']})")
    return JsonResponse(results, safe=False)


def get_friends_objects(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse([], safe=False)

    friends = user.friends.all()
    friend_ids = [friend.id for friend in friends]

    qs = ARTextObject.objects.filter(creator__id__in=friend_ids).only(
        "id", "latitude", "longitude", "text_content", 
        "font", "font_size", "text_align", "text_colour",
        "object_colour", "shape", "width", "height", "depth",
        "rotation_x", "rotation_y", "rotation_z"
    )

    results = []
    updated_ids = []

    for obj in qs:
        results.append({
            "id": obj.id,
            "text": obj.text_content,
            "shape": obj.shape,
            "width": obj.width,
            "height": obj.height,
            "depth": obj.depth,
            "rotation": [obj.rotation_x, obj.rotation_y, obj.rotation_z],
            "latitude": obj.latitude,
            "longitude": obj.longitude,
        })
        updated_ids.append(obj.id)

    if updated_ids:
        ARTextObject.objects.filter(id__in=updated_ids).update(
            view_count=F("view_count") + 1
        )

    return JsonResponse(results, safe=False)



