# ratios: loc_comments=61:2 imports_exports=3:5 calls_definitions=11:6
# GPT/Claude generated; context, prompt Erin Spencer
"""Tests for the Option D UCNS one-way-map candidate gate."""

from __future__ import annotations

import importlib.util
import pathlib


_spec = importlib.util.spec_from_file_location(
    "one_way_map_gate",
    pathlib.Path(__file__).parent.parent / "pcea-ucns" / "one_way_map_gate.py",
)
owg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(owg)


def _complete_candidate() -> dict:
    return {
        "id": "toy-lossy-nonproduct-map",
        "public_map": "public = F(secret, base) with an explicitly lossy non-product image",
        "private_material": ["secret UCNS object"],
        "public_material": ["base object", "lossy image"],
        "shared_secret": "KDF(canonical honest shared image)",
        "attacks": {name: "planned harness" for name in owg.REQUIRED_ATTACKS},
    }


def test_complete_attack_agenda_can_pass_without_security_claims() -> None:
    result = owg.evaluate_candidate(_complete_candidate())

    assert result.ok
    assert result.missing_attacks == ()
    assert result.forbidden_patterns == ()
    assert result.notes == ()


def test_missing_inverse_families_block_happy_path_work() -> None:
    candidate = _complete_candidate()
    candidate["attacks"] = {"quotient_division": "planned harness"}

    result = owg.evaluate_candidate(candidate)

    assert not result.ok
    assert "minkowski_set_basis" in result.missing_attacks
    assert "scaling_law" in result.missing_attacks
    assert "candidate lacks required attack coverage" in result.notes


def test_known_broken_public_map_families_are_rejected() -> None:
    for public_map in (
        "public = secret ⊠ base",
        "public = multiply(secret, base)",
        "set-project(secret ⊠ base)",
    ):
        candidate = _complete_candidate()
        candidate["public_map"] = public_map
        result = owg.evaluate_candidate(candidate)

        assert not result.ok
        assert result.forbidden_patterns


def test_positive_security_claim_blocks_candidate_gate() -> None:
    candidate = _complete_candidate()
    candidate["security_claim"] = "secure KEM"

    result = owg.evaluate_candidate(candidate)

    assert not result.ok
    assert "remove positive security claims before the attack agenda passes" in result.notes


def test_required_attack_set_names_the_current_option_d_obstructions() -> None:
    assert owg.REQUIRED_ATTACKS == {
        "quotient_division",
        "prefix_normalization_readout",
        "minkowski_set_basis",
        "catalogue_pruning",
        "finite_keyspace_enumeration",
        "meet_in_the_middle",
        "active_malleability",
        "honest_correctness_at_scale",
        "scaling_law",
    }
# ratios: loc_comments=61:2 imports_exports=3:5 calls_definitions=11:6
