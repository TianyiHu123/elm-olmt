# iter009 - Alpha-50 LBFGS Refinement and Forcing-Group Ablation

## Status

- Iteration ID: `iter009`
- Run slug: `spinup_surrogate_iter009_<variant>`
- Status: `completed`
- Phase: `selection and closeout complete`
- Site profile: `development/hpc/puma.md`
- Started: `2026-07-23T02:07:28Z`
- Closed: `2026-07-23T02:23:36Z`

## Runtime Contract

| Field | Value |
| --- | --- |
| Run mode and stop conditions | One finite 15-variant, five-seed matrix (75 leaves). Continue through terminal accounting, aggregation, selection, and closeout. Independent scientific rejections continue; application/code/configuration failures outside the one bounded preflight correction stop for fresh authorization. |
| HPC confirmed | Yes: UA Puma login host `junonia.hpc.arizona.edu`, using `development/hpc/puma.md`; user approved this contract on 2026-07-22 America/Phoenix / 2026-07-23 UTC. |
| Submission/monitoring authority | Authorized for scaffolding, static tests, independent read-only review, variant-local Slurm preparation, one bounded no-training preflight, the locked matrix submission, continuous monitoring, aggregation, selection, and closeout. |
| Resource policy and caps | Puma `standard`, account `chopinsong`, one node/task, 10 CPUs (50 GB implied), 30 minutes, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread BLAS/OpenMP, and per-task `XDG_CACHE_HOME`. Preflight uses 1 CPU (5 GB implied) and 5 minutes. |
| Closeout commit authority | Authorized: at most one closeout commit after all closeout artifacts are complete. |

The user replied `approved` after a request explicitly naming the selected Puma profile, finite
15-variant / 75-leaf scope, preparation/submission/continuous-monitoring authority, resource caps,
retry boundaries, and closeout commit. One minimal import/launch/configuration correction and rerun
of the same bounded preflight is authorized if it fails before training. Separately, each matrix
leaf may be retried once only for a scheduler/resource interruption within the stated caps. A
second preflight failure, changed failure class, scientific-control change, or post-preflight
application/code/configuration failure requires fresh authorization.

## Context and Objective

- Prior baseline and evidence: iter008 selected `(32,), tanh, lbfgs, alpha=50` with full45. Its
  median validation R2 is `0.7935/0.7937`, minimum R2 is `0.6820/0.6820`, R2 IQR is
  `0.0646/0.0612`, median per-seed RMSE ratio is `0.9499/0.9561`, absolute median validation RMSE
  is `4661.8/469.7`, and warning fractions are zero for `TOTSOMC/TOTSOMN`.
- Hypothesis: a narrow regularization sweep around alpha 50 may improve the selected LBFGS model,
  while global 0.80 correlation pruning and direct exclusion of FLDS/WIND/PSRF climatology inputs
  test two focused alternatives to the full45 schema without changing the architecture.
- Objective: choose the strongest gate-passing alpha and feature-policy combination while retaining
  the iter008 alpha-50 full45 control in the matrix.

## Fixed Controls and Variant Matrix

- Cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL; all
  `ppe6_I20TRCNPRDCTCBC`.
- Split mode: `by_member`; train fraction: `0.8`; targets: `TOTSOMC,TOTSOMN`.
- Seeds: `10001-10005`; model: `(32,), tanh, lbfgs`; learning rate `1e-3` is provenance-only.
- Alpha values: `25`, `35`, `50`, `65`, `75`.
- Feature policies: `full45` uses the strict iter006/iter008 45-feature schema with no filtering;
  `corr080_prioritydrop` uses that schema as an eligible pool with global pre-split correlation
  threshold `0.80`; `drop_flds_wind_psrf` uses a strict 32-feature schema and forcing variables
  `PRECTmms,FSDS,TBOT,RH`, directly excluding all 13 FLDS/WIND/PSRF climatology features.
