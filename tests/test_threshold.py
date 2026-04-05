# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for Shamir's Secret Sharing (GF(256) inline implementation).
"""

import os
import pytest

from guardian_state.threshold import reconstruct_secret, split_secret


def test_2_of_3_round_trip():
    secret = os.urandom(32)
    shares = split_secret(secret, threshold=2, n=3)
    assert reconstruct_secret(shares[:2]) == secret


def test_3_of_5_round_trip():
    secret = os.urandom(32)
    shares = split_secret(secret, threshold=3, n=5)
    assert reconstruct_secret(shares[:3]) == secret


def test_all_shares_reconstruct():
    secret = os.urandom(16)
    shares = split_secret(secret, threshold=2, n=5)
    assert reconstruct_secret(shares) == secret


def test_any_subset_of_threshold_reconstructs():
    secret = os.urandom(32)
    shares = split_secret(secret, threshold=3, n=5)
    # Try all 5-choose-3 combinations
    from itertools import combinations
    for combo in combinations(shares, 3):
        assert reconstruct_secret(list(combo)) == secret


def test_below_threshold_gives_wrong_result():
    """k-1 shares should NOT reconstruct the secret."""
    secret = os.urandom(32)
    shares = split_secret(secret, threshold=3, n=5)
    recovered = reconstruct_secret(shares[:2])
    assert recovered != secret


def test_share_count():
    shares = split_secret(b"test", threshold=2, n=7)
    assert len(shares) == 7


def test_share_indices_are_1_based():
    shares = split_secret(b"test", threshold=2, n=3)
    indices = [idx for idx, _ in shares]
    assert sorted(indices) == [1, 2, 3]


def test_shares_are_different():
    secret = os.urandom(32)
    shares = split_secret(secret, threshold=2, n=3)
    blobs = [sb for _, sb in shares]
    # All share blobs should be distinct
    assert len(set(blobs)) == len(blobs)


def test_threshold_exceeds_n_raises():
    with pytest.raises(ValueError):
        split_secret(b"x", threshold=5, n=3)


def test_threshold_less_than_2_raises():
    with pytest.raises(ValueError):
        split_secret(b"x", threshold=1, n=3)


def test_empty_secret_raises():
    with pytest.raises(ValueError):
        split_secret(b"", threshold=2, n=3)


def test_long_secret():
    secret = os.urandom(256)
    shares = split_secret(secret, threshold=3, n=5)
    assert reconstruct_secret(shares[:3]) == secret
