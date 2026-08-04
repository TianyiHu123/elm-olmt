# Spinup-Forcing Coupling - Current Handoff

## Live State

- Active iteration: `iter001`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-08-03T18:19:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `approved` and exhausted at closeout
- Kickoff goal and stop boundary: establish the nine-site historical forcing-surrogate offline
  baseline for `SR`; continue through terminal accounting, aggregation, immutable gate evaluation,
  durable records, cross-record validation, and the approved closeout branch.
- User response and approval timestamp: exact response `Approve the package as written`; accepted
  `2026-07-31T20:15:05-07:00`.
- Confirmed HPC system and profile: Puma on `junonia.hpc.arizona.edu`;
  `development/hpc/puma.md`.
- Approved output root, layout, creation authority, and retention policy: exact root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to
  `spinup_forcing_coupling_iter001_pilot/`, `spinup_forcing_coupling_iter001_baseline/`, and
  `spinup_forcing_coupling_iter001_aggregate/`; retain the validated memmap/layout, pilot
  artifact/scalers, 100 production records, aggregates/plots, submitted material, logs, and
  accounting; no production models; temporary unbacked `/xdisk` storage.
- Locked dependencies, scope, exclusions, gates, and decision rule: exact approved plan
  `iterations/iter001_plan.md` SHA-256
  `74ee92bddb286d194a899785ac82de0647f74a058a74888b32f4890d88ac3433`; nine local case pickles,
  `SR`, `random_time_window`, train fraction 0.8, pilot seed 10001, production seeds 10001-10100,
  historical quick grid/three-fold CV/12 workers, complete declared input schema, direct output
  layout, complete metrics/diagnostics and eight-repeat pooled importance; no coupling, saved-model
  inference validation, feature selection, extra tuning, accuracy retraining, or gate changes;
  functional/data-integrity gates only and no numerical accuracy threshold.
- Recorded later amendments remain historical authority evidence: pilot OOM rerun at 150 GB /
  `N_JOBS=4` / four hours with memmap reuse; conditional 12-hour timeout retry unused; validator
  repair and validation-only job; replacement production array at 150 GB / `N_JOBS=4` / six hours /
  `1-100%10` with amended 206-task cap and no second OOM/application retry.
- Closeout branch: at most one bounded local closeout commit; no push; exclude raw outputs,
  memmap, models, logs, and unrelated `.README.md.swp`.

## Current Objective

Historical nine-site SR forcing-surrogate offline baseline

Nine sites; SR; random_time_window; seeds 10001-10100; pooled/per-site metrics; eight-repeat pooled permutation importance; no coupling or saved-artifact inference

## Best Evidence So Far

