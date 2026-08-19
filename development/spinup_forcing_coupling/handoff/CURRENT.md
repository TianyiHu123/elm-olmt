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
- Last updated: `2026-08-19T15:22:00-07:00`

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

Iter015 is closed. Iter016 kickoff is **approved** (`2026-08-19`): experimental multi-seed MAP ensemble procedure at ABBY `daily/0.50` and JERC `hourly/0.75` with nine seeds, Tier-A acceptance retention, reusable diagnostic tools, and a comprehensive closeout report. Do **not** initialize scaffold, submit jobs, or execute until the user explicitly authorizes workflow start.

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

Iter016 remains `not_initialized` (kickoff approved; workflow not started). Next step when authorized: initialize `iterations/iter016.md`, scaffold `slurm/iter016/` and reusable `tools/`, independent review, then preflight through closeout per the approved package below.

## Next Iteration Plan (Kickoff Approved — Do Not Execute Yet)

<!-- ITER016_PLAN_BEGIN -->
## Iter016 — multi-seed MAP ensemble operational experiment (kickoff approved)

- Sequential ID: `iter016`
- Status: `not_initialized` (kickoff approved; workflow not started)
- Work type: `implementation` (experimental operational procedure; evidence collection for future operational policy)
- Run slug: `spinup_forcing_coupling_iter016_<work_unit>`
- User approval timestamp: `2026-08-19T15:22:00-07:00`

### Evidence-derived objective and hypothesis

- Objective: run a **bounded multi-seed MAP ensemble experiment** at fixed site-specific configurations to establish an operational procedure for collecting best parameter sets per healthy seed, documenting seed-health exclusions, and diagnosing whether retained MAPs show **equifinality** or **convergence**. Treat `64×8000` hybrid-init chains as mode-discovery evidence, not a calibrated posterior. Publish one MAP vector per Tier-A-healthy seed plus a diagnostic package (not a success gate).
- Hypothesis: additional seeds at JERC `hourly/0.75` will discover distinct high-likelihood decomposition modes with near-equal SR skill (equifinality under SR-only constraints); ABBY `daily/0.50` may instead show seed agreement (convergence). Site-specific outcomes are valid; equifinality is not required for iteration success.
- Evidence basis: Iter015 integrity passed with `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`; JERC cross-seed width ~0.485 on `hourly/0.75` with flat MAP SR (~0.667) and seed 9009 unhealthy (acceptance 0.089); ABBY `daily/0.50` unique non-dominated with low width (0.024).

### Locked experimental design

| Site | Config | Resolution | DE-scale | Seeds |
| --- | --- | --- | --- | --- |
| ABBY | `daily/0.50` | daily | 0.50 | `9009–9017` (9) |
| JERC | `hourly/0.75` | hourly | 0.75 | `9009–9017` (9) |

- Chain: `64×8000`, checkpoints every 2000; transformed coordinates; `de_mixture`; `site_hybrid_pool_reuse_v1`
- Initialization: `hybrid_high_l_maximin` q=0.90; frozen pools ABBY `3627bb1d…`, JERC `40ac807e…` (Iter015 rebuild identity)
- **Rerun all nine seeds** in iter016 scratch for uniform provenance (operational procedure)

### Upstream dependencies and trust assumptions

| Dependency | Role | Path / identity |
| --- | --- | --- |
| Iter002 forcing SR | coupled likelihood | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Spinup `drop21_corr080` | coupled spinup | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| ABBY Iter012 Revision1 ledger | hybrid rebuild input | `ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b` |
| JERC Iter012 Revision1 ledger | hybrid rebuild input | `25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d` |
| Iter015 frozen hybrid pools | walker geometry provenance | ABBY `3627bb1d…`; JERC `40ac807e…` |
| NEON v4 observations | SR target | ABBY `e5f7b679…`; JERC `a5507878…` |
| Iter015 summaries | prior evidence / contrast | `summaries/iter015/` (read-only reference) |

