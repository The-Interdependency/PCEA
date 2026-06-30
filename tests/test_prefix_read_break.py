# ratios: loc_comments=18:7 imports_exports=3:2 calls_definitions=7:2
# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for the prefix-read structural break.

Pins the decisive negative result: a factor of P is reconstructable
directly from P's prefix block, with no key-space search, at any depth.
Skipped without ucns.
"""

import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "prefix_read_break",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "prefix_read_break.py",
)
prb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prb)

pytestmark = pytest.mark.skipif(
    not prb.UCNS_AVAILABLE, reason="ucns not installed; prefix-read break inert"
)


def test_flat_objects_are_reconstructed_without_search():
    r = prb.prefix_read_break(depth=0, trials=60)
    assert r["rate"] > 0.95


def test_payload_nesting_does_not_block_the_break():
    r = prb.prefix_read_break(depth=1, trials=60)
    assert r["rate"] > 0.95
# ratios: loc_comments=18:7 imports_exports=3:2 calls_definitions=7:2
