# ratios: loc_comments=60:19 imports_exports=3:3 calls_definitions=20:4
# GPT/Claude generated; context, prompt Erin Spencer
"""Option D gate for UCNS-native one-way-map candidates.

This module is deliberately small and dependency-free. It does not test UCNS
arithmetic and it does not bless a candidate. It records the minimum evidence a
future UCNS public map must provide before the proving ground treats it as more
than a sketch.

The current research boundary is strict: after the product, quotient, prefix,
and lossy-projection/Minkowski breaks, a candidate must clear several inverse
families before happy-path KEM code is useful. |∆|Passing this gate means only
"attack agenda complete enough to run," not "secure."|∆|
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import NamedTuple


REQUIRED_ATTACKS = {
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

FORBIDDEN_PUBLIC_MAP_PATTERNS = (
    "public = secret ⊠ base",
    "public = base ⊠ secret",
    "public = multiply(secret, base)",
    "public = multiply(base, secret)",
    "set-project(secret ⊠ base)",
)


class GateResult(NamedTuple):
    """Result of checking whether an Option D candidate is ready to attack."""

    ok: bool
    missing_attacks: tuple[str, ...]
    forbidden_patterns: tuple[str, ...]
    notes: tuple[str, ...]


def _present_attacks(candidate: Mapping[str, object]) -> set[str]:
    attacks = candidate.get("attacks", {})
    if isinstance(attacks, Mapping):
        return {str(name) for name, spec in attacks.items() if spec}
    if isinstance(attacks, Iterable) and not isinstance(attacks, (str, bytes)):
        return {str(name) for name in attacks}
    return set()


def evaluate_candidate(candidate: Mapping[str, object]) -> GateResult:
    """Return the missing evidence for a proposed UCNS one-way-map candidate.

    Expected candidate keys are intentionally plain dictionaries so research
    sketches, JSON, or YAML can feed this without importing UCNS. Required keys:
    ``id``, ``public_map``, ``private_material``, ``public_material``,
    ``shared_secret``, and ``attacks``.
    """

    notes: list[str] = []
    for key in ("id", "public_map", "private_material", "public_material", "shared_secret"):
        if not candidate.get(key):
            notes.append(f"missing required field: {key}")

    public_map = str(candidate.get("public_map", "")).lower()
    forbidden = tuple(
        pattern for pattern in FORBIDDEN_PUBLIC_MAP_PATTERNS if pattern.lower() in public_map
    )
    if forbidden:
        notes.append(
            "public map matches a family already broken by quotient/product or Minkowski analysis"
        )

    present = _present_attacks(candidate)
    missing = tuple(sorted(REQUIRED_ATTACKS - present))
    if missing:
        notes.append("candidate lacks required attack coverage")

    if candidate.get("security_claim"):
        notes.append("remove positive security claims before the attack agenda passes")

    return GateResult(
        ok=not missing and not forbidden and not notes,
        missing_attacks=missing,
        forbidden_patterns=forbidden,
        notes=tuple(notes),
    )


def is_ready_for_happy_path(candidate: Mapping[str, object]) -> bool:
    """True only when the candidate has a complete attack agenda and no claims."""

    return evaluate_candidate(candidate).ok
# ratios: loc_comments=60:19 imports_exports=3:3 calls_definitions=20:4
