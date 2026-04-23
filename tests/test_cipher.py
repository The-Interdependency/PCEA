# GPT/Claude generated; context, prompt Erin Spencer
import pytest

from pcea.cipher import decrypt_seed, decrypt_state, encrypt_seed, encrypt_state

CIRCLES = 7
TENSORS = 7


def _seed(base: int = 1) -> list[list[int]]:
    return [[(base + c * TENSORS + t) for t in range(TENSORS)] for c in range(CIRCLES)]


def _zero_seed() -> list[list[int]]:
    return [[0] * TENSORS for _ in range(CIRCLES)]


def test_roundtrip_simple():
    seed = _seed(10)
    last = _seed(1)
    assert decrypt_seed(encrypt_seed(seed, last), last) == seed


def test_roundtrip_zero_seed():
    seed = _zero_seed()
    last = _seed(5)
    assert decrypt_seed(encrypt_seed(seed, last), last) == seed


def test_encrypt_changes_nonzero_values():
    seed = _seed(7)
    last = _seed(3)
    assert encrypt_seed(seed, last) != seed


def test_zero_elements_are_encrypted():
    # Zero values are encrypted like any other value on the Möbius disk — they
    # do not stay zero (that would leak which positions are zero).
    seed = _zero_seed()
    last = _seed(99)
    encrypted = encrypt_seed(seed, last)
    assert encrypted != seed
    assert decrypt_seed(encrypted, last) == seed


def test_roundtrip_negative_values():
    seed = [[-(c * TENSORS + t + 1) for t in range(TENSORS)] for c in range(CIRCLES)]
    last = _seed(7)
    assert decrypt_seed(encrypt_seed(seed, last), last) == seed


def test_roundtrip_mixed_signs():
    seed = [[(1 if (c + t) % 2 == 0 else -1) * (c * TENSORS + t + 1) for t in range(TENSORS)] for c in range(CIRCLES)]
    last = _seed(42)
    assert decrypt_seed(encrypt_seed(seed, last), last) == seed


def test_different_last_seeds_give_different_output():
    seed = _seed(50)
    enc1 = encrypt_seed(seed, _seed(1))
    enc2 = encrypt_seed(seed, _seed(2))
    assert enc1 != enc2


def test_seed_idx_affects_output():
    seed = _seed(10)
    last = _seed(5)
    enc0 = encrypt_seed(seed, last, seed_idx=0)
    enc1 = encrypt_seed(seed, last, seed_idx=1)
    assert enc0 != enc1


def test_interlocking_circles_affect_output():
    seed = _seed(10)
    # Modify a value in circle 0 of last_seed — should affect circle 3 and 4
    # (the heptagram neighbors ±3 mod 7)
    last_a = _seed(5)
    last_b = _seed(5)
    last_b[0][0] = 999  # change circle 0, tensor 0
    # circle 3 and 4 use circle 0 as a neighbor → their encrypted output changes
    enc_a = encrypt_seed(seed, last_a)
    enc_b = encrypt_seed(seed, last_b)
    assert enc_a[3] != enc_b[3] or enc_a[4] != enc_b[4]


def test_roundtrip_large_values():
    seed = [[10**9 * (c + 1) + t for t in range(TENSORS)] for c in range(CIRCLES)]
    last = _seed(999)
    assert decrypt_seed(encrypt_seed(seed, last), last) == seed


def test_zero_last_seed_still_encrypts():
    seed = _seed(5)
    last = _zero_seed()
    encrypted = encrypt_seed(seed, last)
    assert encrypted != seed
    assert decrypt_seed(encrypted, last) == seed


def test_encrypt_state_roundtrip():
    state = [_seed(i * 10) for i in range(1, 4)]
    last = [_seed(i) for i in range(1, 4)]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_encrypt_seed_wrong_shape_raises():
    import pytest
    bad = [[1, 2, 3]]
    good = _seed()
    with pytest.raises(ValueError):
        encrypt_seed(bad, good)
    with pytest.raises(ValueError):
        encrypt_seed(good, bad)


def test_encrypt_state_length_mismatch_raises():
    import pytest
    state = [_seed(10), _seed(20)]
    last = [_seed(1)]
    with pytest.raises(ValueError):
        encrypt_state(state, last)
    with pytest.raises(ValueError):
        decrypt_state(state, last)


def test_encrypt_state_seed_idx_varies():
    state = [_seed(10), _seed(10)]
    last = [_seed(5), _seed(5)]
    encrypted = encrypt_state(state, last)
    # Same seed values at different positions should encrypt differently
    assert encrypted[0] != encrypted[1]
