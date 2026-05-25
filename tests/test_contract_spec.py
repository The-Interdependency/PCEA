# GPT/Claude generated; context, prompt Erin Spencer
"""Contract-level tests for the PCEA↔UCNS boundary assumptions."""

from __future__ import annotations

import ast
import pathlib

import pytest

from pcea import decrypt_state, encrypt_state
from pcea.contract import (
    DECISION,
    FORBIDDEN_UCNS_SYMBOLS,
    RUNTIME_MODULES,
    SECURITY_INVARIANT,
    contract_statement,
)


CIRCLES = 7
TENSORS = 7


def _seed(base: int = 1) -> list[list[int]]:
    return [[(base + c * TENSORS + t) for t in range(TENSORS)] for c in range(CIRCLES)]


def _module_tree(file_path: pathlib.Path) -> ast.AST:
    source = file_path.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(file_path))


def test_contract_decision_is_option_a() -> None:
    """PCEA must invert via keys (Option A), not UCNS inverse APIs."""
    assert DECISION == "A"


def test_contract_statement_mentions_invariant() -> None:
    statement = contract_statement()
    assert "Option A" in statement
    assert SECURITY_INVARIANT in statement


def test_readme_boundary_is_aligned_with_contract() -> None:
    readme = pathlib.Path("README.md").read_text(encoding="utf-8")
    assert "decrypt/invert **via keys**" in readme
    assert "Security rests on key management" in readme


def test_decrypt_requires_matching_key_state() -> None:
    """Using the wrong last_state must fail to recover plaintext."""
    state = [_seed(100), _seed(200)]
    last = [_seed(1), _seed(2)]
    wrong_last = [_seed(3), _seed(4)]

    encrypted = encrypt_state(state, last)
    recovered_wrong = decrypt_state(encrypted, wrong_last)

    assert recovered_wrong != state


def test_runtime_has_no_forbidden_imports_or_calls() -> None:
    """Release-blocking guardrail: no UCNS inverse/catalogue symbols in runtime code."""
    for relative_path in RUNTIME_MODULES:
        file = pathlib.Path(relative_path)
        tree = _module_tree(file)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name.lower().split(".")[0]
                    assert imported not in FORBIDDEN_UCNS_SYMBOLS, (
                        f"Forbidden import '{alias.name}' found in {file}"
                    )
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or "").lower().split(".")[0]
                assert module not in FORBIDDEN_UCNS_SYMBOLS, (
                    f"Forbidden module import-from '{node.module}' found in {file}"
                )
                for alias in node.names:
                    assert alias.name.lower() not in FORBIDDEN_UCNS_SYMBOLS, (
                        f"Forbidden symbol import '{alias.name}' found in {file}"
                    )
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    assert node.func.id.lower() not in FORBIDDEN_UCNS_SYMBOLS, (
                        f"Forbidden function call '{node.func.id}' found in {file}"
                    )
                elif isinstance(node.func, ast.Attribute):
                    assert node.func.attr.lower() not in FORBIDDEN_UCNS_SYMBOLS, (
                        f"Forbidden method call '{node.func.attr}' found in {file}"
                    )


@pytest.mark.parametrize("word_bits", [32, 64, 128])
def test_forward_roundtrip_is_self_sufficient(word_bits: int) -> None:
    """Roundtrip must succeed using forward arithmetic + key material only."""
    state = [_seed(10), _seed(20), _seed(30)]
    last = [_seed(1), _seed(2), _seed(3)]
    encrypted = encrypt_state(state, last, word_bits=word_bits)
    assert decrypt_state(encrypted, last, word_bits=word_bits) == state
