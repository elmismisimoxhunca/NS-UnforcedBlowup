# Phase boundary and statement ownership

Current authorization: Phase 0 infrastructure only. Do not begin Phase 1 mathematics, claim an unforced theorem, submit research, or progress to later gates without the human's new instructions. The requested Palomar infrastructure preflight is not a release authorization for this unsolved target.

Only the human may edit `statements/Challenge_unforced_Euler.lean`, its authoritative hash, or any designated `Challenge.lean`. Verify `statements/HUMAN_SOURCE.sha256` before and after work. Preserve the supplied target including its placeholder `sorry`; never treat that placeholder as a proved solution. Do not invent missing `Challenge_NS.lean`.

# Audit before action

Read `LEDGER.md` and your assignment in `audit/runs/` before any work. Every model invocation needs an exact saved prompt, SHA-256, date, actual model/identity, input commit, assigned worktree and explicit scope. If your invocation is not registered, stop and tell the coordinator.

For every tool action, immediately record intent, command/tool, result/exit code, evidence location, files changed and any claim in your assigned `audit/runs/<run-id>/ACTIONS.md`. Include failed attempts, not only successes. Use observed/proposed/verified/refuted/unresolved labels. Link the BB transcript as supporting provenance; do not expose secrets or personal data. Record follow-up prompts and resumptions as additional run entries. No unlogged subdelegation.

Work only in your assigned worktree and file allowlist. Analysis and Lean lanes never share a writable checkout. The Lean lane receives fixed statements, not authority to weaken or restate them. Raise statement problems to the coordinator/human without edits. The coordinator alone integrates changes and signs/pushes them through the Notebook's existing keyring; never copy private keys to other machines.

# Verification

Read the pinned upstream Euler README before build work. Preserve exact Lean and Mathlib pins in `upstream.lock.json`; never run `lake update`, permit toolchain auto-updates or disable real Comparator sandboxing. Report mismatches and unsupported command syntax rather than silently changing pins. G0 requires build exit 0, expected Challenge-only warning, exact permitted axiom evidence, and Comparator/NanoDa success using the unmodified upstream config.

When making claims or reviewing evidence, distinguish upstream forced-Euler verification from the unproved unforced-Euler target. Independent adversarial review must cite actual artifacts. No new mathematical claim enters `notes/accepted/` without its prescribed review passes; no Phase 1 notes are authorized now.

Finish by checking the assigned acceptance criteria against actual files and runtime evidence, checking the frozen statement hash, listing changed files and unresolved blockers, and returning evidence paths. Passing one build is not completion of other checks. Do not commit or push unless explicitly assigned; retain all failed-attempt notes.
