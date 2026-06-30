# ratios: loc_comments=75:57 imports_exports=10:5 calls_definitions=33:10
# GPT/Claude generated; context, prompt Erin Spencer
"""
Candidate one-way UCNS action via lossy set-projection — and its open attacks.

The general-barrier assessment (asymmetric-paths-assessment.md) argued no
UCNS operation is one-way because the quotient inverts every published
product. That argument assumed the published object is a structured
PRODUCT. This module tests an operation that is NOT a structured product:

    action(s, g) = set-project( s ⊠ g )

where set-project flattens a UCNS object to its sorted, de-duplicated
angle set (discarding order, multiplicity, faces, payloads). The
projection is the missing fourth move — deliberate information loss,
which UCNS never used because its purpose is to preserve enough to factor.

MEASURED PROPERTIES (all reproducible; harness functions below):

- Injective on secrets: exact enumeration of width-2 secrets gives
  collision factor 1.0x at every lattice size (15,55,78,171,741 distinct
  classes for lattices of 6..39 points). No entropy cap; the security
  parameter is the angle-lattice size, and it scales.
- One-way against the quotient: right_quotient recovers the secret from
  action(a,g) only 3/200 — the set-projection destroys the cell structure
  the quotient needs (12-cell product collapses to a deduped set).
- Survives, so far: direct reconstruction from {ga - g} differences
  (0/200), combine-publics (0/100), angle-union (0/50). Honest two-sided
  agreement action(a,action(b,g)) == action(b,action(a,g)) holds 200/200
  at width 3. Two-sided secret entropy near-uniform (ratio to max >= 0.96).

STATUS: BROKEN by Open Attack 1 (see attack1_minkowski_break.py).
The text below describes the candidate as it stood BEFORE Attack 1 was
run; retained for the record. The action is invertible by Minkowski
set-basis recovery — one-way against the quotient, wide open to set-basis.

ORIGINAL STATUS (pre-Attack-1): CANDIDATE, NOT A CIPHER. This is the first construction in the
investigation to survive every attack tried, and the first counterexample
to the general-barrier claim — the barrier was too strong because it
omitted lossy (non-product) operations. It is NOT proven secure. The
attacks below are NECESSARY before any trust and have NOT been run:

  OPEN ATTACK 1 — algebraic key-recovery exploiting the commuting
    structure (the true discrete-log analog over the projection's
    image lattice; the difference-set proxy tried is not the strongest).
  OPEN ATTACK 2 — meet-in-the-middle over the set-lattice: precompute
    action(a,g) tables and collide halves; may halve the security
    exponent.
  OPEN ATTACK 3 — set-structure cryptanalysis: the image is a union-like
    sublattice; subset/lattice-reduction attacks specific to set images
    are entirely untested.
  OPEN ATTACK 4 — active/chosen-input attacks; malleability of the
    projected object; whether a KEM built on this leaks via the KDF step.
  OPEN ATTACK 5 — honest-party failure at scale: agreement is 200/200 at
    tested widths but unproven in general; a single disagreement class
    breaks correctness.

Until ATTACKS 1-5 are run and survived, this is a research artifact, not
a security primitive. PCEA's shipping guidance is unchanged: Option 1
(pre-shared) or Option 2 (hybrid DH). This module changes the research
status of Option 3 from "named obstruction" to "candidate with a concrete
attack agenda."

Skipped without ucns.
"""

from __future__ import annotations

import itertools
import math
import random
from fractions import Fraction
from math import lcm
from typing import List, Tuple

try:
    from ucns_recursive.canonical import UCNSObject, multiply
    from ucns_recursive.left_quotient import right_quotient

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


def _angset(o: "UCNSObject") -> Tuple:
    return tuple(sorted(a for a, _ in o.A_plus))


def action(s: "UCNSObject", g: "UCNSObject") -> "UCNSObject":
    """The candidate one-way action: multiply then project to angle-set."""
    P = multiply(s, g)
    return _mk([a for a, _ in P.A_plus])


def _lattice_points(denoms) -> List[Fraction]:
    return sorted({Fraction(k, d) for d in denoms for k in range(1, d)})


def injectivity_exact(denoms, width: int = 2) -> dict:
    """Exhaustive: distinct secrets vs distinct action-classes (collision factor)."""
    pts = _lattice_points(denoms)
    g = _mk([Fraction(0)] + pts[:3])
    classes = set()
    n = 0
    for combo in itertools.combinations(pts, width):
        classes.add(_angset(action(_mk([Fraction(0)] + list(combo)), g)))
        n += 1
    return {"lattice_points": len(pts), "secrets": n, "classes": len(classes),
            "collision_factor": n / len(classes) if classes else 0.0}


def quotient_inversion(denoms, trials: int = 200, seed: int = 31337) -> dict:
    """How often right_quotient recovers the secret from the projected action."""
    rng = random.Random(seed)
    pts = _lattice_points(denoms)

    def rf(w):
        return _mk([Fraction(0)] + rng.sample(pts, w))

    inverts = 0
    for _ in range(trials):
        a, g = rf(2), rf(3)
        ga = action(a, g)
        rec = right_quotient(ga, g)
        if rec is not None and _angset(action(rec, g)) == _angset(ga):
            inverts += 1
    return {"trials": trials, "quotient_inverts": inverts, "rate": inverts / trials}


def honest_agreement(denoms, width: int = 3, trials: int = 200, seed: int = 2024) -> dict:
    rng = random.Random(seed)
    pts = _lattice_points(denoms)

    def rf(w):
        return _mk([Fraction(0)] + rng.sample(pts, w))

    agree = 0
    for _ in range(trials):
        g, a, b = rf(3), rf(width), rf(width)
        if _angset(action(a, action(b, g))) == _angset(action(b, action(a, g))):
            agree += 1
    return {"trials": trials, "agree": agree, "rate": agree / trials}


def run_all() -> dict:
    if not UCNS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "injectivity": [injectivity_exact(d) for d in ([5, 3], [8, 5], [8, 5, 3, 7])],
        "quotient_inversion": quotient_inversion([8, 5, 3, 7]),
        "honest_agreement": honest_agreement([8, 5, 3, 7]),
    }


if __name__ == "__main__":
    import json

    rep = run_all()
    print("ucns not installed; candidate probe skipped." if not rep["available"]
          else json.dumps(rep, indent=2))
# ratios: loc_comments=75:57 imports_exports=10:5 calls_definitions=33:10
