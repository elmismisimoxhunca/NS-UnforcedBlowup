# Model-run ledger

One row per recorded model invocation. Exact task prompts are saved and SHA-256 hashed; BB retains the full tool transcript internally. Hashes cover the task prompt, not undisclosed provider system context. Status updates must preserve failed attempts. No research proof is claimed.

| Run | UTC | Model | Prompt SHA-256 | Outcome |
|---|---|---|---|---|
| coordinator-seq-1170 | 2026-09-08T17:04:01.906000+00:00 | cpa/gpt-6-astra | `9450d11b5037bf0a4a5b31d5c73ef308fae1ea223df56d3247f65bfe37f576f9` | completed_scope_discovery; [prompt](audit/prompts/coordinator-seq-1170.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-1422 | 2026-09-08T17:07:07.504000+00:00 | cpa/gpt-6-astra | `8f1953621420da5eeaacb1976acbdb380a64c51edcb30ffd4498fce0ca1911a3` | in_progress; [prompt](audit/prompts/coordinator-seq-1422.txt); [actions](audit/COORDINATOR_ACTIONS.md) |
| coordinator-seq-1426 | 2026-09-08T17:07:22.238000+00:00 | cpa/gpt-6-astra | `98b6c2c91017af4e2992ef56ef08e88734de01d7bc73426e1e45922f6fe0005d` | in_progress; [prompt](audit/prompts/coordinator-seq-1426.txt); [actions](audit/COORDINATOR_ACTIONS.md) |

Subagents must be registered with an assignment, input revision, worktree, exact prompt hash, and file allowlist before spawning. Each writes its own ACTIONS.md. The coordinator reconciles agent-reported claims against artifacts before acceptance. No subagents have yet been launched for this research project.

The inherited initial LICENSE commit predates this audit and is not retrospectively represented as signed. Public Git commit timestamps/signatures attest repository history, not mathematical correctness or discovery priority.

| g0-lean-tools-001 | 2026-09-08T17:22:17.233206+00:00 | cpa/gpt-6-astra | `26f1ab49bae660e74f7b161d4f77398a87a2a219e79d1d38a88f8d0a43409710` | assigned, not started; [prompt](audit/prompts/g0-lean-tools-001.txt); [actions](audit/runs/g0-lean-tools-001/ACTIONS.md) |

| g0-policy-audit-001 | 2026-09-08T17:22:17.234309+00:00 | cpa/gpt-6-astra | `3524c265bc861284faf8e32de07a4eabab77e3fb9f5aac4b4d90f6e4ea272873` | assigned, not started; [prompt](audit/prompts/g0-policy-audit-001.txt); [actions](audit/runs/g0-policy-audit-001/ACTIONS.md) |
