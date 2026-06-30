# ratios: loc_comments=20:13 imports_exports=3:2 calls_definitions=8:2
# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for the quotient-guided pruning scaling result.

Pins the POSITIVE finding: both cheap quotient-guided attacks scale
~linearly in |key space| (constant-factor speedup, not polynomial break).
A real break would show a slope materially below 1. Skipped without ucns.
"""

import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "pruning_scaling",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "pruning_scaling.py",
)
ps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ps)

pytestmark = pytest.mark.skipif(
    not ps.UCNS_AVAILABLE, reason="ucns not installed; scaling test inert"
)


def test_prefix_angle_attack_is_not_polynomial_break():
    # Use the full size range the published slope (~0.89) is measured on;
    # 3-point subsamples drop the high-N points where linearity is clearest.
    r = ps.prefix_angle_scaling([8, 5], 3, sizes=(40, 80, 160, 320, 640), trials=30)
    # ratio-to-|KS| stays bounded away from 0 => constant-factor, not a
    # polynomial break (which would show ratio decaying toward 0).
    ratios = [m / n for n, m in r["data"]]
    assert min(ratios) > 0.04, f"ratio collapsed (poly break signature): {ratios}"
    assert r["slope"] > 0.8


def test_strong_prune_attack_is_not_polynomial_break():
    r = ps.strong_prune_scaling([8, 5], 3, sizes=(80, 320, 1000), trials=25)
    # The cipher's own carrier-support pruning, turned adversarial, still
    # does not shrink the search below linear.
    assert r["slope"] > 0.8
# ratios: loc_comments=20:13 imports_exports=3:2 calls_definitions=8:2