- Work type: `implementation`.
- Upstream dependency identities: source manifest SHA-256
  `1f71df1bf801b9fec152acdca063204554fbfe4fbb1d3d1562204d2bb10be7a6`; dependency manifest SHA-256
  `e718a00fcccb361c5e70ca89dc51b558aa7dc7611d4e198ef31b357ca08fb1c9`; production config SHA-256
  `ef9b837bcdeb85ea96438ac6e9321a37623aa13ac9156d9ed96d5c942c104246`; repository commit
  `2648998d4ceb08ecf72859a7d5200c0e3a5eb41d`.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter001`
- Preflight job `23467631` and composite pilot (`23473876` training + `23475958` validation) passed.
- Failed first production array `23476014` remains classified: leaves 1-15 `OUT_OF_MEMORY 0:125`,
  leaves 16-100 cancelled before execution under universal-defect authority.
- Replacement production array `23476164`: all 100 leaves `COMPLETED 0:0`; exact-100 eligibility
  passed at `2026-08-03T14:49:08-07:00`.
- Aggregation job `23489654`: `COMPLETED 0:0` in 23 seconds; `AGGREGATION_PASS` with
  `warning_fraction=0.000000`; aggregate SHA-256
  `b75510b4f1fc64109d5be942e93d4af1662bd1c7a2a07c565f065245ce69f0a3`; aggregate-validation SHA-256
  `63a0b23bf9337c762e4d6583eac4ce4ac67efc01ba904847a71666c6b6fc9611`.
- Pooled test R2 mean/median `0.945275` / `0.945557`; pooled test RMSE mean/median `0.210745` /
  `0.209810`; pooled R2 gap mean/median `0.012502` / `0.012155`; pooled RMSE ratio mean/median
  `1.254273` / `1.244005`; pooled overfitting warning fraction `0.0`.
- Acceptance result: `pass`
- Decision: Technical offline baseline validated; predictive quality characterized; coupling readiness not established

## Current Risks or Blockers

- No active Iter001 jobs remain.
- `/xdisk` retention is temporary and unbacked; raw outputs stay outside Git.
- Iter001 does not establish coupling readiness or saved-artifact inference validation.
- The Iter002 planning-only proposal grants no runtime authority until a consolidated kickoff
  package is approved.

## Next Action

1. Iter001 is closed; the Iter002 planning-only proposal below is recorded and matches
   `iterations/iter001.md`.
2. Present one consolidated kickoff package built from that plan and obtain approval before
   initializing `iter002`.

## Next Iteration Plan (Planning Only)

### Planning Status and Authority Boundary

- Proposed iteration: `iter002`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime, scheduler, directory-creation, and commit authority: none

This planning-only proposal grants no initialization, Python, compute, scheduler, retry,
cancellation, or commit authority. It becomes the finalized plan only when included unchanged
in an approved consolidated kickoff package. Copy this section unchanged into
`handoff/CURRENT.md`.

### 1. Sequential ID and work type

- Sequential ID: `iter002`
- Work type: `implementation`
- Proposed run slugs: `spinup_forcing_coupling_iter002_preflight`,
  `spinup_forcing_coupling_iter002_release`, and
  `spinup_forcing_coupling_iter002_validate`

### 2. Evidence-derived objective and optional hypothesis

Objective: publish one trusted, versioned `forcing-surrogate-v1` artifact from a full-data
refit under the locked Iter001 scientific configuration, with spinup-style saved-artifact
inference validation and full-data in-sample feature-importance evidence, so later coupling
work can depend on a stable standalone forcing artifact.

Evidence basis: Iter001 closed `pass` with technical offline baseline validation and
predictive-quality characterization (pooled test R2 mean/median about `0.945`; overfitting
warning fraction `0.0`), but explicitly excluded saved-artifact inference validation and
coupling readiness. Spinup Iter012 released `spinup-surrogate-v1` and validated only
forcing-bridge design-matrix compatibility while awaiting a real forcing artifact.

Optional hypothesis: a full-data refit that first reproduces the Iter001 seed-`10001` split
metrics within spinup-style tolerances, then fits all rows into a versioned artifact with
load/inference gates and full-data importance sidecars, is sufficient to unblock later
coupling development without performing live coupling in Iter002.

### 3. Proposed upstream dependencies and trust assumptions

| Dependency | Role | Trust / lock |
| --- | --- | --- |
| Closed Iter001 records and manifests | Scientific baseline and provenance | Immutable; reuse nine cases, target `SR`, complete ordered schema, quick grid, CV, and split protocol |
| Iter001 validated memmap and layout | Feature matrix reuse | Read-only; lock exact memmap/layout hashes before execution |
| Iter001 pilot stats / validation | Reproduction reference | Seed-`10001` pooled metrics and artifact identity are reproduction-gate targets |
| Nine case pickles and forcing/restart data | Input provenance | Same trust model as Iter001; re-verify identity and schema in preflight |
| `OLMT_puma` and `development/hpc/puma.md` | Runtime and site | Puma; account `chopinsong`; partition `standard` |
| Repository source at kickoff | Implementation surface | Lock commit and bounded Iter002 source manifest during preparation |

Spinup `drop32` / `drop21_corr080` artifacts and live forcing-bridge SR coupling checks are out
of dependency scope for Iter002.

### 4. Bounded scope, work units, and exclusions

Locked `forcing-surrogate-v1` detail configuration to embed in the artifact and sidecars:

| Field | Locked value |
| --- | --- |
| `schema_version` | `forcing-surrogate-v1` |
| `release_version` | `iter002-v1` |
| Cases (order) | ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL (`*_ppe6_I20TRCNPRDCTCBC`) |
| Target | `SR` only |
| Forcing families | `PRECTmms`, `FSDS`, `FLDS`, `TBOT`, `RH`, `WIND`, `PSRF`, plus all existing engineered features |
| Spinup-state inputs | `TOTSOMC`, `TOTSOMN` |
| Parameters | exact ordered `ensemble_parms` across the nine cases |
| Feature schema | complete Iter001 ordered schema with no filtering; store names and schema hash |
| Hyperparameters | historical `--quick-grid`; `CV_FOLDS=3` |
| Workers | `N_JOBS=4` |
| Reproduction split | `random_time_window`; train fraction `0.8`; seed `10001` |
| Fit scope for released weights | `full_data` after successful reproduction gate |
| Importance | 8-repeat pooled permutation importance on the full-data fitted weights; scored on the full training population; `random_state=10001`; not seed-`10001` holdout importance |
| Inference tolerances | `rtol=1e-10`, `atol=1e-8` |
| Output contract | Iter001 direct `--outputdir` layout |

In scope:

1. Public versioned loader and predict API (and thin CLI if needed) that accepts only
   `forcing-surrogate-v1`.
2. Release tooling that reuses the locked Iter001 memmap/layout read-only; reproduces the
   seed-`10001` split fit and gates pooled metrics against the Iter001 pilot within
   `rtol`/`atol`; performs the full-data refit; writes the versioned pickle,
   `artifact_manifest.json`, and validation report; and computes full-data in-sample
   8-repeat pooled permutation importance with release tables and plots.
3. Fresh-process load and batch-inference validation with spinup-style positive and negative
   gates.
4. Iteration-specific Slurm material, manifests, validators, synthetic tests, durable records,
   handoff validation, and closeout.

Proposed finite work units:

| # | Work unit | Purpose |
| --- | --- | --- |
| 1 | Preflight | Imports, environment/dependency/memmap identity, and schema fixtures; no training |
| 2 | Release | Reproduction gate, full-data artifact build, and full-data importance |
| 3 | Validate | Fresh-process load, inference agreement, schema failure gates, and sidecar identity |

Nominal scheduler-task count: 3. Provisional hard cap: 5, allowing one minimal preflight
correction/rerun and one same-scope scheduler/resource retry across release/validate.

Exclusions: live spinup-forcing coupling or real bridge SR integration; 100-seed production
ensemble retraining; feature selection, filtering, or importance-based promotion;
hyperparameter search beyond the locked quick grid; numerical accuracy or coupling-readiness
thresholds beyond functional and inference-integrity gates; recomputing seed-`10001` held-out
importance already provided by Iter001; durable archival beyond `/xdisk` retention of
validated release outputs.

Importance labeling: Iter002 importance is full-data in-sample permutation importance of the
released weights. It is diagnostic characterization only, not held-out generalization
evidence. Iter001 remains the held-out seed-`10001` and 100-seed importance baseline.

### 5. Tentative acceptance gates and decision rule

Overall pass only if all hold:

1. Authoritative terminal accounting exists for every task and every failure is classified.
2. Reproduction gate: seed-`10001` split refit matches locked Iter001 pilot pooled metrics
   within `rtol=1e-10` and `atol=1e-8`; exact cases, target, split, schema, and quick-grid
   provenance verify. This stage does not require an importance product.
3. Full-data importance gate: complete finite 8-repeat pooled permutation importance over the
   ordered schema for the full-data model; tables and plot exist; feature order matches the
   schema.
4. Release artifact gate: `forcing-surrogate-v1` pickle exists with the embedded detail
   configuration above, models, scalers, training layout, and provenance; colocated manifest
   hashes match; fit scope is recorded as `full_data`.
5. Inference gate: fresh-process load succeeds; pre-save versus post-load predictions agree
   within `rtol`/`atol`; malformed, legacy, or wrong-schema inputs fail closed; batch
   inference returns finite `SR`.
6. Compact `summaries/iter002/` decision evidence is complete, and the four durable records
   agree after closeout validation.

Decision rule: pass means the standalone full-data forcing artifact is identity-locked and
inference-validated for later coupling development, with full-data importance characterized.
No predictive-accuracy threshold is imposed. Pass does not claim live coupling readiness or
spinup-bridge integration.

### 6. Proposed site and resource envelope, preflight, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / env | `chopinsong` / `standard` / `OLMT_puma` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling` |
| Directory creation | only `spinup_forcing_coupling_iter002_preflight/`, `spinup_forcing_coupling_iter002_release/`, and `spinup_forcing_coupling_iter002_validate/` |
| Retention | validated artifact, manifest, validation report, importance tables/plots, submitted material, logs, and accounting on `/xdisk` (temporary, unbacked); Iter001 memmap remains shared read-only; no Git of large binaries |
| Preflight | 1 CPU, derived about 5 GB, 15 minutes |
| Release | `--mem=120G` (Puma-derived CPUs), `N_JOBS=4`, walltime 10 hours; read-only Iter001 memmap reuse |
| Validate | at most 10 CPUs and about 50 GB class, at most 1 hour; exact shape finalized at kickoff from fixture size |
| Review | independent read-only agent required before preflight and release |
| Retry | one minimal preflight correction/rerun; one same-scope scheduler/resource retry per failed release or validate job; no automatic application, schema, numerical, OOM, or timeout retry |
| Cancellation | recorded Iter002 job IDs only, under a proven universal pre-execution defect |
| Stop | after terminal accounting, immutable gates, durable records, cross-record validation, and the approved closeout branch |

