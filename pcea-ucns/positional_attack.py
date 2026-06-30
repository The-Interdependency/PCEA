# ratios: loc_comments=68:26 imports_exports=8:2 calls_definitions=18:4
# GPT/Claude generated; context, prompt Erin Spencer
"""
Positional attack harness for PCEA-UCNS Q1.

ucns-crypto-domain-v0.md Q1 CONJECTURES that a private key can hide in
angle position / face bits / payload structure at a fixed public carrier,
because the Carrier-LCM Law only projects the carrier. This module tests
that conjecture directly, using the existing UCNS search — which already
recovers host angles AND face structures, not just carriers.

It measures two distinct quantities at a held-fixed public carrier:

- RECOMPOSE rate: fraction of public products for which factor_search_v08
  finds *some* (A, B) with A ⊠ B = P. For a KEM this is the relevant
  attack: recovering ANY valid factor pair breaks the scheme, because the
  shared secret derives from the factorization, not from a unique key.
- EXACT-PRIVATE rate: fraction where the recovered left factor equals the
  actual private factor (angles AND faces). Stricter; informative about
  how much structure leaks even past non-uniqueness.

MEASURE, not assert. A domain that resists this harness is not thereby
secure; a domain that falls IS thereby refuted as a key location.
"""

from __future__ import annotations

import random
from fractions import Fraction
from math import lcm
from typing import List

try:
    from ucns_recursive.canonical import UCNSObject, multiply
    from ucns_recursive.factor_search_v08 import SEQ_PRIME, factor_search_v08

    UCNS_AVAILABLE = True
except ImportError:  # pragma: no cover
    UCNS_AVAILABLE = False


def _mk(angles: List[Fraction], faces: List[int]) -> "UCNSObject":
    n_min = 1
    for a in angles:
        frac = (a % 2) / 2
        if frac != 0:
            n_min = lcm(n_min, frac.denominator)
    return UCNSObject(2 * n_min, n_min, [(a, None) for a in angles], faces)


def _keylike(rng: random.Random, carrier_denoms: List[int], width: int) -> "UCNSObject":
    """A key-like object: angles drawn over a fixed carrier's lattice,
    private structure = which positions + face bits, carrier held public."""
    poss = sorted({Fraction(k, d) for d in carrier_denoms for k in range(1, d)})
    angles = [Fraction(0)] + rng.sample(poss, min(width, len(poss)))
    faces = [rng.randint(0, 1) for _ in range(len(angles))]
    return _mk(angles, faces)


def positional_recovery(
    carrier_denoms: List[int],
    width: int,
    trials: int = 60,
    seed: int = 7,
) -> dict:
    """Run the positional attack at a fixed carrier domain.

    Returns recompose and exact-private recovery counts. A high recompose
    rate refutes the Q1 conjecture for this domain: the search recovers a
    usable factorization despite the carrier being fixed and public.
    """
    rng = random.Random(seed)
    recompose = 0
    exact_private = 0
    for _ in range(trials):
        A = _keylike(rng, carrier_denoms, width)
        B = _keylike(rng, carrier_denoms, width)
        P = multiply(A, B)
        r = factor_search_v08(P, prune=False)
        if r is not SEQ_PRIME:
            recompose += 1
            if r[0].A_plus == A.A_plus and r[0].F_plus == A.F_plus:
                exact_private += 1
    return {
        "carrier_denoms": carrier_denoms,
        "width": width,
        "trials": trials,
        "recompose": recompose,
        "exact_private": exact_private,
        "recompose_rate": recompose / trials,
        "exact_private_rate": exact_private / trials,
    }


def run_all() -> dict:
    if not UCNS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "results": [
            positional_recovery([3, 5], 3),          # carrier 15
            positional_recovery([8, 5], 4),          # carrier 40 — named candidate
            positional_recovery([3, 5, 7], 5),       # carrier 105
        ],
    }


if __name__ == "__main__":
    import json

    rep = run_all()
    if not rep["available"]:
        print("ucns not installed; positional harness skipped.")
    else:
        print(json.dumps(rep, indent=2))
# ratios: loc_comments=68:26 imports_exports=8:2 calls_definitions=18:4
