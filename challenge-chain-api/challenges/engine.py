"""Challenge generation engine.

Pure Python, no Django imports: a registry of generator functions plus
deterministic seeding, so the same (seed, difficulty, kinds) always yields the
same challenge set.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Callable

DIFFICULTIES = ("easy", "medium", "hard")


@dataclass(frozen=True)
class Spec:
    """What a generator returns: everything needed to store one challenge."""

    prompt: str
    payload: dict[str, Any]  # shown to the player
    expected: Any  # never shown; compared against the submitted solution


Generator = Callable[[random.Random, str], Spec]
_REGISTRY: dict[str, Generator] = {}


def register(kind: str) -> Callable[[Generator], Generator]:
    """Decorator: `@register("sorting")` adds a generator under that kind."""

    def decorator(fn: Generator) -> Generator:
        if kind in _REGISTRY:
            raise ValueError(f"generator already registered: {kind}")
        _REGISTRY[kind] = fn
        return fn

    return decorator


def available_kinds() -> list[str]:
    return sorted(_REGISTRY)


def derive_seed(*parts: object) -> int:
    """Stable across processes and Python versions (unlike built-in hash())."""
    digest = hashlib.sha256(":".join(map(str, parts)).encode()).digest()
    return int.from_bytes(digest[:8], "big")


def plan(seed: str, kinds: list[str], per_kind: int) -> list[str]:
    """Running order for a session: kinds shuffled by the seed, `per_kind` of each in a row."""
    unknown = [k for k in kinds if k not in _REGISTRY]
    if unknown:
        raise ValueError(f"unknown challenge kind(s): {', '.join(unknown)}")
    shuffled = list(kinds)
    random.Random(derive_seed(seed, "order")).shuffle(shuffled)
    return [kind for kind in shuffled for _ in range(per_kind)]


def generate(seed: str, difficulty: str, kind: str, position: int) -> Spec:
    """Build one challenge. Each (seed, kind, position) gets its own independent RNG."""
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"difficulty must be one of {DIFFICULTIES}")
    rng = random.Random(derive_seed(seed, kind, position))
    return _REGISTRY[kind](rng, difficulty)
