from django.apps import AppConfig


class ChallengesConfig(AppConfig):
    name = "challenges"

    def ready(self):
        # Importing the package registers every generator with the engine.
        from . import generators  # noqa: F401
