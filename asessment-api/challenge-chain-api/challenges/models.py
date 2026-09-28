import secrets

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from . import engine


def new_key() -> str:
    return secrets.token_urlsafe(16)


class Session(models.Model):
    """A chained set of challenges, generated from a seed and shared by its players."""

    seed = models.CharField(max_length=64)
    difficulty = models.CharField(max_length=10)
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="challenge_sessions", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    @transaction.atomic
    def create(cls, *, seed, difficulty, kinds, per_kind=2, players=()):
        order = engine.plan(seed, kinds, per_kind)  # validates kinds
        session = cls.objects.create(seed=seed, difficulty=difficulty)
        session.players.set(players)

        challenges = []
        for position, kind in enumerate(order, start=1):
            spec = engine.generate(seed, difficulty, kind, position)
            challenges.append(
                Challenge(
                    session=session,
                    position=position,
                    kind=kind,
                    prompt=spec.prompt,
                    payload=spec.payload,
                    expected=spec.expected,
                )
            )
        Challenge.objects.bulk_create(challenges)
        return session


class Challenge(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="challenges")
    position = models.PositiveIntegerField()
    # Unguessable handle: the only way to address a challenge over the API.
    key = models.CharField(max_length=32, unique=True, default=new_key)
    kind = models.CharField(max_length=40)
    prompt = models.TextField()
    payload = models.JSONField()
    expected = models.JSONField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "position"], name="unique_position_per_session"
            )
        ]

    def previous(self):
        return self.session.challenges.filter(position__lt=self.position).order_by("-position").first()

    def next(self):
        return self.session.challenges.filter(position__gt=self.position).first()


class Attempt(models.Model):
    """One player's go at one challenge. The clock starts when they first fetch it."""

    class Status(models.TextChoices):
        OPEN = "open"
        SOLVED = "solved"
        FAILED = "failed"

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="attempts")
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="challenge_attempts"
    )
    started_at = models.DateTimeField(default=timezone.now)
    solved_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["challenge", "player"], name="one_attempt_per_player")
        ]

    @property
    def status(self) -> str:
        if self.solved_at:
            return self.Status.SOLVED
        if self.failed_at:
            return self.Status.FAILED
        return self.Status.OPEN

    @property
    def elapsed_seconds(self):
        end = self.solved_at or self.failed_at
        return (end - self.started_at).total_seconds() if end else None

    def submit(self, solution) -> bool:
        """Grade a solution. One submission settles the attempt either way."""
        correct = solution == self.challenge.expected
        if correct:
            self.solved_at = timezone.now()
        else:
            self.failed_at = timezone.now()
        self.save(update_fields=["solved_at", "failed_at"])
        return correct
