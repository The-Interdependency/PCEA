# A UCNS Key-Encapsulation Feasibility Investigation

**Status:** Research note. Reports a sequence of measured attacks against
candidate UCNS-based key-encapsulation (KEM) domains for PCEA-UCNS. It
establishes **no positive security claim** beyond what each measurement
licenses; it does establish, at exact strength, which candidate
constructions are refuted and which survive their most natural attacks.

**Method discipline:** every result below is produced by a reproducible
harness in `pcea-ucns/` and pinned by a test in `tests/` (skipped when
ucns is absent). All attacks use the *real* UCNS factorization tools —
`factor_search_v08`, `left_quotient`, and the Carrier-LCM-Law pruning
corollaries — pointed adversarially. Numbers are reproduced from a single
harvest run; seeds and parameters are in the harnesses.

**Accreditation:** Claude generated from repository context as prompted by
Erin Spencer. Reproduced against The-Interdependency/ucns at the
Carrier-LCM Law + pruning + canonical-selection release.

---

## The question

PCEA is a sound symmetric keyed transform; it is not asymmetric (see
`PLAN.md`, `contract.py`). A UCNS-KEM would supply the missing primitive,
with a private key recoverable only by solving a UCNS problem believed
hard. The investigation asks, empirically: **is there a UCNS construction
whose private key resists recovery by the factorization tools UCNS already
ships?**

## The arc, in six steps

Each step overturned or sharpened the previous; the conclusion is neither
"secure" nor "broken" but a precisely located open problem.

### 1. Carrier choice is not a hiding place (refuted)

By the Carrier-LCM Law, `n_min(A ⊠ B) = lcm(n_min(A), n_min(B))`. Measured:
private carrier supports {2} and {2,5} yield public carrier 80 with support
exactly {2,5}. The public product's carrier reveals the union of the
factors' carrier supports. **A secret in carrier choice is public by
construction.** (`attack_harness.py`)

### 2. The oracle domain is exhaustively breakable (forbidden)

On the frozen depth-2 oracle domain — ORACLE-COMPLETE in the UCNS ledger —
`factor_search_v08` recovers 52/60 (~87%) of random products. **Forbidden
for keys.** (`attack_harness.py`)

### 3. Angle position at fixed carrier is not a hiding place (refuted)

The v0 spec conjectured a key could hide in angle position / face / payload
at a fixed public carrier. Measured at carriers 15, 40, 105: recompose
**60/60**, exact private factor ~48%, no improvement with larger carrier.
Fixing the carrier removes the carrier leak but leaves the whole
factorization attack intact, and **non-uniqueness means the attacker needs
only some recomposing pair, not the exact key.** (`positional_attack.py`)

### 4. Ordered triple products: partial protection, not safety

For `P = A ⊠ B ⊠ C` with C private: recompose 80/80, but the first split is
**never** the clean (A⊠B, C) — 0/80. Ordered composition smears the
private-factor boundary. Yet recursive peeling still recovers C ~49%.
**Degraded, not defeated.** (`three_factor_attack.py`)

### 5. Factor count is irrelevant; non-uniqueness looked fatal

Recovery does not decay with factor count (2..6 factors: ~40–67%, flat).
For a 5-factor product the search finds the true ordered (prefix, C) split
0/80 and some other valid decomposition 80/80 — **the public product has
many ordered factorizations.** This appeared to defeat any KEM: bind the
secret to any decomposition and the attacker supplies one; bind it to the
unique true one and honest parties cannot recover it. (`factor_count_sweep.py`)

### 6. The quotient corrects the verdict (hardness relocated)

The previous step measured the full object space. The `left_quotient`
primitive, restricted to a finite key space, disagrees: given public
`P = A ⊠ B` with A, B in the key space, the number of key-space candidates
that left-divide P is **mean ~1.1, max 2** — the private factor is nearly
*unique within the key space*. The factorizer's many decompositions land
**outside** the key space ~55% of the time; they are not usable keys.
**Full-space non-uniqueness does not defeat a key-space-restricted KEM.**
(`quotient_attack.py`)

### 7. The break attempt fails — constant-factor, not polynomial

The relocated danger: a quotient-*guided* search beating brute-force
enumeration. Two cheap attacks — prefix-angle ordering, and the cipher's
own carrier-support pruning turned adversarial — measured by scaling in
|key space| from 40 to 1000:

| Attack | Cost scaling | ratio-to-\|KS\| |
|---|---|---|
| Prefix-angle ordering | ~ \|KS\|^0.89 | flat ~0.10 |
| Carrier-support + prefix prune | ~ \|KS\|^1.03 | flat ~0.10 |

A polynomial break shows ratio → 0; here it holds flat. Both attacks are
**constant-factor (Θ(\|KS\|))** — they reorder the search, they do not
shrink it. A ~10× constant is absorbed by a few key bits.
(`pruning_scaling.py`)

## What is established

- **Refuted constructions:** carrier-choice keys; fixed-carrier
  angle-position keys; oracle-domain keys; reliance on full-space
  factorization hardness.
- **Surviving regime:** a *finite, structured key space* in which the
  private factor is quotient-unique, attacked by *linear* quotient-guided
  search. This regime resists its most natural attacks, including the
  cipher's own pruning corollaries.
- **Not established:** any hardness proof. The surviving regime rests on
  two unproven conditions — the key space is infeasible to enumerate, and
  no *sublinear* quotient-guided search exists.

## The open problem, cleanly stated

> **Is there a sublinear quotient-guided search over a structured UCNS key
> space?**

This is sharper than "is UCNS factoring hard." The linear-heuristic class
is empirically eliminated; the live question is whether the *recursive
payload quotient* or algebraic relations among divisors leak structure
that compounds across depth. That is the next probe (a payload-depth-aware
attack, measured by the same scaling law).

## Relationship to PCEA's shipped claims

None of this changes PCEA's current status. PCEA remains a sound symmetric
transform whose security rests on key management (`contract.py`); the
asymmetric UCNS-KEM remains experimental and unproven. If the open problem
resolves toward an attack, PCEA-UCNS falls back to symmetric-only, which
the contract already guarantees. If it resolves toward hardness, PCEA-UCNS
becomes a candidate public-key construction — pending formal review, never
self-certified.

## Reproduce

```
PYTHONPATH=/path/to/ucns python pcea-ucns/attack_harness.py
PYTHONPATH=/path/to/ucns python pcea-ucns/positional_attack.py
PYTHONPATH=/path/to/ucns python pcea-ucns/three_factor_attack.py
PYTHONPATH=/path/to/ucns python pcea-ucns/factor_count_sweep.py
PYTHONPATH=/path/to/ucns python pcea-ucns/quotient_attack.py
PYTHONPATH=/path/to/ucns python pcea-ucns/pruning_scaling.py
```

Tests: `PYTHONPATH=/path/to/ucns python -m pytest tests/` (harness tests
skip cleanly without ucns).

## hmmm

- The arc's shape is itself the finding: a construction that is refuted in
  the full space and survives in a restricted one is exactly what a KEM is
  — RSA is trivial over the integers and hard only in the structured
  semiprime domain. The question was never "is UCNS hard" but "is there a
  UCNS domain where it is."
- The next probe could end the investigation either direction. State both
  outcomes before running it, so neither is a surprise that tempts a
  rationalization.
