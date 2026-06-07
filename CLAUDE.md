# CLAUDE.md — PCEA: Prime Circular Encryption Algorithm

This file gives AI assistants context needed to work effectively in this repository.

---

## What This Repo Is

`pcea` (pip package: **`pcea`**, v0.1.0) is a zero-dependency pure-Python library
implementing the **Prime Circular Encryption Algorithm** — a bijective base-`p`
additive cipher built on a Möbius-disk codec, a prime circle, and a SHA-256 key
stream keyed by the previous state.

Primary use case: encrypting neural architecture state (pre-quantized integer
tensors) using the relationship between the current state and the previous
state. Framework-agnostic — callers pre-quantize their framework's weight or
activation tensors into integer arrays. One of the four-letter-acronym libraries
published under The Interdependency.

<!-- BEGIN GENERATED:manifest -->
<!-- Generated from pyproject + repo tree by .agents/skills/manifest/generate.py — DO NOT EDIT BY HAND. Refresh with `python .agents/skills/manifest/generate.py --write`. -->

| Field | Value |
|---|---|
| Package | `pcea` |
| Version | `0.1.0` |
| Description | Prime Circular Encryption Algorithm — neural architecture state encryption |
| Status | hmmm |
| Python | >=3.9 |
| License | MIT |
| Build backend | `setuptools.build_meta` |
| Author(s) | Erin Patrick Spencer <wayseer@interdependentway.org> |
| Repository | https://github.com/The-Interdependency/PCEA |
| Runtime dependencies | none (stdlib only) |
| Optional extras | `dev` |
| Keywords | none |
| CI workflows | `contract-boundary.yml`, `manifest-check.yml` |
| Top-level directories | `benchmarks/` · `pcea/` · `tests/` |

<sub>Derived from `pyproject.toml` + the repo tree. Unknown fields surface as `hmmm` rather than a guess.</sub>
<!-- END GENERATED:manifest -->

> The block above is generated from `pyproject.toml` + the repo tree by the `manifest` living-spec tool (`.agents/skills/manifest/`) and gated in CI (`.github/workflows/manifest-check.yml`) — do not hand-edit between the markers; run `python .agents/skills/manifest/generate.py --write` after changing version/deps/layout.

**Python requirement:** ≥ 3.9 (CI matrix: 3.9, 3.11, 3.13)
**External dependencies:** none at runtime (stdlib only — `hashlib`, `copy`); `pytest` for dev
**License:** MIT (relicensed from AGPL-3.0)

---

## Data Model

State is hierarchical:

```
state  : list of seeds          (list[list[list[int]]])
seed   : 7 circles × 7 tensors  (list[list[int]], CIRCLE_COUNT × TENSOR_COUNT)
```

Each circle is itself a tensor; each seed is itself a tensor. `encrypt_seed` /
`decrypt_seed` operate on one 7×7 seed; `encrypt_state` / `decrypt_state`
map over a list of seeds.

`word_bits` (default 64, `DEFAULT_WORD_BITS`) sets the Möbius disk size and
**must match** between sender and receiver. Larger values support wider integer
ranges.

---

## Algorithm

For each element at `(seed_idx, circle_idx c, tensor_idx t)`:

1. **Prime select** — `p = prime_at(c * 7 + t)`, wrapping over the 53-prime circle.
2. **Möbius encode** — `u = mobius_encode(value, word_bits)` maps the signed integer
   to an unsigned two's-complement position. The two disk halves (positive /
   negative) are indistinguishable to an observer — **sign does not leak**.
3. **Fixed-width digits** — decompose `u` into exactly `k = digit_count(p, word_bits)`
   standard base-`p` digits (little-endian, each in `{0, …, p-1}`). Fixed width
   means **magnitude does not leak** through output length.
4. **Key stream** — `key_stream(...)` derives `k` digits via SHA-256 from the
   contributors (own value plus heptagram neighbors at circles `±3 mod 7`) and
   the hierarchical address `(seed_idx, c, t)`.
5. **Additive shift** — `e_j = (v_j + k_j) mod p`; decrypt is `v_j = (e_j - k_j) mod p`,
   then `mobius_decode` recovers the signed value.

```
encrypt digit: e_j = (v_j + k_j) mod p
decrypt digit: v_j = (e_j - k_j) mod p
```

Decryption requires the **same `last_state`** and `word_bits`. A wrong key state
fails recovery by design.

---

## Repository Layout

```
pcea/
  __init__.py     Public API — see exports below
  cipher.py       Core encrypt/decrypt; seed/state orchestration; heptagram contributors
  codec.py        Möbius disk codec + fixed-width base-p (mobius_encode/decode, to_fixed, from_fixed, digit_count)
  kdf.py          key_stream — SHA-256 key derivation from contributors + address
  primes.py       PRIME_CIRCLE (first 53 primes 2..241), CIRCLE_SIZE, prime_at
  instance.py     PCEAInstance — stateful session that auto-advances last_state
  contract.py     PCEA↔UCNS interface-contract constants (DECISION, invariants, forbidden symbols)

tests/            pytest suite (see Gotchas re: test_contract_spec.py)
benchmarks/
  bench.py        Throughput/latency benchmark across codec → kdf → element → seed → state → instance

.github/workflows/
  contract-boundary.yml   CI gate running tests/test_contract_spec.py on PRs + pushes to main

.agents/skills/   meta-module-build / msdmd / test-build agent skill docs

pyproject.toml    Package config (setuptools, MIT, Python >= 3.9)
README.md  LICENSE
```

---

## Development Workflow

