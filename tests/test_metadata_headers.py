# ratios: loc_comments=17:7 imports_exports=2:1 calls_definitions=8:1
# GPT/Claude generated; context, prompt Erin Spencer
"""Enforce the repository metadata + ratios-seal convention on Python modules.

The ``ratios:`` bookend is the line-1 (and last-line) seal — nothing may sit
above it. The provenance header rides immediately beneath it, on line 2.
"""

from __future__ import annotations

import pathlib

HEADER = "# GPT/Claude generated; context, prompt Erin Spencer"
ROOTS = (pathlib.Path("pcea"), pathlib.Path("tests"))


def test_all_python_modules_have_ratios_seal_and_metadata_header() -> None:
    missing: list[str] = []
    for root in ROOTS:
        for file in sorted(root.glob("*.py")):
            lines = file.read_text(encoding="utf-8").splitlines()
            # Line 1 must be the ratios seal; the provenance header sits on
            # line 2, directly beneath it.
            has_seal = bool(lines) and lines[0].lstrip().startswith("# ratios:")
            header_line = lines[1] if has_seal and len(lines) > 1 else ""
            if not has_seal or header_line.strip() != HEADER:
                missing.append(str(file))

    assert not missing, (
        "Modules missing the ratios seal (line 1) + metadata header (line 2): "
        + ", ".join(missing)
    )
# ratios: loc_comments=17:7 imports_exports=2:1 calls_definitions=8:1