- Variance filtering is disabled. Correlation filtering is enabled only for
  `corr080_prioritydrop`. All variants use stats-only output and eight permutation repeats.
- Locked manifest: `development/spinup_surrogate/slurm/iter009/iter009_variants.tsv`.

The matrix is the cross-product of five alpha values and three feature policies: 15 variants and
75 required leaves. Expected output roots are
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter009_<variant>/`.

## Decision and Retry Rules

- Eligibility: exactly five readable stats JSON files for every variant, covering seeds
  `10001-10005`; no incomplete variant is eligible and no selection occurs with an incomplete
  matrix.
- Gates apply independently to both targets against the iter008 selected baseline: median
  validation R2 at least baseline minus `0.01`; minimum R2 at least baseline minus `0.02`; R2 IQR
  no more than baseline plus `0.02`; median of the five per-seed validation/training RMSE ratios no
  more than baseline plus `0.02`; and zero overfit warnings. Absolute validation RMSE is reported
  alongside normalized metrics.
- Rank full gate passers by mean cross-target median validation R2, then lower mean median RMSE
  ratio, then lower alpha. The alpha-50 full45 control remains eligible under identical rules.
- A complete gate failure is a scientific rejection; independent variants continue.
- One automatic validation-only retry may apply one minimal import/launch/configuration correction
  and rerun the same no-training preflight. One separate retry per matrix leaf is allowed only for
  a scheduler/resource interruption within the approved cap. Any other application/code/configuration
  failure, changed failure class, scientific-control change, resource increase, or new submission
  outside this matrix requires fresh authorization.

## Provenance and Job Ledger

| Variant | Canonical script and SHA-256 | Variant-local submitted copy/config and SHA-256 | Variant-local log paths | Commit | Dirty diff/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all 15 manifest variants | `slurm/iter009/case.train_surrogate_spinup_iter009.slurm`; `7a7d58294ee14e64a040f591c2a67191c78ee3055db68324ace814a7ed07d8d1` | `UQ_output/<run_slug>/submit_<variant>.slurm` with canonical hash; `submission_config.env` hashes below | `UQ_output/<run_slug>/slurm_%A_%a.out`; `slurm_%A_%a.err` | source head `a22b7bbe23e0c3d9874f90c711dc904e416d786c` | `iterations/iter009_source_manifest.txt`; `323ac1031062af5a6dd05fb9f2b3a4ff33040f264cda80cea9dcf0a6f13be611` | `23370953-23370967` mapped below | COMPLETED (75/75) | no retry |

## Execution and Diagnostics

- Static validation: all three Slurm scripts passed `bash -n`; the Python validator compiled; the
  manifest has 15 unique variants, five alpha values, and three feature policies; `git diff
  --check` passed.
- Independent review round 1: `block`. The reviewer confirmed the matrix, full45/drop32 semantics,
  fixed root, resources, cache isolation, and flat artifact layout, but required stricter
  config/copy-to-manifest preflight validation, rejection of unlocked config tuples and worker
  overrides, exact result seed/metadata checks before aggregation, and immutable materialization.
  Those issues were addressed in the canonical script, materializer, preflight validator, and new
  `validate_iter009_results.py`; passing re-review is required before preflight.
- Independent review round 2: `pass`. The reviewer verified the exact 15-row cross-product,
  canonical full45/drop32 definitions, manifest-to-config equality, byte-identical submitted-copy
  checks, non-sourcing config parser, locked worker settings, immutable materialization, and exact
  seed/model/metadata/schema validation before aggregation. Reviewed canonical SHA-256 is
  `7a7d58294ee14e64a040f591c2a67191c78ee3055db68324ace814a7ed07d8d1`; manifest SHA-256 is
  `d10f423c09f64b38d90237c493945d5d0b1848076f79c5e5e662d26274220ceb`.
- Materialization: all 15 variant roots were created with byte-identical submitted copies
  (SHA-256 `7a7d58294ee14e64a040f591c2a67191c78ee3055db68324ace814a7ed07d8d1`) and locked
  seven-field `submission_config.env` files. The first sandboxed invocation had no permission to
  create the external output roots and wrote nothing; the approved unsandboxed `bash -e`
  invocation completed all 15 roots. Config hashes are recorded below before matrix submission.
- Preflight submission: `/usr/bin/sbatch --parsable
  --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter009_validate_%j.out
  --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter009_validate_%j.err
  development/spinup_surrogate/slurm/iter009/validate_iter009.slurm`; job `23370951`.
- Preflight result: `COMPLETED`, exit `0:0`, elapsed `00:00:25`, 1 CPU / 5 GB implied,
  MaxRSS `266672K`. The log reports `global feature-filter invariants passed` and `iter009
  manifest and no-training feature-policy invariants passed`; no validation-only retry was used.
- Matrix submission template, executed once for every locked manifest variant:
  `/usr/bin/sbatch --parsable --chdir=<variant-root>
  --output=<variant-root>/slurm_%A_%a.out --error=<variant-root>/slurm_%A_%a.err
  --export=ALL,SUBMISSION_CONFIG=<variant-root>/submission_config.env
  <variant-root>/submit_<variant>.slurm`.
- Submitted arrays (each `1-5`):
  `s32_tanh_lbfgs_a25_lr1e3_full45=23370953`,
  `s32_tanh_lbfgs_a25_lr1e3_corr080_prioritydrop=23370955`,
  `s32_tanh_lbfgs_a25_lr1e3_drop_flds_wind_psrf=23370954`,
  `s32_tanh_lbfgs_a35_lr1e3_full45=23370956`,
  `s32_tanh_lbfgs_a35_lr1e3_corr080_prioritydrop=23370957`,
  `s32_tanh_lbfgs_a35_lr1e3_drop_flds_wind_psrf=23370958`,
  `s32_tanh_lbfgs_a50_lr1e3_full45=23370960`,
  `s32_tanh_lbfgs_a50_lr1e3_corr080_prioritydrop=23370959`,
  `s32_tanh_lbfgs_a50_lr1e3_drop_flds_wind_psrf=23370961`,
  `s32_tanh_lbfgs_a65_lr1e3_full45=23370962`,
  `s32_tanh_lbfgs_a65_lr1e3_corr080_prioritydrop=23370963`,
  `s32_tanh_lbfgs_a65_lr1e3_drop_flds_wind_psrf=23370964`,
  `s32_tanh_lbfgs_a75_lr1e3_full45=23370965`,
  `s32_tanh_lbfgs_a75_lr1e3_corr080_prioritydrop=23370967`, and
  `s32_tanh_lbfgs_a75_lr1e3_drop_flds_wind_psrf=23370966`.
- Variant-local submission-copy/configuration and log-path evidence: all 15 roots use
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter009_<variant>/`
  with `submit_<variant>.slurm`, `submission_config.env`, and root-level
  `slurm_%A_%a.out/.err`; exact config hashes are below.
