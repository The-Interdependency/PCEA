# ratios: loc_comments=38:2 imports_exports=1:10 calls_definitions=20:10
# GPT/Claude generated; context, prompt Erin Spencer
from pcea.kdf import key_stream


def test_output_length():
    assert len(key_stream([42, 1, 2], 0, 0, 0, 10, 7)) == 10


def test_digits_in_range():
    for p in [2, 3, 7, 13, 241]:
        result = key_stream([999, 0, 1], 5, 3, 2, 50, p)
        assert all(0 <= d < p for d in result)


def test_deterministic():
    a = key_stream([7, 3, 11], 0, 1, 2, 20, 11)
    b = key_stream([7, 3, 11], 0, 1, 2, 20, 11)
    assert a == b


def test_different_contributors_give_different_stream():
    a = key_stream([0, 0, 0], 0, 0, 0, 32, 7)
    b = key_stream([1, 0, 0], 0, 0, 0, 32, 7)
    assert a != b


def test_zero_contributors_not_zero_stream():
    result = key_stream([0, 0, 0], 0, 0, 0, 32, 7)
    assert any(d != 0 for d in result)


def test_different_seed_idx_gives_different_stream():
    a = key_stream([42, 1, 2], 0, 3, 4, 32, 7)
    b = key_stream([42, 1, 2], 1, 3, 4, 32, 7)
    assert a != b


def test_different_circle_idx_gives_different_stream():
    a = key_stream([42, 1, 2], 0, 0, 4, 32, 7)
    b = key_stream([42, 1, 2], 0, 1, 4, 32, 7)
    assert a != b


def test_different_tensor_idx_gives_different_stream():
    a = key_stream([42, 1, 2], 0, 3, 0, 32, 7)
    b = key_stream([42, 1, 2], 0, 3, 1, 32, 7)
    assert a != b


def test_neighbor_contribution_matters():
    # Same own value, different neighbors
    a = key_stream([10, 0, 0], 0, 0, 0, 32, 7)
    b = key_stream([10, 5, 0], 0, 0, 0, 32, 7)
    assert a != b


def test_length_beyond_one_hash_block():
    result = key_stream([1, 2, 3], 0, 0, 0, 100, 5)
    assert len(result) == 100
    assert all(0 <= d < 5 for d in result)
# ratios: loc_comments=38:2 imports_exports=1:10 calls_definitions=20:10
