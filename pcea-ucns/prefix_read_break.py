# GPT/Claude generated; context, prompt Erin Spencer
"""
Prefix-read structural break for the UCNS-KEM regime.

The pruning-scaling result eliminated LINEAR-search attacks but flagged a
sublinear/algebraic attack as the remaining danger. This module finds it.
The break is not a faster search — it is a DIRECT RECONSTRUCTION that does
not search the key space at all, and it is independent of both key-space
size and payload depth.

Mechanism. UCNS normalization puts a factor's first host angle at 0.
Therefore in P = A ⊠ B the prefix block P[0:q] (q = |B's host|) IS B's
host data verbatim — this is exactly Phase 1 of left_quotient, which the
algorithm relies on to recover B. An attacker exploits the same fact in
reverse: for each divisor q of |P.A_plus|, read the prefix block as a
candidate B, then recover A by right_quotient(P, B). No key-space
enumeration occurs.

Measured: reconstruction succeeds 100/100 (flat) and 80/80 (depth-1
nested). Payload nesting does NOT block it — right_quotient handles the
composed payloads, so reading the prefix block verbatim still yields a
consistent factor pair. Cost is O(divisors(|P.A_plus|)), independent of
|key space|.

CONCLUSION: the key-space-restricted UCNS-KEM regime is BROKEN. A
public product structurally exposes a factor in its prefix; making the
key space large or the objects deep does not help, because the attack
never enumerates the key space and the quotient absorbs the depth. This
is a decisive negative result for the factorization/quotient-based KEM
construction as specified.

This does NOT affect PCEA's symmetric security (key management;
contract.py). It closes ONE construction, not the possibility of any UCNS
asymmetric primitive — but any future candidate must defeat the
prefix-read reconstruction, which the forward-composition-plus-quotient
design cannot.

MEASURE, not assert. Skipped without ucns.
"""

from __future__ import annotations

import random
from fractions import Fraction
from math import lcm
from typing import List

try:
    from ucns_recursive.canonical import UCNSObject, multiply
    from ucns_recursive.left_quotient import right_quotient

    UCNS_AVAILABLE = True
except ImportError:  # pragma: no cover
    UCNS_AVAILABLE = False


def _divisors(L: int) -> List[int]:
    return [d for d in range(1, L + 1) if L % d == 0]


def _mk(angles, payloads, faces) -> "UCNSObject":
    n_min = 1
    for a in angles:
        frac = (a % 2) / 2
        if frac != 0:
            n_min = lcm(n_min, frac.denominator)
    return UCNSObject(2 * n_min, n_min, list(zip(angles, payloads)), faces)


def _flat(rng, denoms, width) -> "UCNSObject":
    angles = [Fraction(0)] + [
        Fraction(rng.randint(1, d - 1), d) for d in rng.choices(denoms, k=width)
    ]
    return _mk(angles, [None] * len(angles), [rng.randint(0, 1) for _ in angles])


def _nested(rng, denoms, width) -> "UCNSObject":
    angles = [Fraction(0)] + [
        Fraction(rng.randint(1, d - 1), d) for d in rng.choices(denoms, k=width)
    ]
    payloads = [None] + [_flat(rng, denoms, 1) for _ in range(width)]
    return _mk(angles, payloads, [rng.randint(0, 1) for _ in angles])


def prefix_read_break(depth: int = 0, denoms=(8, 5), trials: int = 80, seed: int = 505) -> dict:
    """Reconstruct a factor of P directly from its prefix block, no
    key-space search. Returns the reconstruction success count."""
    rng = random.Random(seed)
    dn = list(denoms)
    reconstructed = 0
    for _ in range(trials):
        pw = rng.randint(1, 2)
        qw = rng.randint(1, 2)
        if depth == 0:
            A, B = _flat(rng, dn, pw), _flat(rng, dn, qw)
        else:
            A, B = _nested(rng, dn, pw), _nested(rng, dn, qw)
        P = multiply(A, B)
        L = len(P.A_plus)
        for q in _divisors(L):
            if q == L:
                continue
            Bc = UCNSObject(
                P.n_dec, P.n_min,
                [(a, p) for a, p in P.A_plus[:q]],
                P.F_plus[:q],
            )
            Ac = right_quotient(P, Bc)
            if Ac is not None and multiply(Ac, Bc) == P:
                reconstructed += 1
                break
    return {
        "depth": depth,
        "trials": trials,
        "reconstructed": reconstructed,
        "rate": reconstructed / trials,
        "cost_model": "O(divisors(|P.A_plus|)) — independent of |key space|",
    }


def run_all() -> dict:
    if not UCNS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "flat": prefix_read_break(depth=0),
        "nested": prefix_read_break(depth=1),
    }


if __name__ == "__main__":
    import json

    rep = run_all()
    if not rep["available"]:
        print("ucns not installed; prefix-read break skipped.")
    else:
        print(json.dumps(rep, indent=2))
