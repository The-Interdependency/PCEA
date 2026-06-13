# PCEA — Prime Circular Encryption Algorithm

Pure-Python, zero-dependency library implementing a prime-circular Möbius disk cipher for neural architecture state.

## Purpose

PCEA encrypts pre-quantized integer neural architecture state using the relationship between the current state and the previous (`last_state`) state. It is framework-agnostic: callers convert weights, activations, or other architecture state into integer seeds before calling the library.

Runtime state is structured as a list of seeds. Each seed is a `7×7` integer array: 7 circles × 7 tensors.

## Algorithm

For each integer value at address `(seed_idx, circle_idx, tensor_idx)`:

1. Select prime base `p = prime_at(circle_idx * 7 + tensor_idx)` from the fixed 53-prime circle.
2. Map the signed integer onto a fixed-width unsigned Möbius disk position:
   `u = value mod 2^word_bits`.
3. Encode `u` as exactly `k = digit_count(p, word_bits)` standard base-`p` digits in `[0, p - 1]`.
4. Derive `k` key digits in `[0, p - 1]` with SHA-256 from:
   - the previous value at the same `(circle_idx, tensor_idx)`,
   - the two heptagram neighbor previous values at `(circle_idx - 3) mod 7` and `(circle_idx + 3) mod 7`,
   - `seed_idx`, `circle_idx`, `tensor_idx`, and a counter.
5. Shift each digit additively modulo `p`.
6. Reconstruct the encrypted unsigned integer from the shifted digits.

Decryption repeats the same prime selection, fixed-width digit encoding, and key-stream derivation, then subtracts the key digits modulo `p` and decodes the unsigned Möbius position back to a signed integer.

```
encrypt: e_j = (v_j + k_j) mod p
decrypt: v_j = (e_j - k_j) mod p
```

Fixed-width base-`p` encoding prevents output digit count from revealing the original value's magnitude class. The Möbius disk mapping lets positive and negative values share one fixed-width unsigned space; `word_bits` must be large enough for the caller's value range and must match between sender and receiver.

## Usage

```python
from pcea import PCEAInstance, decrypt_state, encrypt_state

seed0 = [[0 for _ in range(7)] for _ in range(7)]
last_state = [seed0]

state1 = [[circle * 10 + tensor for tensor in range(7)] for circle in range(7)]
state2 = [[100 + circle * 10 + tensor for tensor in range(7)] for circle in range(7)]

# Stateless: caller manages last_state.
encrypted = encrypt_state([state1], last_state)
recovered = decrypt_state(encrypted, last_state)
assert recovered == [state1]

# Stateful: each instance advances last_state automatically.
enc = PCEAInstance(seed=last_state)
dec = PCEAInstance(seed=last_state)

e1 = enc.encrypt([state1])
e2 = enc.encrypt([state2])

assert dec.decrypt(e1) == [state1]
assert dec.decrypt(e2) == [state2]
```

## Testing and PCEA-UCNS research harnesses

The shipped `pcea/` package is the symmetric, state-synchronized transform described above. Its correctness and contract tests live in `tests/test_cipher.py`, `tests/test_codec.py`, `tests/test_kdf.py`, `tests/test_instance.py`, and `tests/test_contract_spec.py`.

The `pcea-ucns/` directory is different: it is an attack-and-feasibility workspace for possible UCNS-native key-establishment or gonal/state-communication layers around PCEA. Those files do **not** upgrade the symmetric PCEA runtime into a proven public-key encryption system. They record candidate constructions, measured breaks, and open gates for any future PCEA-UCNS layer. See `pcea-ucns/README.md` for the concrete proving-ground workflow.

Important testing boundaries:

- PCEA runtime tests run without `ucns` and cover round trips, key-state mismatch behavior, fixed-width codec behavior, KDF determinism/sensitivity, and state advancement.
- PCEA-UCNS tests are attack/regression harnesses. They are skipped when `ucns` is not installed, keeping the symmetric runtime testable without UCNS.
- Passing a PCEA-UCNS harness means only that the measured behavior has not drifted; it is not a proof of cryptographic security.
- Several PCEA-UCNS harnesses intentionally pin breaks or negative findings, including oracle-domain factorization, positional/factor-count attacks, prefix-read reconstruction, and Minkowski set-basis recovery.
- The gonal architecture tests include a measured PCEA-advanced candidate that resists simple frequency/known-plaintext probes in the harness, but the module still marks further attacks and the 53→32 bridge as gates before any shipped `gonal_cipher.py`.

Useful commands:

```bash
python -m pytest -q
python -m pytest -q tests/test_cipher.py tests/test_codec.py tests/test_kdf.py tests/test_instance.py tests/test_contract_spec.py
python -m pytest -q tests/test_attack_harness.py tests/test_positional_attack.py tests/test_quotient_attack.py tests/test_prefix_read_break.py tests/test_projection_action_candidate.py tests/test_pruning_scaling.py tests/test_attack1_minkowski_break.py tests/test_three_factor_attack.py tests/test_factor_count_sweep.py tests/test_gonal_architecture.py
```

## PCEA ↔ UCNS Boundary (v0 contract decision)

PCEA is specified to decrypt/invert **via keys**, not via UCNS inverse operations.
That means:

- PCEA consumes only forward arithmetic substrate behavior.
- Security rests on key management (`last_state` synchronization and protection), not on any assumption that arithmetic inversion is hard.
- A mismatch in key state must fail recovery by design.

This keeps PCEA cryptographic claims decoupled from UCNS analytic-frontier work.

Enforcement:

- `tests/test_contract_spec.py` is a release gate for this boundary.
- `.github/workflows/contract-boundary.yml` runs this gate in CI for pull requests and pushes to `main`.

## Install

```
pip install .          # runtime — no dependencies
pip install ".[dev]"   # adds pytest
```

## License

**MIT** licensed. See `LICENSE`. (Relicensed from AGPL-3.0 to MIT for
frictionless adoption.)

## Author

Erin Patrick Spencer — interdependentway.org
