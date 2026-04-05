"""
Tests for HKDF key derivation and nonce derivation.
"""

import os

from guardian_state.kdf import derive_keys, derive_nonce


def test_derive_keys_deterministic():
    ikm = os.urandom(32)
    live1, meta1 = derive_keys(ikm, epoch=1, key_id="k1", guardian_node_id="node1")
    live2, meta2 = derive_keys(ikm, epoch=1, key_id="k1", guardian_node_id="node1")
    assert live1 == live2
    assert meta1 == meta2


def test_derive_keys_length():
    ikm = os.urandom(32)
    live, meta = derive_keys(ikm, epoch=1, key_id="k1", guardian_node_id="node1")
    assert len(live) == 32
    assert len(meta) == 32


def test_derive_keys_live_and_meta_are_different():
    ikm = os.urandom(32)
    live, meta = derive_keys(ikm, epoch=1, key_id="k1", guardian_node_id="node1")
    assert live != meta


def test_derive_keys_epoch_changes_output():
    ikm = os.urandom(32)
    live1, meta1 = derive_keys(ikm, epoch=1, key_id="k1", guardian_node_id="node1")
    live2, meta2 = derive_keys(ikm, epoch=2, key_id="k1", guardian_node_id="node1")
    assert live1 != live2
    assert meta1 != meta2


def test_derive_keys_key_id_changes_output():
    ikm = os.urandom(32)
    live1, _ = derive_keys(ikm, epoch=1, key_id="k1", guardian_node_id="node1")
    live2, _ = derive_keys(ikm, epoch=1, key_id="k2", guardian_node_id="node1")
    assert live1 != live2


def test_derive_nonce_length():
    ikm = os.urandom(32)
    nonce = derive_nonce(epoch=1, key_id="k1", seal_counter=0, guardian_node_id="node1", ikm=ikm)
    assert len(nonce) == 12


def test_derive_nonce_unique_per_seal_counter():
    ikm = os.urandom(32)
    nonces = {
        derive_nonce(epoch=1, key_id="k1", seal_counter=i, guardian_node_id="node1", ikm=ikm)
        for i in range(100)
    }
    assert len(nonces) == 100, "Each seal_counter value must produce a unique nonce"


def test_derive_nonce_unique_per_epoch():
    ikm = os.urandom(32)
    n1 = derive_nonce(epoch=1, key_id="k1", seal_counter=0, guardian_node_id="node1", ikm=ikm)
    n2 = derive_nonce(epoch=2, key_id="k1", seal_counter=0, guardian_node_id="node1", ikm=ikm)
    assert n1 != n2


def test_derive_nonce_deterministic():
    ikm = os.urandom(32)
    n1 = derive_nonce(epoch=5, key_id="key", seal_counter=3, guardian_node_id="gn1", ikm=ikm)
    n2 = derive_nonce(epoch=5, key_id="key", seal_counter=3, guardian_node_id="gn1", ikm=ikm)
    assert n1 == n2
