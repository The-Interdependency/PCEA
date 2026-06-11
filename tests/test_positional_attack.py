# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for the positional attack harness.

Pins the MEASURED refutation of the Q1 conjecture: at a fixed public
carrier, factor_search_v08 still recovers a usable factorization. Skipped
without ucns. Not a security proof — a regression gate on a finding.
"""

import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "positional_attack",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "positional_attack.py",
)
pa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pa)

pytestmark = pytest.mark.skipif(
    not pa.UCNS_AVAILABLE, reason="ucns not installed; positional harness inert"
)


def test_fixed_carrier_does_not_resist_recompose():
    # The Q1 conjecture predicts low recovery; the measurement refutes it.
    for denoms, width in [([3, 5], 3), ([8, 5], 4), ([3, 5, 7], 5)]:
        r = pa.positional_recovery(denoms, width, trials=40)
        assert r["recompose_rate"] > 0.8, (
            f"carrier {denoms} unexpectedly resisted recompose: {r}"
        )


def test_larger_carrier_does_not_help():
    # Scaling the carrier does not reduce recompose rate — the hardness
    # is not in carrier magnitude.
    small = pa.positional_recovery([3, 5], 3, trials=40)
    large = pa.positional_recovery([3, 5, 7], 5, trials=40)
    assert large["recompose_rate"] >= small["recompose_rate"] - 0.1
