# GPT/Claude generated; context, prompt Erin Spencer
"""
Bijective prime-base codec for PCEA.

Bijective base-p encoding represents each positive integer with digits in
{1, ..., p}. Unlike standard base-p, there are no leading zeros, so every
positive integer has a unique representation of exactly ceil(log_p(n))
digits. This guarantees that encrypted values always have the same digit
count as the originals, making decryption unambiguous.

    to_bijective(n, p)        -> digits (little-endian, each in 1..p)
    from_bijective(digits, p) -> positive integer
    key_digits(key, n, p)     -> n digits of abs(key) in standard base p (0..p-1)
"""
from __future__ import annotations


def to_bijective(n: int, p: int) -> list[int]:
    """Decompose positive integer n into bijective base-p digits, little-endian."""
    if n <= 0:
        return []
    digits: list[int] = []
    while n > 0:
        d = n % p
        if d == 0:
            d = p
        digits.append(d)
        n = (n - d) // p
    return digits


def from_bijective(digits: list[int], p: int) -> int:
    """Reconstruct positive integer from bijective base-p digits, little-endian."""
    result = 0
    power = 1
    for d in digits:
        result += d * power
        power *= p
    return result


def key_digits(key: int, length: int, p: int) -> list[int]:
    """Extract `length` digits of abs(key) in standard base p (0..p-1), little-endian."""
    k = abs(key)
    out: list[int] = []
    for _ in range(length):
        out.append(k % p)
        k //= p
    return out
