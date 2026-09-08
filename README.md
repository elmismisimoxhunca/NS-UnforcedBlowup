# Unforced blow-up via the layered route

**Research program, not a proved result. Phase 0 is in progress.**

This is the public repository supplied by Sebastián Rodrigo for the `unforced-blowup` program. The current scope is infrastructure only. No Phase 1 analysis, unforced Euler proof, Navier–Stokes result, Clay claim, or release is authorized by a green upstream build.

## Targets and credit

The intended order is unforced smooth finite-energy 3D Euler on ℝ³, forced Navier–Stokes, then unforced Navier–Stokes. The layered program is credited to **Diego Córdoba and Luis Martínez-Zoroa**. The upstream Euler/Boussinesq/IPM work is credited to **Alpöge–Buckmaster(–Coiculescu)**; consult the individual public papers for their exact author lists. This repository does not adjudicate personal allegations or claim their work as ours.

The upstream [fluid_lean](https://github.com/tristanbuckmaster/fluid_lean) formalization describes Claude (Anthropic) authorship under Alpöge's direction. Attribution and licenses are preserved in `NOTICE` and `licenses/`. Our AI-assisted work is disclosed in `LEDGER.md` and `audit/`.

## Human-owned statement

`statements/Challenge_unforced_Euler.lean` is extracted from the human's supplied text without editing its Lean contents. `audit/prompts/human-challenge.txt` preserves the wrapper and `statements/HUMAN_SOURCE.sha256` fixes the exact extracted bytes. It deliberately contains `sorry`: **it is an unproved target, not a solution**. Only the human may change it. Its upstream inheritance diff will be retained; differences will be reported rather than silently corrected.

`Challenge_NS.lean` has not been supplied. No replacement will be invented. Upstream `euler-blowup/Challenge.lean` is a separate, forced-Euler statement and must remain untouched during G0.

## Phase 0 acceptance

- Pinned upstream Euler source build on Ubuntu 24.04, exact Lean `leanprover/lean4:v4.32.2`, Mathlib `81a5d257c8e410db227a6665ed08f64fea08e997`; **never run `lake update`**.
- Clean `scripts/PrintAxioms.lean` and unmodified upstream Comparator configuration, including NanoDa; real sandbox, not a fake-landrun substitute.
- Evidence-linked ledger, signed public commits, separate analysis/Lean worktrees, immutable human statement, licenses and honest disclosures.
- Reusable snapshot after verification; a separate small analysis VM as requested. Boussinesq and affinecore source builds are deferred by the plan's speed modifications unless required.
- Palomar policy/submission preflight; report external prerequisites and policy incompatibilities honestly.

**Stop after Phase 0 and await human Phase 1 instructions.** The full supplied plan is in `docs/IMPLEMENTATION_PLAN.md`; this stop boundary overrides its proposed Phase 1 overlap for the current assignment.

## Reproducibility

`upstream.lock.json` records source revisions. `scripts/bootstrap-euler-base.sh` installs the exact toolchain and checks pins; `scripts/build-euler-base.sh` starts the Euler source build and axiom printout. The installed Lake has no `-j` CLI option, so the build uses CPU affinity `0-23` and `LEAN_NUM_THREADS=24`; this is a resource setting, not a claim of exactly 24 concurrent subprocesses.

The build VM is `bb-c4-dev` in `judicial-airie/us-central1-b`: 32 vCPUs, 248 GiB RAM, 200 GB Hyperdisk Balanced. Runtime artifacts and full build logs live outside Git; compact evidence, exit codes and checksums will be committed. No benchmark or reproducible gate pass is claimed until recorded evidence supports it.
