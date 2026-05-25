# GPT/Claude generated; context, prompt Erin Spencer
"""PCEA↔UCNS interface-contract constants and guardrails.

This module centralizes the contract boundary so docs, tests, and tooling share
one source of truth.
"""
from __future__ import annotations

DECISION = "A"  # Invert via keys, never via UCNS inverse/catalogue APIs.

SECURITY_INVARIANT = (
    "PCEA security rests on key management, not on UCNS inversion hardness. "
    "Adversaries are assumed able to invert carrier arithmetic."
)

FORBIDDEN_UCNS_SYMBOLS = {
    "ucns",
    "left_quotient",
    "right_quotient",
    "left_quotient_payload",
    "factor_search",
    "factor_search_v06",
    "is_seq_composite",
    "catalogue",
}

RUNTIME_MODULES = (
    "pcea/__init__.py",
    "pcea/cipher.py",
    "pcea/instance.py",
    "pcea/kdf.py",
    "pcea/codec.py",
    "pcea/primes.py",
)


def contract_statement() -> str:
    """Canonical contract statement for docs/UX surfaces."""
    return (
        "PCEA decrypts/inverts via keys (Option A), never via UCNS inverse APIs. "
        + SECURITY_INVARIANT
    )
