# ratios: loc_comments=161:11 imports_exports=3:3 calls_definitions=9:3
# GPT/Claude generated; context, prompt Erin Spencer
"""Concrete candidate specs for the non-Option-D UCNS/PCEA evolution paths.

These specs do for the remaining options what ``option_d_ucns_map.py`` does for
Option D: feed a concrete artifact into a small gate so the proving ground has
something auditable before code grows around it. They are not implementations and
not security claims. |∆|A passing spec means the next harness is well-scoped;
it does not mean the option is production-ready.|∆|
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import NamedTuple


REQUIRED_SPEC_KEYS = {
    "id",
    "option",
    "artifact",
    "boundary",
    "public_material",
    "private_material",
    "required_checks",
    "next_harness",
}

OPTION_FAMILY_SPECS: dict[str, dict[str, object]] = {
    "provisioned-symmetric-pcea": {
        "id": "provisioned-symmetric-pcea",
        "option": "A",
        "artifact": "ratcheted-authenticated-session-v0 spec around provisioned PCEA state",
        "boundary": "Pre-shared-key mode only; not UCNS public-key encryption.",
        "public_material": [
            "algorithm version",
            "message number",
            "associated data",
            "MAC tag",
            "optional UCNS context id",
        ],
        "private_material": [
            "provisioned seed",
            "traffic secret",
            "last_state",
            "ratchet secret",
        ],
        "required_checks": [
            "wrong_key_failure",
            "transcript_binding",
            "replay_rejection",
            "reordering_rejection",
            "decrypt_failure_state_rollback",
            "key_separation",
            "resynchronization_metadata_leakage",
        ],
        "next_harness": "Build a non-runtime session prototype with verify-before-advance decrypt behavior.",
    },
    "ucns-context-binding": {
        "id": "ucns-context-binding",
        "option": "B",
        "artifact": "canonical-ucns-transcript-context-v0 spec for KDF/MAC associated data",
        "boundary": "UCNS supplies context binding only; not secrecy.",
        "public_material": [
            "canonical UCNS identity object",
            "session id",
            "capability label",
            "algorithm version",
        ],
        "private_material": [
            "provisioned or KEM-derived traffic secret",
            "PCEA ratchet state",
        ],
        "required_checks": [
            "identity_substitution_changes_keys",
            "session_substitution_changes_keys",
            "capability_substitution_changes_keys",
            "canonical_equivalent_context_matches",
            "unknown_key_share_rejection",
        ],
        "next_harness": "Define canonical UCNS serialization fixtures and KDF/MAC transcript tests.",
    },
    "hybrid-kem-keys-pcea": {
        "id": "hybrid-kem-keys-pcea",
        "option": "C",
        "artifact": "hybrid-kem-policy-record-v0 before any KEM/DH implementation",
        "boundary": "Cold-start secrecy comes from reviewed KEM/DH policy, not UCNS hardness.",
        "public_material": [
            "KEM or DH public key",
            "encapsulation packet",
            "algorithm identifiers",
            "handshake transcript",
        ],
        "private_material": [
            "KEM or DH private key",
            "derived shared secret",
            "PCEA traffic secret",
        ],
        "required_checks": [
            "dependency_policy_decision",
            "external_test_vectors_required",
            "invalid_public_key_rejection",
            "downgrade_rejection",
            "transcript_binding",
            "no_homegrown_crypto_without_review",
        ],
        "next_harness": "Write a decision record choosing dependency exception, audited vendoring, org-owned implementation, or no hybrid path.",
    },
    "pcea-advanced-gonal-state-channel": {
        "id": "pcea-advanced-gonal-state-channel",
        "option": "E",
        "artifact": "53-to-32-gonal-bridge-v0 spec for synchronized state channels",
        "boundary": "Synchronized-agent state channel only; not cold-start key establishment.",
        "public_material": [
            "public gonal vocabulary",
            "ciphertext angle sequence",
            "algorithm parameters",
        ],
        "private_material": [
            "instantiation seed",
            "private phase",
            "private vertex permutation",
            "PCEA keystream position",
        ],
        "required_checks": [
            "bridge_collision_rate",
            "alphabet_reuse_groups",
            "chosen_plaintext_probe",
            "known_plaintext_probe",
            "state_recovery_probe",
            "long_run_legitimate_recovery",
        ],
        "next_harness": "Turn the 53-to-32 bridge from illustrative slice logic into parameterized attack fixtures.",
    },
    "ucns-commitments-delayed-disclosure": {
        "id": "ucns-commitments-delayed-disclosure",
        "option": "F",
        "artifact": "ucns-commit-open-transcript-v0 using standard-library hashing",
        "boundary": "Commitment/transcript discipline only; not encryption and not a trapdoor.",
        "public_material": [
            "commitment digest",
            "canonical UCNS commitment context",
            "algorithm version",
        ],
        "private_material": [
            "opened value",
            "nonce",
            "optional shared transcript secret",
        ],
        "required_checks": [
            "binding_under_canonical_equivalence",
            "low_entropy_bruteforce_visibility",
            "nonce_entropy_requirement",
            "context_substitution_rejection",
            "replay_rejection",
        ],
        "next_harness": "Prototype commit/open fixtures and brute-force low-entropy openings to quantify hiding limits.",
    },
}


class SpecResult(NamedTuple):
    """Validation result for a concrete non-D option candidate spec."""

    ok: bool
    missing_keys: tuple[str, ...]
    notes: tuple[str, ...]


def evaluate_spec(spec: Mapping[str, object]) -> SpecResult:
    """Validate that an option family spec is ready for its first harness."""

    missing = tuple(sorted(key for key in REQUIRED_SPEC_KEYS if not spec.get(key)))
    notes: list[str] = []
    if spec.get("security_claim"):
        notes.append("remove positive security claims before implementation")
    if not spec.get("required_checks"):
        notes.append("required_checks must name concrete failure/attack gates")
    boundary = str(spec.get("boundary", "")).lower()
    if "not" not in boundary:
        notes.append("boundary must state what the option is not")
    return SpecResult(ok=not missing and not notes, missing_keys=missing, notes=tuple(notes))


def spec_ids() -> set[str]:
    """Return ids for the non-D options currently fed into the spec gate."""

    return set(OPTION_FAMILY_SPECS)
# ratios: loc_comments=161:11 imports_exports=3:3 calls_definitions=9:3