```bash
# Install with dev dependencies (pytest)
pip install -e ".[dev]"

# Runtime install only (no test deps)
pip install .

# Run the full test suite (pyproject sets testpaths = ["tests"])
pytest

# Run only the CI contract-boundary gate (mirrors the workflow)
PYTHONPATH=. python -m pytest -q tests/test_contract_spec.py

# Run the performance benchmark
python benchmarks/bench.py
```

No linter or formatter is configured. Keep code consistent with existing style:
pure stdlib, `from __future__ import annotations`, no third-party runtime libraries.

---

## Public API

`pcea/__init__.py` is the stable public surface. Exports:

| Group | Names |
|-------|-------|
| Cipher | `encrypt_seed`, `decrypt_seed`, `encrypt_state`, `decrypt_state`, `PCEAInstance` |
| Codec | `mobius_encode`, `mobius_decode`, `digit_count`, `to_fixed`, `from_fixed` |
| KDF | `key_stream` |
| Constants | `CIRCLE_COUNT`, `TENSOR_COUNT`, `DEFAULT_WORD_BITS`, `PRIME_CIRCLE`, `CIRCLE_SIZE`, `prime_at` |
| Contract | `CONTRACT_DECISION`, `contract_statement` |

```python
from pcea import encrypt_state, decrypt_state, PCEAInstance

def seed(base):                       # 7×7 integer array
    return [[base + c * 7 + t for t in range(7)] for c in range(7)]

# Stateless (caller manages last_state); state/last_state are lists of seeds
state      = [seed(10), seed(20)]
last_state = [seed(1),  seed(2)]
encrypted  = encrypt_state(state, last_state)            # optional: word_bits=64
assert decrypt_state(encrypted, last_state) == state

# Stateful — PCEAInstance auto-advances last_state after each call
enc = PCEAInstance(seed=[seed(0)])
dec = PCEAInstance(seed=[seed(0)])
e1 = enc.encrypt([seed(99)])
assert dec.decrypt(e1) == [seed(99)]
```

---

## Key Conventions

- **No external runtime dependencies** — stdlib only. Do not add runtime deps.
- **Fixed-width invariant** — encrypted output always has exactly
  `digit_count(p, word_bits)` digits; sign and magnitude must not leak. Do not break this.
- **Shapes are validated** — seeds must be 7×7; `encrypt_state`/`decrypt_state`
  require `state` and `last_state` to have the same number of seeds.
- **`word_bits` must match** across encrypt/decrypt and between paired instances.
- `PRIME_CIRCLE` in `primes.py` is authoritative — first 53 primes, 2 through 241,
  generated by a sieve. Do not modify the sequence or `CIRCLE_SIZE`.
- `PCEAInstance` auto-advances `last_state` to the plaintext after each
  `encrypt()` / `decrypt()`. Paired encoder/decoder instances must be initialized
  with the same `seed` and process states in the same order to stay synchronized.
- **Metadata header** — every `*.py` file under `pcea/` and `tests/` must start
  with the exact line `# GPT/Claude generated; context, prompt Erin Spencer`.
  `tests/test_metadata_headers.py` enforces this.
- **PCEA↔UCNS contract (Option A)** — PCEA decrypts/inverts via keys, never via
  UCNS inverse/catalogue APIs. `contract.py` holds the canonical constants and the
  list of `FORBIDDEN_UCNS_SYMBOLS`. `tests/test_contract_spec.py` is the release gate.
- `cipher.py`, `codec.py`, and `kdf.py` are security-critical — treat changes with
  extra scrutiny. Do not ship machine-generated crypto without independent review.

---

## Gotchas

- **`tests/test_contract_spec.py` is currently broken** — it contains an unresolved
  merge conflict (duplicated `for` loops, e.g. `RUNTIME_FILES` vs `RUNTIME_MODULES`)
  that causes an `IndentationError` at collection time and also lacks the required
  metadata header. As a result a plain `pytest` aborts during collection (the bad
  file interrupts the whole run).
- **Excluding the file does NOT make the suite green.** Running
  `pytest --ignore=tests/test_contract_spec.py` lets the other modules collect,
  but `tests/test_metadata_headers.py` still fails: it globs
  `pcea/*.py` and `tests/*.py` on disk, and `tests/test_contract_spec.py` is
  still present without the required header line. So the exclusion run reports
  one failure (the metadata-header test) with the rest passing — not a clean
  pass. To actually get a green suite you must fix the file (resolve the merge
  conflict and add the header), not merely skip it. Re-derive the exact pass
  count from `pytest -q` rather than trusting a hard-coded number here.
  The intended logic lives in `pcea/contract.py` (use `RUNTIME_MODULES` and
  `FORBIDDEN_UCNS_SYMBOLS`); resolving this file is the natural first fix.
- CI (`contract-boundary.yml`) runs only `test_contract_spec.py`, so the broken file
  blocks that gate too.

---

## Related Repos

| Repo | Role |
|------|------|
| The-Interdependency/interdependent-lib | Meta-package bundling pcea + ptca + ucns + aimmh |
| The-Interdependency/ptca | Tensor context architecture (shares the 53-prime-circle and ±3 heptagram adjacency) |
| The-Interdependency/ucns | Arithmetic substrate; PCEA consumes only its forward behavior (see contract) |

---

## Git Workflow

- Main branch: `main`
- Feature branches: `feat/<description>`, `fix/<description>`, `docs/<description>`
- Commit style: Conventional Commits (`feat(pcea):`, `fix(cipher):`, etc.)
- Author: Erin Patrick Spencer (wayseer@interdependentway.org)
- License: MIT (relicensed from AGPL-3.0)

## Agent module-build doctrine

Before adding a new module, route, service, adapter, schema, worker, engine,
UI panel, migration, or experiment, read:

`./.agents/skills/meta-module-build/SKILL.md`

New module work should start with a `MODULE_BUILD` block. Unknown fields must
be marked `hmmm`, not guessed.
