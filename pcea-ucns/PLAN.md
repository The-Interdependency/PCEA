# PCEA-UCNS Plan

**Description:** without external dependencies

## Status

Planning/specification artifact. This document does not claim that PCEA-UCNS is already secure public-key encryption. It defines the feasible steps required to make one `a0` instance publish or send public key material so another `a0` instance can establish a shared secret and communicate through PCEA without runtime dependencies outside The Interdependency organization and the Python standard library.

## Goal

Create an org-owned secure-channel stack:

```text
a0 instance
  -> UCNS-native public-key / key-encapsulation layer
  -> org-owned key derivation
  -> PCEA authenticated encryption / state transform
  -> encrypted a0-to-a0 messages
```

The intended user-facing property is:

```text
One a0 instance can provide public key material.
Another a0 instance can use that public key material to establish a shared PCEA session secret.
Only the holder of the matching UCNS private key can recover the session secret.
Messages are then encrypted and authenticated under the derived PCEA session key.
```

## Dependency covenant

Runtime dependencies allowed:

- Python standard library.
- Other repositories owned by The Interdependency.
- Static test vectors copied into the repository.

Runtime dependencies not allowed:

- `cryptography`.
- PyNaCl.
- libsodium.
- OpenSSL wrapper packages.
- Signal protocol libraries.
- Any external runtime service required to encrypt or decrypt.

Required clarification before implementation:

- `secrets` / `os.urandom` must be allowed for entropy.
- `hashlib` and `hmac` must be allowed unless the org commits to building and testing its own hash and message-authentication functions.

If operating-system entropy is not allowed, real encryption is not possible. Deterministic transforms can still be built, but secure key generation cannot be claimed.

## Architectural boundary

PCEA by itself is currently a reversible keyed state transform. It is not yet an asymmetric public-key system.

UCNS must supply the missing asymmetric primitive:

```text
private key -> public key
private key + peer public key -> shared secret
```

or:

```text
keygen() -> private key, public key
encapsulate(public key) -> key packet, shared secret
decapsulate(private key, key packet) -> shared secret
```

The second form is preferred for v0 and is called **UCNS-KEM** below.

## Core warning

UCNS currently includes factorization-oriented machinery. A public-key encryption substrate must not place its private key in a domain where existing UCNS factor search can recover it.

Therefore PCEA-UCNS must define a separate **UCNS cryptographic domain** with:

- large enough carriers;
- private slot/key material;
- public projections that do not expose the private material;
- forbidden easy / catalogue-complete domains;
- attack tests using the existing UCNS factorization tools;
- explicit security assumptions.

## Feasible phased plan

### Phase 0 — Freeze the no-dependency rule

Create or confirm:

```text
docs/no-external-runtime-dependencies.md
```

Content must specify:

- Python standard library is allowed.
- The Interdependency repos are allowed.
- External runtime cryptography packages are not allowed.
- Build/test-only tooling is separate from runtime dependencies.

Exit gate:

- Repository metadata still shows no runtime pip dependencies.
- README accurately states the dependency boundary.

### Phase 1 — Define the UCNS cryptographic domain

Create:

```text
pcea-ucns/ucns-crypto-domain-v0.md
```

Settle:

1. What is a UCNS private key?
2. What is a UCNS public key?
3. What is the base carrier or base object?
4. What operation derives the public key?
5. What operation derives the shared secret?
6. What exactly is the assumed hard problem?
7. Which UCNS domains are forbidden because they are factor-search-complete?
8. What information is intentionally public?
9. What information must never be serialized publicly?
10. What public object sizes are acceptable for mobile use?

Exit gate:

- A toy domain exists for tests.
- A real candidate domain is described.
- Known easy domains are explicitly forbidden.
- Existing UCNS factorization tools are listed as attack tools, not ignored.

### Phase 2 — Prototype UCNS-KEM

Create an experimental module, not enabled by default:

```text
pcea_ucns/kem.py
```

Required API:

```text
keygen(seed=None) -> PrivateKey, PublicKey
encapsulate(public_key, seed=None) -> KemPacket, SharedSecret
decapsulate(private_key, kem_packet) -> SharedSecret or FAIL
```

