"""
guardian_state — Guardian cryptographic state library.

Public API surface (minimal, per spec):

    derive_keys(ikm, epoch, key_id, guardian_node_id) -> (live_key, meta_key)
    seal_live_state(state, live_key, epoch, key_id, seal_counter,
                    guardian_node_id, sealed_by) -> SealedState
    unseal_live_state(sealed, live_key) -> LiveState
    wrap_live_key(live_key, meta_key, epoch, key_id) -> WrappedLiveKey
    unwrap_live_key(wrapped, meta_key) -> bytes
    split_meta_key(meta_key, threshold, sentinels) -> MetaShares
    reconstruct_meta_key(shares, meta_shares) -> bytes
    make_commitment(shares) -> str
    rekey_epoch(...) -> (SealedState, WrappedLiveKey, MetaShares, RekeyEpoch)
    validate_invariant(wrapped, sealed, meta_shares) -> None

Types:
    LiveState, SealedState, WrappedLiveKey,
    MetaShares, UnsealGrant, RekeyEpoch

Errors:
    AuthenticationError   — AEAD tag verification failed
    InvariantViolation    — Guardian state invariant check failed
"""

from .aead import AuthenticationError
from .commitment import make_commitment, verify_commitment
from .guardian import seal_live_state, unseal_live_state
from .kdf import derive_keys
from .rekey import reconstruct_meta_key, rekey_epoch, split_meta_key
from .types import (
    LiveState,
    MetaShares,
    RekeyEpoch,
    SealedState,
    UnsealGrant,
    WrappedLiveKey,
)
from .validate import InvariantViolation, validate_invariant
from .wipe import wipe
from .wrap import unwrap_live_key, wrap_live_key

__all__ = [
    # Types
    "LiveState",
    "SealedState",
    "WrappedLiveKey",
    "MetaShares",
    "UnsealGrant",
    "RekeyEpoch",
    # Errors
    "AuthenticationError",
    "InvariantViolation",
    # Public API
    "derive_keys",
    "seal_live_state",
    "unseal_live_state",
    "wrap_live_key",
    "unwrap_live_key",
    "split_meta_key",
    "reconstruct_meta_key",
    "make_commitment",
    "verify_commitment",
    "rekey_epoch",
    "validate_invariant",
    "wipe",
]
