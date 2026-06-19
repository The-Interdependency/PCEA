# GPT/Claude generated; context, prompt Erin Spencer
"""Tests for concrete non-Option-D UCNS/PCEA evolution specs."""

from __future__ import annotations

import importlib.util
import json
import pathlib


ROOT = pathlib.Path(__file__).parent.parent
LEDGER = ROOT / "pcea-ucns" / "candidate-ledger.json"

_spec = importlib.util.spec_from_file_location(
    "option_family_specs", ROOT / "pcea-ucns" / "option_family_specs.py"
)
option_specs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(option_specs)


def test_all_remaining_option_specs_pass_their_gate() -> None:
    for spec in option_specs.OPTION_FAMILY_SPECS.values():
        result = option_specs.evaluate_spec(spec)
        assert result.ok, (spec["id"], result)


def test_specs_cover_the_non_option_d_families() -> None:
    assert option_specs.spec_ids() == {
        "provisioned-symmetric-pcea",
        "ucns-context-binding",
        "hybrid-kem-keys-pcea",
        "pcea-advanced-gonal-state-channel",
        "ucns-commitments-delayed-disclosure",
    }


def test_specs_are_not_positive_security_claims() -> None:
    for spec in option_specs.OPTION_FAMILY_SPECS.values():
        assert "security_claim" not in spec
        assert "not" in spec["boundary"].lower()
        assert spec["required_checks"]


def test_option_specs_are_registered_in_ledger() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    candidates = {candidate["id"]: candidate for candidate in ledger["candidates"]}

    for spec_id in option_specs.spec_ids():
        assert spec_id in candidates
        assert "pcea-ucns/option_family_specs.py" in candidates[spec_id]["harness"]
        assert "tests/test_option_family_specs.py" in candidates[spec_id]["tests"]
