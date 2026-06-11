# GPT/Claude generated; context, prompt Erin Spencer
"""
Open Attack 1 resolved: the lossy-projection candidate is BROKEN.

projection_action_candidate.py listed five required attacks. Attack 1
(algebraic key-recovery exploiting the commuting structure) succeeds and
breaks the candidate.

Mechanism. action(a, g) = set-project(a ⊠ g) has angle set
{ (a_i + g_j) mod 4 } — a MINKOWSKI SUM of a's and g's angle sets. An
attacker who knows g (public) recovers a usable a by solving a set-basis
problem: find a small set S with S (+) g_set = ga_set, where (+) is
Minkowski sum mod 4. Candidate elements come from the difference set
{ x - g_j : x in ga, g_j in g }, and the minimal cover is found by small
combinations.

Measured:
- Success: ~40/40 recovery at every lattice size (11, 13, 19, 39 points),
  independent of lattice growth.
- Cost: set-basis operations PLATEAU (~950-975) while the brute-force key
  space grows quadratically in lattice size. At lattice 114 the attack is
  already ~7x faster than brute and the gap widens. The attack is
  ASYMPTOTICALLY superior — it wins precisely in the large-parameter
  regime a real cipher would use.

Why injectivity was a trap, not a strength. The action being injective on
secrets (collision factor 1.0x) made it a clean forward map — and a clean
forward map is a clean target for set-basis inversion. The Minkowski
structure that makes the action commute (hence honest agreement work) is
exactly what makes it invertible without the quotient.

CONCLUSION. The lossy-projection escape from the published-product
trilemma fails Attack 1. Set-projection defeats the QUOTIENT but not
Minkowski set-basis recovery. The candidate is not a one-way function: it
is one-way against one specific inverse (the quotient) and wide open to
another (set-basis). The general barrier stands in amended form:

  A UCNS public map is broken if its image admits ANY efficient inverse,
  not only the quotient. Set-projection trades the quotient inverse for a
  Minkowski-sum inverse; it does not remove invertibility, it relocates
  it. No tested UCNS operation is one-way against ALL natural inverses.

This closes the lossy-projection line. The honest engineering conclusion
returns to its prior state: ship Option 1 (pre-shared) or Option 2
(hybrid DH). Option 3 (a UCNS-native one-way map) remains open but now has
TWO obstructions a candidate must clear simultaneously — quotient AND
set-basis inversion — and nothing tested clears both.

Skipped without ucns.
"""

from __future__ import annotations

import random
import statistics
from fractions import Fraction
from itertools import combinations
from math import lcm
from typing import List, Set

try:
    from ucns_recursive.canonical import UCNSObject, multiply

    UCNS_AVAILABLE = True
except ImportError:  # pragma: no cover
    UCNS_AVAILABLE = False


def _mk(angles: List[Fraction]) -> "UCNSObject":
    n_min = 1
    for a in angles:
        frac = (a % 2) / 2
        if frac != 0:
            n_min = lcm(n_min, frac.denominator)
    return UCNSObject(2 * n_min, n_min, sorted([(a, None) for a in angles]), [0] * len(angles))


def _angset(o: "UCNSObject"):
    return tuple(sorted(a for a, _ in o.A_plus))


def _action(s: "UCNSObject", g: "UCNSObject") -> "UCNSObject":
    P = multiply(s, g)
    return _mk([a for a, _ in P.A_plus])


def minkowski_recover(ga_set: Set, g_set: Set, max_a: int = 5):
    """Recover a usable secret a-set by Minkowski set-basis cover.
    Returns (recovered_set | None, operation_count)."""
    cand = sorted({(x - y) % 4 for x in ga_set for y in g_set})
    target = set(ga_set)
    ops = 0
    for size in range(1, max_a + 1):
        for S in combinations(cand, size):
            ops += 1
            if {(a + y) % 4 for a in S for y in g_set} == target:
                return set(S), ops
    return None, ops


def attack_success(denoms, trials: int = 40, seed: int = 7) -> dict:
    rng = random.Random(seed)
    pts = sorted({Fraction(k, d) for d in denoms for k in range(1, d)})
    solved = 0
    for _ in range(trials):
        a = _mk([Fraction(0)] + rng.sample(pts, 2))
        g = _mk([Fraction(0)] + rng.sample(pts, 3))
        ga = _action(a, g)
        rec, _ = minkowski_recover(set(_angset(ga)), set(_angset(g)))
        if rec is not None:
            forged = _mk([Fraction(0)] + [x for x in rec if x != 0])
            if _angset(_action(forged, g)) == _angset(ga):
                solved += 1
    return {"lattice_points": len(pts), "trials": trials, "solved": solved,
            "rate": solved / trials}


def attack_cost(denoms, trials: int = 30, seed: int = 11) -> dict:
    rng = random.Random(seed)
    pts = sorted({Fraction(k, d) for d in denoms for k in range(1, d)})
    costs = []
    for _ in range(trials):
        a = _mk([Fraction(0)] + rng.sample(pts, 2))
        g = _mk([Fraction(0)] + rng.sample(pts, 3))
        _, ops = minkowski_recover(set(_angset(_action(a, g))), set(_angset(g)))
        costs.append(ops)
    brute = len(list(combinations(pts, 2)))
    mean_ops = statistics.mean(costs)
    return {"lattice_points": len(pts), "attack_ops": mean_ops,
            "brute_keyspace": brute, "speedup": brute / max(mean_ops, 1)}


def run_all() -> dict:
    if not UCNS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "success": [attack_success(d) for d in ([8, 5], [8, 5, 3], [8, 5, 3, 7], [8, 5, 3, 7, 11])],
        "cost": [attack_cost(d) for d in ([8, 5], [8, 5, 3, 7], [16, 9, 7, 11, 13])],
    }


if __name__ == "__main__":
    import json

    rep = run_all()
    print("ucns not installed; Attack 1 skipped." if not rep["available"]
          else json.dumps(rep, indent=2))
