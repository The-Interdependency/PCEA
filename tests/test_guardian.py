# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for seal_live_state / unseal_live_state round-trips and rekey.
"""

import os
import pytest

from guardian_state import (
    AuthenticationError,
    LiveState,
    derive_keys,
    rekey_epoch,
    seal_live_state,
    unseal_live_state,
)


def _make_state(epoch=1):
    return LiveState(
        epoch=epoch,
        spiral={"phase": 0.1, "magnitude": 1.0, "base": 2.0},
        cores={"Phi": [[1, 0], [0, 1]], "Psi": [[0, 1], [1, 0]], "Omega": [[1, 1], [1, 1]]},
        density_matrix=[[0.5, 0.0], [0.0, 0.5]],
        coherence=0.95,
        transport={"type": "identity"},
        last_renorm=0.0,
    )


def _seal(state, epoch=1, key_id="k1", seal_counter=0):
    ikm = os.urandom(32)
    live_key, _ = derive_keys(ikm, epoch, key_id, "node1")
    return seal_live_state(state, live_key, epoch, key_id, seal_counter, "node1", "guardian1"), live_key


def test_seal_unseal_round_trip():
    state = _make_state()
    sealed, live_key = _seal(state)
    recovered = unseal_live_state(sealed, live_key)
    assert recovered.epoch == state.epoch
    assert recovered.coherence == state.coherence
    assert recovered.spiral == state.spiral
    assert recovered.cores == state.cores


def test_sealed_state_epoch_matches():
    state = _make_state(epoch=3)
    ikm = os.urandom(32)
    live_key, _ = derive_keys(ikm, 3, "k1", "node1")
    sealed = seal_live_state(state, live_key, 3, "k1", 0, "node1", "guardian1")
    assert sealed.epoch == 3


def test_wrong_key_raises():
    state = _make_state()
    sealed, _ = _seal(state)
    wrong_key = os.urandom(32)
    with pytest.raises(AuthenticationError):
        unseal_live_state(sealed, wrong_key)


def test_different_seal_counters_produce_different_nonces():
    state = _make_state()
    ikm = os.urandom(32)
    live_key, _ = derive_keys(ikm, 1, "k1", "node1")
    s1 = seal_live_state(state, live_key, 1, "k1", 0, "node1", "g1")
    s2 = seal_live_state(state, live_key, 1, "k1", 1, "node1", "g1")
    assert s1.nonce != s2.nonce


def test_rekey_increases_epoch():
    old_state = _make_state(epoch=1)
    new_sealed, new_wrapped, new_meta, rekey_rec = rekey_epoch(
        old_state=old_state,
        old_epoch=1,
        new_ikm=os.urandom(32),
        new_epoch=2,
        key_id="k1",
        guardian_node_id="node1",
        sealed_by="guardian1",
        seal_counter=0,
        new_threshold=2,
        sentinels=["s1", "s2", "s3"],
    )
    assert new_sealed.epoch == 2
    assert new_wrapped.epoch == 2
    assert new_meta.epoch == 2
    assert rekey_rec.from_epoch == 1
    assert rekey_rec.to_epoch == 2


def test_rekey_new_epoch_must_exceed_old():
    with pytest.raises(ValueError):
        rekey_epoch(
            old_state=_make_state(epoch=5),
            old_epoch=5,
            new_ikm=os.urandom(32),
            new_epoch=5,
            key_id="k1",
            guardian_node_id="node1",
            sealed_by="g1",
            seal_counter=0,
            new_threshold=2,
            sentinels=["s1", "s2"],
        )


def test_rekey_round_trip_unseals():
    old_state = _make_state(epoch=1)
    new_ikm = os.urandom(32)
    new_sealed, new_wrapped, _, _ = rekey_epoch(
        old_state=old_state,
        old_epoch=1,
        new_ikm=new_ikm,
        new_epoch=2,
        key_id="k1",
        guardian_node_id="node1",
        sealed_by="guardian1",
        seal_counter=0,
        new_threshold=2,
        sentinels=["s1", "s2", "s3"],
    )
    # Derive the new live key and verify we can unseal
    new_live_key, _ = derive_keys(new_ikm, 2, "k1", "node1")
    recovered = unseal_live_state(new_sealed, new_live_key)
    assert recovered.epoch == 2
