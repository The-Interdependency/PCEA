# UCNS Cryptographic Domain — v0

**Status:** SPECIFICATION / PLANNING artifact. This document does **not**
claim a secure public-key system exists. It defines a candidate UCNS
cryptographic domain for PCEA-UCNS (see `PLAN.md`) and forbids domains
that the existing UCNS factorization tools demonstrably break. The
forbidden-domain conclusions are derived from measured attacks
(`attack_harness.py`, gated by `tests/test_attack_harness.py`), not from
argument.

**Accreditation:** Claude generated from repository context as prompted
by Erin Spencer; attack numbers reproduced from `attack_harness.run_all()`
against The-Interdependency/ucns at the Carrier-LCM Law + pruning
release.

**Security posture (inherited from `contract.py`):** PCEA's symmetric
security rests on key management, and adversaries are assumed able to
invert carrier arithmetic. This document concerns the *asymmetric* layer
UCNS must supply, where the hardness assumption is different and not yet
established. Nothing here upgrades PCEA's current claims.

---

## What today's UCNS results force

Three measured facts shape every answer below.

1. **The Carrier-LCM Law is a leak.** `n_min(A ⊠ B) = lcm(n_min(A),
   n_min(B))` (DEFENDED + TEST-BACKED in ucns). Measured: private
   carrier supports {2} and {2,5} produce public carrier 80 with support
   exactly {2,5}. **A secret encoded in carrier choice is public by
   construction.** The private key must live where the Law does not
   project: not in the carrier.

2. **The oracle domain is exhaustively breakable.** Measured: 52/60
   (~87%) of random products on the frozen depth-2 oracle domain are
   recovered by `factor_search_v08`. This domain is ORACLE-COMPLETE in
   the ucns ledger. **Categorically forbidden for key material.**

3. **Pruning is an attacker's accelerator.** Measured: Carrier-LCM-Law
   payload pruning removes ~71% of the candidate catalogue for free on
   the {2,5} product. Any domain whose key space is enumerable as a
   payload catalogue inherits this speedup against it.

## The ten questions (PLAN.md Phase 1)

**1. What is a UCNS private key?**
Candidate: structure the public projection's carrier does *not* reveal —
specifically (a) the angle *positions* within a fixed, publicly-known
carrier, (b) face-bit configuration, and (c) payload structure at a depth
beyond any catalogue-complete domain. NOT carrier choice (leaked, fact 1).

**2. What is a UCNS public key?**
A UCNS object whose carrier and gross shape are publishable, derived from
the private key by a forward operation (composition) such that recovering
the private structure requires cross-prime factoring (the open frontier).

**3. What is the base carrier or base object?**
A carrier in the analytic-frontier regime — minimally the **carrier-40,
⟨2,5⟩ cross-prime instance** named in the ucns frontier docs: the
smallest case where forward composition stays in-lattice but factoring
must cross prime lines. Real candidates scale the prime set and carrier
well beyond any oracle-complete bound.

**4. What operation derives the public key?**
Forward `multiply` (Law-governed, fast, public). The public key is a
product; the private key is a factor whose recovery is the hard problem.

**5. What operation derives the shared secret?**
KEM-style (preferred per PLAN.md): `encapsulate` composes the peer public
key with fresh randomness into a packet; `decapsulate` uses the private
factor to recover the shared object, which is then run through the
existing `kdf.key_stream` to a PCEA session key. The arithmetic produces
key *material*; `hashlib` does the final derivation.

**6. What exactly is the assumed hard problem?**
**Cross-prime UCNS factoring outside catalogue-complete domains:** given a
public product P with carrier in the frontier regime, recover a private
factor when the catalogue is NOT sufficient (so Theorem N does not apply)
and the prime support spans multiple primes (so forward-lattice closure
gives no shortcut). This problem is **OPEN in ucns** — which is the only
reason it is a candidate. Its hardness is **assumed, not proved**; if the
analytic frontier closes constructively, this assumption dies with it.

**7. Which UCNS domains are forbidden (factor-search-complete)?**
- The frozen depth-2 **oracle domain** (measured ~87% recovery).
- Any domain where the key catalogue is **catalogue-sufficient** for
  Theorem N (factorization complete by construction).
- Any domain whose key carrier's prime support is **small enough to
  enumerate** the pruned catalogue (fact 3: pruning + small support =
  tractable search).
- Any single-prime / prime-power carrier domain (no cross-prime hardness
  to hide behind).

**8. What information is intentionally public?**
Carrier (leaked anyway, fact 1), object depth, gross cell count, the KEM
packet, and all algorithm parameters. Security must survive their
disclosure.

**9. What information must never be serialized publicly?**
Private angle positions within the carrier, private face bits, private
payload structure, the recovered shared object, and the PCEA session key.
The public-key serializer must be incapable of emitting these
(PLAN.md Phase 2 exit gate).

**10. What public object sizes are acceptable for mobile?**
Target: public key and KEM packet each serializable in low single-digit
kilobytes, decapsulation within interactive latency on the reference
device (Termux / Galaxy A16). Carrier magnitude trades directly against
both — a Phase-2 measurement, not a guess.

## Toy domain (for tests)

A deliberately breakable domain: small ⟨2,5⟩ carriers, catalogue
provided. Used to confirm the harness *recovers* keys here (negative
control — the domain MUST fall), so that survival on the real candidate
domain is meaningful by contrast.

## Real candidate domain (described, not secured)

Cross-prime carriers well beyond oracle-complete bounds, private structure
in angle position / face / deep payload, public projection via forward
composition. **Explicitly unproven.** The path to any security claim runs
through the ucns analytic frontier, not through this document.

## Attack tools (named, not ignored — PLAN.md requirement)

`factor_search_v08`, `left_quotient` / `right_quotient`,
`prune_catalogue` / `prune_payload_catalogue`, `canonical_factorization`,
and the frozen oracle catalogue. `attack_harness.py` wires the first set
against candidate domains; expanding it to the full set is the Phase-1
follow-on.

## hmmm

- The hardness assumption (Q6) is load-bearing and **unproved**; it is
  the same open problem as ucns cross-prime widening, now wearing a
  security hat. If that frontier closes, PCEA-UCNS must fall back to
  symmetric-only — which `contract.py` already ensures it can.
- Q1's claim that angle-position is not Law-projected needs its own
  attack: a positional analog of `factor_search`. Not yet built; until
  it is, "the Law doesn't reach here" is a conjecture, not a result.