### Tier A filter (strict retention only)

| Gate | Criterion |
| --- | --- |
| A1 | `CAMPAIGN_PASS` and full production artifact contract |
| A2 | Mean walker acceptance ∈ **[0.20, 0.50]** |

All Tier-A-passing seeds: MAP vector saved to ensemble inventory. Tier-A-failing seeds: documented exclusion rationale. Wasserstein, τ-change, R̂/ESS, and equifinality metrics are **diagnostic only**, not retention gates.

### Equifinality / convergence diagnostics (non-gating)

**Layer 1 — MAP cross-seed (primary):** on Tier-A-healthy seeds, pairwise parameter distance/Wasserstein (full physical + decomposition `(k, rf)` subspace), MAP SR RMSE spread, overlap-aligned MAP SR timeseries overlay with ELM precal reference.

**Layer 2 — per-seed post-burn clouds (confirmatory):** subsampled walkers per seed; seed-to-seed cloud Wasserstein; between-seed / within-seed width ratio; seed-colored physical corner. Compare seed clouds pairwise; do not pool all walkers without seed structure.

**Diagnostic labels (informational, not pass/fail):**

| Label | Heuristic |
| --- | --- |
| `converged` | max pairwise MAP W &lt; 0.05; MAP SR spread &lt; 0.01 |
| `equifinal_candidate` | MAP SR spread &lt; 0.01; decomposition W ≥ 0.05 between ≥2 groups |
| `mixed` | partial separation |
| `insufficient_retained` | &lt;2 Tier-A seeds |

Cloud layer adds `confirmed` / `revised` / `unconfirmed` relative to the MAP label.

### Bounded scope, work units, and exclusions

| # | Work unit | Submitters | Tasks |
| --- | --- | ---: | ---: |
| 1 | Materialization | — | — |
| 2 | Preflight | 1 | — |
| 3 | Pool rebuild ABBY | 1 | — |
| 4 | Pool rebuild JERC | 1 | — |
| 5 | Production array ABBY | 1 | 9 |
| 6 | Production array JERC | 1 | 9 |
| 7 | Analysis (orchestrates reusable tools) | 1 | — |
| 8 | Handoff validation | 1 | — |

Nominal **8 submitters, 18 production tasks**; cap ~25 (one preflight correction; ≤3 array-index recoveries per site; one analysis retry; one handoff retry).

**Production scheduling:** one Slurm **array job per site** (`#SBATCH --array=0-8`); array index maps to `SEEDS=(9009 9010 9011 9012 9013 9014 9015 9016 9017)`. Per-task resources: 16 CPU / 4 h / `standard` / `chopinsong`.

**Approved output root and layout:**

`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter016/` with `preflight/`, `pool_rebuild/{abby,jerc}/`, `production/{abby,jerc}/<config>/seed_<seed>/`, `analysis/`. Array submitters live under `production/abby/` and `production/jerc/`.

**Exclusions:** no 36-leaf matrix; no TIM revert; no new search; no `rank_dominated`; no posterior promotion; no within-seed clustering as primary operational product; no equifinality success gate; no claim of unique decomposition parameters from SR alone.

### Reusable tools (`development/spinup_forcing_coupling/tools/`)

Implement as JSON-spec CLIs (merge-ready to main code later); `slurm/iter016/analyze_iter016.py` orchestrates only.

| Tool | Purpose |
| --- | --- |
| `ensemble_seed_health.py` | Tier A acceptance filter + per-seed sampler stats |
| `ensemble_map_inventory.py` | MAP extraction, log-posterior, SR skill; retained inventory |
| `ensemble_equifinality_diagnostics.py` | MAP cross-seed matrix; cloud geometry; diagnostic labels |
| `plot_ensemble_sr_overlay.py` | MAP SR timeseries overlay + ELM precal |
| `plot_ensemble_physical_corner.py` | Seed-colored post-burn physical corner |

