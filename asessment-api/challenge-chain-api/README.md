# challenge-chain-api

A small Django REST service that serves **chained, deterministically generated challenges** over HTTP. There is no front end: the API *is* the interface. A player fetches a challenge, solves it in their own code, posts the answer, and is handed a link to the next one.

It's deliberately compact: two endpoints, a pluggable generator engine, and a test suite.

## What it does

Most puzzle platforms are built around a web page. This one is built around a protocol. Each challenge is a small, well-defined data problem (sort these numbers, compute this checksum), and the player's job is to write a client that follows the chain: fetch, solve, submit, follow the `next` link, repeat until the response says `"complete": true`.

Because the interface is just HTTP and JSON, players can work in any language and any tooling. Solving it well means handling auth headers, parsing responses, following links and dealing with failure, as well as getting the answer right.

A typical run looks like this:

1. A **session** is created from a seed, a difficulty and a list of challenge kinds. The engine generates every challenge up front and stores it with its expected answer.
2. A player is enrolled in the session and given a token and the first challenge's URL.
3. The player `GET`s that challenge and receives a prompt and a payload (for example a list of integers).
4. They `POST` a solution. If it's correct, the response includes the URL of the next challenge; if not, the attempt is closed.
5. The final correct submission returns `"complete": true`.

## How challenges are generated

Each challenge kind is a generator: a function that takes a seeded random number generator and a difficulty, and returns three things: a **prompt** (what to do), a **payload** (the data to do it to) and the **expected answer**. The engine calls the generators, shuffles the running order from the seed, and stores the results.

Everything derives from the session seed, so two sessions with the same seed contain identical challenges in identical order. That makes runs reproducible and comparable, and makes the generators easy to test. Difficulty changes the size and range of the data rather than the rules of the task.

The two bundled generators are intentionally simple:

- **`sorting`** returns a list of integers to sort. Higher difficulties mean longer lists, larger values and negatives.
- **`checksum`** returns a string and a modulus, and the prompt gives the formula to apply. Higher difficulties mean longer strings and larger moduli.

The registry is the point of the design: a new challenge kind is one function with a decorator, and nothing else in the codebase has to change.

## Endpoints

All requests need `Authorization: Bearer <token>`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/challenges/<key>/` | Fetch a challenge. The first fetch starts the player's clock. |
| `POST` | `/api/v1/challenges/<key>/submit/` | Body: `{"solution": ...}`. A correct answer returns the link to the next challenge. |

Example submit response:

```json
{"correct": true, "status": "solved", "elapsed_seconds": 4.213,
 "next": {"key": "…", "url": "/api/v1/challenges/…/"}, "complete": false}
```

## Design notes

- **Generator registry.** Generators are plain functions registered with `@register("kind")` and return a `Spec` (prompt, payload, expected answer). Adding a challenge type is one small file. See `challenges/engine.py` and `challenges/generators/`.
- **Deterministic seeding.** Each challenge draws from its own `random.Random`, seeded from a SHA-256 of `(session seed, kind, position)`. The same seed always produces the same session, including running order, and the engine never touches global RNG state or Python's per-process `hash()`.
- **Pure engine.** `engine.py` has no Django imports, so it is trivially unit-testable.
- **Ordered unlock.** A challenge can only be fetched once the previous one is solved, enforced server-side rather than by keeping keys secret.
- **Server-side timing.** Elapsed time is measured from the server's record of the first fetch, so clients can't supply their own timestamps.
- **No key probing.** Unknown keys and keys belonging to other players both return `404`.
- **One submission settles an attempt.** A wrong answer fails the attempt permanently.
- **Answers stay server-side.** `expected` is never serialised.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py demo_session          # prints a token and the first challenge URL
python manage.py runserver
```

```bash
curl -H "Authorization: Bearer $TOKEN" localhost:8000$START_URL
curl -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"solution": [1, 2, 3]}' localhost:8000$START_URL/submit/
```

## Tests

```bash
python manage.py test
```

Covers determinism, difficulty scaling, auth, enrolment, unlock order, single-shot grading, and chain completion.

## Layout

```
challenges/
  engine.py        registry, seeding, planning (no Django)
  generators/      sorting.py, checksum.py
  models.py        Session, Challenge, Attempt
  views.py         the two endpoints
  tests.py
```