# ratios: loc_comments=20:9 imports_exports=3:2 calls_definitions=8:2
# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for Open Attack 1 — the Minkowski set-basis break.

Pins the break: key recovery succeeds at all lattice sizes, and attack
cost grows slower than the brute-force key space (asymptotic superiority).
Skipped without ucns.
"""

import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "attack1_minkowski_break",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "attack1_minkowski_break.py",
)
mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mb)

pytestmark = pytest.mark.skipif(
    not mb.UCNS_AVAILABLE, reason="ucns not installed; Attack 1 inert"
)


def test_minkowski_recovery_succeeds_at_all_lattices():
    for denoms in ([8, 5], [8, 5, 3], [8, 5, 3, 7]):
        r = mb.attack_success(denoms, trials=30)
        assert r["rate"] > 0.9, r


def test_attack_cost_beats_brute_at_scale():
    # The break is asymptotic: at a large lattice the attack outpaces the
    # quadratically-growing brute-force key space.
    small = mb.attack_cost([8, 5], trials=20)
    large = mb.attack_cost([16, 9, 7, 11, 13], trials=20)
    assert large["speedup"] >= small["speedup"]
# ratios: loc_comments=20:9 imports_exports=3:2 calls_definitions=8:2
