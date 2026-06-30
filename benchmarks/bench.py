# ratios: loc_comments=145:41 imports_exports=11:8 calls_definitions=81:11
"""
PCEA performance benchmark.

Measures throughput (elements/s, seeds/s) and latency (µs/call) for every
layer of the PCEA stack:

  1. Codec primitives  — mobius_encode / mobius_decode / to_fixed / from_fixed
  2. Key derivation    — key_stream
  3. Single element    — _encrypt_element / _decrypt_element
  4. Single seed       — encrypt_seed / decrypt_seed  (7×7 = 49 elements)
  5. Multi-seed state  — encrypt_state / decrypt_state at 1, 8, 64, 512 seeds
  6. PCEAInstance      — stateful .encrypt / .decrypt round-trip

Run with:
    python benchmarks/bench.py
"""
from __future__ import annotations

import statistics
import time

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPS = 5  # independent timing repetitions per benchmark


def _make_seed(fill: int = 1234) -> list[list[int]]:
    return [[fill] * 7 for _ in range(7)]


def _make_state(n: int, fill: int = 1234) -> list[list[list[int]]]:
    return [_make_seed(fill + i) for i in range(n)]


def timeit_reps(fn, n_calls: int, reps: int = REPS):
    """
    Run fn() n_calls times, repeat `reps` times independently.
    Returns (best_seconds_per_call, median_seconds_per_call).
    """
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for _ in range(n_calls):
            fn()
        times.append((time.perf_counter() - t0) / n_calls)
    return min(times), statistics.median(times)


def _row(label: str, best_s: float, med_s: float, throughput_label: str, throughput: float) -> str:
    return (
        f"  {label:<42}"
        f"  best {best_s * 1e6:>9.2f} µs"
        f"  median {med_s * 1e6:>9.2f} µs"
        f"  {throughput_label} {throughput:>12,.0f} /s"
    )


def header(title: str) -> None:
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


# ---------------------------------------------------------------------------
# 1. Codec primitives
# ---------------------------------------------------------------------------

def bench_codec() -> None:
    from pcea import mobius_encode, mobius_decode, to_fixed, from_fixed, digit_count

    WORD_BITS = 64
    P = 53  # a prime from the circle
    K = digit_count(P, WORD_BITS)
    V = 999_999_999
    U = mobius_encode(V, WORD_BITS)
    DIGITS = to_fixed(U, P, K)

    N = 100_000
    header("1. Codec primitives")

    for label, fn in [
        ("mobius_encode", lambda: mobius_encode(V, WORD_BITS)),
        ("mobius_decode", lambda: mobius_decode(U, WORD_BITS)),
        (f"to_fixed (p={P}, k={K})", lambda: to_fixed(U, P, K)),
        (f"from_fixed (p={P}, k={K})", lambda: from_fixed(DIGITS, P)),
    ]:
        best, med = timeit_reps(fn, N)
        print(_row(label, best, med, "ops", 1 / best))


# ---------------------------------------------------------------------------
# 2. Key derivation
# ---------------------------------------------------------------------------

def bench_kdf() -> None:
    from pcea import key_stream, digit_count
    from pcea.primes import prime_at

    CONTRIBUTORS = [42, 17, 99]

    N = 5_000
    header("2. Key derivation (key_stream)")

    for p_idx, label in [(0, "p=2 (smallest)"), (25, "p=101 (mid)"), (52, "p=241 (largest)")]:
        p = prime_at(p_idx)
        k = digit_count(p, 64)
        fn = lambda p=p, k=k: key_stream(CONTRIBUTORS, 0, 0, 0, k, p)
        best, med = timeit_reps(fn, N)
        print(_row(f"key_stream {label} → {k} digits", best, med, "calls", 1 / best))


# ---------------------------------------------------------------------------
# 3. Single element
# ---------------------------------------------------------------------------

def bench_element() -> None:
    from pcea.cipher import _encrypt_element, _decrypt_element, DEFAULT_WORD_BITS

    last_seed = _make_seed(500)
    VALUE = 1_000_000
    WORD_BITS = DEFAULT_WORD_BITS

    encrypted = _encrypt_element(VALUE, 0, 3, 3, last_seed, WORD_BITS)

    N = 2_000
    header("3. Single element  (circle=3, tensor=3)")

    best, med = timeit_reps(
        lambda: _encrypt_element(VALUE, 0, 3, 3, last_seed, WORD_BITS), N
    )
    print(_row("_encrypt_element", best, med, "elements", 1 / best))

    best, med = timeit_reps(
        lambda: _decrypt_element(encrypted, 0, 3, 3, last_seed, WORD_BITS), N
    )
    print(_row("_decrypt_element", best, med, "elements", 1 / best))