- Queue/accounting evidence: monitoring jobs `23370953-23370967` (excluding preflight job
  `23370951` and unused scheduler ID gaps) reached terminal accounting. All 75 allocation rows
  are `COMPLETED`, exit `0:0`; no retry was used.
- Resource diagnostics: every leaf received `billing=10,cpu=10,mem=50G,node=1`; elapsed range
  `00:01:17-00:02:09`; batch-step MaxRSS range `37314780K-52427868K`.
- Aggregation job `23371111` submitted with `/usr/bin/sbatch --parsable` using
  `slurm/iter009/aggregate_iter009.slurm` (SHA-256
  `de96af3b041defa8733d91a4a36bb9b8398e0ce02f9068582e223269cb56fa09`) and root-level
  `spinup_iter009_aggregate_%j.out/.err` logs. It validates exact results before summarization.
- Aggregation result: `COMPLETED`, exit `0:0`, elapsed `00:00:17`, MaxRSS `42004K`. The exact
  validator passed every seed/run/model/schema invariant and aggregation wrote 15 summary plus 15
  feature-stability JSON files.
- Failure or rejection evidence: no execution failure. Alpha 25/35 variants are scientific
  rejections for warning fraction `0.2/0.2`; alpha 65/75 variants are scientific rejections for
  median/minimum R2, with two alpha-75 policies also exceeding the TOTSOMC RMSE-ratio cap.

