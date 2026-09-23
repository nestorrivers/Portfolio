"""
Integration points.

These two functions are the only place this app decides who may approve
things. To plug the app into an existing project, rewrite them to use
that project's groups or permissions, for example:
    return user.has_perm("authentication.approve_location")
"""


def can_authenticate_users(user):
    profile = getattr(user, "profile", None)
    return bool(profile and profile.authorised_to_authenticate_users)


def can_approve_locations(user):
    profile = getattr(user, "profile", None)
    return bool(profile and profile.authorised_to_approve_authorised_locations)