Resource rationale from Iter001: corrected `N_JOBS=4` peaks were about 100-105 GB, so 120 GB
is plausible with thin headroom; 12-worker 120 GB shapes OOM'd. Longest production leaf was
4.70 h and the pilot was 3.85 h; 10 hours provides practical headroom for reproduction,
full-data fit, and full-population importance without the tighter 6-hour risk.

### 7. Expected evidence, artifacts, and record updates

- Versioned artifact such as
  `.../spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl`
- `artifact_manifest.json` and `validation_report.json`
- Full-data importance JSON/CSV and summary plot in the release directory and
  `summaries/iter002/`
- Reproduction and inference gate JSON
- Public loader/predict code and tests in the repository
- Canonical scripts, configs, manifests, and validators under `slurm/iter002/`
- Finalized `iterations/iter002.md`, `ITERATION_SUMMARY.md` append, `registry.csv` row, and
  rebuilt `handoff/CURRENT.md`
- Handoff validator identity, command, output, and passing result

### 8. Fresh consolidated kickoff-approval boundary

Before initialization or execution, present one complete consolidated kickoff package that
includes this plan unchanged and states the runtime contract, exact output-root authority,
lifecycle authorities, resource and retry boundaries, cancellation scope, outside-sandbox
`sbatch` / job-scoped monitoring-accounting / bounded `scancel` authorities, and whether one
closeout commit is authorized. Obtain one explicit user approval of that complete package.
A goal, this planning section, or remembered command approval grants none of those
authorities.

## Next Session Start Protocol

1. Read this handoff and `WORKFLOW.md`.
2. Read `iterations/iter001.md` and confirm its Proposed Next-Iteration Plan matches this
   handoff unchanged.
3. Do not initialize `iter002` until a fresh consolidated kickoff package built from that plan
   is approved.
4. Inspect Git state and external artifact retention before any new work.

## Artifact References

- Current/latest report: `development/spinup_forcing_coupling/iterations/iter001.md`
- Approved plan: `development/spinup_forcing_coupling/iterations/iter001_plan.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter001/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter001/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
