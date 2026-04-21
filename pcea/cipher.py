# GPT/Claude generated; context, prompt Erin Spencer
"""
Prime-circular base number cipher.

For each index i, the prime p = prime_at(i) is the number base.
state[i] is decomposed into bijective base-p digits (each in {1, ..., p}).
Each digit is additively shifted by the corresponding digit of
last_state[i % L] in standard base p, then wrapped within {1, ..., p}:

    Encrypt: e_j = ((v_j - 1 + k_j) mod p) + 1
    Decrypt: v_j = ((e_j - 1 - k_j) mod p) + 1

The prime cycles circularly (CIRCLE_SIZE = 53), and the last_state key
source cycles with period L = len(last_state).
"""
from __future__ import annotations

from .codec import from_bijective, key_digits, to_bijective
from .primes import prime_at


def _encrypt_element(value: int, position: int, key: int) -> int:
    if value == 0:
        return 0
    p = prime_at(position)
    sign = -1 if value < 0 else 1
    v_digits = to_bijective(abs(value), p)
    k_digits = key_digits(key, len(v_digits), p)
    e_digits = [((vd - 1 + kd) % p) + 1 for vd, kd in zip(v_digits, k_digits)]
    return sign * from_bijective(e_digits, p)


def _decrypt_element(encrypted: int, position: int, key: int) -> int:
    if encrypted == 0:
        return 0
    p = prime_at(position)
    sign = -1 if encrypted < 0 else 1
    e_digits = to_bijective(abs(encrypted), p)
    k_digits = key_digits(key, len(e_digits), p)
    v_digits = [((ed - 1 - kd) % p) + 1 for ed, kd in zip(e_digits, k_digits)]
    return sign * from_bijective(v_digits, p)


def encrypt_state(state: list[int], last_state: list[int]) -> list[int]:
    """
    Encrypt state using last_state as the per-position key source.

    Args:
        state: current architecture state as a flat integer sequence.
        last_state: previous state; must be non-empty.

    Returns:
        Encrypted state as a flat integer sequence of the same length.
    """
    L = len(last_state)
    return [_encrypt_element(state[i], i, last_state[i % L]) for i in range(len(state))]


def decrypt_state(encrypted: list[int], last_state: list[int]) -> list[int]:
    """
    Decrypt state produced by encrypt_state given the same last_state.

    Args:
        encrypted: encrypted state as returned by encrypt_state.
        last_state: the same last_state used during encryption.

    Returns:
        Recovered state as a flat integer sequence.
    """
    L = len(last_state)
    return [_decrypt_element(encrypted[i], i, last_state[i % L]) for i in range(len(encrypted))]
