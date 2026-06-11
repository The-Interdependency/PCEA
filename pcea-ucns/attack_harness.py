# GPT/Claude generated; context, prompt Erin Spencer
"""
UCNS factorization attack harness for PCEA-UCNS domain design.

This module exists to MEASURE, not to assert. It points the real UCNS
factorization tools (factor_search_v08 and the Carrier-LCM-Law pruning
corollaries) at candidate cryptographic domains and reports what they
recover. The forbidden-domain list in ucns-crypto-domain-v0.md is
derived from these measurements, not from argument.

Run as an attack tool, not a security proof: a domain that survives
this harness is NOT thereby secure; a domain that falls IS thereby
forbidden. Absence of recovery here is necessary, never sufficient.

Dependency note: this is a TEST/DESIGN tool. It imports ucns (an
Interdependency repo, allowed per the dependency covenant) but lives
outside the PCEA runtime modules (see contract.RUNTIME_MODULES) and is
never imported by the cipher. It is skipped if ucns is not installed.
"""

from __future__ import annotations

import random
from fractions import Fraction
from math import lcm
from typing import List, Optional

try:
    from ucns_recursive.canonical import UCNSObject, multiply
    from ucns_recursive.catalogue_pruning import (
        prime_support,
        prune_payload_catalogue,
    )
    from ucns_recursive.domains import generate_payload_catalogue
    from ucns_recursive.factor_search_v08 import SEQ_PRIME, factor_search_v08

    UCNS_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without ucns
    UCNS_AVAILABLE = False


def _obj(denoms: List[int], faces: Optional[List[int]] = None) -> "UCNSObject":
    """Build a flat UCNS object with host angles 1/d for each d in denoms."""
    cells = [(Fraction(0), None)] + [(Fraction(1, d), None) for d in denoms]
    faces = faces or [0] * len(cells)
    n_min = 1
    for a, _ in cells:
        frac = (a % 2) / 2
        if frac != 0:
            n_min = lcm(n_min, frac.denominator)
    return UCNSObject(2 * n_min, n_min, cells, faces)


def carrier_support_leak(A: "UCNSObject", B: "UCNSObject") -> dict:
    """ATTACK 1 — the Carrier-LCM Law leak.

    By the Law, n_min(A ⊠ B) = lcm(n_min(A), n_min(B)), so the public
    product's carrier prime support is exactly the union of the factors'.
    Any secret encoded in carrier CHOICE is therefore public by
    construction. Returns the leaked support set.
    """
    P = multiply(A, B)
    return {
        "private_support_A": prime_support(A.n_min),
        "private_support_B": prime_support(B.n_min),
        "public_carrier": P.n_min,
        "leaked_support": prime_support(P.n_min),
    }


def oracle_domain_recovery(trials: int = 60, seed: int = 1) -> dict:
    """ATTACK 2 — recovery rate on the frozen depth-2 oracle domain.

    This domain is ORACLE-COMPLETE in the UCNS claims ledger:
    factorization there is exhaustive. Measures the fraction of random
    products factor_search_v08 recovers. A high rate is the empirical
    justification for forbidding this domain for key material.
    """
    catalogue = generate_payload_catalogue()
    atoms = [c for c in catalogue if c is not None]
    rng = random.Random(seed)
    recovered = 0
    for _ in range(trials):
        P = multiply(rng.choice(atoms), rng.choice(atoms))
        if factor_search_v08(P, catalogue=catalogue) is not SEQ_PRIME:
            recovered += 1
    return {"trials": trials, "recovered": recovered, "rate": recovered / trials}


def pruning_acceleration(A: "UCNSObject", B: "UCNSObject") -> dict:
    """ATTACK 3 — pruning as a key-search accelerator.

    The Carrier-LCM-Law payload pruning (Corollary 2) is a sound
    pre-filter — for the attacker. Measures how much of the candidate
    key space it eliminates for free on the product of A and B.
    """
    P = multiply(A, B)
    full = generate_payload_catalogue()
    pruned = prune_payload_catalogue(P, full)
    return {
        "full": len(full),
        "pruned": len(pruned),
        "eliminated_fraction": 1 - len(pruned) / len(full) if full else 0.0,
    }


def run_all() -> dict:
    """Run every attack and return a structured report."""
    if not UCNS_AVAILABLE:
        return {"available": False}
    A, B = _obj([8]), _obj([5])
    return {
        "available": True,
        "attack1_carrier_leak": carrier_support_leak(A, B),
        "attack2_oracle_recovery": oracle_domain_recovery(),
        "attack3_pruning_acceleration": pruning_acceleration(A, B),
    }


if __name__ == "__main__":
    import json

    report = run_all()
    if not report["available"]:
        print("ucns not installed; attack harness skipped.")
    else:
        print(json.dumps(report, indent=2, default=lambda s: sorted(s)))