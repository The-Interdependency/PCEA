# GPT/Claude generated; context, prompt Erin Spencer
from pcea.kdf import key_stream


def test_output_length():
    assert len(key_stream(42, 0, 10, 7)) == 10


def test_digits_in_range():
    for p in [2, 3, 7, 13, 241]:
        result = key_stream(999, 5, 50, p)
        assert all(0 <= d < p for d in result)


def test_deterministic():
    assert key_stream(7, 3, 20, 11) == key_stream(7, 3, 20, 11)


def test_different_last_val_gives_different_stream():
    a = key_stream(0, 0, 32, 7)
    b = key_stream(1, 0, 32, 7)
    assert a != b


def test_zero_last_val_is_not_zero_stream():
    result = key_stream(0, 0, 32, 7)
    assert any(d != 0 for d in result)


def test_different_position_gives_different_stream():
    a = key_stream(42, 0, 32, 7)
    b = key_stream(42, 1, 32, 7)
    assert a != b


def test_length_beyond_one_hash_block():
    # SHA-256 yields 32 bytes; request more than 32 digits
    result = key_stream(1, 0, 100, 5)
    assert len(result) == 100
    assert all(0 <= d < 5 for d in result)


def test_large_last_val():
    result = key_stream(10**15, 7, 20, 13)
    assert len(result) == 20
    assert all(0 <= d < 13 for d in result)


def test_negative_last_val():
    pos = key_stream(-5, 0, 10, 7)
    neg_excluded = key_stream(5, 0, 10, 7)
    assert pos != neg_excluded


def test_different_primes_same_inputs():
    a = key_stream(42, 0, 10, 3)
    b = key_stream(42, 0, 10, 7)
    # Same raw bytes, different modular reduction
    assert a != b
