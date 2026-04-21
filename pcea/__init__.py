# GPT/Claude generated; context, prompt Erin Spencer
"""
pcea — Prime Circular Encryption Algorithm.

Encrypts neural architecture state using a prime-circular base number cipher.
State is structured as seeds: each seed is 7 circles × 7 tensors. Each circle
is itself a tensor; each seed is itself a tensor. The same operation applies
at every level.

Zero external dependencies. Framework-agnostic: callers supply pre-quantized
integer representations of their weights or activations.

Public API:

    encrypt_seed(seed, last_seed, seed_idx)   -> encrypted_seed
    decrypt_seed(encrypted, last_seed, seed_idx) -> seed

    encrypt_state(state, last_state)           -> encrypted_state
    decrypt_state(encrypted, last_state)       -> state

    PCEAInstance(seed)                         -> stateful session
        .encrypt(state)                        -> encrypted_state
        .decrypt(encrypted)                    -> state

Constants:

    CIRCLE_COUNT   — 7 circles per seed
    TENSOR_COUNT   — 7 tensors per circle
    PRIME_CIRCLE   — 53-prime circular basis
    CIRCLE_SIZE    — 53
"""

from .cipher import CIRCLE_COUNT, TENSOR_COUNT, decrypt_seed, decrypt_state, encrypt_seed, encrypt_state
from .instance import PCEAInstance
from .kdf import key_stream
from .primes import CIRCLE_SIZE, PRIME_CIRCLE, prime_at

__all__ = [
    "encrypt_seed",
    "decrypt_seed",
    "encrypt_state",
    "decrypt_state",
    "PCEAInstance",
    "key_stream",
    "CIRCLE_COUNT",
    "TENSOR_COUNT",
    "PRIME_CIRCLE",
    "CIRCLE_SIZE",
    "prime_at",
]
