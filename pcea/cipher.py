# GPT/Claude generated; context, prompt Erin Spencer
"""
Prime-circular Möbius disk cipher.

Each tensor value is first mapped to an unsigned position on a Möbius disk
(mobius_encode), then encoded as a fixed-width sequence of base-p digits.
Each digit is additively shifted by a key digit from the SHA-256 key stream.
The result is an unsigned integer of fixed magnitude — sign and original
magnitude do not leak.

    Encrypt digit: e_j = (v_j + k_j) mod p
    Decrypt digit: v_j = (e_j - k_j) mod p

Prime selection: p = prime_at(circle_idx * 7 + tensor_idx)
Fixed digit count: k = digit_count(p, word_bits)
Key: SHA-256(own + heptagram neighbors ±3, seed_idx, circle_idx, tensor_idx)
"""

# === MODULE_BUILD ===
# id: pcea_cipher
#   module_name: cipher
#   module_kind: engine
#   summary: prime-circular Mobius disk cipher: fixed-width base-p digit encode with SHA-256 keyed additive shift
#   owner: Erin Spencer
#   public_surface: encrypt_seed, decrypt_seed, encrypt_state, decrypt_state, CIRCLE_COUNT, TENSOR_COUNT, DEFAULT_WORD_BITS
#   internal_surface: _validate_seed, _contributors, _encrypt_element, _decrypt_element
#   auth_boundary: none
#   storage_boundary: none
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: tests.test_cipher
#   rollout: default_enabled
#   rollback: remove module and its references
#   requires: pcea_codec, pcea_kdf, pcea_primes
#   since: 2026-06-02
#   unresolved: security-critical module; changes require independent crypto review
# === END MODULE_BUILD ===

from __future__ import annotations

from .codec import digit_count, from_fixed, mobius_decode, mobius_encode, to_fixed
from .kdf import key_stream
from .primes import prime_at

CIRCLE_COUNT = 7
TENSOR_COUNT = 7
DEFAULT_WORD_BITS = 64


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
    word_bits: int,
) -> int:
    p = prime_at(circle_idx * TENSOR_COUNT + tensor_idx)
    k = digit_count(p, word_bits)
    u = mobius_encode(value, word_bits)
    v_digits = to_fixed(u, p, k)
    ks = key_stream(_contributors(last_seed, circle_idx, tensor_idx), seed_idx, circle_idx, tensor_idx, k, p)
    e_digits = [(vd + kd) % p for vd, kd in zip(v_digits, ks)]
    return from_fixed(e_digits, p)


def _decrypt_element(
    encrypted: int,
    seed_idx: int,
    circle_idx: int,
    tensor_idx: int,
    last_seed: list[list[int]],
    word_bits: int,
) -> int:
    p = prime_at(circle_idx * TENSOR_COUNT + tensor_idx)
    k = digit_count(p, word_bits)
    e_digits = to_fixed(encrypted, p, k)
    ks = key_stream(_contributors(last_seed, circle_idx, tensor_idx), seed_idx, circle_idx, tensor_idx, k, p)
    v_digits = [(ed - kd) % p for ed, kd in zip(e_digits, ks)]
    u = from_fixed(v_digits, p)
    return mobius_decode(u, word_bits)


def encrypt_seed(
    seed: list[list[int]],
    last_seed: list[list[int]],
    seed_idx: int = 0,
    word_bits: int = DEFAULT_WORD_BITS,
) -> list[list[int]]:
    """
    Encrypt a seed (7×7 tensor) using last_seed as the key source.

    Args:
        seed:      7×7 integer array — current architecture state for this seed.
        last_seed: 7×7 integer array — previous seed state.
        seed_idx:  position of this seed in the architecture.
        word_bits: Möbius disk size in bits; must match between encrypt and decrypt.

    Returns:
        Encrypted seed as a 7×7 array of unsigned integers.
    """
    _validate_seed(seed, "seed")
    _validate_seed(last_seed, "last_seed")
    return [
        [
            _encrypt_element(seed[c][t], seed_idx, c, t, last_seed, word_bits)
            for t in range(TENSOR_COUNT)
        ]
        for c in range(CIRCLE_COUNT)
    ]


def decrypt_seed(
    encrypted: list[list[int]],
    last_seed: list[list[int]],
    seed_idx: int = 0,
    word_bits: int = DEFAULT_WORD_BITS,
) -> list[list[int]]:
    """
    Decrypt a seed produced by encrypt_seed given the same last_seed and word_bits.

    Args:
        encrypted: 7×7 array as returned by encrypt_seed.
        last_seed: the same last_seed used during encryption.
        seed_idx:  position of this seed in the architecture.
        word_bits: Möbius disk size in bits; must match the value used during encryption.

    Returns:
        Recovered seed as a 7×7 integer array.
    """
    _validate_seed(encrypted, "encrypted")
    _validate_seed(last_seed, "last_seed")
    return [
        [
            _decrypt_element(encrypted[c][t], seed_idx, c, t, last_seed, word_bits)
            for t in range(TENSOR_COUNT)
        ]
        for c in range(CIRCLE_COUNT)
    ]


def encrypt_state(
    state: list[list[list[int]]],
    last_state: list[list[list[int]]],
    word_bits: int = DEFAULT_WORD_BITS,
) -> list[list[list[int]]]:
    """Encrypt a full architecture state: list of seeds."""
    if not state:
        return []
    if len(state) != len(last_state):
        raise ValueError("state and last_state must contain the same number of seeds")
    return [encrypt_seed(state[i], last_state[i], i, word_bits) for i in range(len(state))]


def decrypt_state(
    encrypted: list[list[list[int]]],
    last_state: list[list[list[int]]],
    word_bits: int = DEFAULT_WORD_BITS,
) -> list[list[list[int]]]:
    """Decrypt a full architecture state: list of seeds."""
    if not encrypted:
        return []
    if len(encrypted) != len(last_state):
        raise ValueError("encrypted and last_state must contain the same number of seeds")
    return [decrypt_seed(encrypted[i], last_state[i], i, word_bits) for i in range(len(encrypted))]
