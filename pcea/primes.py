# GPT/Claude generated; context, prompt Erin Spencer
"""
Prime circle for PCEA.

PRIME_CIRCLE is a fixed sequence of 53 primes used as the circular bases
for prime-circular base number encryption. The index wraps modulo CIRCLE_SIZE,
matching the prime-indexed topology convention used across this system.
"""

# === MODULE_BUILD ===
# id: pcea_primes
#   module_name: primes
#   module_kind: schema
#   summary: fixed 53-prime circle used as the circular bases for prime-circular base encryption
#   owner: Erin Spencer
#   public_surface: prime_at, PRIME_CIRCLE, CIRCLE_SIZE
#   internal_surface: _sieve
#   auth_boundary: none
#   storage_boundary: none
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: tests.test_primes
#   rollout: default_enabled
#   rollback: remove module and its references
#   requires: none
#   since: 2026-06-02
#   unresolved: none
# === END MODULE_BUILD ===

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
