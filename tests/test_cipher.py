# GPT/Claude generated; context, prompt Erin Spencer
from pcea.cipher import decrypt_state, encrypt_state


def test_roundtrip_simple():
    state = [1, 2, 3, 4, 5]
    last = [10, 20, 30, 40, 50]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_roundtrip_all_zeros():
    state = [0, 0, 0]
    last = [1, 2, 3]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_encrypt_changes_nonzero_values():
    state = [7, 14, 21]
    last = [3, 3, 3]
    encrypted = encrypt_state(state, last)
    assert encrypted != state


def test_zero_elements_stay_zero():
    state = [0, 5, 0]
    last = [99]
    encrypted = encrypt_state(state, last)
    assert encrypted[0] == 0
    assert encrypted[2] == 0


def test_roundtrip_negative_values():
    state = [-1, -100, -999]
    last = [7, 13, 2]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_roundtrip_mixed_signs():
    state = [-5, 0, 5, -100, 100]
    last = [42]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_last_state_shorter_than_state():
    state = list(range(1, 20))
    last = [1, 2, 3]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_last_state_longer_than_state():
    state = [1, 2]
    last = list(range(1, 100))
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_different_last_states_give_different_output():
    state = [42, 43, 44]
    enc1 = encrypt_state(state, [1, 2, 3])
    enc2 = encrypt_state(state, [4, 5, 6])
    assert enc1 != enc2


def test_roundtrip_large_values():
    state = [10**9, 10**12, 10**15]
    last = [999, 888, 777]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_roundtrip_single_element():
    assert decrypt_state(encrypt_state([42], [7]), [7]) == [42]


def test_empty_state():
    assert encrypt_state([], [1]) == []
    assert decrypt_state([], [1]) == []


def test_zero_key_is_identity():
    # key_digits of 0 are all zeros → shift is zero → encrypted == original
    state = [1, 2, 3, 4, 5]
    last = [0, 0, 0, 0, 0]
    assert encrypt_state(state, last) == state


def test_roundtrip_long_state():
    state = list(range(1, 201))
    last = [7, 11, 13, 17, 19]
    assert decrypt_state(encrypt_state(state, last), last) == state


def test_encrypt_same_value_different_positions_gives_different_output():
    # Same value and key at different positions uses different primes → different result
    state = [100, 100, 100]
    last = [50, 50, 50]
    encrypted = encrypt_state(state, last)
    # Not all encrypted values should be equal (different primes at positions 0,1,2)
    assert len(set(encrypted)) > 1
