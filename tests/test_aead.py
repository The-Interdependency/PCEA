# GPT/Claude generated; context, prompt Erin Spencer
"""
Tests for AES-256-GCM seal / unseal.
"""

import os
import pytest

from guardian_state.aead import AuthenticationError, seal, unseal


def _key():
    return os.urandom(32)

def _nonce():
    return os.urandom(12)


def test_round_trip():
    k, n = _key(), _nonce()
    pt = b"the quick brown fox"
    aad = b"some aad"
    ct = seal(k, n, pt, aad)
    assert unseal(k, n, ct, aad) == pt


def test_ciphertext_differs_from_plaintext():
    k, n = _key(), _nonce()
    pt = b"secret data"
    ct = seal(k, n, pt, b"")
    assert ct != pt


def test_tampered_ciphertext_raises():
    k, n = _key(), _nonce()
    ct = seal(k, n, b"message", b"aad")
    tampered = bytearray(ct)
    tampered[0] ^= 0xFF
    with pytest.raises(AuthenticationError):
        unseal(k, n, bytes(tampered), b"aad")


def test_wrong_key_raises():
    n = _nonce()
    ct = seal(_key(), n, b"message", b"aad")
    with pytest.raises(AuthenticationError):
        unseal(_key(), n, ct, b"aad")


def test_wrong_aad_raises():
    k, n = _key(), _nonce()
    ct = seal(k, n, b"message", b"correct aad")
    with pytest.raises(AuthenticationError):
        unseal(k, n, ct, b"wrong aad")


def test_wrong_nonce_raises():
    k = _key()
    ct = seal(k, _nonce(), b"message", b"aad")
    with pytest.raises(AuthenticationError):
        unseal(k, _nonce(), ct, b"aad")


def test_empty_plaintext_round_trip():
    k, n = _key(), _nonce()
    ct = seal(k, n, b"", b"aad")
    assert unseal(k, n, ct, b"aad") == b""


def test_invalid_key_length_raises():
    with pytest.raises(ValueError):
        seal(os.urandom(16), _nonce(), b"msg", b"")


def test_invalid_nonce_length_raises():
    with pytest.raises(ValueError):
        seal(_key(), os.urandom(8), b"msg", b"")
