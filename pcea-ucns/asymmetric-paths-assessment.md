# Asymmetric UCNS: Paths Assessed After the Prefix-Read Break

**Status:** Research assessment. Records why the natural escape routes
from the prefix-read break (`feasibility-investigation.md` step 8) also
fail, and what that implies for the three forward options. No positive
security claim. Measurements from `pcea-ucns/` probes; reproduced against
The-Interdependency/ucns at the quotient + Law release.

---

## The pattern under all the failures

The prefix-read break works because UCNS `multiply` is **invertible by a
total, constructive quotient**. Every asymmetric construction tried
publishes a product of a secret with a known object — and that is exactly
a quotient problem, which UCNS solves by design. The quotient is the
universal solvent: the property that makes UCNS excellent for
factorization research is the property that makes it cryptographically
transparent.

## Escapes tested and refuted

- **Secret rotation** (publish a cyclic rotation of A⊠B to break angle-0
  anchoring): mean **1 attempt** to break — the unrotated prefix-read
  already succeeds, and re-normalization is O(L). Adds no hardness.
- **Lossy homomorphic invariant** (publish a cheap invariant that
  composes but hides angles): the only homomorphic invariants found are
  the carrier (leaked by the Law) and face-parity (200/200 homomorphic,
  but trivially public). No invariant is both homomorphic AND hard.
- **Diffie-Hellman style**: requires commutativity; UCNS `multiply` is
  **non-commutative (1/200)**. Ruled out structurally.
- **Non-commutative semigroup / conjugacy exchange** (the braid-group
  analogue, building ON non-commutativity): honest parties agree via
  associativity (60/60), but the attacker recovers the secret **60/60**
  via `right_quotient(a⊠w, w)`. Braid crypto survives on HARD conjugacy;
  UCNS has EASY quotient.

**Common cause:** every scheme exposes `secret ⊠ public` or
`public ⊠ secret`, and the quotient inverts both. A UCNS asymmetric
primitive would require a public projection that is NOT a recoverable
product of the secret — which forward composition cannot provide.

## The three forward options, assessed

### Option 1 — Pre-shared / out-of-band symmetric (RECOMMENDED for the a0 ecosystem)

PCEA symmetric is sound and shipping. For devices provisioned together —
the actual a0 deployment — a shared seed generated once with `os.urandom`
and never transmitted needs **no asymmetric primitive at all**. Fully
within the dependency covenant. Not a compromise: the correct tool when
parties share a provisioning moment. **This leaves the ecosystem with
working encryption today.**

### Option 2 — Hybrid: standard KEM keying PCEA (RECOMMENDED if cold-channel is required now)

The covenant forbids `cryptography`/PyNaCl/libsodium but allows
`hashlib`, `hmac`, `secrets`. A classical X25519/DH exchange in pure
stdlib `int` arithmetic establishes a shared secret over an open channel;
PCEA encrypts under it, unchanged. Costs: not UCNS-native, not
post-quantum. Gains: ships now on assumptions the world already trusts.
The asymmetric hardness lives in discrete-log, not UCNS — honest and
battle-tested.

### Option 3 — A genuinely new UCNS one-way map (RESEARCH, open)

Not closed in principle, but every composition-based route is now closed
in practice. A candidate must publish something that is NOT a recoverable
product — e.g. a one-way *hash-like* UCNS digest with a trapdoor, or a
hardness imported from a problem the quotient does not solve (a lattice
embedded in UCNS coordinates, say). This abandons "public key = a forward
UCNS product," which is the only construction family the break and this
assessment have actually tested. Months, may dead-end. The honest reason
to pursue it is the post-quantum + no-imported-trust vision, not
near-term need.

## Recommendation

For the a0 ecosystem now: **Option 1** (pre-shared symmetric). If
stranger-to-stranger over an open channel becomes a real requirement
before Option 3 bears fruit: **Option 2** (hybrid). Keep **Option 3** as
a standing research bet, now sharpened — the requirement is no longer
"make factoring hard" but "find a UCNS public map that is not a quotient
problem," which is a precise and probably hard target.

## hmmm

- The result is not "UCNS can't do crypto." It is "UCNS forward
  composition is a window, and you cannot build a vault out of windows."
  A vault would need a different UCNS operation — one not yet identified —
  whose inverse is not constructive. Whether such an operation exists
  inside UCNS's three primitives is genuinely open; nothing tested so far
  reaches it.
- Encryption is not lost. Public-key-WITHOUT-pre-sharing-OVER-UCNS is
  lost. Those are different sentences, and conflating them would be the
  one dishonest move available here.

---

## Addendum: the three primitives, tested individually

The escapes above all attacked epicyclic composition. UCNS has three
irreducible primitives — gonal inscription, Möbius topology (the face /
spinor double cover), and epicyclic composition. Each was probed for
quotient-invisible secret structure.

- **Epicyclic composition** — broken (prefix-read; the whole
  investigation).
- **Gonal inscription** (the carrier/lattice) — no hidden secret. The
  Law leaks the carrier; angle positions are pinned up to the ordinary
  factorization non-uniqueness, which enumeration resolves. Nothing here
  the quotient + enumeration does not reach.
