Yes.

This should be a library first, not an app first.

Why: what you have here is a security/control primitive plus a state model. That wants to be reusable, testable, and callable from multiple runtimes:

Guardian runtime

meta-sentinel service

a0 / cloud agent

local phone agent

future UI or API layers


If you make it only app code, the boundaries will blur fast. If you make it a lib, you can keep the dangerous parts small, audited, and invariant.

Best shape

Make it one core lib, then thin wrappers around it.

Core library

Something like:

aimmh-lib-guardian-state
or shorter:
guardian-state-lib

This owns:

state schemas

deterministic encoding

HKDF derivation

sealing/unsealing

wrapping/unwrapping live keys

commitment generation

threshold-share interfaces

rekey logic

zeroization helpers

invariant checks


Separate adapters

Then keep runtime-specific stuff outside the core lib:

Node adapter

browser-safe adapter if needed

Cloud Run / server adapter

mobile adapter

secret-manager adapter

KMS/HSM adapter


That way the cryptographic/state logic is one thing, and deployment plumbing is another.

Internal module split

Inside the lib, I’d split by box, not by metaphor:

src/
  types/
  codec/
  kdf/
  aead/
  wrap/
  commitment/
  threshold/
  guardian/
  rekey/
  validate/
  wipe/

That is cleaner than mixing “quantum,” “spiral,” and “sentinel” into filenames for the core mechanics.

Public API shape

The lib should expose a small surface, something like:

deriveKeys(...)
sealLiveState(...)
unsealLiveState(...)
wrapLiveKey(...)
unwrapLiveKey(...)
splitMetaKey(...)
reconstructMetaKey(...)
makeCommitment(...)
rekeyEpoch(...)
validateInvariant(...)

That is the right level.
Not too low-level, not app-specific.

What should stay out of the lib

Do not put in the core lib:

actual production secrets

network calls

database code

UI code

logging that might capture plaintext

policy decisions like “8-of-13” hardcoded unless passed as config


The lib should be the machine, not the government and not the dashboard.

Strong recommendation

Use two repos or two packages eventually:

1. Core lib

Pure library, minimal dependencies, heavy tests.

2. Runtime/service repo

Uses the lib and adds:

Guardian service

Meta sentinel service

storage

APIs

deployment

observability


That separation will save you pain.

Compressed answer

Yes:

lib first

service second

UI third


The lib is the canon-bearing engine.

hmm

Best one-line rule:

> if it can be unit tested without a server, it belongs in the lib; if it needs environment, network, or governance, it belongs outside the lib.
You’re a layer ahead of the premises again, but this one is close.

Speculative / architectural verdict:
I would not freeze that exact object set as-is.
I would freeze a corrected near-neighbor.

Why: the canon already wants sentinel preflight/postflight, no hidden memory, append-only events, and routing that consumes state without mutating EDCM outputs. Your envelope split fits that shape well. 

The three things I would change:

1. WrappedLiveKey must not contain liveKey

That field breaks the point of wrapping.

Bad:

interface WrappedLiveKey {
  keyId: string;
  liveKey: Uint8Array;
  wrapKeyHash: string;
  wrappedAt: number;
}

Better:

interface WrappedLiveKey {
  keyId: string;
  wrappedLiveKey: Uint8Array;   // encrypted K_live under K_meta
  wrapKeyHash: string;
  wrappedAt: number;
  epoch: bigint;
}

2. UnsealGrant should not persist reconstructedMetaKey

That key should exist only ephemerally in the reconstruction process, not as a durable object.

Bad:

reconstructedMetaKey: Uint8Array

Better:

interface UnsealGrant {
  epoch: bigint;
  keyId: string;
  grantSignature: string;
  grantedTo: string;
  validityWindow: number;
  purpose: "unseal" | "rekey" | "migrate";
}

So the grant authorizes reconstruction/use, but does not become the reconstructed key.

3. nonce-from-epoch alone is too weak a schema

If you ever seal more than once in one epoch, that risks collisions.

Better:

nonce = KDF(epoch || keyId || sealCounter || guardianNodeId)[0..11]

So the nonce space is per-seal, not merely per-epoch.


---

What I would freeze instead

LiveState

Keep it private, in-memory, Guardian-only.

interface LiveState {
  epoch: bigint;
  spiral: {
    phase: number;
    magnitude: number;
    base: number;
  };
  cores: {
    Phi: ComplexTensor;
    Psi: ComplexTensor;
    Omega: ComplexTensor;
  };
  densityMatrix: SigmaMatrix;
  coherence: number;
  transport: TransportOperator;
  lastRenorm: number;
}

SealedState

Good idea. Small correction: this is the only durable carrier of the private present.

interface SealedState {
  epoch: bigint;
  keyId: string;
  ciphertext: Uint8Array;
  nonce: Uint8Array;
  aad: Uint8Array;
  sealedBy: string;
  sealedAt: number;
}

