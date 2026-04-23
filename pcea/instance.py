# GPT/Claude generated; context, prompt Erin Spencer
"""
Stateful PCEA instance.

PCEAInstance tracks last_state (a list of seeds) automatically. After each
encrypt or decrypt call, last_state advances to the current plaintext seeds
so that sender and receiver stay synchronized without manual state management.

Each seed is a 7×7 structure: 7 circles × 7 tensors. Each circle is itself
a tensor; each seed is itself a tensor.
"""
from __future__ import annotations

import copy

from .cipher import DEFAULT_WORD_BITS, decrypt_state, encrypt_state

Seed = list[list[int]]
State = list[Seed]


def _zero_seed() -> Seed:
    return [[0] * 7 for _ in range(7)]


class PCEAInstance:
    """
    Stateful prime-circular encryption session.

    Maintains last_state (list of seeds) internally. After each encrypt call
    last_state advances to the plaintext seeds. The receiver's decrypt call
    mirrors this. Both sides must be initialized with the same seed and
    process states in the same order.

    Args:
        seed:      initial last_state as a non-empty list of 7×7 seeds
                   (list[list[list[int]]]).
        word_bits: Möbius disk size in bits. Must match between sender and
                   receiver. Default 64; set higher for larger value ranges.
    """

    def __init__(self, seed: State, word_bits: int = DEFAULT_WORD_BITS) -> None:
        if not seed:
            raise ValueError("seed must be non-empty")
        for i, s in enumerate(seed):
            if (not isinstance(s, list) or len(s) != 7
                    or any(not isinstance(row, list) or len(row) != 7 for row in s)):
                raise ValueError(f"seed[{i}] must be a 7×7 list of integers")
        self._last: State = copy.deepcopy(seed)
        self._word_bits = word_bits

    def encrypt(self, state: State) -> State:
        """Encrypt state and advance internal last_state to state."""
        encrypted = encrypt_state(state, self._last, self._word_bits)
        if state:
            self._last = copy.deepcopy(state)
        return encrypted

    def decrypt(self, encrypted: State) -> State:
        """Decrypt encrypted state and advance internal last_state to recovered state."""
        state = decrypt_state(encrypted, self._last, self._word_bits)
        if state:
            self._last = copy.deepcopy(state)
        return state

    @property
    def last_state(self) -> State:
        """Read-only snapshot of the current last_state."""
        return copy.deepcopy(self._last)
