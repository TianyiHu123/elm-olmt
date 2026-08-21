# Spinup-Forcing Coupling - Current Handoff

Closeout identity: Iteration ID `iter016`; Status `completed`; Work type `implementation`; Objective `multi-seed MAP ensemble operational experiment`; Bounded scope `1 preflight; 2 hybrid rebuilds; 2 production arrays (18 tasks); 1 analysis; 1 handoff validation`; Overall acceptance result `pass`; Decision `ABBY=equifinal_candidate_all_tier_a; JERC=equifinal_candidate_partial_tier_a`

## Live State

- Active iteration: none (Iter016 closed)
- Last closed iteration: `iter016`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter016`
- Last updated: `2026-08-19T18:00:00-07:00`

## Best Evidence So Far

- Iter016: 18/18 production leaves; ABBY 9/9 Tier A with MAP SR spread `0.005`; JERC 6/9 Tier A with spread `0.001`; both sites diagnostic `equifinal_candidate`.
- Reusable ensemble tools under `tools/` with README.
- Comprehensive report: `summaries/iter016/ITER016_REPORT.md`.

## Gate Result and Decision

- Overall acceptance: `pass` (integrity gates).
- Decision: `ABBY=equifinal_candidate_all_tier_a; JERC=equifinal_candidate_partial_tier_a`.
- No equifinality success gate; no posterior promotion.

## Current Risks or Blockers

- `/xdisk` products are temporary and unbacked.
- Analysis required one correction submission beyond nominal retry (tool schema vs production JSON); recorded in iteration report.
- Handoff submitter shares receipt filenames with analysis submitter — use direct `sbatch` for handoff or separate receipt paths in future iterations.

## Next Action

Read-only bootstrap for Iter017 kickoff when user approves a new consolidated package. No execution authority until kickoff approval.

## Next Iteration Plan (Planning-Only — Not Approved)

### Iter017 — coupled optimization-pipeline consolidation and regression

**Status:** `not_initialized`. This planning-only proposal authorizes no initialization,
code/scaffold creation, Python execution, scheduler action, external-directory creation, retry,
cancellation, or commit beyond the present planning commit. A fresh consolidated kickoff package
remains required.

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

1. Read this handoff, `WORKFLOW.md`, `iterations/iter016.md`, and `development/hpc/puma.md`.
2. Inspect Git and scheduler state before any submission.
3. Present consolidated kickoff package for Iter017 or other user-directed work.

## Artifact References

- Latest report: `development/spinup_forcing_coupling/iterations/iter016.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter016/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter016`
