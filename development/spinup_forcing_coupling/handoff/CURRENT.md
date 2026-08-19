# Spinup-Forcing Coupling - Current Handoff

Closeout identity: Iteration ID `iter015`; Status `completed`; Work type `implementation`; Objective `hybrid-init Iter011 configuration matrix at ABBY and JERC`; Bounded scope `1 preflight; 2 hybrid rebuilds; 36 64x8000 leaves; 1 analysis; 1 handoff validation; user-directed ELM-precal plot makeup`; Overall acceptance result `pass`; Decision `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`

## Live State

- Active iteration: `iter015`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Objective: `hybrid-init Iter011 configuration matrix at ABBY and JERC`
- Bounded scope: `1 preflight; 2 hybrid rebuilds; 36 64x8000 leaves; 1 analysis; 1 handoff validation; user-directed ELM-precal plot makeup`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter015`
- Last updated: `2026-08-18T19:14:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `approved`; iteration closed
- Kickoff goal and stop boundary: Execute Iter015 through authorized closeout; 41 nominal tasks, cap 52; stop after terminal accounting, analysis, four-record validation, and the authorized closeout commit
- User response and approval timestamp: `approves the complete package`; `2026-08-18T15:28:00-07:00`. Addendum `2026-08-18T18:09:00-07:00`: after jobs finish, makeup replots of `Predictions_SR_posterior.png` to include ELM precal.
- Confirmed HPC system and profile: UArizona Puma; `development/hpc/puma.md`; host `junonia.hpc.arizona.edu`; account `chopinsong`; partition `standard`
- Approved output root, layout, creation authority, and retention policy: `/xdisk/.../spinup_forcing_coupling_iter015/` with `preflight/`, `pool_rebuild/{abby,jerc}/`, `production/{abby,jerc}/{hourly,daily}_{0.50,0.75,1.00}/seed_{9009,9010,9011}/`, `analysis/`; makeup logs in `analysis/replot/`
- Locked dependencies, scope, exclusions, gates, and decision rule: Iter002 forcing `8d139b32…`; spinup `1427dc56…`; ABBY ledger `ec8b34ed…`; JERC ledger `25382a57…`; ABBY hybrid pool `3627bb1d…`; JERC hybrid identity `40ac807e…`; `hybrid_high_l_maximin` q=0.90; `site_hybrid_pool_reuse_v1`; Iter011 decision rule; no posterior promotion
- Lifecycle and outside-sandbox authority: prepare through closeout; `sbatch` for locked submissions/resubmissions; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; `scancel` only for recorded Iter015 IDs under cancellation conditions
- Resources, retry boundaries, and cancellation scope: preflight 4 CPU/30 min; rebuild 8 CPU/2 h; leaf 16 CPU/4 h; analysis 4 CPU/2 h; handoff 2 CPU/30 min; makeup replot 8 CPU/6 h; one preflight correction; one rebuild retry each; ≤6 leaf recoveries; one analysis retry; one handoff retry; recorded Iter015 IDs only
- Closeout branch: one local closeout commit authorized; no push

## Current Objective

Iter015 is closed. Do not execute Iter016 until a fresh consolidated kickoff package is approved.

## Best Evidence So Far

- Preflight `23589106`, rebuilds `23589146`/`23589147`, 36 production leaves, makeup `23589330`, and analysis `23589339` all COMPLETED `0:0`. Analysis `23589325` FAILED missing `elm_precal` (`application_gate`) and was repaired by makeup.
- ABBY hybrid pool `3627bb1df152e2f4356787a6634c96dfe533bc2ca55a30a7aa90fc4d9fd50592`; JERC hybrid pool `40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df`.
- Site decisions: `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`. No selected configuration. No posterior promotion.
- ABBY eligible only `hourly/1.00`; unique non-dominated `daily/0.50`. JERC eligible none; unique non-dominated hourly `0.50/0.75/1.00`.
- Makeup replotted all 36 `Predictions_SR_posterior.png` figures with overlap-aligned ELM precal; ELM RMSE ABBY `6.6896`, JERC `1.5752`.
- Handoff validator `23589486` COMPLETED `0:0` `00:00:22`; output `ITER015_HANDOFF_VALIDATE_PASS leaves=36 ABBY=inconclusive_seed_instability JERC=inconclusive_seed_instability` and `HANDOFF_VALIDATE_SLURM_PASS`. Command: `cd .../analysis && ./submit_handoff_after_analysis.sh` (canonical `submit_handoff.sh` collides with analysis receipts).
- Overall acceptance result: `pass`
- Decision: `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`

## Current Risks or Blockers

- No active blocker.
- `/xdisk` products are temporary and unbacked.
- Coupled `case.output['SR']` is full-forcing length; ELM precal overlays must use overlap indices.
- Aggregate R̂/ESS fields are null; W is reported and is not a veto.

## Next Action

