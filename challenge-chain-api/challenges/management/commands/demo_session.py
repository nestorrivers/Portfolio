from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.urls import reverse
from rest_framework.authtoken.models import Token

from challenges import engine
from challenges.models import Session


class Command(BaseCommand):
    help = "Create a demo player and session, and print a token plus the first challenge URL."

    def add_arguments(self, parser):
        parser.add_argument("--seed", default="demo")
        parser.add_argument("--difficulty", default="easy", choices=engine.DIFFICULTIES)
        parser.add_argument("--per-kind", type=int, default=2)

    def handle(self, *args, **opts):
        user, _ = get_user_model().objects.get_or_create(username="demo")
        token, _ = Token.objects.get_or_create(user=user)
        session = Session.create(
            seed=opts["seed"],
            difficulty=opts["difficulty"],
            kinds=engine.available_kinds(),
            per_kind=opts["per_kind"],
            players=[user],
        )
        first = session.challenges.first()
        self.stdout.write(f"token: {token.key}")
        self.stdout.write(f"start: {reverse('challenge-detail', args=[first.key])}")