- **Möbius topology** (the face/gauge structure) — **the one primitive
  with quotient-invisible structure**, and the spec predicted it (§ line
  508: factors are unique only within the canonical XOR gauge; recovery
  may differ by a constant XOR flip). Measured: prefix-read recovers a
  valid factor pair but the TRUE faces **0/80** — the face structure is
  genuinely not pinned by the public product.

  **But the gauge orbit is exactly 2 — a single global bit.** The freedom
  is "differ by a constant XOR flip," one bit, not per-cell entropy. Face
  combos recomposing the same product (same angles): mean **2.0, min 2,
  max 2**. The Möbius primitive hides exactly one bit from the quotient —
  real, the closest any primitive came, and far short of a key. An
  attacker enumerates both gauge representatives in one step.

## Revised verdict on the primitives

Quotient-invisibility exists in UCNS — in the Möbius face gauge — but its
entropy is one bit, fixed by the double-cover's two-sheet structure. It
resists the *quotient* and falls to *enumeration*, the same split that
sank the key-space regime. No primitive, alone or in the combinations
tested, yields a high-entropy quotient-invisible secret.

The sharpened research target (Option 3) becomes concrete: a UCNS
construction would need to **amplify the one-bit Möbius gauge into
per-cell or per-payload gauge freedom** — many independent bits the
quotient cannot pin — without that freedom collapsing back to a global
constant. Whether the recursive payload structure admits a *per-depth*
independent gauge is the one question these probes did not settle, and
the only place a high-entropy UCNS-native secret could still hide.

## hmmm (addendum)

- The Möbius seam carries exactly one bit because crossing it twice
  restores orientation — the double cover is, definitionally, a single
  bit of topology. To get more bits you need more seams: independent
  twist-points per payload depth. That is not obviously available and not
  obviously forbidden. It is the last unfalsified corner, and it is
  small.
- Honest scale: this is a one-bit result, not a cipher. It is reported
  because it is the only quotient-invisible structure found, and because
  naming exactly where the entropy is (and isn't) is what lets the
  research question be precise instead of hopeful.

---

## The general barrier (why a fourth or fifth primitive does not help)

Two further candidates were tested: **per-payload independent gauge
seams** and **radial growth as a fourth primitive**. Both fail, and the
second failure generalizes the first into a structural impossibility that
does not depend on which primitives UCNS has.

**Per-payload seams.** If each payload depth carried an independent
Möbius gauge bit, entropy would scale with depth. Measured: the depth-1
host-face orbit stays **2.0** — the double cover's bit propagates, it
does not multiply. The seams are the same seam seen at depth, not
independent twist-points. No entropy gain.

**Radial growth (4th primitive).** Add a radial coordinate r per cell —
the object on a spiral, not just the circle. Tested against the
publish/agree/invert trilemma:

- r propagated into P by an **invertible** rule (additive, multiplicative)
  → attacker inverts it; same one-DOF gauge trap as faces. Not secret.
- r propagated by a **one-way** rule → honest parties cannot agree on a
  shared value either; it is a KDF bolted onto UCNS, not UCNS arithmetic.
- r kept **free** (not in P) → no agreement channel; the parties have no
  way to converge on it without transmitting it, i.e. publishing it.

**The trilemma, stated generally:**

> Any value both parties can derive from a PUBLISHED UCNS product is, by
> definition, derivable FROM that product — so an adversary holding the
> product derives it too. A coordinate is either published (hence
> recoverable, the quotient being total) or free (hence un-shareable). No
> coordinate, and no number of coordinates, escapes this.

This is not a UCNS limitation; it is the defining requirement of
public-key exchange. Diffie–Hellman escapes the trilemma **only** because
exponentiation is one-way: the published `g^a` does not reveal `a`. UCNS
supplies no one-way operation — the quotient inverts every published
product — so adding primitives (radial, more seams, future ones) cannot
help unless one of them is **one-way**, and none of UCNS's operations is.

## Final terminus

A UCNS-native public-key primitive requires a UCNS operation whose
forward direction is computable and whose inverse is not — a trapdoor.
UCNS's three (and any naturally-composed fourth) primitives are all
constructively invertible; that invertibility is the source of the
factorization results UCNS exists for. **The same property that makes
UCNS a powerful factorization algebra makes it incapable of hiding a
trapdoor** — IF the published object is a structured product.

**Correction (see `projection_action_candidate.py`).** The clause above
is load-bearing and was too strong. The barrier assumed the public object
is a structured PRODUCT, which the quotient inverts. A *lossy projection*
— `action(s,g) = set-project(s ⊠ g)`, discarding order, multiplicity,
faces, payloads — is not a structured product, and the quotient inverts
it only 3/200. It is injective on secrets (collision factor 1.0×, exact
enumeration), so it has scalable entropy, yet it resists the quotient
because the projection destroys the cell structure inversion needs. This
is a candidate one-way UCNS action and the first counterexample to the
barrier. It is NOT a proven primitive — five concrete attacks remain unrun
(algebraic key-recovery, meet-in-the-middle, set-structure cryptanalysis,
active/malleability, honest-failure-at-scale). The honest revision: the
obstruction is real for product-based constructions and *defeated in
principle* by deliberate information loss, with security still unproven.
