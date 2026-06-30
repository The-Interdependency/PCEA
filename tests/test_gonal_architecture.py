# ratios: loc_comments=18:13 imports_exports=3:2 calls_definitions=7:2
# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for the two-gonal architecture exploration.

Pins both the BREAK (static private gonal falls to frequency analysis) and
the FIX (PCEA-advanced gonal resists it; legitimate reader recovers all).
The advancing-gonal test is skipped if the real PCEA cipher is not
importable. These pin a measured candidate, NOT a security guarantee — see
the module's UNRUN ATTACKS gate.
"""

import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location(
    "gonal_architecture",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "gonal_architecture.py",
)
ga = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ga)

import pytest


def test_static_gonal_falls_to_frequency_analysis():
    # The break: a static private gonal is a substitution cipher.
    r = ga.static_gonal_frequency_break()
    assert r["rate"] > 0.5, r


@pytest.mark.skipif(not ga.REAL_PCEA, reason="real PCEA cipher not importable")
def test_advancing_gonal_resists_and_reader_recovers():
    r = ga.advancing_gonal_resists()
    # frequency analysis collapses to ~random
    assert r["frequency_recovery_rate"] < 0.1, r
    # known-plaintext does not predict held-out tokens
    assert r["known_plaintext_heldout_rate"] < 0.1, r
    # legitimate reader recovers everything
    assert r["legitimate_recovery"] == r["count"], r
# ratios: loc_comments=18:13 imports_exports=3:2 calls_definitions=7:2
