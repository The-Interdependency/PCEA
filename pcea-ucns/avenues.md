# Potential Avenues for UCNS-Assisted PCEA Without External Dependencies

**Status:** research agenda for the proving ground. This file lists avenues to
try, the reason each might help, the known reason it might fail, and the first
harness that should be built before anyone treats the avenue as progress.

**Boundary:** PCEA's current shipped value is the symmetric, state-synchronized
transform in `pcea/`. The avenues below are for key establishment, identity,
state communication, or authentication around that transform while preserving
this dependency rule: Python standard library plus The Interdependency-owned
repositories only.

|∆|None of these avenues is a security claim.|∆| The preferred proving-ground
outcome is still a clean refutation with a reproducible harness. A surviving
candidate earns a harder attack, not trust.

## Current constraints to respect

1. **No external runtime cryptography package.** `hashlib`, `hmac`, `secrets`,
   and `os.urandom` are acceptable standard-library tools; `cryptography`,
   PyNaCl, libsodium wrappers, OpenSSL wrappers, and network services are not.
2. **PCEA runtime must not depend on UCNS inverse/catalogue APIs.** UCNS attack
   tooling belongs in this proving ground unless the PCEA↔UCNS contract is
   deliberately changed and reviewed.
3. **Published UCNS products are dangerous.** Existing harnesses found carrier
   leakage, oracle-domain factor recovery, positional recovery, prefix-read
   reconstruction, and Minkowski set-basis inversion in candidate families.
4. **Authentication is not optional.** A future channel needs integrity,
   transcript binding, replay discipline, and key separation; encryption-only
   transforms are insufficient for production communication.

## Avenue 1 — Provisioned symmetric channel first

**Idea:** Treat the no-dependency problem as a deployment problem: provision two
`a0` instances with a shared secret/seed out of band, then use PCEA as the
state transform plus standard-library `hmac`/`hashlib` for transcript-bound
message authentication and key separation.

**Why it may help:** It avoids the broken UCNS-native asymmetric line entirely
and can work today for devices or agents that are paired before deployment.

**Known weakness:** It does not solve cold-start public-key encryption. It moves
trust to provisioning, backup, rotation, and revocation.

**First proving-ground task:** Write a channel sketch that derives independent
keys for encryption-state advancement, authentication, replay counters, and
rekeying from one provisioned seed. Add tests for wrong-key failure, transcript
binding, replay rejection, and ratchet desynchronization recovery.

**Go/no-go gate:** Accept only as a pre-shared-key mode. Do not describe it as
UCNS public-key encryption.

## Avenue 2 — Hybrid standard KEM as an explicit exception path

**Idea:** Keep PCEA as the payload/state transform, but use a reviewed standard
KEM or Diffie-Hellman implementation to establish the initial shared secret.
The dependency covenant would have to decide whether this can be an
Interdependency-owned implementation, a vendored audited file, or an explicit
external exception.

**Why it may help:** It gives a realistic cold-start channel while the native
UCNS hard problem remains blocked or open.

**Known weakness:** Implementing standard cryptography in-repo is high-risk;
using an external package violates the strict no-external-runtime-dependency
rule unless the policy changes.

**First proving-ground task:** Write a decision record, not code: dependency
exception versus org-owned implementation versus no hybrid path. If code is
ever attempted, require independent test vectors, negative tests, and review
before connecting it to PCEA.

**Go/no-go gate:** Do not ship homegrown standard crypto merely because it is
zero-dependency. A zero-dependency bug is still a bug.

## Avenue 3 — UCNS as identity and transcript structure, not hardness

**Idea:** Use UCNS objects to name agents, sessions, capabilities, and message
contexts, but do not ask UCNS factorization to hide the secret. Secrets come
from provisioned entropy or a separately approved KEM; UCNS contributes
canonical context that is hashed into keys and MAC transcripts.

**Why it may help:** It preserves UCNS semantics and Interdependency ownership
without resting security on a broken or unproven UCNS one-way function.

**Known weakness:** This is not UCNS-native public-key encryption. It is a
structured key schedule and identity layer.

**First proving-ground task:** Define canonical UCNS transcript serialization
and test that changing any identity/session/capability field changes derived
keys and tags. Add collision/canonicalization tests for equivalent UCNS forms.

**Go/no-go gate:** Ship only if documentation says UCNS is context binding, not
the source of secrecy.

## Avenue 4 — Search for a UCNS one-way map outside published products

**Idea:** Stop publishing `A ⊠ B`-style products that expose prefix blocks or
Minkowski sums. Look for a UCNS-derived public map whose image is lossy in a way
that is not inverted by quotient, prefix-read reconstruction, set-basis
recovery, or catalogue search.

**Why it may help:** The breaks so far are often attacks on product structure,
normalization, or additive angle sets. A non-product public map may avoid those
specific readouts.

**Known weakness:** The lossy set-projection attempt already failed by
Minkowski set-basis recovery. A new map must beat more than one inverse.

**First proving-ground task:** For every candidate map `public = F(secret,
base)`, write four attacks before writing happy-path code:

1. quotient/left-right division where applicable;
2. prefix or normalization readout;
3. angle-set difference / Minkowski basis recovery;
4. finite key-space enumeration with pruning.

**Go/no-go gate:** A candidate must survive all four at toy scale before it is
worth scaling. Survival at toy scale is still only permission to attack harder.

## Avenue 5 — Hide composition order rather than factor values

**Idea:** The existing product attacks assume or exploit ordered structure.
Investigate whether a secret permutation/schedule of UCNS operations can make
public reconstruction ambiguous to the attacker but reproducible to honest
parties that share a small seed.

**Why it may help:** It targets the structural readout layer rather than just
making factors larger.

