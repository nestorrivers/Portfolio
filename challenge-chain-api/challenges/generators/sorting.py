from ..engine import Spec, register

# difficulty -> (min length, max length, magnitude of values)
PARAMS = {
    "easy": (5, 8, 50),
    "medium": (8, 14, 500),
    "hard": (15, 30, 10_000),
}


@register("sorting")
def sorting(rng, difficulty):
    low, high, magnitude = PARAMS[difficulty]
    floor = 1 if difficulty == "easy" else -magnitude
    numbers = [rng.randint(floor, magnitude) for _ in range(rng.randint(low, high))]
    return Spec(
        prompt=f"Sort these {len(numbers)} integers in ascending order.",
        payload={"numbers": numbers},
        expected=sorted(numbers),
    )