# ---------------------------------------------------------------------------
# 4. Single seed  (7×7 = 49 elements)
# ---------------------------------------------------------------------------

def bench_seed() -> None:
    from pcea import encrypt_seed, decrypt_seed, DEFAULT_WORD_BITS

    seed = _make_seed(1000)
    last_seed = _make_seed(500)
    WORD_BITS = DEFAULT_WORD_BITS
    ELEMENTS = 49

    encrypted = encrypt_seed(seed, last_seed, 0, WORD_BITS)

    N = 200
    header("4. Single seed  (7×7 = 49 elements)")

    best, med = timeit_reps(
        lambda: encrypt_seed(seed, last_seed, 0, WORD_BITS), N
    )
    print(_row("encrypt_seed", best, med, "seeds", 1 / best))
    print(f"    → {1 / best * ELEMENTS:>12,.0f} elements/s  (best)")

    best, med = timeit_reps(
        lambda: decrypt_seed(encrypted, last_seed, 0, WORD_BITS), N
    )
    print(_row("decrypt_seed", best, med, "seeds", 1 / best))
    print(f"    → {1 / best * ELEMENTS:>12,.0f} elements/s  (best)")


# ---------------------------------------------------------------------------
# 5. Multi-seed state
# ---------------------------------------------------------------------------

def bench_state() -> None:
    from pcea import encrypt_state, decrypt_state, DEFAULT_WORD_BITS

    WORD_BITS = DEFAULT_WORD_BITS

    header("5. encrypt_state / decrypt_state — varying seed count")

    for n_seeds in [1, 8, 64, 512]:
        state = _make_state(n_seeds, 1000)
        last_state = _make_state(n_seeds, 500)
        elements = n_seeds * 49

        encrypted = encrypt_state(state, last_state, WORD_BITS)

        N = max(1, 400 // n_seeds)

        best_e, _ = timeit_reps(
            lambda: encrypt_state(state, last_state, WORD_BITS), N
        )
        best_d, _ = timeit_reps(
            lambda: decrypt_state(encrypted, last_state, WORD_BITS), N
        )

        print(
            f"  {n_seeds:>4} seeds ({elements:>5} elements)"
            f"  enc {best_e * 1e3:>7.2f} ms  {elements / best_e:>10,.0f} el/s"
            f"  |  dec {best_d * 1e3:>7.2f} ms  {elements / best_d:>10,.0f} el/s"
        )


# ---------------------------------------------------------------------------
# 6. PCEAInstance  (stateful round-trip)
# ---------------------------------------------------------------------------

def bench_instance() -> None:
    from pcea import PCEAInstance

    header("6. PCEAInstance  (stateful encrypt + decrypt round-trip)")

    for n_seeds in [1, 8, 64]:
        init_state = _make_state(n_seeds, 0)
        payload = _make_state(n_seeds, 9999)
        elements = n_seeds * 49

        enc = PCEAInstance(init_state)
        dec = PCEAInstance(init_state)

        N = max(1, 200 // n_seeds)

        best_e, _ = timeit_reps(lambda: enc.encrypt(payload), N)
        enc2 = PCEAInstance(init_state)
        encrypted_once = enc2.encrypt(payload)
        best_d, _ = timeit_reps(lambda: dec.decrypt(encrypted_once), N)

        print(
            f"  {n_seeds:>4} seeds ({elements:>5} elements)"
            f"  enc {best_e * 1e3:>7.2f} ms  {elements / best_e:>10,.0f} el/s"
            f"  |  dec {best_d * 1e3:>7.2f} ms  {elements / best_d:>10,.0f} el/s"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print(f"Python {sys.version}")
    print(f"PCEA benchmark  ({REPS} repetitions each)")

    bench_codec()
    bench_kdf()
    bench_element()
    bench_seed()
    bench_state()
    bench_instance()

    print(f"\n{'─' * 80}")
    print("  Done.")
    print(f"{'─' * 80}\n")
# ratios: loc_comments=145:41 imports_exports=11:8 calls_definitions=81:11
