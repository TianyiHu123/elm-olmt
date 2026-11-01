# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan: `development/three_stage_surrogate/PLAN.md`
- Current/active locked SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Phase/alignment: progression item 5 GPP development; `aligned_with_scoped_deviation`
- Approved deviation: fixed published all-819 predicted-C/N inputs for both GPP fit and validation;
  validation is GPP-stage conditional, not end-to-end held-out evidence.

## Live State

- Latest iteration: `iter005`
- Active iteration: none
- Work type: `implementation`
- Status: `completed`
- Phase: `closed`
- Package state: `closed`
- Active job scope: none; every recorded job has authoritative terminal accounting
- Active monitoring: none; revised validation job `24488737` terminal `COMPLETED 0:0`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-31T22:17:39-07:00`

## Active Kickoff Package and Runtime Authority

- Goal/stop: four sequential jobs—combined preparation, smoke, 655/164 baseline, final validation;
  continue through terminal accounting, immutable gates, concise records, one no-push commit, and
  the user decision `freeze_baseline` or `optimization_required`.
- User approval: `Full package approved` at `2026-10-31T16:37:48-07:00`, after the complete revised
  package combined preflight/materialization/materialization validation.
- System/profile: UA Puma `junonia.hpc.arizona.edu`; `development/hpc/puma.md`;
  `chopinsong/standard`; `OLMT_puma`; no GPU.
- Root/layout: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter005_abby_jerc_gpp_baseline`;
  `runs/{prepare,smoke,baseline,validation}`; temporary unbacked `/xdisk`.
- Locked contract: exact identities, first-655/last-164 development split, fixed 43-feature schema,
  physical GPP, fixed `(128,)` ReLU/Adam MLP, fixed upstream handoff, all valid hours, technical
  gates/metrics, zero fixed-test and zero spinup execution.
- Authority: bounded implementation/tests/material, independent reviews, four submissions,
  monitoring/accounting/evaluation, up to three additional same-contract submissions, bounded
  cancellation, concise records, and one no-push commit.
- Resources: prepare 4 CPUs/20 GB/4 h; smoke 4 CPUs/20 GB/2 h; baseline total 200 GB/derived 40 CPUs/
  16 h; validation 8 CPUs/40 GB/4 h. OOM/timeout or resource increase requires fresh approval.
