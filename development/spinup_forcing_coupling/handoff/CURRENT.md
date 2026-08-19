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

Iter015 is closed. Iter016 planning targets a multi-seed equifinal parameter ensemble for operational SR use. Do not execute until a fresh consolidated kickoff package is approved.

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

Iter016 remains `not_initialized`. Next step is to discuss and lock the equifinal-ensemble kickoff package (operational configuration per site, seed-health thresholds, ensemble schema).

## Next Iteration Plan (Planning Only)

This is planning-only. Do not initialize, scaffold, or submit until a fresh consolidated kickoff approval.

<!-- ITER016_PLAN_BEGIN -->
## Proposed Iter016 plan - multi-seed equifinal parameter ensemble for operational SR use

- Sequential ID: `iter016`
- Status: `not_initialized`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter016_<work_unit>`

### Evidence-derived objective and hypothesis

- Objective: define and characterize a **multi-seed equifinal parameter ensemble** for operational SR use at ABBY and JERC. Treat Iter015 hybrid `64×8000` chains as **mode-discovery evidence**, not as a calibrated posterior. Publish one representative parameter set per retained seed/mode, plus local cloud geometry and an SR predictive envelope across modes.
- Hypothesis: JERC physical-corner plots and cross-seed width (0.345–0.896 on hourly configs vs Iter011 TIM ~0.003) reflect **parameter equifinality for soil decomposition**: different `(k, rf)` clusters can yield nearly identical MAP SR (~0.667 RMSE) because SR alone does not identify the cascade. Multiple MCMC seeds are a practical way to discover distinct high-likelihood modes; an operational product should retain those modes as an ensemble rather than collapse to one vector.
- Evidence basis: Iter015 integrity passed but both sites are `inconclusive_seed_instability`; JERC has no tau-eligible configuration, R-hat ~2, bulk ESS ~250, and seed 9009 remains unhealthy on `hourly/0.75` (acceptance 0.089); MAP skill is flat across the six-configuration matrix; ABBY `daily/0.50` shows low cross-seed width (0.024) and may represent a single well-agreed mode rather than JERC-style seed separation.

### Upstream dependencies and trust assumptions

| Dependency | Role | Path | Identity |
| --- | --- | --- | --- |
| Iter015 production leaves | read-only mode-discovery evidence | `.../spinup_forcing_coupling_iter015/production/` | 36 `CAMPAIGN_PASS` leaves |
| Iter015 summaries and analysis | paired metrics, corners, skill | `summaries/iter015/`, scratch `analysis/` | aggregate + per-leaf diagnostics |
| Iter002 forcing SR | coupled likelihood reference | Iter002 release pickle | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Spinup `drop21_corr080` | coupled spinup | Iter012 spinup release | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| Iter015 frozen hybrid pools | provenance for walker geometry | ABBY `3627bb1d…`; JERC `40ac807e…` | Iter015 rebuild hashes |
| NEON v4 observations | SR target | eval v4 | ABBY `e5f7b679…`; JERC `a5507878…` |

### Bounded scope, work units, and exclusions

Proposed work sequence (planning only; exact work units to be locked at kickoff):

1. **Do not operationalize parameters from Iter015 8k chains as a calibrated posterior.** Chains remain discovery evidence under incomplete mixing.
2. **Treat SR as the operational target and parameters as a set.** The deliverable is a documented equifinal ensemble and SR predictive envelope, not a single “best” vector per site.
3. **Build a per-site mode inventory from existing multi-seed runs.** For each site and locked operational configuration (to be chosen at kickoff; JERC evidence points to hourly hybrid; ABBY TBD), retain one representative parameter set per healthy seed (MAP or documented local representative) plus the associated local cloud from post-burn samples.
4. **Apply explicit seed-health gates before retention.** Exclude seeds with clearly unhealthy sampler behavior (e.g. JERC 9009 on `hourly/0.75`: acceptance 0.089, tau-change 0.548). Document exclusion criteria in the kickoff package.
5. **Test claimed equifinality before labeling a mode physical.** Require near-equal log-posterior and SR skill across retained modes, parameter separation in decomposition space, and either cross-seed recurrence or confirmation that a mode is not a single-short-chain artifact. Modes failing these tests remain “candidate modes under incomplete mixing.”
6. **Within-seed clustering is diagnostic only, not the primary product generator.** If clustering is used at all, apply it to **pooled post-burn samples across seeds** to name modes; do not emit separate operational products from within-seed clusters by default.
7. **If unique parameters are required later**, that is out of scope for this line unless additional constraints (stocks, other fluxes, tighter priors) are added in a separate iteration.

Tentative work units: mode-inventory analysis on Iter015 artifacts; equifinality and seed-health audit; ensemble manifest authoring; SR envelope plots; handoff validation. Optional bounded re-run only if kickoff proves existing leaves insufficient for mode labeling.

Exclusions: no TIM revert; no new search; no `rank_dominated`; no 36-leaf matrix rerun; no within-seed clustering as primary operational product; no posterior promotion; no claim of unique soil-decomposition parameters from SR alone; no reuse of Iter015 8k chains as fully mixed posterior evidence without explicit kickoff language.

### Tentative acceptance gates and decision rule

- Integrity: reproducible mode inventory from Iter015 artifacts; overlap-aligned ELM precal on any replotted SR figures.
- Operational gates: each retained mode documents MAP (or representative), log-posterior, SR skill vs ELM precal, and local cloud stats; excluded seeds have recorded health rationale; equifinality claims are either supported or explicitly downgraded to “candidate under incomplete mixing.”
- Decision rule (tentative): `ensemble_supported` if at least two healthy, SR-equivalent modes are documented per site; `partial_ensemble` if only one healthy mode survives gates; `inconclusive` if modes cannot be separated from mixing artifacts. This replaces the Iter011 configuration-selection rule for this iteration.

### Proposed site and resource envelope

- Primary path: **offline analysis** on existing Iter015 scratch and Git summaries; Puma not required unless kickoff adds validation reruns.
- If validation reruns are added: Puma `chopinsong`/`standard`; `OLMT_puma` / micromamba `2.0.2-2`; scope locked at kickoff.
- Retry/cancellation: standard bounded analysis retry; no large matrix unless explicitly approved.

### Expected evidence, artifacts, and record updates

- Git summaries under `summaries/iter016/`: per-site mode inventory, equifinality audit, seed-health exclusions, SR predictive envelope, ensemble manifest schema.
- Optional scratch under `spinup_forcing_coupling_iter016/` if kickoff adds reruns.
- Records: `iterations/iter016.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`.

### Fresh consolidated kickoff-approval boundary

Planning only. Iter016 remains `not_initialized` until the user approves a complete consolidated kickoff package. Detailed operational configuration choice, seed-health thresholds, and ensemble schema will be discussed and locked at kickoff.
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
