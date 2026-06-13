# PCEA-UCNS Proving Ground

This directory is the proving ground for UCNS-assisted PCEA ideas. It is not
runtime PCEA, not a shipped key-exchange layer, and not a security proof. Its
job is to make candidate constructions fail loudly, measure the ones that do
not fail immediately, and preserve the exact boundary between a usable symmetric
PCEA transform and speculative UCNS-native key establishment.

## What this proving ground can do

1. **Refute hiding places for private key material.**
   Harnesses such as `attack_harness.py`, `positional_attack.py`,
   `factor_count_sweep.py`, `prefix_read_break.py`, and
   `attack1_minkowski_break.py` point UCNS recovery tools at proposed private
   slots and record when those slots are readable, enumerable, or structurally
   invertible.

2. **Separate full-space attacks from key-space-restricted attacks.**
   `quotient_attack.py` and `pruning_scaling.py` distinguish “the attacker can
   find some recomposing factorization” from “the attacker can find a valid
   private key inside the intended key space,” then measure whether cheap
   pruning changes the asymptotic search cost.

3. **Turn negative results into release gates.**
   Tests under `tests/test_*attack*.py`, `tests/test_*sweep.py`, and related
   files pin measured breaks and partial results. A passing test often means a
   known break is still reproduced, not that the construction is secure.

4. **Explore state/gonal communication candidates.**
   `gonal_architecture.py` tests a PCEA-advanced gonal idea against simple
   frequency and known-plaintext probes. It remains experimental: the module
   itself names unresolved gates before any shipped `gonal_cipher.py` should
   exist.

5. **Protect the runtime boundary.**
   The proving ground may import UCNS and run attack tooling. The shipped
   `pcea/` runtime must remain the symmetric, state-synchronized transform and
   must not silently depend on UCNS inversion or catalogue APIs.

## What it cannot honestly do yet

- It cannot claim PCEA-UCNS is secure public-key encryption.
- It cannot turn a passing attack harness into a proof of hardness.
- It cannot replace authentication, nonce/session design, or key-management
  requirements for a production channel.
- It cannot ship a UCNS-KEM while the current documents mark the native UCNS
  key-establishment line as blocked or open.

## Current tested lanes

| Lane | Main files | What the lane is for | Present meaning |
|---|---|---|---|
| Baseline UCNS factor attacks | `attack_harness.py`, `positional_attack.py` | Check whether carrier choice, oracle domains, or fixed-carrier positions hide keys | Mostly negative: easy domains are forbidden |
| Factor-count and non-uniqueness | `three_factor_attack.py`, `factor_count_sweep.py` | Test whether more factors hide a designated private factor | Partial smearing, not a safe KEM foundation by itself |
| Key-space restriction | `quotient_attack.py`, `pruning_scaling.py` | Ask whether the private factor is unique inside a finite key space and whether pruning beats brute search | Useful distinction; cheap pruning measured as constant-factor, not a proof |
| Structural readout breaks | `prefix_read_break.py`, `attack1_minkowski_break.py` | Look for direct reconstruction or algebraic inversion that bypasses key-space search | Negative gates: tested candidate families break |
| Gonal/state communication | `gonal_architecture.py` | Explore PCEA-advanced private gonal rotation for state/token communication | Experimental; further bridge/attack gates remain |

## How to use it

Run the whole repository:

```bash
python -m pytest -q
```

Run the symmetric PCEA runtime gate only:

```bash
python -m pytest -q tests/test_cipher.py tests/test_codec.py tests/test_kdf.py tests/test_instance.py tests/test_contract_spec.py
```

Run the UCNS proving-ground tests:

```bash
python -m pytest -q tests/test_attack_harness.py tests/test_positional_attack.py tests/test_quotient_attack.py tests/test_prefix_read_break.py tests/test_projection_action_candidate.py tests/test_pruning_scaling.py tests/test_attack1_minkowski_break.py tests/test_three_factor_attack.py tests/test_factor_count_sweep.py tests/test_gonal_architecture.py
```

If `ucns` is not installed, UCNS-dependent tests skip by design. That skip is
an environment limitation, not a positive result. To harvest real UCNS attack
numbers, install the matching The Interdependency UCNS package/repository in
the test environment, rerun the proving-ground tests, and update the measured
figures only when the harness seeds and parameters are also recorded.

## Rule for adding a new candidate

A new candidate belongs here only if it includes:

1. A short statement of the claimed private material, public material, and
   shared-secret derivation.
2. A harness that tries to break that claim with the strongest existing UCNS
   recovery primitive that applies.
3. A pytest gate that pins the measured result.
4. A document update saying whether the result is a break, a partial survival,
   or an unresolved gate.
5. No runtime import path from `pcea/` into the proving-ground code unless the
   PCEA↔UCNS contract is deliberately changed and reviewed.

The preferred outcome is a clean refutation. A candidate that survives one
harness should immediately earn a harder harness, not a security claim.
