"""
Tests for key wrap / unwrap.
"""

import os
import pytest

from guardian_state.aead import AuthenticationError
from guardian_state.wrap import unwrap_live_key, wrap_live_key


def test_round_trip():
    live_key = os.urandom(32)
    meta_key = os.urandom(32)
    wrapped = wrap_live_key(live_key, meta_key, epoch=1, key_id="k1")
    recovered = unwrap_live_key(wrapped, meta_key)
    assert recovered == live_key


def test_wrong_meta_key_raises():
    live_key = os.urandom(32)
    meta_key = os.urandom(32)
    wrapped = wrap_live_key(live_key, meta_key, epoch=1, key_id="k1")
    with pytest.raises(AuthenticationError):
        unwrap_live_key(wrapped, os.urandom(32))


def test_wrapped_live_key_contains_no_plaintext():
    live_key = os.urandom(32)
    meta_key = os.urandom(32)
    wrapped = wrap_live_key(live_key, meta_key, epoch=1, key_id="k1")
    # The wrapped blob should not contain the plaintext live_key verbatim
    assert live_key not in wrapped.wrapped_live_key


def test_wrap_key_hash_is_hex():
    wrapped = wrap_live_key(os.urandom(32), os.urandom(32), epoch=1, key_id="k1")
    int(wrapped.wrap_key_hash, 16)  # should not raise


def test_epoch_and_key_id_bound_in_aad():
    live_key = os.urandom(32)
    meta_key = os.urandom(32)
    wrapped = wrap_live_key(live_key, meta_key, epoch=1, key_id="k1")
    # Mutate epoch — unwrap should fail because AAD changes
    import dataclasses
    wrong_epoch = dataclasses.replace(wrapped, epoch=999)
    with pytest.raises(AuthenticationError):
        unwrap_live_key(wrong_epoch, meta_key)


def test_two_wraps_produce_different_blobs():
    live_key = os.urandom(32)
    meta_key = os.urandom(32)
    w1 = wrap_live_key(live_key, meta_key, epoch=1, key_id="k1")
    w2 = wrap_live_key(live_key, meta_key, epoch=1, key_id="k1")
    # Different random nonces each time
    assert w1.wrapped_live_key != w2.wrapped_live_key
