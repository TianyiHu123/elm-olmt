# Spinup-Forcing Coupling - Current Handoff

Iteration ID `iter017`; Status `planned`; Work type `implementation`; Objective `coupled optimization-pipeline consolidation and regression`; Bounded scope `1 preflight; 4 initialization/rebuild jobs; 12 optimization leaves; 4 reporting jobs; 1 handoff validation`; Overall acceptance result `pending`; Decision `pending`

## Live State

- Active iteration: `iter017`
- Last closed iteration: `iter016`
- Status: `in_progress`
- Phase: `preflight`
- Active job IDs: none; `23608697` and `23608738` preflight attempts terminal `FAILED 1:0`
- Site profile: `development/hpc/puma.md`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression`
- Last updated: `2026-08-20T19:16:22-07:00`

## Best Evidence So Far

- Iter016 provides the settled ABBY/JERC configurations and multi-seed evidence.
- Iter017 additional correction 3 passed independent review
  (`ec05d3f6486a58168d6906c97cf275726952eb70`, root-relative compile paths);
  refresh the preflight package and submit its final authorized retry; no Iter017 result exists.

## Gate Result and Decision

- Overall acceptance: pending.
- Decision: pending.
- No posterior promotion is in scope.

## Current Risks or Blockers

- `/xdisk` products are temporary and unbacked.
- Extensive code revision requires source lock, independent review, and correction-cycle accounting before each authorized retry.

## Next Action

Finish the implementation/source lock, then obtain independent review before materializing and submitting preflight.

## Finalized Iter017 Plan and Runtime Contract

### Iter017 — coupled optimization-pipeline consolidation and regression

**Status:** `planned`; the user approved the complete package at `2026-08-20T19:16:22-07:00`.
The authoritative detailed contract and live ledger are in `iterations/iter017.md`.

#### Objective and evidence basis

Finalize a clear, maintainable coupled forcing-MCMC pipeline and test it end to end before the
separate nine-site operational campaign (proposed `iter018`). Iter013--016 settled the ABBY/JERC
configurations and demonstrated the need for reproducible multi-seed products, but their
iteration scripts and reusable tools remain split across development paths. Iter017 is an
implementation/integrity regression, not a scientific calibration campaign.

#### Locked planning scope

1. Keep generic `model_ELM/MCMC.py` isolated. Retain parallel coupled modules
   `MCMC_forcing.py`, `coupling_pipeline.py`, `mcmc_geometry.py`, `mcmc_diagnostics.py`, and
   `mcmc_spinup_modes.py`; clean their contracts/imports and record a retirement inventory. Do
   not create a new package.
2. Extract raw-chain artifact writing from `MCMC_forcing.py` into neutral
   `model_ELM/mcmc_artifacts.py`; move post-burn selection into `mcmc_diagnostics.py`; retire
   only code proven iteration-bound, with a replacement or archival rationale.
3. Consolidate `initialize_pipeline.py` and `optimize_surrogate_forcing.py` as canonical
   initialization/rebuild and optimization adapters. Add standalone `report_optimization.py`
   for a separate reporting job, materialized with its source snapshot into the run directory.
   Training and forcing-surrogate runtime are compatibility-tested only.
4. Use one immutable universal YAML configuration with `shared`, `initialization`,
   `optimization`, and `reporting` sections. Each manually submitted stage consumes its allowed
   subset and writes a resolved stage manifest; no pipeline launcher is in scope.
5. Preserve existing optimization-leaf products. Add standardized user-facing products under
   `reports/`; reporting source/logs/receipts live under `postprocess/`.
6. Draft four YAML examples and a README outline under
   `development/spinup_forcing_coupling/examples/iter017/`. After evidence exists, record
   validation under `summaries/iter017/` and promote only validated instructions to `README.md`.

#### Regression matrix and joint contract

Each path is `initialization/rebuild -> three seeded optimization leaves -> dependent reporting`.
Use 64 walkers, 2,000 steps, checkpoints at 1,000/2,000, and seeds `9009, 9010, 9011`.
These chains are regression-only and establish no convergence, posterior, or scientific claim.

| Path | Initialization | Target | Seeds |
| --- | --- | --- | --- |
| `abby_fresh_daily_050` | single-site fresh search | ABBY daily / DEMove 0.50 | 9009--9011 |
| `jerc_rebuild_hourly_075` | single-site ledger rebuild | JERC hourly / DEMove 0.75 | 9009--9011 |
| `joint_abby_jerc_daily_050` | joint fresh search | ABBY+JERC daily / DEMove 0.50 | 9009--9011 |
| `joint_abby_jerc_hourly_075` | joint fresh search | ABBY+JERC hourly / DEMove 0.75 | 9009--9011 |

Joint mode uses one common candidate pool, shared parameter vector, and joint-MAP from the summed
objective. It writes one joint parameter/diagnostic package plus site-specific skill and
time-series products. `fit_error=true` estimates one shared `sigma_SR` bound from all valid
sites; site-order invariance is required.

Per-seed reporting always runs. Multi-seed reporting writes Tier-A retention/exclusion evidence,
parameter inventory, geometry, and SR envelope only when at least two seeds are retained;
otherwise it writes explicit `insufficient_retained` evidence and never substitutes unhealthy
seeds.

#### Outputs, dependencies, acceptance, and boundaries

The proposed root is
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression/`,
with `preflight/`, four path directories, and `handoff/`. Each path contains `campaign.yaml`,
`initialization/`, `optimization/seed_<seed>/`, `postprocess/`, and `reports/`. `/xdisk` is
temporary and unbacked; raw chains, NetCDF products, and plots remain outside Git.

