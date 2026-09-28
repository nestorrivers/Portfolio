from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from . import engine
from .models import Session


def make_session(players=(), seed="test-seed", difficulty="easy", per_kind=2):
    return Session.create(
        seed=seed,
        difficulty=difficulty,
        kinds=engine.available_kinds(),
        per_kind=per_kind,
        players=players,
    )


class EngineTests(APITestCase):
    def test_same_seed_gives_same_content_but_new_keys(self):
        a, b = make_session(), make_session()
        content = lambda s: [(c.kind, c.prompt, c.payload, c.expected) for c in s.challenges.all()]
        self.assertEqual(content(a), content(b))
        self.assertFalse(
            {c.key for c in a.challenges.all()} & {c.key for c in b.challenges.all()}
        )

    def test_different_seed_changes_content(self):
        a, b = make_session(seed="one"), make_session(seed="two")
        payloads = lambda s: [c.payload for c in s.challenges.all()]
        self.assertNotEqual(payloads(a), payloads(b))

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            Session.create(seed="x", difficulty="easy", kinds=["nope"])

    def test_difficulty_scales_output(self):
        easy = make_session(difficulty="easy").challenges.filter(kind="sorting").first()
        hard = make_session(difficulty="hard").challenges.filter(kind="sorting").first()
        self.assertLess(len(easy.payload["numbers"]), len(hard.payload["numbers"]))


class ApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.player = User.objects.create_user("player")
        self.outsider = User.objects.create_user("outsider")
        self.session = make_session(players=[self.player], per_kind=1)
        self.first, self.second = list(self.session.challenges.all())
        self.auth(self.player)

    def auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.key}")

    def get(self, challenge):
        return self.client.get(f"/api/v1/challenges/{challenge.key}/")

    def submit(self, challenge, solution):
        return self.client.post(
            f"/api/v1/challenges/{challenge.key}/submit/", {"solution": solution}, format="json"
        )

    def test_requires_bearer_token(self):
        self.client.credentials()
        self.assertEqual(self.get(self.first).status_code, 401)

    def test_non_players_get_404(self):
        self.auth(self.outsider)
        self.assertEqual(self.get(self.first).status_code, 404)

    def test_expected_output_is_never_exposed(self):
        body = self.get(self.first).json()
        self.assertNotIn("expected", body)
        self.assertEqual(body["position"], 1)
        self.assertEqual(body["total"], 2)

    def test_later_challenges_are_locked(self):
        self.assertEqual(self.get(self.second).status_code, 403)

    def test_must_fetch_before_submitting(self):
        self.assertEqual(self.submit(self.first, self.first.expected).status_code, 409)

    def test_correct_solution_unlocks_next(self):
        self.get(self.first)
        body = self.submit(self.first, self.first.expected).json()
        self.assertTrue(body["correct"])
        self.assertEqual(body["next"]["key"], self.second.key)
        self.assertFalse(body["complete"])
        self.assertEqual(self.get(self.second).status_code, 200)

    def test_wrong_solution_ends_the_attempt(self):
        self.get(self.first)
        body = self.submit(self.first, "wrong").json()
        self.assertFalse(body["correct"])
        self.assertEqual(body["status"], "failed")
        self.assertEqual(self.submit(self.first, self.first.expected).status_code, 409)
        self.assertEqual(self.get(self.second).status_code, 403)  # still locked

    def test_final_challenge_completes_the_chain(self):
        self.get(self.first)
        self.submit(self.first, self.first.expected)
        self.get(self.second)
        body = self.submit(self.second, self.second.expected).json()
        self.assertTrue(body["complete"])
        self.assertIsNone(body["next"])

    def test_malformed_body_is_a_400(self):
        self.get(self.first)
        response = self.client.post(
            f"/api/v1/challenges/{self.first.key}/submit/", {"answer": 1}, format="json"
        )
        self.assertEqual(response.status_code, 400)
