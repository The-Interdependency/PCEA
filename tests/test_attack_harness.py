# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for the UCNS attack harness.

These are not security proofs. They pin the MEASURED behavior that the
domain spec relies on, so that a change in UCNS (or in this harness)
which alters the forbidden-domain conclusions fails loudly.

Skipped entirely when ucns is not installed, keeping PCEA's core suite
dependency-free.
"""

import pytest

import importlib.util, pathlib
_spec = importlib.util.spec_from_file_location(
    "attack_harness",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "attack_harness.py",
)
ah = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ah)

pytestmark = pytest.mark.skipif(
    not ah.UCNS_AVAILABLE, reason="ucns not installed; attack harness inert"
)


def test_carrier_law_leaks_factor_support():
    A, B = ah._obj([8]), ah._obj([5])
    r = ah.carrier_support_leak(A, B)
    # The public carrier's support is exactly the union of the private
    # supports — the Law leak, the central design constraint.
    union = set(r["private_support_A"]) | set(r["private_support_B"])
    assert set(r["leaked_support"]) == union


def test_oracle_domain_is_highly_recoverable():
    r = ah.oracle_domain_recovery(trials=60, seed=1)
    # Empirical justification for forbidding the oracle domain for keys:
    # the majority of products are recovered by factor_search_v08.
    assert r["rate"] > 0.5


def test_pruning_eliminates_substantial_search_space():
    A, B = ah._obj([8]), ah._obj([5])
    r = ah.pruning_acceleration(A, B)
    # Pruning is an attacker accelerator: it removes a large fraction of
    # the candidate key space at no cost.
    assert r["eliminated_fraction"] > 0.25