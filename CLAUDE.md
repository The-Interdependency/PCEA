# CLAUDE.md — PCEA: Prime Circular Encryption Algorithm

This file gives AI assistants context needed to work effectively in this repository.

---

## What This Repo Is

`pcea` (pip package: **`pcea`**, v0.1.0) is a zero-dependency pure-Python library implementing the **Prime Circular Encryption Algorithm** — a bijective base-`p` additive cipher keyed by a rotating schedule of the first 53 primes.

Primary use case: encrypting neural architecture state (pre-quantized integer tensors) using the relationship between the current state and the previous state. One of the four-letter acronym libraries published under The Interdependency.

**Python requirement:** ≥ 3.9  
**External dependencies:** none (stdlib only — math, dataclasses)  
**License:** Apache 2.0

---

## Algorithm

For each index `i` in the state:
1. Select prime `p = PRIME_CIRCLE[i % 53]` — first 53 primes: 2, 3, 5, …, 241
2. Decompose `state[i]` into bijective base-`p` digits — each digit in `{1, …, p}`
3. Extract key digits from `last_state[i % L]` in standard base `p`
4. Shift each digit additively mod `p`, staying in `{1, …, p}`
5. Reconstruct the encrypted value

```
encrypt: e_j = ((v_j - 1 + k_j) mod p) + 1
decrypt: v_j = ((e_j - 1 - k_j) mod p) + 1
```

Bijective base-`p` encoding guarantees that encrypted values always have the same digit count as originals. Decryption requires the same `last_state`.

---

## Repository Layout

```
pcea/
  __init__.py     Public API — exports encrypt_state, decrypt_state, PCEAInstance
  cipher.py       Core encrypt/decrypt logic — bijective base-p + digit shift
  codec.py        Codec helpers (bytes encode/decode for network/storage)
  instance.py     PCEAInstance — stateful session that auto-advances last_state
  kdf.py          Key derivation function helpers
  primes.py       PRIME_CIRCLE constant (first 53 primes: 2..241)

tests/
  test_*.py       pytest test suite

pyproject.toml    Package config (setuptools, Apache-2.0, Python >= 3.9)
README.md
LICENSE
```

---

## Development Workflow

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Runtime install only (no test deps)
pip install .
```

No linter or formatter configured yet. Keep code consistent with existing style: pure stdlib, dataclasses, no third-party libraries.

---

## Public API

```python
from pcea import encrypt_state, decrypt_state, PCEAInstance

# Stateless (caller manages last_state)
state      = [1000, 2000, 3000]   # pre-quantized integers
last_state = [500, 600, 700]

encrypted  = encrypt_state(state, last_state)
recovered  = decrypt_state(encrypted, last_state)
assert recovered == state

# Stateful (PCEAInstance auto-advances last_state)
enc = PCEAInstance(seed=[1, 2, 3])
dec = PCEAInstance(seed=[1, 2, 3])

e1 = enc.encrypt([100, 200, 300])
e2 = enc.encrypt([400, 500, 600])

assert dec.decrypt(e1) == [100, 200, 300]
assert dec.decrypt(e2) == [400, 500, 600]
```

---

## Key Conventions

- **No external dependencies** — stdlib only. Do not add runtime deps.
- **Bijective base-p invariant** — encrypted values always have the same digit count as originals. Do not break this property.
- `PRIME_CIRCLE` in `primes.py` is authoritative — 53 primes, 2 through 241. Do not modify.
- `PCEAInstance` auto-advances `last_state` after each `encrypt()` / `decrypt()` call. Paired encoder/decoder instances must be initialized with the same `seed` to stay synchronized.
- `pcea/__init__.py` is the stable public API surface — only add exports here that are intentional and stable.
- `cipher.py` is the security-critical module — treat any changes to it with extra scrutiny. Do not use Copilot-generated crypto without independent review.

---

## What Does Not Exist Yet

- No CI/CD pipeline
- No linting or formatting config (prefer `ruff` when adding)
- No type stubs or `py.typed` marker
- No streaming mode for large tensors

---

## Related Repos

| Repo | Role |
|------|------|
| The-Interdependency/interdependent-lib | Meta-package bundling pcea + ptca + ucns + aimmh |
| The-Interdependency/ptca | Tensor context architecture (uses same 53-prime-circle concept) |
| The-Interdependency/a0 | Agent platform that consumes PCEA for state security |

---

## Git Workflow

- Main branch: `main`
- Feature branches: `feat/<description>`, `fix/<description>`, `docs/<description>`
- Commit style: Conventional Commits (`feat(pcea):`, `fix(cipher):`, etc.)
- Author: Erin Patrick Spencer (wayseer@interdependentway.org)
- License: Apache 2.0

## Agent module-build doctrine

Before adding a new module, route, service, adapter, schema, worker, engine,
UI panel, migration, or experiment, read:

`./.agents/skills/meta-module-build/SKILL.md`

New module work should start with a `MODULE_BUILD` block. Unknown fields must
be marked `hmmm`, not guessed.
