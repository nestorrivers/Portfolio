import string

from ..engine import Spec, register

ALPHABET = string.ascii_letters + string.digits

# difficulty -> (min length, max length, modulus)
PARAMS = {
    "easy": (8, 16, 256),
    "medium": (24, 48, 65_536),
    "hard": (64, 128, 16_777_216),
}


@register("checksum")
def checksum(rng, difficulty):
    low, high, modulus = PARAMS[difficulty]
    data = "".join(rng.choices(ALPHABET, k=rng.randint(low, high)))
    value = sum(ord(char) * (i + 1) for i, char in enumerate(data)) % modulus
    return Spec(
        prompt=(
            "For each character, multiply its character code by its 1-based position, "
            "sum the results, and return that sum modulo `modulus`."
        ),
        payload={"data": data, "modulus": modulus},
        expected=value,
    )
