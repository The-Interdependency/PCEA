# ratios: loc_comments=55:2 imports_exports=5:5 calls_definitions=21:5
# GPT/Claude generated; context, prompt Erin Spencer
"""Tests for the concrete Option D UCNS map candidate fed into the gate."""

from __future__ import annotations

import importlib.util
import pathlib
from fractions import Fraction
from types import SimpleNamespace


ROOT = pathlib.Path(__file__).parent.parent

_gate_spec = importlib.util.spec_from_file_location(
    "one_way_map_gate", ROOT / "pcea-ucns" / "one_way_map_gate.py"
)
owg = importlib.util.module_from_spec(_gate_spec)
_gate_spec.loader.exec_module(owg)

_candidate_spec = importlib.util.spec_from_file_location(
    "option_d_ucns_map", ROOT / "pcea-ucns" / "option_d_ucns_map.py"
)
option_d = importlib.util.module_from_spec(_candidate_spec)
_candidate_spec.loader.exec_module(option_d)


def test_face_payload_spectrum_candidate_is_fed_to_gate() -> None:
    candidate = option_d.candidate()
    result = owg.evaluate_candidate(candidate)

    assert candidate["id"] == "face-payload-spectrum-projection"
    assert result == option_d.gate_result()
    assert result.ok


def test_fed_candidate_has_every_required_attack_family() -> None:
    candidate = option_d.candidate()

    assert set(candidate["attacks"]) == owg.REQUIRED_ATTACKS


def test_fed_candidate_is_not_a_positive_security_claim() -> None:
    candidate = option_d.candidate()
    public_map = candidate["public_map"].lower()

    assert "security_claim" not in candidate
    assert "secure" not in candidate["shared_secret"].lower()
    assert "public = secret ⊠ base" not in public_map
    assert "set-project(secret ⊠ base)" not in public_map


def test_fed_candidate_names_withheld_ucns_structure() -> None:
    candidate = option_d.candidate()
    public_map = candidate["public_map"]

    assert "do not publish ordered cells" in public_map
    assert "exact angle set" in public_map
    assert "payload bodies" in public_map


def test_spectrum_projection_publishes_only_coarse_ucns_features() -> None:
    payload = SimpleNamespace(A_plus=[(Fraction(1, 11), None)], faces=[1], n_min=11)
    composed = SimpleNamespace(
        n_min=60,
        A_plus=[(Fraction(1, 3), payload), (Fraction(2, 5), None)],
        faces=[0, 1],
    )

    projection = option_d.spectrum_projection(composed)

    assert projection == {
        "carrier_support": (2, 3, 5),
        "cell_count_bucket": "2-3",
        "face_parity_counts": ((0, 1), (1, 1)),
        "payload_depth_counts": ((0, 1), (1, 1)),
        "denominator_buckets": (("2-3", 1), ("4-7", 1)),
    }
    assert "A_plus" not in projection
    assert "faces" not in projection
# ratios: loc_comments=55:2 imports_exports=5:5 calls_definitions=21:5
