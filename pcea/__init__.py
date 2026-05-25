# GPT/Claude generated; context, prompt Erin Spencer
"""
pcea — Prime Circular Encryption Algorithm.

Encrypts neural architecture state using a prime-circular Möbius disk cipher.
State is structured as seeds: each seed is 7 circles × 7 tensors. Each circle
is itself a tensor; each seed is itself a tensor.

Values are mapped to positions on a Möbius disk before encryption. The two
sides of the disk (positive / negative half-planes) are indistinguishable to
an observer — sign does not leak. Fixed-width base-p encoding ensures the
encrypted output always has the same digit count — magnitude does not leak.

word_bits controls the Möbius disk size (default 64). It must match between
sender and receiver. Larger values support wider integer ranges.

Zero external dependencies. Framework-agnostic.

Public API:

    encrypt_seed(seed, last_seed, seed_idx, word_bits)   -> encrypted_seed
    decrypt_seed(encrypted, last_seed, seed_idx, word_bits) -> seed

    encrypt_state(state, last_state, word_bits)           -> encrypted_state
    decrypt_state(encrypted, last_state, word_bits)       -> state

    PCEAInstance(seed, word_bits)                         -> stateful session
        .encrypt(state)                                   -> encrypted_state
        .decrypt(encrypted)                               -> state

Codec:

    mobius_encode(v, word_bits)   -> unsigned position on disk
    mobius_decode(u, word_bits)   -> signed integer
    digit_count(p, word_bits)     -> fixed digit count for prime p
    to_fixed(u, p, k)             -> k base-p digits
    from_fixed(digits, p)         -> unsigned integer
"""

from .cipher import (
    CIRCLE_COUNT,
    DEFAULT_WORD_BITS,
    TENSOR_COUNT,
    decrypt_seed,
    decrypt_state,
    encrypt_seed,
    encrypt_state,
)
from .codec import digit_count, from_fixed, mobius_decode, mobius_encode, to_fixed
from .contract import DECISION as CONTRACT_DECISION, contract_statement
from .instance import PCEAInstance
from .kdf import key_stream
from .primes import CIRCLE_SIZE, PRIME_CIRCLE, prime_at

__all__ = [
    # Cipher
    "encrypt_seed",
    "decrypt_seed",
    "encrypt_state",
    "decrypt_state",
    "PCEAInstance",
    # Codec
    "mobius_encode",
    "mobius_decode",
    "digit_count",
    "to_fixed",
    "from_fixed",
    # KDF
    "key_stream",
    # Constants
    "CIRCLE_COUNT",
    "TENSOR_COUNT",
    "DEFAULT_WORD_BITS",
    "PRIME_CIRCLE",
    "CIRCLE_SIZE",
    "prime_at",
    "CONTRACT_DECISION",
    "contract_statement",
]

