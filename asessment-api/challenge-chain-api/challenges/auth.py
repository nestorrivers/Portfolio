from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    """`Authorization: Bearer <token>` instead of DRF's default `Token <token>`."""

    keyword = "Bearer"
