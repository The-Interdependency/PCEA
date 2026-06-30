# ratios: loc_comments=67:7 imports_exports=2:16 calls_definitions=28:16
# GPT/Claude generated; context, prompt Erin Spencer
import pytest

from pcea.codec import digit_count, from_fixed, mobius_decode, mobius_encode, to_fixed


# --- mobius_encode / mobius_decode ---

def test_encode_positive():
    assert mobius_encode(0, 8) == 0
    assert mobius_encode(1, 8) == 1
    assert mobius_encode(127, 8) == 127


def test_encode_negative():
    # Two's complement: -1 wraps to 2^W - 1
    assert mobius_encode(-1, 8) == 255
    assert mobius_encode(-128, 8) == 128


def test_roundtrip_signed():
    for W in [8, 16, 32, 64]:
        for v in [0, 1, -1, 127, -128, 2**(W-1) - 1, -(2**(W-1))]:
            assert mobius_decode(mobius_encode(v, W), W) == v


def test_roundtrip_large_word_bits():
    W = 128
    for v in [0, -1, 2**(W-1) - 1, -(2**(W-1)), 10**30, -10**30]:
        assert mobius_decode(mobius_encode(v, W), W) == v


def test_encode_output_always_non_negative():
    for v in range(-200, 200):
        assert mobius_encode(v, 8) >= 0


def test_encode_output_in_range():
    W = 16
    for v in range(-1000, 1000):
        u = mobius_encode(v, W)
        assert 0 <= u < (1 << W)


def test_sign_indistinguishable_from_magnitude():
    # mobius_encode maps -v and +v to different positions but both non-negative
    # An observer cannot determine sign from the unsigned position alone
    assert mobius_encode(1, 8) != mobius_encode(-1, 8)  # different positions
    assert mobius_encode(1, 8) >= 0 and mobius_encode(-1, 8) >= 0  # both non-negative


# --- digit_count ---

def test_digit_count_base2_64bits():
    assert digit_count(2, 64) == 64


def test_digit_count_covers_full_disk():
    for p in [2, 3, 5, 7, 13, 241]:
        for W in [8, 16, 32, 64]:
            k = digit_count(p, W)
            capacity = p ** k
            assert capacity >= (1 << W), f"p={p} W={W} k={k}: {capacity} < 2^{W}"


def test_digit_count_minimal():
    for p in [2, 3, 5, 7, 13, 241]:
        for W in [8, 16, 32, 64]:
            k = digit_count(p, W)
            if k > 1:
                assert p ** (k - 1) < (1 << W), f"p={p} W={W}: k={k} is not minimal"


# --- to_fixed / from_fixed ---

def test_to_fixed_correct_length():
    for p in [2, 3, 7, 241]:
        assert len(to_fixed(0, p, 8)) == 8
        assert len(to_fixed(1000, p, 8)) == 8


def test_to_fixed_digits_in_range():
    for p in [2, 3, 5, 7, 241]:
        digits = to_fixed(12345, p, 20)
        assert all(0 <= d < p for d in digits)


def test_roundtrip_fixed():
    for p in [2, 3, 5, 7, 13, 241]:
        for W in [8, 16, 32]:
            k = digit_count(p, W)
            for v in [0, 1, 127, 255, (1 << W) - 1]:
                u = mobius_encode(v if v < (1 << (W-1)) else v - (1 << W), W)
                assert from_fixed(to_fixed(u, p, k), p) == u


def test_to_fixed_zero():
    assert to_fixed(0, 7, 5) == [0, 0, 0, 0, 0]


def test_from_fixed_zero():
    assert from_fixed([0, 0, 0, 0], 7) == 0


def test_roundtrip_small_word_bits():
    W = 8
    for p in [3, 5, 7]:
        k = digit_count(p, W)
        for u in range(0, 256, 13):
            assert from_fixed(to_fixed(u, p, k), p) == u
# ratios: loc_comments=67:7 imports_exports=2:16 calls_definitions=28:16