Schemas: `spinup-forcing-coupling-ensemble-seed-health-v1`, `ensemble-map-inventory-v1`, `ensemble-equifinality-diagnostics-v1`. Reuse `fixed_length_mcmc_diagnostics.py` and physical-corner helpers where applicable. Update `tools/README.md` at closeout.

### Acceptance gates (integrity only — no equifinality success gate)

- Preflight `PREFLIGHT_PASS`; pool rebuild hashes match Iter015 identities
- All 18 array tasks terminal-accounted
- Tier A applied to every seed with documented rationale
- Ensemble inventory and full diagnostic package complete
- **Comprehensive closeout report** finalized (see below)
- Handoff four-record validation pass

Overall acceptance result: `pass` when integrity and completeness gates pass regardless of per-site equifinality/convergence label.

### Closeout report requirement

At closeout, produce **`summaries/iter016/ITER016_REPORT.md`** — a comprehensive report with evidence and conclusions, following the depth of prior iteration reports (`ITER015_REPORT.md` pattern). Required sections:

1. **Closeout identity** — iteration ID, objective, bounded scope, overall acceptance result
2. **Integrity and provenance** — preflight, rebuilds, array jobs, pool hashes, source/dependency manifests
3. **Per-seed production evidence** — acceptance, Tier A pass/fail, MAP skill, exclusion rationale for failed seeds
4. **Ensemble inventory** — all Tier-A-retained MAP parameter sets per site
5. **Equifinality / convergence diagnosis** — Layer 1 MAP results, Layer 2 cloud confirmation, per-site diagnostic label with supporting metrics and figures
6. **Site-specific rationale** — interpret ABBY vs JERC patterns; contrast with Iter015 where relevant
7. **Integrated conclusion** — what this experiment establishes for a future operational MAP-ensemble procedure; explicit limitations (8k chains, SR-only constraints, no posterior promotion)
8. **Next experiment routing** — planning-only suggestions; no unauthorized execution

Supporting tables and JSON artifacts under `summaries/iter016/` must be cited in the report. Copy required evidence from scratch `analysis/` into Git summaries before closeout commit.

### Site and resource envelope

- HPC: UArizona Puma; `development/hpc/puma.md`; account `chopinsong`; partition `standard`
- Environment: `OLMT_puma` / micromamba `2.0.2-2`
- Resources: preflight 4 CPU / 30 min; rebuild 8 CPU / 2 h each; array task 16 CPU / 4 h; analysis 4 CPU / 2 h; handoff 2 CPU / 30 min
- Closeout: one local closeout commit authorized; no push unless user requests

### Expected evidence, artifacts, and record updates

- Git summaries under `summaries/iter016/`: `ITER016_REPORT.md`, seed health, MAP inventory, equifinality diagnosis, plots, ensemble manifests
- Scratch under `spinup_forcing_coupling_iter016/`
- Records at closeout: `iterations/iter016.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`
- Reusable tools under `tools/` with README examples

### Workflow start boundary

Kickoff is approved. Iter016 remains `not_initialized` until the user explicitly authorizes workflow start (scaffold, review, preflight, submission). Do not materialize, submit, or execute before that authorization.
<!-- ITER016_PLAN_END -->

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter015.md`, and `development/hpc/puma.md`.
2. Treat Iter015 as closed. Do not reuse the Iter015 package for new jobs.
3. Iter016 kickoff is approved in the `ITER016_PLAN_BEGIN` block below. Do not initialize or execute until the user explicitly authorizes workflow start.
4. When authorized, initialize from the approved package: `iterations/iter016.md`, `slurm/iter016/`, reusable `tools/`, independent review, then preflight through closeout including `summaries/iter016/ITER016_REPORT.md`.
5. Inspect Git and scheduler state before any new execution.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter015.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter015/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter015/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter015`
