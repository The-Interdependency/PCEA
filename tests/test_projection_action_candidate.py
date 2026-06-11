# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for the projection-action candidate.

Pins the measured properties that make it a candidate: injectivity on
secrets, one-wayness against the quotient, and honest agreement. These are
NECESSARY-not-sufficient; the module docstring lists the open attacks that
must be run before any security claim. Skipped without ucns.
"""

import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "projection_action_candidate",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "projection_action_candidate.py",
)
pac = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pac)

pytestmark = pytest.mark.skipif(
    not pac.UCNS_AVAILABLE, reason="ucns not installed; candidate probe inert"
)


def test_action_injective_on_secrets():
    for denoms in ([5, 3], [8, 5], [8, 5, 3, 7]):
        r = pac.injectivity_exact(denoms)
        assert r["collision_factor"] == 1.0, r


def test_quotient_does_not_invert_projected_action():
    r = pac.quotient_inversion([8, 5, 3, 7], trials=120)
    # The set-projection breaks the quotient: inversion rate must be low.
    assert r["rate"] < 0.1


def test_honest_parties_agree():
    r = pac.honest_agreement([8, 5, 3, 7], width=3, trials=120)
    assert r["rate"] == 1.0
