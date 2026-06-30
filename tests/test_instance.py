# ratios: loc_comments=77:3 imports_exports=2:13 calls_definitions=50:16
# GPT/Claude generated; context, prompt Erin Spencer
import pytest

from pcea.instance import PCEAInstance

CIRCLES = 7
TENSORS = 7


def _seed(base: int = 1) -> list[list[int]]:
    return [[(base + c * TENSORS + t) for t in range(TENSORS)] for c in range(CIRCLES)]


def _state(n: int, base: int = 1) -> list[list[list[int]]]:
    return [_seed(base + i * 100) for i in range(n)]


def _pair(seed_state):
    return PCEAInstance(list(seed_state)), PCEAInstance(list(seed_state))


def test_roundtrip_single_seed():
    init = _state(1, 42)
    enc, dec = _pair(init)
    state = _state(1, 10)
    assert dec.decrypt(enc.encrypt(state)) == state


def test_stateful_two_rounds():
    init = _state(1, 1)
    enc, dec = _pair(init)
    s1 = _state(1, 10)
    s2 = _state(1, 20)
    e1 = enc.encrypt(s1)
    e2 = enc.encrypt(s2)
    assert dec.decrypt(e1) == s1
    assert dec.decrypt(e2) == s2


def test_stateful_many_rounds():
    init = _state(1, 7)
    enc, dec = _pair(init)
    states = [_state(1, i * 50) for i in range(1, 6)]
    encrypted = [enc.encrypt(s) for s in states]
    recovered = [dec.decrypt(e) for e in encrypted]
    assert recovered == states


def test_empty_seed_raises():
    with pytest.raises(ValueError):
        PCEAInstance([])


def test_flat_seed_raises():
    with pytest.raises(ValueError):
        PCEAInstance([[1, 2, 3]])


def test_malformed_seed_raises():
    # Wrong number of circles
    with pytest.raises(ValueError):
        PCEAInstance([[[1] * 7] * 3])

def test_malformed_circle_raises():
    # Wrong number of tensors per circle
    bad = [[[1] * 3 for _ in range(7)]]
    with pytest.raises(ValueError):
        PCEAInstance(bad)


def test_last_state_advances_after_encrypt():
    init = _state(1, 10)
    inst = PCEAInstance(init)
    new_state = _state(1, 99)
    inst.encrypt(new_state)
    assert inst.last_state == new_state


def test_last_state_advances_after_decrypt():
    init = _state(1, 10)
    enc, dec = _pair(init)
    s = _state(1, 55)
    e = enc.encrypt(s)
    dec.decrypt(e)
    assert dec.last_state == s


def test_last_state_returns_copy():
    init = _state(1, 1)
    inst = PCEAInstance(init)
    snap = inst.last_state
    snap[0][0][0] = 999
    assert inst.last_state[0][0][0] != 999


def test_mismatched_seeds_produce_wrong_decrypt():
    enc = PCEAInstance(_state(1, 1))
    dec = PCEAInstance(_state(1, 2))
    state = _state(1, 10)
    assert dec.decrypt(enc.encrypt(state)) != state


def test_empty_state_passthrough():
    inst = PCEAInstance(_state(1, 1))
    assert inst.encrypt([]) == []
    assert inst.decrypt([]) == []


def test_last_state_unchanged_after_empty_encrypt():
    init = _state(1, 7)
    inst = PCEAInstance(init)
    inst.encrypt([])
    assert inst.last_state == init
# ratios: loc_comments=77:3 imports_exports=2:13 calls_definitions=50:16
