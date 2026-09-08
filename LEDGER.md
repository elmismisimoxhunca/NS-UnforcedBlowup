# Model-run ledger

One row per logical BB model/agent invocation, including coordinator continuations. SHA-256 covers the saved task text, not hidden provider system context. Internal tool-response cycles and failures are captured by action logs and retained BB transcripts. No unforced theorem is proved.

| Run | UTC | Model | Prompt SHA-256 | Thread / outcome |
|---|---|---|---|---|
| coordinator-seq-1170 | 2026-09-08T17:04:01.906000+00:00 | cpa/gpt-6-astra | `9450d11b5037bf0a4a5b31d5c73ef308fae1ea223df56d3247f65bfe37f576f9` | thr_n3enf3vjcu: completed_scope_discovery; [prompt](audit/prompts/coordinator-seq-1170.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-1422 | 2026-09-08T17:07:07.504000+00:00 | cpa/gpt-6-astra | `8f1953621420da5eeaacb1976acbdb380a64c51edcb30ffd4498fce0ca1911a3` | thr_n3enf3vjcu: in_progress; [prompt](audit/prompts/coordinator-seq-1422.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-1426 | 2026-09-08T17:07:22.238000+00:00 | cpa/gpt-6-astra | `98b6c2c91017af4e2992ef56ef08e88734de01d7bc73426e1e45922f6fe0005d` | thr_n3enf3vjcu: in_progress; [prompt](audit/prompts/coordinator-seq-1426.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| g0-lean-tools-001 | 2026-09-08T17:22:17.233206+00:00 | cpa/gpt-6-astra | `26f1ab49bae660e74f7b161d4f77398a87a2a219e79d1d38a88f8d0a43409710` | thr_stqvgbz8fw: running; [prompt](audit/prompts/g0-lean-tools-001.txt); [actions](audit/runs/g0-lean-tools-001/ACTIONS.md) |
| g0-policy-audit-001 | 2026-09-08T17:22:17.234309+00:00 | cpa/gpt-6-astra | `3524c265bc861284faf8e32de07a4eabab77e3fb9f5aac4b4d90f6e4ea272873` | thr_p4k3euesm2: running; [prompt](audit/prompts/g0-policy-audit-001.txt); [actions](audit/runs/g0-policy-audit-001/ACTIONS.md) |
| coordinator-seq-2045 | 2026-09-08T17:26:17.089000+00:00 | cpa/gpt-6-astra | `0af95431a0bd4b2e10d5461ada6304273d9955d3b136f3721d895024e56ac925` | thr_n3enf3vjcu: coordinator_continuation; [prompt](audit/prompts/coordinator-seq-2045.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-2048 | 2026-09-08T17:26:20.253000+00:00 | cpa/gpt-6-astra | `760fcb81433261b718b4c89548ce3767bf80002513106e877b079af2bf524aa1` | thr_n3enf3vjcu: coordinator_continuation; [prompt](audit/prompts/coordinator-seq-2048.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-2053 | 2026-09-08T17:26:41.803000+00:00 | cpa/gpt-6-astra | `7a6a405f9ad22ff55d50215ef05bbf30af4edfe4922ffc5397cbdc9aeeef9461` | thr_n3enf3vjcu: coordinator_continuation; [prompt](audit/prompts/coordinator-seq-2053.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-2089 | 2026-09-08T17:31:16.847000+00:00 | cpa/gpt-6-astra | `e044123468f73cbec41d5bacd8adf66bca9e5559d071eb6cb279c678fcb97441` | thr_n3enf3vjcu: coordinator_continuation; [prompt](audit/prompts/coordinator-seq-2089.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-2094 | 2026-09-08T17:31:22.398000+00:00 | cpa/gpt-6-astra | `bc2c6be9f499128c473d4cadd5180417c12c7aa36b36b391564a8810de71175c` | thr_n3enf3vjcu: coordinator_continuation; [prompt](audit/prompts/coordinator-seq-2094.txt); [actions](audit/COORDINATOR_ACTIONS.md) |

The original LICENSE-only commit predates this audit and is not retrospectively represented as signed. Signatures attest a cryptographic history, not mathematical correctness or discovery priority. CODEOWNERS is policy, not evidence that server-side branch protection is configured.
