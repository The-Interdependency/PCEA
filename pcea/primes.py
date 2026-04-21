# GPT/Claude generated; context, prompt Erin Spencer
"""
Prime circle for PCEA.

PRIME_CIRCLE is a fixed sequence of 53 primes used as the circular bases
for prime-circular base number encryption. The index wraps modulo CIRCLE_SIZE,
matching the prime-indexed topology convention used across this system.
"""
from __future__ import annotations


def _sieve(limit: int) -> list[int]:
    composite = bytearray(limit + 1)
    primes: list[int] = []
    for n in range(2, limit + 1):
        if not composite[n]:
            primes.append(n)
            for m in range(n * n, limit + 1, n):
                composite[m] = 1
    return primes


CIRCLE_SIZE: int = 53
PRIME_CIRCLE: tuple[int, ...] = tuple(_sieve(1000)[:CIRCLE_SIZE])


def prime_at(index: int) -> int:
    """Return the prime at circular position index (wraps at CIRCLE_SIZE)."""
    return PRIME_CIRCLE[index % CIRCLE_SIZE]
