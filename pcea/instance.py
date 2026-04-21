# GPT/Claude generated; context, prompt Erin Spencer
"""
Stateful PCEA instance.

PCEAInstance tracks last_state automatically, advancing it after each
encrypt or decrypt call so that sender and receiver stay synchronized
without manual state management.
"""
from __future__ import annotations

from .cipher import decrypt_state, encrypt_state


class PCEAInstance:
    """
    Stateful prime-circular encryption session.

    The instance maintains last_state internally. After each encrypt call,
    last_state advances to the current plaintext state. The receiver's
    decrypt call mirrors this: last_state advances to the recovered plaintext.

    Both sender and receiver must be initialized with the same seed and
    process states in the same order.

    Args:
        seed: initial last_state; must be a non-empty integer sequence.
    """

    def __init__(self, seed: list[int]) -> None:
        if not seed:
            raise ValueError("seed must be non-empty")
        self._last: list[int] = list(seed)

    def encrypt(self, state: list[int]) -> list[int]:
        """Encrypt state and advance internal last_state to state."""
        encrypted = encrypt_state(state, self._last)
        if state:
            self._last = list(state)
        return encrypted

    def decrypt(self, encrypted: list[int]) -> list[int]:
        """Decrypt encrypted state and advance internal last_state to recovered state."""
        state = decrypt_state(encrypted, self._last)
        if state:
            self._last = list(state)
        return state

    @property
    def last_state(self) -> list[int]:
        """Read-only snapshot of the current last_state."""
        return list(self._last)
