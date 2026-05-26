# GPT/Claude generated; context, prompt Erin Spencer
"""Enforce repository metadata header convention on Python modules."""

from __future__ import annotations

import pathlib

HEADER = "# GPT/Claude generated; context, prompt Erin Spencer"
ROOTS = (pathlib.Path("pcea"), pathlib.Path("tests"))


def test_all_python_modules_have_standard_metadata_header() -> None:
    missing: list[str] = []
    for root in ROOTS:
        for file in sorted(root.glob("*.py")):
            first_line = file.read_text(encoding="utf-8").splitlines()[0] if file.read_text(encoding="utf-8") else ""
            if first_line.strip() != HEADER:
                missing.append(str(file))

    assert not missing, (
        "Modules missing required metadata header: " + ", ".join(missing)
    )
