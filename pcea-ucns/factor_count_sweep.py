# ratios: loc_comments=113:28 imports_exports=8:3 calls_definitions=26:8
# GPT/Claude generated; context, prompt Erin Spencer
"""
Factor-count sweep + non-uniqueness diagnosis for PCEA-UCNS.

The three-factor attack showed partial protection (boundary-smearing).
The hopeful hypothesis was that recovery DECAYS as factor count grows —
that a 5- or 6-factor product hides a designated private factor better
than a 3-factor one. This module tests that hypothesis and diagnoses the
underlying cause.

Two measurements at fixed carrier 40 (⟨2,5⟩):

- DECAY: recursive-peel recovery of the designated private factor as
  factor count runs 2..6. Measured FLAT (~40-67%, noise, no downward
  trend). More factors do not help.

- NON-UNIQUENESS (the cause): for a 5-factor product, how often does the
  search's split equal the TRUE ordered (prefix, C) versus some OTHER
  decomposition. Measured: 0/80 true, 80/80 other. The public product
  admits many ordered factorizations.

Conclusion: factor count is irrelevant. Non-uniqueness defeats the KEM at
every count. A shared secret cannot bind to a factorization that is not
unique — either the attacker finds A valid decomposition the protocol
must also accept (broken), or the protocol demands the exact private
decomposition and honest parties cannot reliably agree (non-functional).
This is a structural barrier, not a parameter-tuning problem.

MEASURE, not assert. Skipped without ucns.
"""

from __future__ import annotations

import random
from fractions import Fraction
from math import lcm
from typing import List, Tuple

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


def _keylike(rng: random.Random, denoms: List[int], width: int) -> "UCNSObject":
    poss = sorted({Fraction(k, d) for d in denoms for k in range(1, d)})
    angles = [Fraction(0)] + rng.sample(poss, min(width, len(poss)))
    return _mk(angles, [rng.randint(0, 1) for _ in range(len(angles))])


def _struct(o: "UCNSObject") -> Tuple:
    return (tuple(o.A_plus), tuple(o.F_plus))


def _product(facs: List["UCNSObject"]) -> "UCNSObject":
    P = facs[0]
    for f in facs[1:]:
        P = multiply(P, f)
    return P


def _peel_all(P: "UCNSObject", depth: int) -> List["UCNSObject"]:
    if depth == 0:
        return [P]
    r = factor_search_v08(P, prune=False)
    if r is SEQ_PRIME:
        return [P]
    out: List["UCNSObject"] = []
    for part in r:
        out.extend(_peel_all(part, depth - 1))
    return out


def decay_sweep(
    denoms: List[int],
    width: int,
    counts=(2, 3, 4, 5, 6),
    trials: int = 60,
    seed: int = 21,
) -> dict:
    """Recovery rate of the designated private factor vs factor count."""
    rng = random.Random(seed)
    out = {}
    for nfac in counts:
        recompose = 0
        recovered = 0
        for _ in range(trials):
            facs = [_keylike(rng, denoms, width) for _ in range(nfac)]
            P = _product(facs)
            C = facs[-1]
            r = factor_search_v08(P, prune=False)
            if r is SEQ_PRIME:
                continue
            recompose += 1
            leaves = _peel_all(P, nfac)
            if any(_struct(leaf) == _struct(C) for leaf in leaves):
                recovered += 1
        out[nfac] = {
            "recompose": recompose,
            "recovered": recovered,
            "rate": recovered / trials,
        }
    return out


def nonuniqueness(
    denoms: List[int],
    width: int,
    nfac: int = 5,
    trials: int = 80,
    seed: int = 21,
) -> dict:
    """How often the search's split equals the TRUE ordered (prefix, C)
    versus some OTHER valid decomposition. High 'other' => the product has
    many ordered factorizations => the secret cannot bind to one."""
    rng = random.Random(seed)
    true_split = 0
    other_split = 0
    recompose = 0
    for _ in range(trials):
        facs = [_keylike(rng, denoms, width) for _ in range(nfac)]
        P = _product(facs)
        r = factor_search_v08(P, prune=False)
        if r is SEQ_PRIME:
            continue
        recompose += 1
        X, Y = r
        true_prefix = _product(facs[:-1])
        if _struct(X) == _struct(true_prefix) and _struct(Y) == _struct(facs[-1]):
            true_split += 1
        else:
            other_split += 1
    return {
        "nfac": nfac,
        "recompose": recompose,
        "true_split": true_split,
        "other_split": other_split,
    }


def run_all() -> dict:
    if not UCNS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "decay": decay_sweep([8, 5], 2),
        "nonuniqueness": nonuniqueness([8, 5], 2),
    }


if __name__ == "__main__":
    import json

    rep = run_all()
    if not rep["available"]:
        print("ucns not installed; sweep skipped.")
    else:
        print(json.dumps(rep, indent=2))
# ratios: loc_comments=113:28 imports_exports=8:3 calls_definitions=26:8
