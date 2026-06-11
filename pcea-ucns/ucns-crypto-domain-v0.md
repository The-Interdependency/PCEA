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
**OPEN — the v0 candidate is REFUTED.** The v0 conjecture was that the
private key could hide in angle *position* / face bits / payload at a
fixed public carrier, since the Carrier-LCM Law only projects the
carrier. The positional attack harness (`positional_attack.py`,
`tests/test_positional_attack.py`) refutes this directly: at a held-fixed
public carrier, `factor_search_v08` recovers a recomposing factorization
in **60/60** trials across carriers 15, 40 (the named candidate), and
105, and the *exact* private factor in ~45–57%. Larger carriers do not
help. The reason is structural, not arithmetic: the search already
recovers host angles AND faces, and — decisively — **non-uniqueness means
an attacker needs only SOME factor pair that recomposes P, not the exact
private key**, since the shared secret derives from the factorization.
Holding the carrier fixed removes the carrier leak but leaves the whole
factorization attack intact. A viable private-key location must therefore
defeat factorization itself, not merely the carrier projection — which
returns the entire question to the cross-prime analytic frontier (Q6).

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

## Three-factor candidate (P = A ⊠ B ⊠ C) — partial protection, not safety

After the two-factor Q1 refutation, the natural next candidate is a
private key that is one factor of an ORDERED triple product, with the
public product P = A ⊠ B ⊠ C published and C designated private.
`three_factor_attack.py` measures it (carriers 15, 40, 105):

- **recompose 80/80** — the search always finds *a* valid two-factor
  split of the triple product.
- **first-split-clean 0/80** — but the split is *never* exactly
  (A ⊠ B, C). Ordered composition smears the private-factor boundary: a
  single split cuts across factors, not along them. This is real,
  measurable structure the two-factor case did not have.
- **recursive-peel recovers C ~42–49%** — an attacker who peels
  iteratively (factor the split, then factor the parts) recovers the
  designated private factor about half the time.

**Conclusion: three factors degrade the attack but do not defeat it.**
The boundary-smearing is genuine partial protection — the most promising
direction so far — but a ~45% recovery rate is catastrophic for a key.
Three-factor composition alone is NOT a viable KEM foundation. It is,
however, the first structure that interacts with the attack non-trivially,
and the smearing mechanism (ordered cross-products mixing factor
boundaries) is the thing to understand before the next candidate: more
factors, deeper payloads, or a composition the attacker cannot assume the
order of.

## Factor count is irrelevant — non-uniqueness is the structural defeater

The boundary-smearing in the three-factor case raised the hope that
recovery DECAYS with factor count: that a 5- or 6-factor product hides a
designated private factor better. `factor_count_sweep.py` tests it at
carrier 40 and finds **no decay** — recursive-peel recovery runs ~40–67%
flat across 2..6 factors, noise with no downward trend. More factors give
the attacker more leaves to match, not the defender more cover.

The diagnosis underneath is the important part. For a 5-factor product,
the search's split equals the TRUE ordered (prefix, C) in **0/80** trials
and lands on some OTHER valid decomposition in **80/80**. The public
product admits *many* ordered factorizations. That is fatal independent
of factor count:

- If the KEM secret derives from ANY recomposing decomposition, the
  attacker supplies one and the scheme is **broken**.
- If it derives from the UNIQUE true ordered decomposition, that
  decomposition is not recoverable even by honest parties from P alone,
  so the scheme is **non-functional**.

**Non-uniqueness of UCNS factorization is the structural barrier to a
factorization-based KEM, at every factor count.** This is the same fact
the ucns claims ledger records as "Theorem N returns *a* valid
factorization, not a canonical one" — and the canonical-selection work
(`canonical_factorization`) makes a *deterministic* choice but does not
make the factorization *unique*; an attacker runs the identical selector
and reaches the identical choice. Canonicalization gives determinism, not
secrecy.

The escape, if one exists, is not more factors but a different hardness:
hiding the composition *order* (so the attacker cannot assume left-to-
right), or moving the secret out of the factor-recovery problem entirely
(payload depth past catalogue-completeness, with its own attack tool yet
to be built). Both are open; neither is claimed.

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
and the frozen oracle catalogue. `attack_harness.py` wires the carrier
and pruning attacks; `positional_attack.py` wires the fixed-carrier
positional attack (which refuted Q1 v0). Expanding to the full quotient
and canonical-selection tools is the Phase-1 follow-on.

## hmmm

- The hardness assumption (Q6) is load-bearing and **unproved**; it is
  the same open problem as ucns cross-prime widening, now wearing a
  security hat. If that frontier closes, PCEA-UCNS must fall back to
  symmetric-only — which `contract.py` already ensures it can.
- Q1's conjecture (angle-position hides the key) is now **refuted** by
  `positional_attack.py`: fixing the carrier does not defeat
  factorization, and non-uniqueness means *any* recomposing pair breaks
  the scheme. The consequence is sharp — **there is no "easy" private-key
  location that dodges the frontier.** A UCNS-KEM is feasible *only* if
  cross-prime factoring is genuinely hard, and that is exactly the open
  problem. Phase 2 (`kem.py`) should not be built until that hardness has
  evidence beyond "currently open."
- The honest one-line status: PCEA-UCNS is blocked on a UCNS theorem that
  does not yet exist, and today's attacks confirm the block is real
  rather than a gap in design effort.
- Three-factor composition is the first candidate to interact with the
  attack non-trivially: ordered cross-products smear the private-factor
  boundary (first-split-clean 0/80), but recursive peeling still recovers
  the private factor ~45%. The smearing is the signal worth chasing —
  next probes: (a) does peel recovery fall as factor count grows past 3?
  (b) does hiding the composition order, not just the factors, raise the
  attacker's cost? (c) a quotient-based attack to confirm the result is
  not an artifact of factor_search's loop ordering.
