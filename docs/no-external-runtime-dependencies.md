# No External Runtime Dependencies

**Status:** Policy (PLAN.md Phase 0). Binding for all PCEA runtime
modules.

## Rule

PCEA's runtime — the modules listed in `pcea.contract.RUNTIME_MODULES` —
depends on nothing outside the Python standard library and other
repositories owned by The Interdependency.

**Allowed at runtime:**
- The Python standard library, including `hashlib`, `hmac`, `secrets`,
  and `os.urandom` (entropy and hashing are required for real key
  generation; without OS entropy, secure keygen cannot be claimed).
- Other Interdependency repositories (e.g. `ucns`), where used.
- Static test vectors copied into this repository.

**Not allowed at runtime:**
- `cryptography`, PyNaCl, libsodium, OpenSSL wrappers, Signal-protocol
  libraries, or any external service required to encrypt or decrypt.

**Build/test-only tooling** (e.g. `pytest`) is separate from runtime
dependencies and does not count against this rule.

## Boundary with ucns

The ucns dependency is design/attack-time, not cipher-time. The attack
harness (`pcea-ucns/attack_harness.py`) imports ucns to measure domain
weakness; it is **not** in `RUNTIME_MODULES` and is never imported by the
cipher. PCEA's symmetric core remains importable and testable with no
ucns present (the harness tests skip cleanly in that case).

## Exit gate (Phase 0)

- Repository metadata shows no runtime pip dependencies
  (`pyproject.toml`: only a `dev` optional group).
- README states the dependency boundary accurately.
- Verified by inspection at the date of this file.