**Known weakness:** If honest parties need the schedule as a shared secret, the
problem reduces to pre-shared symmetric state. If the schedule is recoverable
from the public object, the avenue collapses back to existing attacks.

**First proving-ground task:** Build a toy shuffled-composition harness and
measure whether prefix-read and quotient attacks recover an equivalent schedule
or enough factors to derive the same shared secret.

**Go/no-go gate:** Success requires that honest parties derive the same secret
while an attacker with all public material cannot derive an equivalent one. Mere
non-uniqueness is not enough.

## Avenue 6 — Payload-depth domains with new payload attacks

**Idea:** Move candidate secret material into nested payload structure beyond
the currently catalogue-complete domains, then define a KDF over the recovered
payload only honest parties should obtain.

**Why it may help:** It explores a space where existing shallow catalogues may
not be complete.

**Known weakness:** Prefix-read reconstruction already survived depth-1 nesting
in the documented break line. Depth alone is not a defense unless the payload
changes what reconstruction returns.

**First proving-ground task:** Create a depth-scaling harness that measures
prefix-read, quotient, and payload-canonicalization recovery across increasing
depth and payload width.

**Go/no-go gate:** Reject if attack cost is flat or near-linear in public object
size rather than in secret entropy.

## Avenue 7 — Full-state gonal bridge for state communication

**Idea:** Continue the PCEA-advanced gonal line, but treat it as a private
state/message encoding layer for already-synchronized parties, not as public-key
key establishment. The immediate problem is the 53→32 or wider gonal bridge:
map PCEA state to gonal rotation without scalarizing away entropy.

**Why it may help:** Existing gonal tests show static gonals fail and
PCEA-advanced gonals resist simple frequency/known-plaintext probes in the
current harness. The natural next work is to harden the bridge and attack it.

**Known weakness:** The module already records unresolved gates. A weak bridge
can recreate a Vigenere-like repeated-alphabet failure even if PCEA itself is
not the failing piece.

**First proving-ground task:** Specify candidate bridge functions, then test
chosen-plaintext, keystream/state recovery, bridge-collision rate, reuse groups,
and legitimate recovery over long runs.

**Go/no-go gate:** Do not create `gonal_cipher.py` until bridge attacks are
explicitly green at the chosen parameter sizes.

## Avenue 8 — UCNS commitments plus delayed disclosure

**Idea:** Use UCNS public objects as commitments to future state rather than as
public keys. Parties that already share a secret can commit to future rotations,
capabilities, or transcript checkpoints, then reveal or prove consistency later.

**Why it may help:** Commitments may use UCNS structure without asking it to be
a trapdoor one-way function for unknown peers.

**Known weakness:** A commitment scheme still needs binding and hiding proofs or
measurements. If the committed value is low entropy, brute force wins.

**First proving-ground task:** Define a commit/open transcript using
standard-library hashing plus UCNS canonical serialization. Test binding under
canonical-equivalent objects and hiding against low-entropy brute force.

**Go/no-go gate:** Use only for transcript discipline unless the hiding/binding
properties are stated and tested at realistic entropy.

## Avenue 9 — Ratcheted PCEA sessions with resynchronization packets

**Idea:** Improve the operational channel around pre-shared or KEM-derived
secrets: ratchet `last_state`, derive per-message subkeys, authenticate each
message, and include bounded resynchronization packets that do not reveal the
plaintext state.

**Why it may help:** Even if UCNS-native public-key work remains blocked, this
makes the usable PCEA mode safer and testable.

**Known weakness:** Resynchronization metadata can leak state position or become
a replay oracle if not authenticated and transcript-bound.

**First proving-ground task:** Build a non-runtime prototype with message
numbers, associated data, MAC tags, rekey intervals, and failed-decrypt state
rollback. Attack replay, truncation, reordering, and wrong-peer transcripts.

**Go/no-go gate:** No unauthenticated state advancement. Decrypt failure must
not corrupt the receiver's `last_state`.

## Avenue 10 — Machine-readable candidate ledger

**Idea:** Add a small ledger for candidate status: `candidate`, `claim`,
`public_material`, `private_material`, `known_attacks`, `harness`, `test`,
`status`, and `next_attack`.

**Why it may help:** The proving ground already contains many negative and
partial results. A ledger prevents old refuted ideas from reappearing under new
names and makes the next useful harness obvious.

**Known weakness:** A ledger is process, not cryptography.

**First proving-ground task:** Start with the existing lanes from
`pcea-ucns/README.md`, then add one entry per future candidate PR.

**Go/no-go gate:** No new UCNS encryption claim without a ledger entry and a
pytest-backed attack result.

## Suggested next order of work

1. **Near-term useful:** Avenue 9, ratcheted authenticated PCEA sessions, because
   it improves the currently usable symmetric path.
2. **Near-term clarifying:** Avenue 10, the candidate ledger, because it keeps
   the proving ground honest.
3. **Research next:** Avenue 7, full-state gonal bridge, because there is already
   a harness and a named unresolved gate.
4. **High-risk research:** Avenue 4 or 5, new UCNS-native one-way maps or hidden
   composition order, because this is where a no-external-dependency native KEM
   would have to come from.
5. **Policy decision:** Avenue 2, hybrid KEM exception, because it is the most
   realistic cold-start path if native UCNS hardness remains blocked.

## Required evidence before any avenue graduates

- A clear statement of private material, public material, and derived secret.
- A deterministic harness with recorded seeds and parameters.
- A pytest gate that fails when the measured property drifts.
- A negative-test set for wrong keys, replay, transcript changes, and malformed
  public objects.
- A document update that says **break**, **partial survival**, or **open gate**.
- Independent cryptographic review before production use.