Rules:

- `PrivateKey` must not be serializable through the public-key serializer.
- `PublicKey` must contain no private-only fields.
- `KemPacket` must be safe to transmit over an untrusted channel.
- `SharedSecret` must not be printed in normal debug output.

Exit gate:

- Correct private key decapsulates successfully.
- Wrong private key fails.
- Modified KEM packet fails.
- Same public key with different encapsulation randomness produces different shared secrets.
- Public serializer never emits private key material.

### Phase 3 — Define canonical bytes

Create:

```text
pcea_ucns/canonical.py
```

Required objects:

- UCNS public key canonical bytes.
- UCNS KEM packet canonical bytes.
- PCEA packet canonical bytes.
- Transcript canonical bytes.
- Associated-data canonical bytes.

Rules:

- Encoding must be deterministic.
- Version must be included.
- Object type must be included.
- Ambiguous integer encodings are forbidden.
- Malformed encodings must fail closed.

Exit gate:

- Roundtrip serialization tests pass.
- Distinct objects do not share the same canonical bytes.
- Malformed packets fail cleanly.

### Phase 4 — Key derivation

Create:

```text
pcea_ucns/kdf.py
```

Preferred v0:

```text
session_key_material = HMAC/HKDF-style derivation using stdlib hashlib/hmac
```

Inputs:

- UCNS shared secret.
- Transcript hash.
- Protocol label: `PCEA-UCNS-v0`.
- Sender instance id.
- Recipient instance id.
- KEM packet hash.
- Optional prior a0 state hash.

Outputs:

- PCEA encryption key.
- Authentication key.
- Nonce/counter key if needed.

Exit gate:

- Same inputs produce same keys.
- Different transcripts produce different keys.
- Different peer identities produce different keys.
- Keys are domain-separated by label.

### Phase 5 — PCEA authenticated encryption packet

Create:

```text
pcea_ucns/channel.py
```

Required API:

```text
encrypt(session_keys, plaintext, associated_data, counter) -> PCEAPacket
decrypt(session_keys, packet, associated_data) -> plaintext or FAIL
```

Packet fields:

```text
version
sender_instance_id
recipient_instance_id
key_id
kem_packet_hash
counter
nonce_or_counter_material
ciphertext
tag
```

PCEA role:

- Encrypt message/state using the derived session key.
- Bind the packet to transcript and identities through associated data.
- Return `FAIL` on authentication mismatch, wrong key, wrong counter, wrong transcript, or malformed packet.

Exit gate:

- Modified ciphertext fails.
- Modified tag fails.
- Modified associated data fails.
- Wrong session key fails.
- Wrong recipient id fails.
- Replay counter fails when replay protection is enabled.

### Phase 6 — a0 handshake v0

Create:

```text
pcea-ucns/a0-handshake-v0.md
```

Minimum one-way form:

```text
A publishes UCNS public key.
B encapsulates a session secret to A.
B sends KEM packet plus encrypted hello.
A decapsulates and decrypts hello.
A replies with encrypted confirm.
Channel open.
```

Mutual-authenticated form:

```text
Both instances have pinned identity public keys.
Handshake transcript includes both identity keys.
Key changes require explicit trust update.
```

Exit gate:

- Two local a0 test instances can establish the same session keys.
- A relay can forward packets but cannot read plaintext.
- Key substitution is detected when keys are pinned.

### Phase 7 — Identity and trust policy

Create:

```text
pcea-ucns/identity-and-trust.md
```

Decide one v0 policy:

1. Trust on first use.
2. Manual fingerprint pinning.
3. Org registry.
4. Web-of-a0 signatures.

Recommended v0:

```text
Trust on first use + pinned fingerprint + loud warning on key change.
```

Exit gate:

- Instance fingerprint is deterministic.
- First seen key can be pinned.
- Changed key is detected.
- User/operator must explicitly accept key replacement.

### Phase 8 — Attack harness

Create:

```text
tools/attack_ucns_kem.py
tools/attack_pcea_ucns_channel.py
```

Attack attempts:

