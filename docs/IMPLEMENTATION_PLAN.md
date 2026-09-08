Unforced blow-up via the layered route — implementation plan

Target order: (A) unforced smooth finite-energy blow-up for 3D incompressible Euler on ℝ³; then (B) forced Navier–Stokes (viscous ceiling); then (C) unforced Navier–Stokes. A is the arbitrage. B and C reuse everything A builds.

Sources
Lean formalization (Apache 2.0): https://github.com/tristanbuckmaster/fluid_lean
Buckmaster's statement (chronology, credit, allegations): https://cims.nyu.edu/~tristanb/statement.pdf
Papers: Euler https://cims.nyu.edu/~tristanb/euler.pdf · Boussinesq (the readable one) https://cims.nyu.edu/~tristanb/boussinesq.pdf · IPM https://cims.nyu.edu/~tristanb/ipm.pdf
Announcement: https://mastodon.social/@tristanbuckmaster/117233413705701198
Tao's exposition of the mechanism and the unforced outlook: https://terrytao.wordpress.com/2026/09/07/finite-time-blowup-with-smooth-forcing-term-for-the-incompressible-porous-medium-boussinesq-and-incompressible-euler-equations/
Tao's endorsement: https://mathstodon.xyz/@tao/117233527638291447
Córdoba–Martínez-Zoroa, the program this builds on: https://arxiv.org/abs/2410.22920
Competing unforced-Euler route (self-similar profile via PINN), Ganeshram–Duruisseaux–Anandkumar: https://anima-ai.org/2026/09/07/stable-singularity-of-the-euler-equations-on-r3-without-forcing/
Comparator (statement/proof checker used by the repo): https://github.com/leanprover/comparator
Palomar registry (release venue): https://palomar-registry.org/ · Tao's announcement: https://terrytao.wordpress.com/2026/08/18/palomar-a-registry-of-lean-verified-mathematics/ · ICARM announcement: https://icarm.io/news/announcing-palomar-a-registry-of-lean-verified-mathematics/
Clay problem statement (Fefferman), for the target options: https://www.claymath.org/millennium/navier-stokes-equation/
Frozen unforced-Euler statement: Challenge_unforced_Euler.lean (alongside this plan)
Working forced-NS statement (not frozen; Clay-class uniqueness lemma still needed): Challenge_NS.lean

Program credit: Córdoba–Martínez-Zoroa. Euler/Boussinesq/IPM credit: Alpöge–Buckmaster(–Coiculescu).

Phase 0 — Infrastructure (blocking; parallel with everything)

VM

Size to the Euler README's stated build: on the order of 100 GB RAM at ~24 parallel lake jobs, a few hours. Memory scales with -j; fewer jobs on a smaller box works, just slower. Fast local disk matters more than CPU count. Pick whatever Google Cloud will actually sell you that clears that.
Ubuntu 24, elan, Lean leanprover/lean4:v4.32.2 exactly. Mathlib pinned via lake-manifest.json (commit 81a5d257c8e410db227a6665ed08f64fea08e997). Never run lake update.
Clone repo, lake build -j <N> in euler-blowup/ (Mathlib compiles from source at this pin).
Then lake env lean scripts/PrintAxioms.lean and run comparator per README. Do not proceed past Phase 1 until this is green. Snapshot the VM image afterwards — this is your reusable base.
Also build boussinesq-blowup/ and affinecore/; Boussinesq is the readable proof and the likely template for the unforced argument.

Repo hygiene (this is your priority claim)

New public GitHub repo from hour zero: unforced-blowup. Commit early and often, including failed attempts and notes. Signed commits. This is the only defensible timestamp you will have.
NOTICE and README crediting CMZ, Alpöge–Buckmaster–Coiculescu, Apache attribution for vendored code.
LEDGER.md: one line per model run — date, model, prompt hash, outcome. You will need this when someone asks how the proof was produced; the current dispute is exactly about the absence of such a log.

Agents

Two model lanes: an analysis lane (long-context reading, estimates, conjecture formulation) and a Lean lane (Codex or whatever grinds autoformalization best on your setup). Keep them in separate worktrees; the Lean lane only ever gets statements to prove, never the freedom to change them.
One human (you) as the only person allowed to edit Challenge.lean. Everything else is disposable.
Phase 1 — Understanding. Gate 1.

Goal: replace my one-read classification with a verified one. All outputs are markdown in notes/.

