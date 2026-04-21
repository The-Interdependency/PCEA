# GPT/Claude generated; context, prompt Erin Spencer
"""
Hash-based key derivation for PCEA.

Key stream is derived from the hierarchical address (seed, circle, tensor)
and the values at that position plus its heptagram neighbors in the circle
dimension (±3 mod 7, the PTCA adjacency rule). This means each tensor's
encryption depends on its own last_state value AND the last_state of the
two circles it interlocks with — implementing the circular interlocking
property of the seven-disk structure.
"""
from __future__ import annotations

import hashlib


def key_stream(
    contributors: list[int],
    seed_idx: int,
    circle_idx: int,
    tensor_idx: int,
    length: int,
    p: int,
) -> list[int]:
    """
    Derive `length` key digits in [0, p-1] via SHA-256.

    Args:
        contributors: [own_val, left_neighbor_val, right_neighbor_val] —
                      the last_state values at (circle_idx, tensor_idx),
                      ((circle_idx - 3) % 7, tensor_idx), and
                      ((circle_idx + 3) % 7, tensor_idx).
        seed_idx:     index of the seed in the architecture.
        circle_idx:   index of the circle within the seed (0..6).
        tensor_idx:   index of the tensor within the circle (0..6).
        length:       number of key digits to produce.
        p:            prime base; digits are reduced mod p.

    Returns:
        List of `length` integers, each in [0, p-1].
    """
    contrib_str = ":".join(str(c) for c in contributors)
    raw = bytearray()
    counter = 0
    while len(raw) < length:
        payload = f"{contrib_str}:{seed_idx}:{circle_idx}:{tensor_idx}:{counter}".encode()
        raw.extend(hashlib.sha256(payload).digest())
        counter += 1
    return [b % p for b in raw[:length]]
