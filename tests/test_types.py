"""
Tests for frozen type invariants.

Critical: WrappedLiveKey must have no 'live_key' field.
Critical: UnsealGrant must have no 'reconstructed_meta_key' field.
"""

import dataclasses

from guardian_state.types import (
    LiveState,
    MetaShares,
    RekeyEpoch,
    SealedState,
    UnsealGrant,
    WrappedLiveKey,
)


def test_wrapped_live_key_has_no_live_key_field():
    fields = {f.name for f in dataclasses.fields(WrappedLiveKey)}
    assert "live_key" not in fields, (
        "WrappedLiveKey must not have a 'live_key' field — "
        "it defeats the point of wrapping (frozen invariant)"
    )


def test_wrapped_live_key_has_wrapped_live_key_field():
    fields = {f.name for f in dataclasses.fields(WrappedLiveKey)}
    assert "wrapped_live_key" in fields


def test_unseal_grant_has_no_reconstructed_meta_key_field():
    fields = {f.name for f in dataclasses.fields(UnsealGrant)}
    assert "reconstructed_meta_key" not in fields, (
        "UnsealGrant must not have a 'reconstructed_meta_key' field — "
        "grants are authorization artifacts, not key containers (frozen invariant)"
    )


def test_unseal_grant_purpose_values():
    grant = UnsealGrant(
        epoch=1,
        key_id="k1",
        grant_signature="sig",
        granted_to="node1",
        validity_window=300.0,
        purpose="unseal",
    )
    assert grant.purpose == "unseal"


def test_sealed_state_fields():
    fields = {f.name for f in dataclasses.fields(SealedState)}
    for required in ("epoch", "key_id", "ciphertext", "nonce", "aad", "sealed_by", "sealed_at"):
        assert required in fields


def test_meta_shares_fields():
    fields = {f.name for f in dataclasses.fields(MetaShares)}
    for required in ("epoch", "total_shares", "threshold", "shares", "commitment"):
        assert required in fields


def test_rekey_epoch_fields():
    fields = {f.name for f in dataclasses.fields(RekeyEpoch)}
    for required in (
        "from_epoch", "to_epoch", "new_session_secret_commitment",
        "meta_shares_updated", "renorm_confirmed", "spectral_snapshot",
    ):
        assert required in fields


def test_live_state_construction():
    state = LiveState(
        epoch=1,
        spiral={"phase": 0.0, "magnitude": 1.0, "base": 2.0},
        cores={"Phi": None, "Psi": None, "Omega": None},
        density_matrix=None,
        coherence=0.9,
        transport=None,
        last_renorm=0.0,
    )
    assert state.epoch == 1
    assert state.coherence == 0.9
