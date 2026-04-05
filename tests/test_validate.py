# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for validate_invariant().
"""

import os
import pytest

from guardian_state import validate_invariant
from guardian_state.validate import InvariantViolation
from guardian_state.types import MetaShares, SealedState, WrappedLiveKey


def _valid_set(epoch=1):
    wrapped = WrappedLiveKey(
        key_id="k1",
        epoch=epoch,
        wrapped_live_key=os.urandom(48),  # nonce(12) + ciphertext(32) + tag(16) = 60; just needs to be non-empty
        wrap_key_hash="a" * 64,
    )
    sealed = SealedState(
        epoch=epoch,
        key_id="k1",
        ciphertext=os.urandom(48),
        nonce=os.urandom(12),
        aad=b"aad",
        sealed_by="g1",
    )
    shares = [
        {"sentinel_id": "s1", "share": os.urandom(32), "index": 1},
        {"sentinel_id": "s2", "share": os.urandom(32), "index": 2},
        {"sentinel_id": "s3", "share": os.urandom(32), "index": 3},
    ]
    meta = MetaShares(
        epoch=epoch,
        total_shares=3,
        threshold=2,
        shares=shares,
        commitment="x" * 64,
    )
    return wrapped, sealed, meta


def test_valid_set_passes():
    validate_invariant(*_valid_set())


def test_epoch_mismatch_sealed_raises():
    wrapped, sealed, meta = _valid_set(epoch=1)
    import dataclasses
    sealed = dataclasses.replace(sealed, epoch=2)
    with pytest.raises(InvariantViolation, match="epoch mismatch"):
        validate_invariant(wrapped, sealed, meta)


def test_epoch_mismatch_meta_raises():
    wrapped, sealed, meta = _valid_set(epoch=1)
    import dataclasses
    meta = dataclasses.replace(meta, epoch=99)
    with pytest.raises(InvariantViolation, match="epoch mismatch"):
        validate_invariant(wrapped, sealed, meta)


def test_key_id_mismatch_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    sealed = dataclasses.replace(sealed, key_id="different")
    with pytest.raises(InvariantViolation, match="key_id mismatch"):
        validate_invariant(wrapped, sealed, meta)


def test_threshold_below_2_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    meta = dataclasses.replace(meta, threshold=1)
    with pytest.raises(InvariantViolation, match="threshold"):
        validate_invariant(wrapped, sealed, meta)


def test_threshold_exceeds_total_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    meta = dataclasses.replace(meta, threshold=10)
    with pytest.raises(InvariantViolation, match="threshold"):
        validate_invariant(wrapped, sealed, meta)


def test_wrong_shares_count_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    meta = dataclasses.replace(meta, total_shares=5)
    with pytest.raises(InvariantViolation, match="shares list length"):
        validate_invariant(wrapped, sealed, meta)


def test_empty_wrapped_live_key_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    wrapped = dataclasses.replace(wrapped, wrapped_live_key=b"")
    with pytest.raises(InvariantViolation, match="wrapped_live_key"):
        validate_invariant(wrapped, sealed, meta)


def test_empty_ciphertext_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    sealed = dataclasses.replace(sealed, ciphertext=b"")
    with pytest.raises(InvariantViolation, match="ciphertext"):
        validate_invariant(wrapped, sealed, meta)


def test_wrong_nonce_length_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    sealed = dataclasses.replace(sealed, nonce=os.urandom(8))
    with pytest.raises(InvariantViolation, match="nonce"):
        validate_invariant(wrapped, sealed, meta)


def test_duplicate_share_indices_raises():
    wrapped, sealed, meta = _valid_set()
    import dataclasses
    bad_shares = [
        {"sentinel_id": "s1", "share": os.urandom(32), "index": 1},
        {"sentinel_id": "s2", "share": os.urandom(32), "index": 1},  # duplicate
        {"sentinel_id": "s3", "share": os.urandom(32), "index": 3},
    ]
    meta = dataclasses.replace(meta, shares=bad_shares)
    with pytest.raises(InvariantViolation, match="indices"):
        validate_invariant(wrapped, sealed, meta)
