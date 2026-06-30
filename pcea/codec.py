# ratios: loc_comments=27:44 imports_exports=1:5 calls_definitions=8:5
# GPT/Claude generated; context, prompt Erin Spencer
"""
Möbius disk codec for PCEA.

Values are mapped to positions on a Möbius disk before encryption:
- mobius_encode: signed integer → unsigned position in {0..2^W - 1}
- mobius_decode: unsigned position → signed integer

The two sides of the disk are the two two's-complement halves. Positive
values sit in the lower half, negative values wrap to the upper half via
Python's natural modular arithmetic. An observer sees only the encrypted
position — the side (sign) is invisible without the key.

Fixed-width base-p encoding ensures the encrypted output always has exactly
k = digit_count(p, word_bits) digits, so the magnitude of the original
value does not leak through output length.

    mobius_encode(v, word_bits)   -> u in {0..2^W - 1}
    mobius_decode(u, word_bits)   -> v (signed)
    digit_count(p, word_bits)     -> k (fixed digit count for prime p)
    to_fixed(u, p, k)             -> k digits in {0..p-1}, little-endian
    from_fixed(digits, p)         -> unsigned integer
"""

# === MODULE_BUILD ===
# id: pcea_codec
#   module_name: codec
#   module_kind: adapter
#   summary: Mobius disk codec: signed<->unsigned position mapping and fixed-width base-p digit encoding
#   owner: Erin Spencer
#   public_surface: mobius_encode, mobius_decode, digit_count, to_fixed, from_fixed
#   internal_surface: none
#   auth_boundary: none
#   storage_boundary: none
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: tests.test_codec
#   rollout: default_enabled
#   rollback: remove module and its references
#   requires: none
#   since: 2026-06-02
#   unresolved: none
# === END MODULE_BUILD ===

from __future__ import annotations


def mobius_encode(v: int, word_bits: int) -> int:
    """Map signed integer v to unsigned position on the Möbius disk."""
    mask = (1 << word_bits) - 1
    return v & mask


def mobius_decode(u: int, word_bits: int) -> int:
    """Map unsigned Möbius disk position back to signed integer."""
    half = 1 << (word_bits - 1)
    return u if u < half else u - (1 << word_bits)


def digit_count(p: int, word_bits: int) -> int:
    """Fixed number of base-p digits needed to cover the full Möbius disk (2^word_bits positions)."""
    k = 0
    capacity = 1
    while capacity < (1 << word_bits):
        capacity *= p
        k += 1
    return k


def to_fixed(u: int, p: int, k: int) -> list[int]:
    """Encode unsigned integer u as exactly k standard base-p digits, little-endian."""
    digits: list[int] = []
    for _ in range(k):
        digits.append(u % p)
        u //= p
    return digits


def from_fixed(digits: list[int], p: int) -> int:
    """Reconstruct unsigned integer from standard base-p digits, little-endian."""
    result = 0
    power = 1
    for d in digits:
        result += d * power
        power *= p
    return result
# ratios: loc_comments=27:44 imports_exports=1:5 calls_definitions=8:5
