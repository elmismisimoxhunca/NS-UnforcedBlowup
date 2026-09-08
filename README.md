# Lean infrastructure workspace

Pinned build and verification tooling for public Lean sources. No new mathematical result is claimed.

- Dependency revisions: `upstream.lock.json`
- Build tooling: `scripts/`
- Third-party credits and licensing: `NOTICE` and `licenses/`
- Public audit metadata: `LEDGER.md` (hashes only; full records retained locally)

Local working documents and task text are intentionally excluded from this public tree. `scripts/check-public-tree.py` checks a default-deny file allowlist before publication; file contents still require review. This guard does not remove material from older commits.