Materialized configuration hashes (each submitted-copy hash is the canonical
`7a7d58294ee14e64a040f591c2a67191c78ee3055db68324ace814a7ed07d8d1`):

| Variant | `submission_config.env` SHA-256 |
| --- | --- |
| `s32_tanh_lbfgs_a25_lr1e3_full45` | `cbfc1aec070fabe990c6034e8a98645a047ab32c7502a0a3d3dafd60af4efbf9` |
| `s32_tanh_lbfgs_a25_lr1e3_corr080_prioritydrop` | `35d36830db1e8e03bf2ecfa20e0af04d2e648ee35d28a6a1fb67bd371cf7df9c` |
| `s32_tanh_lbfgs_a25_lr1e3_drop_flds_wind_psrf` | `ab9785eac83001fb44c016af01d95abe168f0f9183ce88773162c82d6d738b54` |
| `s32_tanh_lbfgs_a35_lr1e3_full45` | `b2b308cdcfb2d0cce4e8cea55a611564200f743a2d9992fe0f28b161e7293f4b` |
| `s32_tanh_lbfgs_a35_lr1e3_corr080_prioritydrop` | `23ef405fb04c3208abd9bb4e91e300584f32f22d71463e2ac38cf0046c5f499d` |
| `s32_tanh_lbfgs_a35_lr1e3_drop_flds_wind_psrf` | `671bc07f6197f35a9ba009b92ff9c7e208943bf6df316951bf9fcb9b6f7d9ae9` |
| `s32_tanh_lbfgs_a50_lr1e3_full45` | `ee918a30205ed946c6c6226974c23760cc3a047ac95ef851e25cf006f1b29332` |
| `s32_tanh_lbfgs_a50_lr1e3_corr080_prioritydrop` | `b63cbba70255b1c64319fabd129f12ec121ebeb517a572b211e71f9e11250b89` |
| `s32_tanh_lbfgs_a50_lr1e3_drop_flds_wind_psrf` | `2bf71f3a7916145c3b981df6bb397bd3fbda9e24990819c0409569c1c5c635df` |
| `s32_tanh_lbfgs_a65_lr1e3_full45` | `d212480a870c6d90b46613119c8c1361d468710026b206c9a978403b448b75c2` |
| `s32_tanh_lbfgs_a65_lr1e3_corr080_prioritydrop` | `e24260fc8d29789decae2fe2535afc542194b0ecb92cd3974833502695fc564e` |
| `s32_tanh_lbfgs_a65_lr1e3_drop_flds_wind_psrf` | `30d9425d7b3ae4a5a77169627c89b15d7d4ae3e03f0dd97e8c84980523bfc1a9` |
| `s32_tanh_lbfgs_a75_lr1e3_full45` | `25effdc21b80bc40333f74601f6357a31e5d5ef230c690d2bf6bfa474a915db2` |
| `s32_tanh_lbfgs_a75_lr1e3_corr080_prioritydrop` | `f58b7d86a0235bbbc0fc58e251bbcabb1c69609314029a12937dca266be38f78` |
| `s32_tanh_lbfgs_a75_lr1e3_drop_flds_wind_psrf` | `6f5faf1552101137304f277287931002b896a2b1c22d9518a045670af3e4b303` |

## Results and Decision

