# ratios: loc_comments=105:30 imports_exports=10:3 calls_definitions=33:6
# GPT/Claude generated; context, prompt Erin Spencer
"""
Quotient-based attack for PCEA-UCNS — and the key-space reconciliation.

The factor-count sweep concluded non-uniqueness defeats the KEM. That
conclusion used factor_search_v08, which searches the FULL object space.
This module re-runs the question with the left_quotient primitive, which
has no internal search heuristic, and restricts to a candidate KEY SPACE.
The two disagree, and the disagreement is the actual finding.

Two measurements:

- DIVISOR COUNT: given public P = A ⊠ B with A, B from a finite key space,
  how many key-space candidates A' yield a valid left_quotient(P, A')?
  Measured (carrier 40, key space 40): mean ~1.1, max 2. The private left
  factor is nearly UNIQUE within the key space.

- SPACE RECONCILIATION: factor_search's splits land OUTSIDE the key space
  ~55% of the time (full-space factorizations that are not usable keys),
  while the quotient finds the private factor unique within the key space
  37/40.

Corrected conclusion: non-uniqueness in the FULL object space does not by
itself defeat a KEM whose secret is key-space-restricted. But that moves
the hardness, it does not remove it: an attacker who knows the key-space
structure enumerates it and finds the unique divisor by quotient in
|keyspace| cheap operations. Security then rests on (a) the key space
being infeasible to enumerate AND (b) no quotient-guided shortcut beating
brute force. Both are OPEN; neither is claimed. This is a better-posed
problem than 'factorization is hard', not a solved one.

MEASURE, not assert. Skipped without ucns.
"""

from __future__ import annotations

import random
import statistics
from fractions import Fraction
from math import lcm
from typing import List, Tuple

try:
    from ucns_recursive.canonical import UCNSObject, multiply
    from ucns_recursive.factor_search_v08 import SEQ_PRIME, factor_search_v08
    from ucns_recursive.left_quotient import left_quotient

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


def _struct(o: "UCNSObject") -> Tuple:
    return (tuple(o.A_plus), tuple(o.F_plus))


def _key_space(rng: random.Random, denoms: List[int], width: int, n: int) -> List["UCNSObject"]:
    poss = sorted({Fraction(k, d) for d in denoms for k in range(1, d)})
    out: List["UCNSObject"] = []
    seen = set()
    while len(out) < n:
        angles = tuple([Fraction(0)] + rng.sample(poss, min(width, len(poss))))
        faces = tuple(rng.randint(0, 1) for _ in angles)
        if (angles, faces) in seen:
            continue
        seen.add((angles, faces))
        out.append(_mk(list(angles), list(faces)))
    return out


def divisor_count(
    denoms: List[int],
    width: int,
    key_space_size: int = 40,
    trials: int = 40,
    seed: int = 31,
) -> dict:
    """How many key-space candidates left-divide a public product."""
    rng = random.Random(seed)
    KS = _key_space(rng, denoms, width, key_space_size)
    counts: List[int] = []
    for _ in range(trials):
        A = rng.choice(KS)
        B = rng.choice(KS)
        P = multiply(A, B)
        divisors = [Ap for Ap in KS if left_quotient(P, Ap) is not None]
        counts.append(len(divisors))
    return {
        "key_space_size": len(KS),
        "trials": trials,
        "mean_divisors": statistics.mean(counts),
        "min_divisors": min(counts),
        "max_divisors": max(counts),
    }


def space_reconciliation(
    denoms: List[int],
    width: int,
    key_space_size: int = 40,
    trials: int = 40,
    seed: int = 31,
) -> dict:
    """Where do factor_search splits land relative to the key space, and
    is the quotient-found private factor unique within it?"""
    rng = random.Random(seed)
    KS = _key_space(rng, denoms, width, key_space_size)
    ks_structs = {_struct(k) for k in KS}
    q_unique = 0
    fs_in = 0
    fs_out = 0
    for _ in range(trials):
        A = rng.choice(KS)
        B = rng.choice(KS)
        P = multiply(A, B)
        divisors = [Ap for Ap in KS if left_quotient(P, Ap) is not None]
        if len(divisors) == 1:
            q_unique += 1
        r = factor_search_v08(P, prune=False)
        if r is not SEQ_PRIME:
            X, Y = r
            if _struct(X) in ks_structs and _struct(Y) in ks_structs:
                fs_in += 1
            else:
                fs_out += 1
    return {
        "trials": trials,
        "quotient_unique_in_keyspace": q_unique,
        "factor_search_split_in_keyspace": fs_in,
        "factor_search_split_outside_keyspace": fs_out,
    }


def run_all() -> dict:
    if not UCNS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "divisor_count": divisor_count([8, 5], 2),
        "space_reconciliation": space_reconciliation([8, 5], 2),
    }


if __name__ == "__main__":
    import json

    rep = run_all()
    if not rep["available"]:
        print("ucns not installed; quotient attack skipped.")
    else:
        print(json.dumps(rep, indent=2))
# ratios: loc_comments=105:30 imports_exports=10:3 calls_definitions=33:6