Reports require provenance receipts; per-seed acceptance, finite/bounds, saturation,
autocorrelation/steps-per-tau, tau-change, and checkpoint diagnostics; per-site valid count,
RMSE, bias, R2, KGE, and likelihood-consistent log score; physical-corner and prediction plots;
and conditional multi-seed products. Merge parameter text into
`reports/best_parameters/parameter_sets.{csv,txt}` with Tier-A status/provenance. Retain one
exact-input CLM NetCDF per completed seed under `reports/best_parameters/clm_params/`; joint
files are named by joint seed and are not merged.

Lock validated forcing and `drop21_corr080` spinup artifacts, ABBY/JERC observations, and
`fit_error=true` by hashes, ordered schema, site identity, YAML, and manifests at kickoff. Exclude
retraining, observation refresh, TIM revert, tuning, posterior promotion, nine-site operation,
push, PR, and merge actions.

Proposed Puma envelope: `chopinsong`/`standard`; preflight 4 CPUs/30 min; initialization/rebuild
8 CPUs/4 h; each optimization leaf 16 CPUs/4 h; reporting 4 CPUs/2 h; handoff validation
2 CPUs/30 min. Lock array/account concurrency at kickoff.

Integrity acceptance requires module/retirement records, adapter/YAML/static checks,
generic-MCMC and forcing-training import compatibility, joint order invariance, terminal evidence
for all four paths, retained default leaf outputs, safe standardized reporting, parameter-export
validation, and proof that every draft example ran. Sampler health, Tier-A count, skill, and
convergence are descriptive only.

Allow one unchanged scheduler/resource retry per initialization job, optimization leaf, reporting
job, and handoff validator. Separately allow up to three revised-code correction-and-resubmission
cycles for each of preflight, an affected production/reporting path, and handoff. Every cycle
requires failure classification; exact file/rationale/source-identity/job-ID logging in
`iter017.md`; repeated relevant checks and independent review; and rematerialized affected copies.
Identity, configuration, or provenance mismatches stop further affected work; cancellation is
limited to recorded current-iteration IDs under the approved conditions.

#### Records and commit sequence

After a fresh approved kickoff, create the Iter017 record/scaffolding, obtain independent review,
and version-lock submitted copies before Slurm work. The proposed sequence is this planning-only
commit, one explicitly authorized implementation/source-lock commit before preflight, and one
explicitly authorized closeout commit after final validation. Root README promotion follows a
passing regression; the all-nine-site operational example waits for Iter018.

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter017.md`, and `development/hpc/puma.md`.
2. Inspect Git and scheduler state before any submission.
3. Route from the recorded Iter017 phase and contract; do not seek another kickoff package unless a material term changes.

## Artifact References

- Latest report: `development/spinup_forcing_coupling/iterations/iter017.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter017/` (pending eligible results)
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression`
