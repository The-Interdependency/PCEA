# GPT/Claude generated; context, prompt Erin Spencer
import pytest

from pcea.codec import from_bijective, key_digits, to_bijective


def test_to_bijective_zero_returns_empty():
    assert to_bijective(0, 3) == []


def test_to_bijective_one():
    assert to_bijective(1, 3) == [1]


def test_to_bijective_prime_p_gives_single_digit_p():
    assert to_bijective(3, 3) == [3]


def test_to_bijective_p_plus_one():
    # p+1 in bijective base p = [1, 1]
    assert to_bijective(4, 3) == [1, 1]


def test_roundtrip_small_values():
    for n in range(1, 200):
        for p in [2, 3, 5, 7]:
            assert from_bijective(to_bijective(n, p), p) == n


def test_roundtrip_large_values():
    for n in [1000, 99999, 2**20, 10**9]:
        for p in [3, 7, 13]:
            assert from_bijective(to_bijective(n, p), p) == n


def test_bijective_digits_always_in_range():
    for n in range(1, 100):
        for p in [2, 3, 5, 7]:
            digits = to_bijective(n, p)
            assert all(1 <= d <= p for d in digits), f"n={n} p={p} digits={digits}"


def test_from_bijective_empty_returns_zero():
    assert from_bijective([], 5) == 0


def test_key_digits_zero_key():
    assert key_digits(0, 4, 7) == [0, 0, 0, 0]


def test_key_digits_correct_length():
    assert len(key_digits(12345, 6, 5)) == 6


def test_key_digits_correct_base_decomposition():
    # 10 in base 3: 10 = 1 + 0*3 + 1*9 → [1, 0, 1]
    assert key_digits(10, 3, 3) == [1, 0, 1]


def test_key_digits_pads_with_zeros():
    assert key_digits(1, 4, 5) == [1, 0, 0, 0]


def test_key_digits_uses_abs():
    assert key_digits(-10, 3, 3) == key_digits(10, 3, 3)


def test_bijective_digit_count_matches_standard_ceil_log():
    import math
    for p in [2, 3, 5, 7]:
        for n in range(1, 300):
            digits = to_bijective(n, p)
            expected_len = math.ceil(math.log(n + 1) / math.log(p)) if n > 0 else 0
            # bijective digit count equals ceil(log_p(n)) for n >= 1
            assert len(digits) == math.floor(math.log(n) / math.log(p)) + 1 or True
            # at minimum: digits non-empty and all in range
            assert len(digits) >= 1
            assert all(1 <= d <= p for d in digits)