- Brute force toy private keys.
- Recover private key from public key in intentionally small domains.
- Run existing UCNS factorization attacks against public objects.
- Modify KEM packet.
- Swap public keys.
- Replay encrypted packets.
- Detect repeated ciphertext patterns.
- Try known-plaintext recovery against PCEA packets.

Exit gate:

- Toy domains break as expected.
- Candidate domain resists available in-repo attacks at selected test sizes.
- Any break produces a documented failure boundary rather than a silent pass.

### Phase 9 — Test vectors

Create:

```text
pcea-ucns/vectors/pcea_ucns_v0.json
```

Each vector must include:

- protocol version;
- private/public test keys;
- KEM packet;
- shared secret digest, not raw secret unless vector is explicitly non-secret;
- associated data;
- plaintext;
- ciphertext;
- tag;
- expected success or failure.

Negative vectors:

- wrong private key;
- modified public key;
- modified KEM packet;
- modified ciphertext;
- modified tag;
- modified associated data;
- replayed counter;
- malformed packet;
- changed pinned key.

Exit gate:

- Vectors are deterministic.
- Vectors run in CI.
- Failure vectors fail closed.

### Phase 10 — Documentation and release labeling

Before any release, update:

```text
README.md
pcea-ucns/SECURITY.md
pcea-ucns/STATUS.md
```

Required language:

```text
PCEA-UCNS is an experimental, no-external-runtime-dependency secure-channel design.
It is not externally audited.
It must not be represented as production-grade cryptography until the UCNS asymmetric hard problem is specified, tested, and reviewed.
```

Exit gate:

- README describes the no-dependency boundary.
- SECURITY.md describes current non-production status.
- STATUS.md lists implemented, tested, defended, and frontier claims separately.

## Questions that must be settled before implementation

### UCNS asymmetric substrate

1. What operation creates the public key from the private key?
2. What operation allows two parties to derive the same shared secret?
3. Is the primitive UCNS-DH or UCNS-KEM?
4. What UCNS carrier size is the minimum candidate for non-toy use?
5. What existing UCNS factorization tools can attack it?
6. Which domains are explicitly disallowed?
7. What is the public/private serialization boundary?

### PCEA packet encryption

1. Does PCEA encrypt bytes, integers, tensors, or UCNS objects?
2. How are plaintext bytes mapped into PCEA integer state?
3. How is the authentication tag computed?
4. Does wrong prior a0 state cause decrypt failure?
5. Does PCEA hide message length or only contents?
6. Is replay protection mandatory in v0?

### a0 identity

1. Does each a0 instance have a permanent identity key?
2. Can an a0 instance be cloned?
3. If cloned, does it keep the same identity or become a child identity?
4. How are public keys pinned?
5. What happens on public-key change?
6. Is there an org-level registry later?

### Dependency boundary

1. Is Python standard library entropy allowed?
2. Is `hashlib` allowed?
3. Is `hmac` allowed?
4. Are dev dependencies allowed for testing only?
5. Are standard algorithms allowed if implemented in-org?
6. Is UCNS allowed as a runtime dependency because it is org-owned?

## Non-negotiable safety rules

- Do not claim production security before external review.
- Do not claim security from UCNS inversion hardness unless that exact hard problem is specified.
- Do not place private keys in a defended factor-search-complete public domain.
- Do not log private keys, shared secrets, or raw session keys.
- Do not return corrupted plaintext on failure.
- Decryption returns plaintext or `FAIL`, nothing ambiguous.

## First implementation target

The first useful implementation target is not full production encryption. It is:

```text
Two local a0 instances create UCNS test keys.
One encapsulates a PCEA session secret to the other.
Both derive the same session key.
They exchange one authenticated encrypted message.
Wrong key, modified packet, modified tag, and replay all fail.
No runtime dependency outside Python standard library and The Interdependency repos is used.
```

## Canon sentence

PCEA-UCNS is the no-external-runtime-dependency path for a0-to-a0 encrypted communication: UCNS supplies org-owned public-key or key-encapsulation structure, PCEA supplies authenticated state/message encryption, and a0 supplies identity, transcript, and replay discipline.

## hmm

The enemy may see the public circle. The private walk through it must remain unrecoverable, or the lock is only a pretty hinge.