All feature schemas were identical across their five seeds: full45 retained 45 features,
`corr080_prioritydrop` retained 25, and `drop_flds_wind_psrf` retained the locked 32. Metrics are
shown as `TOTSOMC / TOTSOMN`; R2 entries are `median / minimum / IQR`. RMSE is the absolute median
validation RMSE, while RMSE ratio is the median across the five per-seed validation/training ratios.

| Variant | Validation R2 | Validation RMSE | RMSE ratio | Warnings | Decision |
| --- | --- | --- | --- | --- | --- |
| alpha 25 full45 | 0.8538/0.7847/0.0466 ; 0.8542/0.7870/0.0459 | 3668.8 / 367.5 | 0.9652 / 0.9661 | 0.2 / 0.2 | Reject: warning gate |
| alpha 25 corr080 | 0.8547/0.7794/0.0500 ; 0.8540/0.7797/0.0505 | 3708.9 / 370.6 | 0.9588 / 0.9578 | 0.2 / 0.2 | Reject: warning gate |
| alpha 25 drop32 | 0.8506/0.7775/0.0512 ; 0.8519/0.7814/0.0504 | 3696.1 / 370.4 | 0.9551 / 0.9565 | 0.2 / 0.2 | Reject: warning gate |
| alpha 35 full45 | 0.8291/0.7328/0.0564 ; 0.8286/0.7331/0.0584 | 4137.7 / 413.9 | 0.9518 / 0.9518 | 0.2 / 0.2 | Reject: warning gate |
| alpha 35 corr080 | 0.8276/0.7290/0.0619 ; 0.8270/0.7297/0.0618 | 4165.2 / 417.0 | 0.9425 / 0.9440 | 0.2 / 0.2 | Reject: warning gate |
| alpha 35 drop32 | 0.8259/0.7240/0.0599 ; 0.8258/0.7238/0.0586 | 4204.0 / 420.5 | 0.9509 / 0.9519 | 0.2 / 0.2 | Reject: warning gate |
| **alpha 50 full45** | **0.7935/0.6820/0.0646 ; 0.7937/0.6820/0.0612** | **4661.8 / 469.7** | **0.9499 / 0.9561** | **0 / 0** | **Pass; selected** |
| alpha 50 corr080 | 0.7896/0.6760/0.0672 ; 0.7906/0.6766/0.0669 | 4719.5 / 472.6 | 0.9531 / 0.9539 | 0 / 0 | Pass; lower mean median R2 |
| alpha 50 drop32 | 0.7906/0.6723/0.0657 ; 0.7904/0.6722/0.0661 | 4746.2 / 474.8 | 0.9533 / 0.9541 | 0 / 0 | Pass; lower mean median R2 |
| alpha 65 full45 | 0.7605/0.6432/0.0653 ; 0.7571/0.6437/0.0663 | 5106.3 / 510.9 | 0.9605 / 0.9614 | 0 / 0 | Reject: median and minimum R2 |
| alpha 65 corr080 | 0.7546/0.6395/0.0684 ; 0.7539/0.6400/0.0681 | 5165.8 / 517.1 | 0.9653 / 0.9661 | 0 / 0 | Reject: median and minimum R2 |
| alpha 65 drop32 | 0.7496/0.6343/0.0700 ; 0.7554/0.6348/0.0695 | 5183.6 / 518.9 | 0.9646 / 0.9655 | 0 / 0 | Reject: median and minimum R2 |
| alpha 75 full45 | 0.7393/0.6220/0.0680 ; 0.7391/0.6223/0.0704 | 5336.9 / 534.0 | 0.9637 / 0.9645 | 0 / 0 | Reject: median and minimum R2 |
| alpha 75 corr080 | 0.7358/0.6180/0.0669 ; 0.7350/0.6189/0.0667 | 5434.6 / 544.3 | 0.9723 / 0.9732 | 0 / 0 | Reject: R2; C RMSE ratio |
| alpha 75 drop32 | 0.7343/0.6123/0.0670 ; 0.7342/0.6130/0.0671 | 5450.7 / 545.8 | 0.9721 / 0.9730 | 0 / 0 | Reject: R2; C RMSE ratio |