- Outside-sandbox: locked `sbatch`; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`,
  `job-limits`; bounded `scancel` for recorded Iter005 jobs only under approved conditions.

## Closeout Result and Best Evidence

Iter005 is closed with result `pass` and decision `freeze_baseline`. Preparation job `24485863` completed `0:0` in
`00:03:55` with 17.76 GB peak memory; no-training preflight and fresh-process validation passed for
100,442,160 rows, 43 features, full hashes, and 20 reconstructed source rows. Prepared manifest is
`acd9a7bb...416b`, validation report is `fbb6f181...b9e4`, and the cache is eligible. Smoke job
`24485909` completed `0:0` in 28 seconds and separately used 230,400 fit rows and 57,600 validation
inference rows; report SHA-256 is `58799d42...836f`.
Baseline job `24485952` completed `0:0` in 1:34:30 with 32,771,276 KiB batch MaxRSS; the model
stopped after 29 iterations with zero convergence warnings and wrote hash-matching artifact,
predictions, and 12-row metric material.
Validation attempt 1 job `24488350` failed `1:0` after 23 seconds at the locked reload-equivalence
gate because the public raw-feature path supplied float64-scaled values to an estimator trained on
the prepared float32 design. Baseline artifacts/hashes were unchanged. A bounded non-scientific
interface correction now restores float32 at the estimator boundary; regenerated source manifest
is `d8e887f9...87d8`, submitted manifests match, and independent re-review passed with no concerns.
Final attempt 4 preserved diagnostics showing max direct frozen-model reload difference
`4.00543212890625e-05`, max public source-row difference `2.6702880859375e-05`, and max scaled-row
difference `1.7881393432617188e-06`. The frozen model itself therefore changes slightly with
float32 GEMM batch shape: stored predictions used 250,000-row chunks while validation used eight
rows. The locked `rtol=atol=1e-6` gate failed; no baseline artifact was accepted.
The user-approved batch-aware revision then passed in job `24488737`: three original prediction
chunks covering 692,160 rows replayed within unchanged `1e-6` tolerance (max absolute difference
`3.812002717040741e-06`); public batches 1/7/1,000 were finite and exactly same-batch repeatable;
cross-batch difference was `3.337860107421875e-06`; all 12 metric rows were independently
recomputed and matched. Technical validation passed. The full hourly/daily train/validation table
is in `development/three_stage_surrogate/summaries/iter005/summary.md`; pooled validation
hourly R2/RMSE/MAE is `0.911104/4.025672/2.151374`, and pooled daily is
`0.860052/2.366163/1.393406`. Daily metrics come from the same hourly artifact.

## Current Risks or Blockers

- No active blocker. `/xdisk` remains temporary and unbacked; fixed-upstream validation is
  GPP-stage conditional rather than end-to-end held out. Robustness is not yet established.

## Next Action

Recover this closed handoff and obtain fresh consolidated approval for Iter006 before any
initialization or execution. Iter006 should test fixed-configuration robustness first and consider
optimization only if that evidence is poor.

## Artifact References

- Closed report: `development/three_stage_surrogate/iterations/iter005.md`
- Registry: `development/three_stage_surrogate/registry.csv`
- Cumulative summary: `development/three_stage_surrogate/ITERATION_SUMMARY.md`
- Summary destination: `development/three_stage_surrogate/summaries/iter005/`
- Canonical scripts: `development/three_stage_surrogate/slurm/iter005/`
- Scratch output: approved Iter005 root above

## Next Iteration Plan (Planning Only)

### Iter006 - ABBY/JERC fixed-upstream GPP robustness

- Proposed sequential ID and work type: `iter006` / `experiment`.
- Campaign alignment: progression item 5 under locked `PLAN.md` SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`, with the same scoped
  deviation: use the published all-819 predicted-C/N handoff on both sides and label evidence
  `fixed_upstream_gpp_stage`, not end-to-end held out. No campaign-plan amendment is proposed.
- Objective: characterize the frozen Iter005 43-feature, hourly-trained `(128,)` ReLU/Adam GPP
  configuration on 20 fresh synchronized 655/164 development-member splits before deciding whether
  configuration optimization is needed.
- Inputs: immutable snapshot `r0001`, exact 819-development/205-fixed-test split, Iter004
  `release_0001` predicted-C/N handoff, and validated Iter005 interfaces/cache. Each repetition must
  fit feature/target scalers and optimizer stopping state from its 655 training members only; the
  remaining 164 members are inference-only. Fixed-test members remain forbidden.
- Proposed work units: bounded preflight and split/cache validation; separate smoke; throttled
  20-repetition robustness array; deterministic aggregation; independent validation; concise
  closeout records. Preserve full repetition metrics, convergence warnings, coverage/gaps, and
  declared quantiles for hourly and same-artifact complete-day metrics by site and pooled.
- Frozen terms: feature order and history semantics, physical GPP target and units, no clipping,
  model configuration and seed policy, fixed-upstream interpretation, batch-aware inference
  contract, and evaluation definitions. Daily metrics remain derived from hourly predictions; no
  daily model is trained.
- Decision rule: retain the frozen configuration if repeated-split performance and stability are
  acceptable; otherwise conclude `optimization_required` and plan a later configuration screen.
  Iter006 itself performs no configuration search and creates no all-819 GPP release.
- Exclusions: no spinup refit/execution, fixed-test access, feature selection, GPP configuration
  optimization, all-819 GPP fit/release, SR surrogate, full-chain robustness, observations,
  likelihood, MCMC, campaign-plan edit, or push.
- Kickoff requirements: recover current records; lock exact split seeds, output root, array
  throttle, resources and time limits using Iter005's observed memory/runtime as evidence; declare
  retry/cancellation bounds and monitoring; obtain independent read-only review and fresh
  consolidated user approval before initialization, repository Python, directory creation, or
  scheduler action.
- Stop condition: planning only. This proposal grants no runtime, scheduler, retry, directory,
  commit, or execution authority.