Iter016 remains `not_initialized`. Obtain a fresh consolidated kickoff approval before any initialization or scheduler work.

## Next Iteration Plan (Planning Only)

This is planning-only. Do not initialize, scaffold, or submit until a fresh consolidated kickoff approval.

<!-- ITER016_PLAN_BEGIN -->
## Proposed Iter016 plan - longer hybrid MCMC at the two Iter015 interesting configurations

- Sequential ID: `iter016`
- Status: `not_initialized`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter016_<work_unit>`

### Evidence-derived objective and hypothesis

- Objective: test whether a longer fixed-length hybrid chain removes the Iter015 tau-change veto at the two scientifically interesting configurations, then apply the Iter011 decision rule at those configs only.
- Hypothesis: Iter015 hybrid `64×8000` left ABBY `daily/0.50` uniquely non-dominated but ineligible, and left JERC with no tau-eligible configuration. The 8k length, not the hybrid pool, may be driving `max_tau_change > 0.20`.
- Evidence basis: Iter015 integrity passed; ABBY `inconclusive_seed_instability` with eligible `hourly/1.00` and unique non-dominated `daily/0.50`; JERC `inconclusive_seed_instability` with unique non-dominated hourly `0.50/0.75/1.00` and no eligible configs; JERC hourly/0.75 remains the Iter014 hybrid control.

### Upstream dependencies and trust assumptions

| Dependency | Role | Path | Identity |
| --- | --- | --- | --- |
| Iter002 forcing SR | coupled likelihood | Iter002 release pickle | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Spinup `drop21_corr080` | coupled spinup | Iter012 spinup release | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| Iter015 ABBY hybrid pool | walker source | `.../iter015/pool_rebuild/abby/artifacts/candidate_pool.npz` | `3627bb1df152e2f4356787a6634c96dfe533bc2ca55a30a7aa90fc4d9fd50592` |
| Iter015 JERC hybrid pool | walker source | `.../iter015/pool_rebuild/jerc/artifacts/candidate_pool.npz` | `40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df` |
| Frozen Iter012 Revision1 ledgers | provenance only | Iter012 revision1 | ABBY `ec8b34ed…`; JERC `25382a57…` |
| NEON v4 observations | likelihood obs | eval v4 | ABBY `e5f7b679…`; JERC `a5507878…` |

### Bounded scope, work units, and exclusions

- Work units: 1 preflight; 6 MCMC leaves (ABBY `daily/0.50` seeds `9009/9010/9011`; JERC `hourly/0.75` seeds `9009/9010/9011`); 1 analysis; 1 handoff validation.
- Locked chain: reuse Iter015 hybrid pools under `site_hybrid_pool_reuse_v1`; proposed length `64×32000` unless the kickoff package locks a different fixed length.
- Required plot contract: overlap-aligned ELM precal overlay on `Predictions_SR_posterior.png` and `elm_precal` skill rows.
- Exclusions: no TIM, no new search, no `rank_dominated`, no 36-leaf matrix rerun, no reuse of Iter015 8k chains as production evidence, no posterior promotion unless Iter016 gates pass.

### Tentative acceptance gates and decision rule

- Completeness: preflight pass; 6 `CAMPAIGN_PASS` leaves; analysis; handoff validation.
- Interpretability: `max_tau_change ≤ 0.20` on every seed of a configuration.
- Decision rule: sites independent; Iter011 labels (`preferred_configuration_supported`, `default_configuration_retained`, `inconclusive_*`); W/R̂/ESS reported not veto; no posterior promotion unless a site is preferred or default-retained.

### Proposed site and resource envelope

- Puma `chopinsong`/`standard`; `OLMT_puma` / micromamba `2.0.2-2`.
- Tentative resources: preflight 4 CPU / 30 min; leaf 16 CPU / 12 h; analysis 4 CPU / 2 h; handoff 2 CPU / 30 min.
- Retry: one preflight correction; ≤2 leaf recoveries; one analysis retry; one handoff retry.
- Cancellation: recorded Iter016 job IDs only; universal pre-execution defect or user emergency.
- Stop: terminal accounting, analysis, four-record validation, and the authorized closeout branch.

### Expected evidence, artifacts, and record updates

- Scratch tree `spinup_forcing_coupling_iter016/` with `preflight/`, `production/{abby,jerc}/...`, `analysis/`.
- Git records: `iterations/iter016.md`, `summaries/iter016/`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`.

### Fresh consolidated kickoff-approval boundary

Planning only. Iter016 remains `not_initialized` until the user approves a complete consolidated kickoff package.
<!-- ITER016_PLAN_END -->

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter015.md`, and `development/hpc/puma.md`.
2. Treat Iter015 as closed. Do not reuse the Iter015 package for new jobs.
3. If starting Iter016, present a fresh consolidated kickoff package copied from the planning-only proposal above.
4. Inspect Git and scheduler state before any new execution.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter015.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter015/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter015/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter015`
