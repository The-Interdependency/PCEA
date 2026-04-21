# GPT/Claude generated; context, prompt Erin Spencer
"""
Hash-based key derivation for PCEA.

Derives a deterministic stream of key digits from (last_val, position) using
SHA-256. Each call yields 32 bytes; a counter extends the stream as needed.
This eliminates the key exhaustion and zero-passthrough weaknesses of direct
base-p decomposition of last_state values.
"""
from __future__ import annotations

import hashlib


def key_stream(last_val: int, position: int, length: int, p: int) -> list[int]:
    """
    Derive `length` key digits in [0, p-1] from (last_val, position) via SHA-256.

    Args:
        last_val: last_state element used as key source.
        position: element index in state; mixes into the hash so identical
                  last_val values at different positions yield different keys.
        length: number of key digits needed.
        p: prime base; digits are reduced mod p.

    Returns:
        List of `length` integers, each in [0, p-1].
    """
    raw = bytearray()
    counter = 0
    while len(raw) < length:
        payload = f"{last_val}:{position}:{counter}".encode()
        raw.extend(hashlib.sha256(payload).digest())
        counter += 1
    return [b % p for b in raw[:length]]