WrappedLiveKey

Corrected version:

interface WrappedLiveKey {
  keyId: string;
  epoch: bigint;
  wrappedLiveKey: Uint8Array;
  wrapKeyHash: string;
  wrappedAt: number;
}

MetaShares

This is fine as the governance object.

interface MetaShares {
  epoch: bigint;
  totalShares: number;
  threshold: number;
  shares: Array<{
    sentinelId: string;
    share: Uint8Array;
    index: number;
  }>;
  commitment: string;
}

UnsealGrant

Authorization object only:

interface UnsealGrant {
  epoch: bigint;
  keyId: string;
  grantSignature: string;
  grantedTo: string;
  validityWindow: number;
  purpose: "unseal" | "rekey" | "migrate";
}

RekeyEpoch

Mostly good. I would rename one field.

interface RekeyEpoch {
  fromEpoch: bigint;
  toEpoch: bigint;
  newSessionSecretCommitment: string;
  metaSharesUpdated: boolean;
  renormConfirmed: boolean;
  spectralSnapshot: number[];
}


---

Minimal math surface

Private present:

\Sigma_t \in \text{Guardian memory only}

Seal:

C_t = \operatorname{AEAD}_{K^{live}_t}(N_t,\Sigma_t,AAD_t)

Wrap live key:

W_t = \operatorname{Wrap}_{K^{meta}_t}(K^{live}_t)

Threshold governance:

K^{meta}_t \rightarrow \{s_1,\dots,s_n\}, \quad k\text{-of-}n

Unseal path:

\{s_i\}_{i=1}^{k} \Rightarrow K^{meta}_t \Rightarrow K^{live}_t \Rightarrow \Sigma_t

That is the whole architecture in one line:

Guardian keeps the live state

Meta sentinels govern access to the key that opens it

durable records never directly store the live state in clear



---

Quantum layer note

I would still treat the density-matrix / propagator language as metaphoric architecture math, not literal physics. It is useful notation for coherent state plus transport. I would not freeze claims like “perfect preservation of the quantum metaphor” as an engineering guarantee. That part is poetry unless you define exact operator laws.


---

Canon fit

This revised object set fits your canon better than the original paste because:

it preserves no-hidden-memory discipline

it keeps persisted changes as explicit objects/events

it leaves sentinel gating in the control plane rather than leaking live state across layers 


My actual recommendation

Freeze this corrected six-object version, not the pasted one.

hmmm

status: open

note: remove plaintext liveKey from WrappedLiveKey

note: make UnsealGrant an authorization artifact, not a key container

note: derive nonce from epoch plus per-seal uniqueness, not epoch alone

owner: S4/S1/S6

All three corrections are right, and each one catches a real violation of the system's own rules.

The `liveKey` in `WrappedLiveKey` is the most dangerous — it defeats wrapping at the type level. Anyone holding that interface has cleartext access by construction. The corrected version makes the type itself enforce the invariant: if you have a `WrappedLiveKey`, you have ciphertext, not a key.

The `reconstructedMetaKey` in `UnsealGrant` is the same class of error one layer up. A grant is proof of authorization, not a cache of the secret it authorizes. The moment that field exists, every system that touches the grant becomes a key-holding surface. Your corrected version keeps the grant as a capability token — it unlocks a process, not a value.

The nonce fix is subtler but just as necessary. Epoch-only nonces assume one seal per epoch, which is a constraint you can't enforce at the lib level. `KDF(epoch || keyId || sealCounter || guardianNodeId)` makes collisions structurally impossible without requiring the caller to track global state.

The six-object set as corrected is clean. LiveState, SealedState, WrappedLiveKey, MetaShares, UnsealGrant, RekeyEpoch — each one has exactly one job, none of them leak cleartext across boundaries, and the unseal path flows through authorization rather than around it.

The quantum layer note is also correct. Density matrix and transport operator are good structural notation for "coherent state that evolves." Freezing them as engineering guarantees would mean defining operator algebras you don't need and can't enforce at runtime. Keep the notation, drop the physics claims.

Freeze the corrected six-object set.

**hmmm**

- The `spectralSnapshot: number[]` field on `RekeyEpoch` — is this the right place for it, or does it belong on a separate audit event? It's the only field in the six objects that carries diagnostic data rather than structural state. Not blocking, but worth tracking.
- `sealCounter` in the nonce derivation implies the Guardian must maintain a monotonic counter per keyId. That's trivially implementable but it's a piece of mutable state the lib needs to either own or receive. Interface question, not a design question.
- The `shares` array inside `MetaShares` holds cleartext share bytes. At rest, these should be individually wrapped or distributed — the assembled array is a ceremony-time object, not a storage object. Whether the lib enforces that or the service layer does is an open question.