Selected `s32_tanh_lbfgs_a50_lr1e3_full45`. It is the highest-ranked of three full gate passers
and exactly reproduces the iter008 baseline. Lower alpha `25` and `35` materially improved R2 and
absolute RMSE but caused one warning seed out of five for both targets under every feature policy,
so they are scientifically ineligible. Neither correlation pruning nor direct removal of the 13
FLDS/WIND/PSRF features improved the eligible alpha-50 control. No promotion is made.

## Proposed Iter010 Plan (Planning Only)

- Proposed sequential ID and retained baseline: `iter010`; retain
  `s32_tanh_lbfgs_a50_lr1e3_full45`.
- Evidence-derived hypothesis: the warning transition lies between alpha 35 (one warning seed per
  target) and alpha 50 (zero warnings). A full45-only bracket can test whether intermediate
  regularization retains some of alpha 35's R2/RMSE improvement without violating the zero-warning
  gate. Iter009 provides no evidence to continue the corr080 or drop32 arms.
- Tentative fixed controls and candidate matrix: same nine cases, `by_member`/`0.8`, two targets,
  seeds `10001-10005`, `(32,), tanh, lbfgs`, strict full45, disabled variance/correlation filters,
  stats-only output, and alpha `40,42.5,45,47.5,50` (control): five variants and 25 leaves. Record
  the warning seed/reason explicitly for every candidate.
- Tentative acceptance gates and ranking rule: apply the iter009 selected-baseline gates
  independently per target (median/minimum R2 within `0.01/0.02`, IQR within `0.02`, median
  per-seed RMSE ratio within `0.02`, zero warnings), report absolute RMSE, and rank passers by mean
  cross-target median R2, lower mean median RMSE ratio, then lower alpha.
- Proposed site/resources, preflight, reviewer, and retry boundaries: Puma `standard` /
  `chopinsong`, 10 CPUs (50 GB implied), 30 minutes, `N_JOBS=4`, per-task cache isolation,
  variant-local immutable artifacts, read-only reviewer, and bounded no-training preflight. One
  validation-only retry remains separate from one scheduler/resource retry per leaf; other
  application/code/configuration failures stop.
- Expected artifacts and decision record: `iterations/iter010.md`, `slurm/iter010/`, variant-local
  output roots, `summaries/iter010/`, and updated cumulative/handoff/registry records.
- Authorization boundary: a new runtime contract is required; do not scaffold, submit, or execute
  this proposal automatically.

## Proposed Iter010 Plan Revision (Planning Only)

Following the planning discussion after iter009 closeout, revise the proposal as follows while
preserving the original proposal above as provenance:

- Cross all three iter009 full-gate passers (`full45`, `corr080_prioritydrop`, and
  `drop_flds_wind_psrf`) with alphas `40,42.5,45,47.5,50` (alpha 50 is the control), using seeds
  `10001-10100`: 15 variants and 1,500 training leaves.
- Retain the existing validation permutation-importance method and `8` repeats. Aggregate every
  retained feature across the 100 seeds for each variant, separately for `TOTSOMC` and `TOTSOMN`,
  and in a combined cross-target view. Rank by median seed-rank, then median RMSE increase; include
  rank spread and R2-drop diagnostics.
- Retain `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, and single-thread BLAS/OpenMP. In the fixed-parameter
  LBFGS path, `n_jobs` is retained for compatibility with the legacy GridSearchCV path and does
  not create fitting workers; permutation importance remains sequential.
- This revision remains planning-only and requires a fresh iter010 runtime contract before
  scaffolding, code/configuration changes, submission, or execution.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Summary/stability artifacts copied to `summaries/iter009/`
- [x] `ITERATION_SUMMARY.md` updated with objective, settings, evidence, and conclusion
- [x] `registry.csv` updated
- [x] `handoff/CURRENT.md` updated
- [x] One authorized closeout commit created
