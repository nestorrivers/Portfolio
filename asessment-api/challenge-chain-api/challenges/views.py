from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attempt, Challenge


def _load(request, key):
    """404 for both "doesn't exist" and "not yours" so keys can't be probed."""
    return get_object_or_404(
        Challenge.objects.select_related("session"), key=key, session__players=request.user
    )


def _is_unlocked(challenge, user) -> bool:
    previous = challenge.previous()
    return previous is None or Attempt.objects.filter(
        challenge=previous, player=user, solved_at__isnull=False
    ).exists()


def _link(challenge):
    return {"key": challenge.key, "url": reverse("challenge-detail", args=[challenge.key])}


class ChallengeDetail(APIView):
    """GET the challenge. The first successful fetch starts the player's clock."""

    def get(self, request, key):
        challenge = _load(request, key)
        if not _is_unlocked(challenge, request.user):
            return Response({"error": "Solve the previous challenge first."}, status=403)

        attempt, _ = Attempt.objects.get_or_create(challenge=challenge, player=request.user)
        if attempt.status != Attempt.Status.OPEN:
            return Response({"error": f"This challenge is already {attempt.status}."}, status=409)

        return Response(
            {
                "position": challenge.position,
                "total": challenge.session.challenges.count(),
                "kind": challenge.kind,
                "prompt": challenge.prompt,
                "payload": challenge.payload,
                "submit_url": reverse("challenge-submit", args=[challenge.key]),
            }
        )


class ChallengeSubmit(APIView):
    """POST {"solution": ...}. A correct answer returns the link to the next challenge."""

    @transaction.atomic
    def post(self, request, key):
        challenge = _load(request, key)
        if not isinstance(request.data, dict) or "solution" not in request.data:
            return Response({"error": "Body must be a JSON object with a 'solution'."}, status=400)

        attempt = (
            Attempt.objects.select_for_update()
            .filter(challenge=challenge, player=request.user)
            .first()
        )
        if attempt is None:
            return Response({"error": "Fetch the challenge before submitting."}, status=409)
        if attempt.status != Attempt.Status.OPEN:
            return Response({"error": f"This challenge is already {attempt.status}."}, status=409)

        correct = attempt.submit(request.data["solution"])
        body = {
            "correct": correct,
            "status": attempt.status,
            "elapsed_seconds": round(attempt.elapsed_seconds, 3),
        }
        if correct:
            following = challenge.next()
            body["next"] = _link(following) if following else None
            body["complete"] = following is None
        return Response(body)
