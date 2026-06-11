# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for the quotient-based attack and key-space reconciliation.

Pins the corrected finding: the private left factor is nearly UNIQUE
within a finite key space (quotient primitive), even though factor_search
finds many full-space decompositions. Skipped without ucns.
"""

import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "quotient_attack",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "quotient_attack.py",
)
qa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qa)

pytestmark = pytest.mark.skipif(
    not qa.UCNS_AVAILABLE, reason="ucns not installed; quotient attack inert"
)


def test_private_factor_nearly_unique_in_keyspace():
    r = qa.divisor_count([8, 5], 2, key_space_size=40, trials=40)
    # Mean valid divisors close to 1 — the private factor is essentially
    # unique within the key space, contra the full-space non-uniqueness.
    assert r["mean_divisors"] < 1.5


def test_factor_search_splits_often_leave_keyspace():
    r = qa.space_reconciliation([8, 5], 2, key_space_size=40, trials=40)
    # A substantial share of factor_search's full-space splits are not
    # usable keys — the reconciliation between the two primitives.
    assert r["factor_search_split_outside_keyspace"] > 0
    assert r["quotient_unique_in_keyspace"] > r["trials"] * 0.6
