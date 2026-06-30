# ratios: loc_comments=27:1 imports_exports=1:9 calls_definitions=8:10
# GPT/Claude generated; context, prompt Erin Spencer
from pcea.primes import CIRCLE_SIZE, PRIME_CIRCLE, prime_at


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def test_circle_size():
    assert CIRCLE_SIZE == 53


def test_prime_circle_length():
    assert len(PRIME_CIRCLE) == 53


def test_prime_circle_all_prime():
    assert all(_is_prime(p) for p in PRIME_CIRCLE)


def test_prime_circle_starts_with_2():
    assert PRIME_CIRCLE[0] == 2


def test_prime_circle_ends_with_241():
    assert PRIME_CIRCLE[-1] == 241


def test_prime_circle_strictly_increasing():
    assert all(PRIME_CIRCLE[i] < PRIME_CIRCLE[i + 1] for i in range(len(PRIME_CIRCLE) - 1))


def test_prime_at_wraps():
    assert prime_at(0) == prime_at(CIRCLE_SIZE)
    assert prime_at(1) == prime_at(CIRCLE_SIZE + 1)


def test_prime_at_large_index():
    assert prime_at(53 * 100 + 7) == prime_at(7)


def test_prime_at_first():
    assert prime_at(0) == 2
# ratios: loc_comments=27:1 imports_exports=1:9 calls_definitions=8:10