Force inventory. From the Boussinesq paper §5 (and Euler (5.14), (5.26)): list every term that ends up in the physical force, tagged by job — (S) activation/seeding, (R) phase-averaged residual means, (T) terminal grades beyond depth J, (P) pressure/curl bookkeeping. Record the size of each in the scale parameters (N_m, ℓ_m, σ_{m-1}, δ, J_m, Y_*). If a fifth category appears, stop and rethink.
Seeding. Can layer m's seed live in the initial data at t=0 with amplitude ≪ N_m^{-k} for all k and be transported passively by layers < m until τ_m without being distorted or amplified early? This is a linear transport question about the older flow. Want: a lemma statement plus a scaling argument, not a proof.
Residual → stability. Write the precise conjecture: with force set to zero and the correction recursion at depth J_m, the constructed (Γ_J, Ψ_J) is an approximate solution with residual E_J; the true solution with the same data exists on [0,T*) and satisfies ‖∇Γ_true − ∇Γ_J‖ ≤ ½‖∇Γ_J‖ at the center. State exactly which norm and why the amplifying ODE does not amplify E_J.
Sanity from the pros. Read Tao's post and the Boussinesq intro against items 1–3; note every disagreement.

Gate 1 decision. If item 3 looks like a bounded estimate (an energy/weighted estimate in their existing norm framework), go to Phase 2. If it needs a new idea (e.g. a new instability-avoiding modulation), that idea is the project; run it until it resolves or is shown to be a genuine obstruction.

Phase 2 — Model-level proof. Gate 2.

Work at the level of the exact modulation ODEs (Boussinesq Lemma 2.1 / Euler (3.4)) and the residual estimates, not the full PDE.

Stream A (seeding): prove dormant-layer transport control. Deliverable: lemma + proof sketch in the paper's notation, checked by a second model instance adversarially.
Stream B (infinite depth or stability): try both.
B1: show the correction recursion converges as J→∞ with summable residual (scale conditions in (6.3) style, now with δ^J → 0 uniformly). If it does, no stability theorem is needed.
B2: if B1 fails, the stability estimate: bootstrap the error in a weighted norm modeled on (3.8) with weight ρ(t), showing the error's growth rate is strictly below the layer's growth rate.
Stream C (scales): redo §12's sequence selection with the new constraints from A and B. This is where the numbers either close or don't.

Adversarial loop: every claimed lemma gets a fresh model instance with the instruction "find the error." Nothing enters notes/accepted/ without surviving two independent adversarial passes.

Gate 2 decision. A consistent scale sequence exists on paper with all three streams closed → Phase 3. Otherwise, publish the obstruction as a short note (that is still a result) and reassess.

Phase 3 — Paper-level proof (deprioritized; see Speed modifications)
Generate the full argument in the structure of the Euler paper (§§2–14 mapping). Expect the first draft to be, in Buckmaster's words, slop. Do not polish yet — the Lean is the arbiter.
Human-read only the load-bearing sections: the amplitude law, the seeding lemma, the stability/convergence lemma, the scale selection. Everything else is verified by Phase 4.
Phase 4 — Lean (starts the moment Gate 2 passes; overlaps Phase 3)
Statement first. Challenge_unforced_Euler.lean (alongside this plan) is the frozen statement: a minimal diff of the upstream Challenge.lean — SmoothForce deleted, the force argument fixed to fun _ _ => 0 in ClassicalEuler and both InLipschitzClass3 clauses, every other definition and clause byte-identical. Keep the diff against upstream in the repo so reviewers can see the inheritance. Mathlib-only, comparator-checkable. Do not edit after G3.
Reuse map. Inventory what in EulerBlowup/ is equation-agnostic and reusable as-is: Lit/ (CZ, Bogovskii, Schauder, Sobolev), Ring/ and Ring3D/ (the bulk), Num/ machinery (interval certificates — the checker is reusable, the certificates are not), L/ (transport toolkit), vendor/cm24-r2. Expect ~60–70% reuse by line count.
New modules. Seeding transport, convergence/stability, new scale selection, new numerical certificates for the new scale inequalities. Build in dependency order; each module gets its own sorry-free milestone.
Autoformalization loop. Lean lane works lemma-by-lemma from Phase 3 statements. Blueprint style: statement → attempted proof → lake build → error → retry, with a hard cap per lemma before escalating to the analysis lane for a restatement. Track sorry count in CI as the single progress metric.
Green build + comparator + PrintAxioms = done. Nothing is announced before this.
Phase 5 — Release (no arXiv needed)

