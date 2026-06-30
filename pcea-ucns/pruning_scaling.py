# ratios: loc_comments=114:29 imports_exports=11:3 calls_definitions=52:7
# GPT/Claude generated; context, prompt Erin Spencer
"""
Quotient-guided pruning scaling test — the break attempt, and its result.

The quotient attack relocated the hardness to: does a quotient-GUIDED
key-space search beat brute-force enumeration? This module runs that
attack and measures its SCALING, which is what distinguishes a real break
from a harmless constant-factor speedup.

Two cheap-heuristic attacks, scored by how many candidates an attacker
must check before reaching the private factor, as |key space| grows:

- PREFIX-ANGLE ordering: rank candidates by how many of their angles
  appear in P's angle set, check high-rank first.
- STRONGEST CHEAP PRUNE: pre-filter by carrier-support containment (the
  cipher's own Corollary 2 turned against it) AND prefix-angle
  membership, then quotient-check survivors.

Measured (carrier 40, ⟨2,5⟩, width 3, |KS| from 40 to 1000):

- Prefix-angle: cost ~ |KS|^0.89, speedup 3.8x→5.7x (rising but bounded).
- Strongest cheap prune: cost ~ |KS|^1.03, ratio-to-|KS| pinned ~0.10.

RESULT: both attacks are CONSTANT-FACTOR (cost stays Θ(|KS|)), not
polynomial. The heuristics reorder the search; they do not shrink it. A
constant ~10x speedup is absorbed by enlarging the key space a few bits.

This is a POSITIVE result for the KEM, stated at its true strength: no
polynomial break was found AT THE CHEAP-HEURISTIC LEVEL. It is NOT a proof
of hardness — a cleverer quotient-structure attack (e.g. one exploiting
the recursive payload quotient, or algebraic relations among divisors)
could still find sublinear scaling. What today establishes: the obvious
quotient-guided attacks, including the cipher's own pruning corollaries
turned adversarial, do not break the key-space-restricted regime.

MEASURE, not assert. Skipped without ucns.
"""

from __future__ import annotations

import math
import random
import statistics
from fractions import Fraction
from math import lcm
from typing import List, Tuple

try:
    from ucns_recursive.canonical import UCNSObject, multiply
    from ucns_recursive.catalogue_pruning import prime_support
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


def _key_space(rng, denoms, width, n) -> List["UCNSObject"]:
    poss = sorted({Fraction(k, d) for d in denoms for k in range(1, d)})
    out: List["UCNSObject"] = []
    seen = set()
    tries = 0
    while len(out) < n and tries < n * 80:
        tries += 1
        angles = tuple([Fraction(0)] + rng.sample(poss, min(width, len(poss))))
        faces = tuple(rng.randint(0, 1) for _ in angles)
        if (angles, faces) in seen:
            continue
        seen.add((angles, faces))
        out.append(_mk(list(angles), list(faces)))
    return out


def _loglog_slope(data: List[Tuple[int, float]]) -> float:
    xs = [math.log(n) for n, _ in data]
    ys = [math.log(max(m, 0.5)) for _, m in data]
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sxx = sum(x * x for x in xs)
    return (n * sxy - sx * sy) / (n * sxx - sx * sx)


def prefix_angle_scaling(denoms, width, sizes=(40, 80, 160, 320, 640), trials=40, seed=101) -> dict:
    rng = random.Random(seed)
    data = []
    for size in sizes:
        KS = _key_space(rng, denoms, width, size)
        N = len(KS)
        checks = []
        for _ in range(trials):
            A, B = rng.choice(KS), rng.choice(KS)
            P = multiply(A, B)
            L = len(P.A_plus)
            Pang = [a for a, _ in P.A_plus]

            def score(Ap):
                p = len(Ap.A_plus)
                if p == 0 or L % p != 0:
                    return -1
                return sum(1 for a, _ in Ap.A_plus if a in Pang)

            ordered = sorted(KS, key=score, reverse=True)
            c = 0
            for Ap in ordered:
                c += 1
                if left_quotient(P, Ap) is not None and _struct(Ap) == _struct(A):
                    break
            checks.append(c)
        data.append((N, statistics.mean(checks)))
    return {"data": data, "slope": _loglog_slope(data)}


def strong_prune_scaling(denoms, width, sizes=(80, 160, 320, 640, 1000), trials=40, seed=202) -> dict:
    rng = random.Random(seed)
    data = []
    for size in sizes:
        KS = _key_space(rng, denoms, width, size)
        N = len(KS)
        checks = []
        for _ in range(trials):
            A, B = rng.choice(KS), rng.choice(KS)
            P = multiply(A, B)
            Pang = set(a for a, _ in P.A_plus)
            Psup = prime_support(P.n_min)

            def viable(Ap):
                if not prime_support(Ap.n_min) <= Psup:
                    return False
                return all(a in Pang for a, _ in Ap.A_plus)

            cands = [Ap for Ap in KS if viable(Ap)]
            c = 0
            for Ap in cands:
                c += 1
                if left_quotient(P, Ap) is not None and _struct(Ap) == _struct(A):
                    break
            checks.append(c if c > 0 else len(cands))
        data.append((N, statistics.mean(checks)))
    return {"data": data, "slope": _loglog_slope(data)}


def run_all() -> dict:
    if not UCNS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "prefix_angle": prefix_angle_scaling([8, 5], 3),
        "strong_prune": strong_prune_scaling([8, 5], 3),
    }


if __name__ == "__main__":
    import json

    rep = run_all()
    if not rep["available"]:
        print("ucns not installed; scaling test skipped.")
    else:
        for k in ("prefix_angle", "strong_prune"):
            print(f"{k}: cost ~ |KS|^{rep[k]['slope']:.2f}")
            for n, m in rep[k]["data"]:
                print(f"  |KS|={n:5d}  checks={m:6.1f}  ratio={m/n:.3f}")
# ratios: loc_comments=114:29 imports_exports=11:3 calls_definitions=52:7
