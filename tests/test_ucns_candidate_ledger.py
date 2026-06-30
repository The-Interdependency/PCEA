# ratios: loc_comments=56:6 imports_exports=3:4 calls_definitions=17:5
# GPT/Claude generated; context, prompt Erin Spencer
"""Validate the UCNS proving-ground candidate ledger.

The ledger is process guardrail, not a security proof: it makes every UCNS
candidate name its claim, public/private material, known attacks, harnesses,
status, and next attack before anyone treats it as progress.
"""

from __future__ import annotations

import json
import pathlib


LEDGER = pathlib.Path("pcea-ucns/candidate-ledger.json")
REQUIRED_KEYS = {
    "id",
    "claim",
    "public_material",
    "private_material",
    "known_attacks",
    "harness",
    "tests",
    "status",
    "next_attack",
}


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_candidate_ledger_schema_is_complete() -> None:
    data = _ledger()
    allowed_status = set(data["status_values"])
    candidates = data["candidates"]

    assert data["schema_version"] == 1
    assert candidates

    ids = [candidate["id"] for candidate in candidates]
    assert len(ids) == len(set(ids)), "candidate ids must be unique"

    for candidate in candidates:
        assert REQUIRED_KEYS <= candidate.keys(), candidate["id"]
        assert candidate["status"] in allowed_status, candidate["id"]
        assert candidate["claim"].strip(), candidate["id"]
        assert candidate["next_attack"].strip(), candidate["id"]
        assert candidate["public_material"], candidate["id"]
        assert candidate["private_material"], candidate["id"]
        assert candidate["known_attacks"], candidate["id"]


def test_referenced_harnesses_and_tests_exist() -> None:
    for candidate in _ledger()["candidates"]:
        harness = candidate["harness"]
        if harness:
            for part in [item.strip() for item in harness.split(";")]:
                assert pathlib.Path(part).exists(), f"missing harness {part} for {candidate['id']}"
        for test_path in candidate["tests"]:
            assert pathlib.Path(test_path).exists(), (
                f"missing test {test_path} for {candidate['id']}"
            )


def test_no_surviving_ucns_candidate_lacks_a_next_attack() -> None:
    for candidate in _ledger()["candidates"]:
        if candidate["status"] in {"survives-current-harness", "open-research"}:
            assert "None" not in candidate["next_attack"], candidate["id"]
            assert candidate["next_attack"].endswith("."), candidate["id"]


def test_broken_or_forbidden_candidates_stay_out_of_shipping_language() -> None:
    for candidate in _ledger()["candidates"]:
        if candidate["status"] in {"broken", "forbidden"}:
            combined = " ".join(
                [candidate["claim"], candidate["next_attack"], *candidate["known_attacks"]]
            ).lower()
            assert "ship" not in combined
            assert "recommended" not in combined
# ratios: loc_comments=56:6 imports_exports=3:4 calls_definitions=17:5
