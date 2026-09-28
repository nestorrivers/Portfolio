from django.urls import path

from .views import ChallengeDetail, ChallengeSubmit

urlpatterns = [
    path("challenges/<str:key>/", ChallengeDetail.as_view(), name="challenge-detail"),
    path("challenges/<str:key>/submit/", ChallengeSubmit.as_view(), name="challenge-submit"),
]
