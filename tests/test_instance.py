# GPT/Claude generated; context, prompt Erin Spencer
import pytest

from pcea.instance import PCEAInstance


def _pair(seed: list[int]) -> tuple[PCEAInstance, PCEAInstance]:
    return PCEAInstance(list(seed)), PCEAInstance(list(seed))


def test_roundtrip_single_state():
    enc, dec = _pair([42, 7, 13])
    state = [10, 20, 30, 40, 50]
    assert dec.decrypt(enc.encrypt(state)) == state


def test_stateful_two_rounds():
    enc, dec = _pair([1])
    s1, s2 = [10, 20], [30, 40]
    e1 = enc.encrypt(s1)
    e2 = enc.encrypt(s2)
    assert dec.decrypt(e1) == s1
    assert dec.decrypt(e2) == s2


def test_stateful_many_rounds():
    seed = [7, 11, 13]
    enc, dec = _pair(seed)
    states = [[i * 10, i * 20, i * 30] for i in range(1, 8)]
    encrypted = [enc.encrypt(s) for s in states]
    recovered = [dec.decrypt(e) for e in encrypted]
    assert recovered == states


def test_empty_seed_raises():
    with pytest.raises(ValueError):
        PCEAInstance([])


def test_last_state_advances_after_encrypt():
    inst = PCEAInstance([10, 20])
    inst.encrypt([3, 4])
    assert inst.last_state == [3, 4]


def test_last_state_advances_after_decrypt():
    enc, dec = _pair([10, 20])
    e = enc.encrypt([5, 6])
    dec.decrypt(e)
    assert dec.last_state == [5, 6]


def test_last_state_returns_copy():
    inst = PCEAInstance([1, 2, 3])
    snapshot = inst.last_state
    snapshot[0] = 999
    assert inst.last_state[0] == 1


def test_mismatched_seeds_produce_wrong_decrypt():
    enc = PCEAInstance([1, 2, 3])
    dec = PCEAInstance([4, 5, 6])
    state = [10, 20, 30]
    assert dec.decrypt(enc.encrypt(state)) != state


def test_empty_state_passthrough():
    inst = PCEAInstance([1])
    assert inst.encrypt([]) == []
    assert inst.decrypt([]) == []


def test_last_state_unchanged_after_empty_encrypt():
    inst = PCEAInstance([7, 8, 9])
    inst.encrypt([])
    assert inst.last_state == [7, 8, 9]
