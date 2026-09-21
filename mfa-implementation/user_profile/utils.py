from django.core.mail import send_mass_mail
from .models import Profile
from haversine import haversine, Unit



def authorised_location_haversine(authorised_location, user_location):
    authorised_location = authorised_location.coordinates.split(",")
    authorised_location_lat_long = (
        float(authorised_location[0]),
        float(authorised_location[1]),
    )

    user_location = user_location.split(",")

    user_location_lat_long = (float(user_location[0]), float(user_location[1]))

    distance = haversine(
        authorised_location_lat_long, user_location_lat_long, unit=Unit.MILES
    )
    return distance


def send_user_authorisation_request(request, user, reason):
    recipient_list = []


    recipient_list.extend(
        list(
            Profile.objects.filter(
                authorised_to_authenticate_users=True
            ).values_list("user__email", flat=True)
        )
    )
    subject = f"User: {str(user.first_name)} {str(user.last_name)} requires login authorisation."
    message = f"""Hello,

        This email has been sent to request login authentication for user:

            ID: {str(user.pk)}
            Name: {str(user.first_name)} {str(user.last_name)}


        The reason for this request is: {reason}.
        To approve the booking, go to {request.get_host()}/authentication/authorise_pending_user/{user.pk}/.

        Kindly,
        the Chariot team."""

    send_mass_mail(
        subject=subject,
        message=message,
        from_email="",
        recipient_list=recipient_list,
    )


def get_user_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