Primary venue is Palomar (https://palomar-registry.org/), the registry of Lean-verified results run by ICARM / Lean FRO with Tao on the advisory board. It registers an immutable GitHub commit after three automated checks: Comparator (proof proves the frozen statement, pinned Mathlib, standard axioms only), an LLM check that the formal statement fairly renders the informal claim, and a disclosure audit of formalization.yaml. No endorser, no human gate. The fluid_lean repo is already in Palomar's template layout, so keep that layout from day one.

Submission instructions: https://palomar-registry.org/about (read the disclosure requirements before writing formalization.yaml; the AI-assistance disclosures are mandatory and are the point). Questions go to the Palomar channel on the Lean Zulip.
formalization.yaml must credit CMZ and Alpöge–Buckmaster–Coiculescu and state the reuse of their code under Apache 2.0.
For the informal write-up, use a DOI'd deposit that needs no endorsement (Zenodo), released the same day as the Palomar entry and linked from it. Get an arXiv endorser in math.AP later if you want mirroring; a Mathlib contributor asking on Zulip will find one. It is not on the critical path.
Send the preprint and repo link to Buckmaster, Alpöge, Córdoba, Martínez-Zoroa and Tao before the Palomar entry goes public, not after.
Release LEDGER.md with it. Being the first team in this saga with a transparent process log is worth more than being first by a day.
Speed modifications (applied)
Nothing waits on the build. G0 runs on the VM while G1 runs on the analysis lane from the PDFs. Build only euler-blowup/ first; boussinesq-blowup/ and affinecore/ are built later, only if a module from them is actually needed. Snapshot the VM image the moment Euler is green and clone it for every parallel Lean worker rather than rebuilding.
Lean starts at G1, not G2. Two things are safe to formalize before the math closes: the frozen statement file (already written) and the reuse layer — a lake target that imports the upstream Lit/, Ring/, L/, Num/ checker and vendor/cm24-r2 as a library and builds green with nothing else. That is the platform every later lemma sits on, and it is pure engineering. The seeding transport lemma's statement is also likely fixed before its proof is; formalize the statement and let the Lean lane attack it while the analysis lane is still on stability.
No paper before the Lean. Phase 3 is dropped as a gate. Prose is generated from the green Lean at the end, not written in parallel. The human-read sections (amplitude law, seeding, stability/convergence, scale selection) are read as Lean statements plus generated sketches, which is faster and cannot drift from what was proved.
Adversarial review only where it matters. Two independent adversarial passes for the four load-bearing lemmas; one pass for everything else. Lean is the second reviewer for the rest.
Preflight Palomar now. Submit a trivial entry (any small verified lemma) today to learn the submission and disclosure workflow while nothing depends on it. Tao described the process as thorough; do not discover its requirements at G4.
Two VMs, not one. One for the base build and comparator runs (memory-heavy, needs the full Mathlib), one or more small ones for the analysis lane and note-keeping. Lean workers scale horizontally from the snapshot in item 1.

What is not cut: the frozen statement, the ledger, the comparator, the disclosures. Speed comes from parallelism and from letting Lean replace human reading, never from lowering the bar the result has to clear.

Roles (minimum viable team)
You: Challenge.lean owner, gates, attribution, release. Reads the four load-bearing sections.
Analysis lane (model): Phases 1–3, adversarial review.
Lean lane (model): Phase 4.
Optional but strongly advised: one PDE person who can read §7 of the Euler paper in an afternoon. If you cannot get one, expect Gate 2 to take more adversarial rounds.
Gates and kill criteria

No calendar and no token budget. Progress is measured in gates passed. The lanes run continuously; you review at gate boundaries. Kill criteria are mathematical, never resource-based: a gate is abandoned only when the obstruction is shown to be real, not when spending reaches a number.

Gate	Passes when	Kill if
G0	Euler repo green on VM, comparator + PrintAxioms clean	build cannot be made green; fix before anything else
G1	Force inventory, seeding lemma statement, stability conjecture in notes/accepted/	force does a job not in {S,R,T,P} and no reformulation removes it
G2	Consistent scale sequence on paper; streams A, B, C closed under adversarial review	the obstruction is proven to be genuine (the error is amplified at the layer's rate under every tried norm)
G3	Reuse layer green; all load-bearing lemma statements in Lean; Challenge_unforced_Euler.lean frozen	—
G4	sorry = 0, comparator green, standard axioms only	a load-bearing lemma is shown false as stated; restate and continue rather than kill

If Buckmaster–Alpöge or OpenAI post unforced Euler first: switch immediately to verifying their result in Lean against your frozen statement. A second verified proof still has value; a third unverified claim has none.

After A
B (forced NS): the viscous ceiling. Your Phase 2 Stream C tooling is exactly what tests whether growing circulation amplitudes escape it. Draft statement already exists (Challenge_NS.lean).
C (unforced NS): A's stability lemma + B's amplitude redesign. This is the Clay problem as everyone imagines it, options (A)/(B).
Things not to do
Don't feed either lane anything that isn't public. The whole reason this project has value is that it is reconstructable from public material with a public log.
Don't touch Challenge.lean after freezing to make a proof easier. If the statement must change, it's a new file, a new commit, and a note in the ledger explaining why.
Don't announce partial results on social media. Post the obstruction note or the proof, nothing in between.
