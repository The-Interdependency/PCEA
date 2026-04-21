# GPT/Claude generated; context, prompt Erin Spencer
"""
pcea — Prime Circular Encryption Algorithm.

Encrypts neural architecture state using a prime-circular base number cipher.
Accepts state and last_state as flat integer sequences. No external dependencies.
Framework-agnostic: callers supply pre-quantized integer representations of
their weights or activations.

Public API:

    encrypt_state(state, last_state)     -> encrypted_state
    decrypt_state(encrypted, last_state) -> state

    PCEAInstance(seed)                   -> stateful session
        .encrypt(state)                  -> encrypted_state
        .decrypt(encrypted)              -> state

Constants:

    PRIME_CIRCLE   — the 53-prime circular basis
    CIRCLE_SIZE    — 53
    prime_at(i)    — prime at circular position i
"""

from .cipher import decrypt_state, encrypt_state
from .instance import PCEAInstance
from .kdf import key_stream
from .primes import CIRCLE_SIZE, PRIME_CIRCLE, prime_at

__all__ = [
    "encrypt_state",
    "decrypt_state",
    "PCEAInstance",
    "key_stream",
    "PRIME_CIRCLE",
    "CIRCLE_SIZE",
    "prime_at",
]
