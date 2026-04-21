# GPT/Claude generated; context, prompt Erin Spencer
"""
Prime-circular base number cipher.

Operates on seeds: each seed is a 7×7 structure (7 circles × 7 tensors).
Each circle is itself a tensor; each seed is itself a tensor. The same
operation applies at every level.

For each tensor at (circle_idx, tensor_idx), the prime is:
    p = prime_at(circle_idx * 7 + tensor_idx)

The key stream draws from the tensor's own last_state value and the values
at its heptagram neighbors — circles (circle_idx ± 3) % 7 — implementing
the interlocking property of the seven-disk structure.

    Encrypt: e_j = ((v_j - 1 + k_j) mod p) + 1
    Decrypt: v_j = ((e_j - 1 - k_j) mod p) + 1
"""
from __future__ import annotations

from .codec import from_bijective, to_bijective
from .kdf import key_stream
from .primes import prime_at

CIRCLE_COUNT = 7
TENSOR_COUNT = 7


def _validate_seed(s: list[list[int]], name: str) -> None:
    if len(s) != CIRCLE_COUNT or any(len(row) != TENSOR_COUNT for row in s):
        raise ValueError(f"{name} must be a {CIRCLE_COUNT}×{TENSOR_COUNT} integer array")


def _contributors(last_seed: list[list[int]], circle_idx: int, tensor_idx: int) -> list[int]:
    """Own value plus heptagram neighbors (±3 mod 7)."""
    return [
        last_seed[circle_idx][tensor_idx],
        last_seed[(circle_idx - 3) % CIRCLE_COUNT][tensor_idx],
        last_seed[(circle_idx + 3) % CIRCLE_COUNT][tensor_idx],
    ]


def _encrypt_element(
    value: int,
    seed_idx: int,
    circle_idx: int,
    tensor_idx: int,
    last_seed: list[list[int]],
) -> int:
    if value == 0:
        return 0
    p = prime_at(circle_idx * TENSOR_COUNT + tensor_idx)
    sign = -1 if value < 0 else 1
    v_digits = to_bijective(abs(value), p)
    k_digits = key_stream(_contributors(last_seed, circle_idx, tensor_idx), seed_idx, circle_idx, tensor_idx, len(v_digits), p)
    e_digits = [((vd - 1 + kd) % p) + 1 for vd, kd in zip(v_digits, k_digits)]
    return sign * from_bijective(e_digits, p)


def _decrypt_element(
    encrypted: int,
    seed_idx: int,
    circle_idx: int,
    tensor_idx: int,
    last_seed: list[list[int]],
) -> int:
    if encrypted == 0:
        return 0
    p = prime_at(circle_idx * TENSOR_COUNT + tensor_idx)
    sign = -1 if encrypted < 0 else 1
    e_digits = to_bijective(abs(encrypted), p)
    k_digits = key_stream(_contributors(last_seed, circle_idx, tensor_idx), seed_idx, circle_idx, tensor_idx, len(e_digits), p)
    v_digits = [((ed - 1 - kd) % p) + 1 for ed, kd in zip(e_digits, k_digits)]
    return sign * from_bijective(v_digits, p)


def encrypt_seed(
    seed: list[list[int]],
    last_seed: list[list[int]],
    seed_idx: int = 0,
) -> list[list[int]]:
    """
    Encrypt a seed (7×7 tensor) using last_seed as the key source.

    Args:
        seed:      7×7 integer array — current architecture state for this seed.
        last_seed: 7×7 integer array — previous seed state.
        seed_idx:  position of this seed in the architecture.

    Returns:
        Encrypted seed as a 7×7 integer array.
    """
    _validate_seed(seed, "seed")
    _validate_seed(last_seed, "last_seed")
    return [
        [
            _encrypt_element(seed[c][t], seed_idx, c, t, last_seed)
            for t in range(TENSOR_COUNT)
        ]
        for c in range(CIRCLE_COUNT)
    ]


def decrypt_seed(
    encrypted: list[list[int]],
    last_seed: list[list[int]],
    seed_idx: int = 0,
) -> list[list[int]]:
    """
    Decrypt a seed produced by encrypt_seed given the same last_seed.

    Args:
        encrypted: 7×7 integer array as returned by encrypt_seed.
        last_seed: the same last_seed used during encryption.
        seed_idx:  position of this seed in the architecture.

    Returns:
        Recovered seed as a 7×7 integer array.
    """
    _validate_seed(encrypted, "encrypted")
    _validate_seed(last_seed, "last_seed")
    return [
        [
            _decrypt_element(encrypted[c][t], seed_idx, c, t, last_seed)
            for t in range(TENSOR_COUNT)
        ]
        for c in range(CIRCLE_COUNT)
    ]


def encrypt_state(state: list[list[list[int]]], last_state: list[list[list[int]]]) -> list[list[list[int]]]:
    """Encrypt a full architecture state: list of seeds."""
    if not state:
        return []
    if len(state) != len(last_state):
        raise ValueError("state and last_state must contain the same number of seeds")
    return [encrypt_seed(state[i], last_state[i], i) for i in range(len(state))]


def decrypt_state(encrypted: list[list[list[int]]], last_state: list[list[list[int]]]) -> list[list[list[int]]]:
    """Decrypt a full architecture state: list of seeds."""
    if not encrypted:
        return []
    if len(encrypted) != len(last_state):
        raise ValueError("encrypted and last_state must contain the same number of seeds")
    return [decrypt_seed(encrypted[i], last_state[i], i) for i in range(len(encrypted))]
