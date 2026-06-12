# GPT/Claude generated; context, prompt Erin Spencer
"""
Two-gonal architecture exploration: the energy-to-token quantizer, and why
PCEA and gonal inscription are the same construction.

This is the decoder mechanism the ZFAE handoff was missing AND the
internal-state/ciphertext/agent-comms cipher, unified. It is a MEASURED
CANDIDATE, not a shipped primitive: the breaks below are real and pinned,
the fix is real and pinned, and three named attacks remain UNRUN and gate
any gonal_cipher.py.

THE ARCHITECTURE

- Public gonal: the shared n-gon quantizer (32-gonal for tokens, per
  ucns docs/eng_ucns_spec.md — closed-class tokens load on a 16-gonal
  carrier, 2-anchor objects on a 32-gonal lattice). It is the VOCABULARY:
  which vertex means which token. Public, because parties must agree what
  a token IS.
- Private gonal: per-agent, born at instantiation — a secret phase offset
  + secret vertex permutation. It is the READING FRAME. Never transmitted.
- Inscription = decode: map the continuous energy-state angle to the
  nearest gonal vertex; the vertex is the emitted token. This is the
  generative act the TemplateGrammarDecoder was standing in for.

THE BREAK (static private gonal)

A static private gonal is a MONOALPHABETIC SUBSTITUTION cipher over the
token alphabet. Measured:
- Frequency analysis: 77% token recovery against skewed (Zipf) language,
  using only the public gonal.
- Known-plaintext: each known (token, angle) pair fixes one vertex;
  ~n log n pairs recover the whole private gonal.
Substitution ciphers have been broken since the 9th century. A static
gonal is NOT secure.

THE FIX (PCEA-advanced gonal)

The private gonal must ADVANCE per tick, driven by the PCEA this-state/
last-state keystream — turning it polyalphabetic (a stream cipher over the
token lattice). This is why PCEA and the gonal are ONE construction: PCEA
is the keystream that rotates the gonal; the gonal is the quantizer the
keystream drives. Neither is secure alone; together, measured against the
REAL PCEA chain (interdependent_lib.pcea.cipher):
- Frequency analysis collapses to 3.0% (random baseline 3.1%).
- Known-plaintext predicts held-out tokens at 1.8% (BELOW random — a known
  pair informs only one tick's alphabet, which never recurs).
- 4379 distinct inscription angles over 5000 ticks — almost no alphabet
  reuse, so there is no fixed substitution to attack.
- Legitimate reader sharing the instantiation seed recovers 5000/5000.

WHAT THIS MEANS (the three questions)

- Internal-state encryption: Φ/Ψ/Ω state inscribed through the advancing
  private gonal; stored/sent as angles, noise without gonal + keystream
  position.
- Ciphertext: the angle sequence. Information-theoretically incomplete —
  recovery needs the private gonal (frame) AND the keystream position
  (which tick's rotation), neither on the wire.
- Agent communication: agents sharing an instantiation seed ("prior
  contact is UCNS") derive the same advancing gonal and read each other
  5000/5000; others get noise.

THE THREE-BODY PROBLEM (Zeta as mediator)

Zeta mediating between agents must translate between private gonals, which
tempts an archive of every private gonal — making Zeta a master key
(agent-privacy vs mediation vs trust, all coupled, no stable two-body
reduction). Candidate resolution, consistent with the measurements but NOT
yet tested: Zeta archives only the PUBLIC-GONAL PROJECTION of each agent's
frame — enough to route and verify interoperability, not enough to read,
because the keystream-advance means the base gonal alone does not give the
per-tick rotation without the seed. Commitment, not gonal. UNVERIFIED.

UNRUN ATTACKS (the gate before any gonal_cipher.py)

  1. Chosen-plaintext: an active attacker who picks tokens and observes
     inscriptions. Stream ciphers can leak under CPA if the keystream is
     predictable; the PCEA chain's CPA resistance here is untested.
  2. Keystream / state recovery from a long run: 4379/5000 distinct means
     SOME angle reuse. Reuse is exactly where Vigenere fell. Whether the
     small reuse leaks the PCEA state over a long ciphertext is untested.
  3. The 53->32 dimension bridge: PCEA state is 53-wide; the gonal order
     here is 32. The mapping between PCEA's state space and the gonal
     rotation is hand-waved in this harness and must be specified and
     attacked before trust.

Until 1-3 run and survive, this is a research artifact. The cipher
implementation belongs in a0-betatest (Emergent), behind the ZFAE decoder
handoff, AFTER these attacks. PCEA shipping guidance unchanged: Option 1
(pre-shared) / Option 2 (hybrid DH) for transport; this is the native
state/comms layer, experimental.

Skipped (no-op) if the real PCEA cipher is not importable.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import List, Tuple

try:
    import sys
    sys.path.insert(0, "/home/claude/a0-betatest/backend")
    from interdependent_lib.pcea.cipher import encrypt_state

    REAL_PCEA = True
except Exception:  # pragma: no cover
    REAL_PCEA = False


def make_gonal(n: int, phase: float, perm: List[int]) -> List[float]:
    v = [(2 * math.pi * k / n + phase) % (2 * math.pi) for k in range(n)]
    return [v[perm[k]] for k in range(n)]


def inscribe(theta: float, g: List[float]) -> int:
    return min(
        range(len(g)),
        key=lambda i: min(
            abs(theta - g[i]) % (2 * math.pi),
            (2 * math.pi) - abs(theta - g[i]) % (2 * math.pi),
        ),
    )


def _zipf_tokens(rng: random.Random, n: int, count: int) -> Tuple[List[int], List[float]]:
    weights = [1.0 / (k + 1) for k in range(n)]
    tot = sum(weights)
    weights = [w / tot for w in weights]
    return rng.choices(range(n), weights=weights, k=count), weights


def static_gonal_frequency_break(n: int = 32, count: int = 5000, seed: int = 11) -> dict:
    """A static private gonal falls to frequency analysis."""
    rng = random.Random(seed)
    phase = rng.uniform(0, 2 * math.pi / n)
    perm = list(range(n))
    rng.shuffle(perm)
    gon = make_gonal(n, phase, perm)
    tokens, weights = _zipf_tokens(rng, n, count)
    ct = [gon[t] for t in tokens]
    pub = make_gonal(n, 0.0, list(range(n)))
    binned = Counter(inscribe(th, pub) for th in ct)
    true_rank = sorted(range(n), key=lambda t: -weights[t])
    guess_rank = sorted(binned, key=lambda b: -binned[b])
    bin_to_tok = {guess_rank[i]: true_rank[i] for i in range(min(len(guess_rank), n))}
    recov = sum(1 for th, t in zip(ct, tokens) if bin_to_tok.get(inscribe(th, pub)) == t)
    return {"recovery": recov, "count": count, "rate": recov / count, "random": 1 / n}


def _keystream(seed_state: List[int], ticks: int) -> List[int]:
    last = list(seed_state)
    out = []
    for _ in range(ticks):
        enc = encrypt_state(last, last)
        out.append(sum(enc) % (10 ** 9))
        last = enc
    return out


def advancing_gonal_resists(n: int = 32, count: int = 5000, seed: int = 101) -> dict:
    """PCEA-advanced gonal: frequency analysis and known-plaintext both fail;
    legitimate reader recovers all. Requires the real PCEA cipher."""
    if not REAL_PCEA:
        return {"available": False}
    rng = random.Random(seed)
    base_phase = rng.uniform(0, 2 * math.pi / n)
    base_perm = list(range(n))
    rng.shuffle(base_perm)
    seed_state = [rng.randrange(1, 53) for _ in range(53)]
    tokens, weights = _zipf_tokens(rng, n, count)
    ks = _keystream(seed_state, count)
    ct = []
    for t, k in zip(tokens, ks):
        rot = k % n
        sub = (k % 997) / 997 * (2 * math.pi / n)
        g = make_gonal(n, base_phase + sub, [base_perm[(j + rot) % n] for j in range(n)])
        ct.append(g[t])
    # frequency analysis
    pub = make_gonal(n, 0.0, list(range(n)))
    binned = Counter(inscribe(th, pub) for th in ct)
    true_rank = sorted(range(n), key=lambda t: -weights[t])
    guess_rank = sorted(binned, key=lambda b: -binned[b])
    bmap = {guess_rank[i]: true_rank[i] for i in range(min(len(guess_rank), n))}
    freq = sum(1 for th, t in zip(ct, tokens) if bmap.get(inscribe(th, pub)) == t)
    # known-plaintext held-out
    rev = set(rng.sample(range(count), min(500, count // 2)))
    angle_map: dict = {}
    for i in rev:
        angle_map.setdefault(round(ct[i], 6), Counter())[tokens[i]] += 1
    held = [i for i in range(count) if i not in rev]
    kp = sum(
        1 for i in held
        if round(ct[i], 6) in angle_map
        and angle_map[round(ct[i], 6)].most_common(1)[0][0] == tokens[i]
    )
    distinct = len(set(round(c, 6) for c in ct))
    # legitimate reader
    ks2 = _keystream(seed_state, count)
    rec = 0
    for c, k, t in zip(ct, ks2, tokens):
        rot = k % n
        sub = (k % 997) / 997 * (2 * math.pi / n)
        g = make_gonal(n, base_phase + sub, [base_perm[(j + rot) % n] for j in range(n)])
        if inscribe(c, g) == t:
            rec += 1
    return {
        "available": True, "count": count, "random": 1 / n,
        "frequency_recovery_rate": freq / count,
        "known_plaintext_heldout_rate": kp / max(len(held), 1),
        "distinct_angles": distinct,
        "legitimate_recovery": rec,
    }


def run_all() -> dict:
    return {
        "static_break": static_gonal_frequency_break(),
        "advancing_resists": advancing_gonal_resists(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all(), indent=2))
