# PCEA — Prime Circular Encryption Algorithm

Pure-Python, zero-dependency library implementing the prime-circular base number encryption algorithm for neural architecture state.

## Purpose

Encrypts neural architecture state using the relationship between the current state and the previous (last) state. No external dependencies. Framework-agnostic: operates on flat integer sequences — callers pre-quantize their framework's weight or activation tensors.

## Algorithm

For each index `i` in the state:

1. Select prime `p = PRIME_CIRCLE[i % 53]` (circular indexing over 53 primes: 2, 3, 5, …, 241)
2. Decompose `state[i]` into bijective base-`p` digits — each digit in `{1, …, p}`
3. Extract key digits from `last_state[i % L]` in standard base `p`
4. Shift each digit additively mod `p`, staying within `{1, …, p}`
5. Reconstruct the encrypted value

Bijective base-`p` encoding guarantees that encrypted values always have the same digit count as the originals. Decryption is the additive inverse and requires the same `last_state`.

```
encrypt: e_j = ((v_j - 1 + k_j) mod p) + 1
decrypt: v_j = ((e_j - 1 - k_j) mod p) + 1
```

## Usage

```python
from pcea import encrypt_state, decrypt_state, PCEAInstance

# Stateless (caller manages last_state)
state      = [1000, 2000, 3000]   # pre-quantized integers
last_state = [500,  600,  700]

encrypted  = encrypt_state(state, last_state)
recovered  = decrypt_state(encrypted, last_state)
assert recovered == state

# Stateful (instance advances last_state automatically)
enc = PCEAInstance(seed=[1, 2, 3])
dec = PCEAInstance(seed=[1, 2, 3])

e1 = enc.encrypt([100, 200, 300])
e2 = enc.encrypt([400, 500, 600])

assert dec.decrypt(e1) == [100, 200, 300]
assert dec.decrypt(e2) == [400, 500, 600]
```


## PCEA ↔ UCNS Boundary (v0 contract decision)

PCEA is specified to decrypt/invert **via keys**, not via UCNS inverse operations.
That means:

- PCEA consumes only forward arithmetic substrate behavior.
- Security rests on key management (`last_state` synchronization and protection), not on any assumption that arithmetic inversion is hard.
- A mismatch in key state must fail recovery by design.

This keeps PCEA cryptographic claims decoupled from UCNS analytic-frontier work.

## Install

```
pip install .          # runtime — no dependencies
pip install ".[dev]"   # adds pytest
```

## Author

Erin Patrick Spencer — interdependentway.org
