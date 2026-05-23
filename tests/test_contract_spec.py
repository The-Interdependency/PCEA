"""Contract-level tests for the PCEA↔UCNS boundary assumptions.

These tests codify the v0 decision-forcing contract in executable form for PCEA:
- PCEA inversion/decryption is key-derived (from last_state), not UCNS inverse APIs.
- Security must not rely on arithmetic non-invertibility.
- The package must not import UCNS or catalogue-dependent inverse operations.
"""

from __future__ import annotations

import pathlib

import pytest

from pcea import decrypt_state, encrypt_state


CIRCLES = 7
TENSORS = 7



def _seed(base: int = 1) -> list[list[int]]:
    return [[(base + c * TENSORS + t) for t in range(TENSORS)] for c in range(CIRCLES)]



def test_decrypt_requires_matching_key_state() -> None:
    """Using the wrong last_state must fail to recover plaintext."""
    state = [_seed(100), _seed(200)]
    last = [_seed(1), _seed(2)]
    wrong_last = [_seed(3), _seed(4)]

    encrypted = encrypt_state(state, last)
    recovered_wrong = decrypt_state(encrypted, wrong_last)

    assert recovered_wrong != state



def test_no_ucns_dependency_in_runtime_modules() -> None:
    """PCEA runtime code should remain independent from UCNS inverse buckets."""
    runtime_files = [
        pathlib.Path("pcea/__init__.py"),
        pathlib.Path("pcea/cipher.py"),
        pathlib.Path("pcea/instance.py"),
        pathlib.Path("pcea/kdf.py"),
        pathlib.Path("pcea/codec.py"),
        pathlib.Path("pcea/primes.py"),
    ]
    forbidden_tokens = {
        "ucns",
        "left_quotient",
        "right_quotient",
        "factor_search",
        "catalogue",
    }

    for file in runtime_files:
        text = file.read_text(encoding="utf-8").lower()
        for token in forbidden_tokens:
            assert token not in text, f"Forbidden token '{token}' found in {file}"


@pytest.mark.parametrize("word_bits", [32, 64, 128])
def test_forward_roundtrip_is_self_sufficient(word_bits: int) -> None:
    """Roundtrip must succeed using forward arithmetic + key material only."""
    state = [_seed(10), _seed(20), _seed(30)]
    last = [_seed(1), _seed(2), _seed(3)]
    encrypted = encrypt_state(state, last, word_bits=word_bits)
    assert decrypt_state(encrypted, last, word_bits=word_bits) == state
