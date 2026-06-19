# GPT/Claude generated; context, prompt Erin Spencer
"""Concrete Option D UCNS map candidate fed into the one-way-map gate.

This is a candidate *specification*, not a cipher and not a security result. It
names one map family worth attacking next: a face/payload spectrum projection.
The map is intentionally not a published UCNS product. It composes a secret and
base internally, then publishes only coarse spectrum data: carrier support,
cell-count buckets, face-parity counts, payload-depth counts, and denominator
buckets. It withholds ordered cells, exact angle set, multiplicity, faces, and
payload bodies.

Rationale: previous candidates failed by publishing too much product structure
or by reducing to a Minkowski angle-set basis problem. This candidate asks
whether a coarser UCNS-derived spectrum can keep honest-party agreement while
denying quotient, prefix, and set-basis inverses. |∆|No harness has shown that
yet; this file only feeds the map into the required attack-agenda gate.|∆|
"""

from __future__ import annotations

import importlib.util
import pathlib
from collections import Counter
from collections.abc import Mapping, Sequence


_GATE_PATH = pathlib.Path(__file__).with_name("one_way_map_gate.py")
_GATE_SPEC = importlib.util.spec_from_file_location("one_way_map_gate", _GATE_PATH)
one_way_map_gate = importlib.util.module_from_spec(_GATE_SPEC)
_GATE_SPEC.loader.exec_module(one_way_map_gate)


FACE_PAYLOAD_SPECTRUM_CANDIDATE: dict[str, object] = {
    "id": "face-payload-spectrum-projection",
    "public_map": (
        "public = spectrum_projection(compose(secret, base)); publish carrier-support, "
        "cell-count buckets, face-parity counts, payload-depth counts, and denominator "
        "buckets; do not publish ordered cells, exact angle set, multiplicity, faces, "
        "or payload bodies"
    ),
    "private_material": [
        "secret UCNS object",
        "exact angle positions",
        "exact faces",
        "payload bodies",
    ],
    "public_material": [
        "base UCNS object",
        "carrier-support spectrum",
        "cell-count buckets",
        "face-parity counts",
        "payload-depth counts",
        "denominator buckets",
        "algorithm parameters",
    ],
    "shared_secret": (
        "KDF over a future honest bilateral spectrum image if, and only if, "
        "honest agreement survives the correctness-at-scale harness"
    ),
    "attacks": {
        "quotient_division": "Attempt left/right quotient using every spectrum-compatible lift.",
        "prefix_normalization_readout": "Check whether canonical normalization leaks host prefixes or ordered cells through the buckets.",
        "minkowski_set_basis": "Run set-basis recovery against every denominator bucket and against bucket refinements.",
        "catalogue_pruning": "Measure catalogue pruning from carrier support, cell-count, face-parity, and depth constraints.",
        "finite_keyspace_enumeration": "Enumerate finite toy key spaces and count compatible secrets per public spectrum.",
        "meet_in_the_middle": "Split the spectrum constraints into independent halves and measure collision speedup.",
        "active_malleability": "Mutate base/public spectrum fields and check whether derived secrets or accept/reject behavior leak structure.",
        "honest_correctness_at_scale": "Test bilateral agreement and failure rate as carrier, depth, and payload width grow.",
        "scaling_law": "Fit attack cost versus key-space size and reject if any inverse is sublinear or plateaus.",
    },
}


def _pow2_bucket(value: int) -> str:
    if value <= 0:
        return "0"
    lower = 1 << (value.bit_length() - 1)
    upper = (lower << 1) - 1
    return str(lower) if lower == upper else f"{lower}-{upper}"


def _prime_support(value: int) -> tuple[int, ...]:
    n = abs(value)
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            factors.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor += 1 if divisor == 2 else 2
    if n > 1:
        factors.append(n)
    return tuple(factors)


def _payload_depth(payload: object) -> int:
    if payload is None:
        return 0
    nested = getattr(payload, "A_plus", None)
    if nested is not None:
        return 1 + max((_payload_depth(child) for _, child in nested), default=0)
    if isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        return 1 + max((_payload_depth(child) for child in payload), default=0)
    return 1


def spectrum_projection(composed: object) -> dict[str, object]:
    """Project a composed UCNS-like object to the candidate public spectrum.

    The function accepts a UCNSObject-like value by protocol: ``n_min``,
    ``A_plus`` as ``(angle, payload)`` pairs, and optional ``faces``. It does
    not multiply secrets by bases; callers must feed the already-composed
    object from the UCNS harness. Exact angles, ordered cells, payload bodies,
    and exact face vectors are deliberately not returned.
    """

    cells = list(getattr(composed, "A_plus", ()) or ())
    faces = list(getattr(composed, "faces", ()) or ())
    den_buckets = Counter()
    depth_counts = Counter()
    for angle, payload in cells:
        denominator = int(getattr(angle, "denominator", 1))
        den_buckets[_pow2_bucket(denominator)] += 1
        depth_counts[_payload_depth(payload)] += 1

    face_parity = Counter(int(face) % 2 for face in faces)
    return {
        "carrier_support": _prime_support(int(getattr(composed, "n_min", 0) or 0)),
        "cell_count_bucket": _pow2_bucket(len(cells)),
        "face_parity_counts": ((0, face_parity[0]), (1, face_parity[1])),
        "payload_depth_counts": tuple(sorted(depth_counts.items())),
        "denominator_buckets": tuple(sorted(den_buckets.items())),
    }


GATE_RESULT = one_way_map_gate.evaluate_candidate(FACE_PAYLOAD_SPECTRUM_CANDIDATE)


def candidate() -> Mapping[str, object]:
    """Return the concrete Option D candidate currently fed to the gate."""

    return FACE_PAYLOAD_SPECTRUM_CANDIDATE


def gate_result():
    """Return the gate result for the fed candidate."""

    return GATE_RESULT
