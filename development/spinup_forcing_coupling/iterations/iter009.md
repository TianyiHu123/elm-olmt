# iter009 - ABBY and JERC sampler-geometry pilot

## Status

- Iteration ID: `iter009`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter009_preflight`,
  `spinup_forcing_coupling_iter009_initialize`,
  `spinup_forcing_coupling_iter009_{b,t,i,m,tim}_campaign`, and
  `spinup_forcing_coupling_iter009_validate`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Summary path: `development/spinup_forcing_coupling/summaries/iter009`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Started: `2026-08-10T20:29:27-07:00`
- Closed: `2026-08-11T14:20:00-07:00`

## Finalized Plan

The finalized plan is the complete Iter009 proposal copied unchanged from the closed Iter008
report into `handoff/CURRENT.md` under **Finalized Iter009 Plan**. That body, including the
five-arm matrix, transformation contract, initialization preprocessing, integrity and geometry
gates, resources, retries, exclusions, evidence, and closeout branch, is immutable for this
iteration.

- Objective: determine whether Iter008 poor mixing primarily arises from parameter scaling and
  bounds, initial walker placement, or the default stretch proposal, without changing the
  physical posterior.
- Hypothesis: bounded geometry interventions can improve acceptance, terminal overlap, stable
  autocorrelation estimates, and cross-seed agreement at both ABBY and JERC.
- Scope: five arms (`B`, `T`, `I`, `M`, `TIM`), separate ABBY/JERC chains, three seeds per
  site-arm, 64 walkers x 8,000 steps, 15 dimensions, 16 workers, checkpoints and immutable
  dual-coordinate chains. This is exactly 30 campaign leaves.
- Exclusions: no change to likelihood, prior, physical bound, surrogate, observation, case,
  site window, coupled schema, feature, or scientific model; no joint MCMC, predictive campaign,
  automatic proposal tuning, or scientific-quality/convergence claim from this pilot.
- Decision: all integrity gates must pass. Geometry qualification and selection use only the
  immutable rules in the finalized plan; no least-bad arm is selected if none qualifies.
- Stop: terminal accounting, immutable integrity evaluation, geometry qualification and route,
  durable records, cross-record validation, and the authorized closeout branch.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approve for the complete iter009 package`; `2026-08-10T20:29:27-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Iter009 sampler-geometry pilot; 33 nominal scheduler tasks across eight submissions and 42-task hard cap; stop as finalized above |
| Confirmed HPC system and site profile | University of Arizona Puma, `development/hpc/puma.md` |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; creation limited to the eight finalized Iter009 run directories; `/xdisk` is temporary and unbacked; raw/large outputs remain outside Git |
| Locked dependencies, scope, exclusions, gates, and decision rule | Complete finalized plan in `handoff/CURRENT.md`; forcing, spinup, observations, Iter008 chains, cases, likelihood, priors, bounds, matrix, seeds, and gates are immutable |
| Lifecycle authority | Initialization, preparation, scoped source/config changes, run-directory creation, independent read-only review, compute-node preflight/initialization, submission, continuous monitoring/accounting, evaluation, records, validation, and closeout |
| Resources and retry boundaries | Preflight 2 CPUs/10 GB/30 min; initialize 4 CPUs/20 GB/1 h; campaign leaves 16 CPUs/80 GB/4 h/16 workers; validate 4 CPUs/20 GB/2 h; exact retry limits as finalized |
| Cancellation scope | Recorded Iter009 jobs only; only the finalized proven universal or arm-specific pre-execution defect conditions |
| Outside-sandbox authority | Locked `sbatch` and contract-allowed resubmissions; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, job-history, and job-limits; bounded `scancel` under the stated rule |
| Closeout branch | One bounded local closeout commit after final validation; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | SHA-256 |
| --- | --- | --- | --- | --- |
| Iter002 forcing surrogate | Coupled `SR` | external Iter002 release | `forcing-surrogate-v1` | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 spinup | Coupled state | external Iter012 `drop21_corr080` release | `spinup-surrogate-v1` | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| ABBY / JERC observations | Likelihood targets | NEON v4 evaluation files | `SR:SR_err` | `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` / `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` |
| Iter008 raw chains | Initialization source | external Iter008 ABBY / JERC campaigns | unthinned physical chains | `5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87` / `34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080` |

- Preparation base: clean `b086a212390af5f198a27799b92d8bc5ce09a321`; planning commit
  `dff5da3373e9e61800e9a65fdd28fa0344066d5b` is the clean initialization HEAD.
- Execution source is locked only by the reviewed Iter009 source manifest after authorized
  preparation; it must contain only contract-controlled paths.
- Environment: `OLMT_puma`; exact micromamba module/version is a preflight requirement.

## Provenance and Job Ledger

| Work unit | Job IDs | State | Notes |
| --- | --- | --- | --- |
| preflight | `23538732`, `23538737`, `23538751` | terminal `COMPLETED 0:0` | User approved one additional launcher-only correction/review/rerun after the original retry boundary: `23538732` lacked `pytest`; `23538737` lacked repository `PYTHONPATH`; reviewed retry-2 copy `23538751` passed in 28 s using 2 CPUs / 10 GB, with eight all-pass smoke cases and 512 total proposals. |
| initialize | `23538764` | terminal `COMPLETED 0:0` | completed in 15 s using 4 CPUs / 20 GB; both pools pass the ≥640 requirement and all 12 immutable initialization bundles exist |
| B array | `23538767_[1-6]`, recovery 1 `23538796_[1-6]`, recovery 2 `23538844_[1-6]` | recovery 2 terminal `COMPLETED 0:0` | original all-six failure occurred before model work from uppercase `${INITIALIZATION}`. Recovery 1 reached coupled-site preparation then failed before sampling on non-existent HDF backend access. The reviewed HDF-creation recovery completed all six leaves. |
| T array | `23538909_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| I array | `23538920_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| M array | `23538931_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| TIM array | `23538937_[1-6]` | terminal `COMPLETED 0:0` | all six final leaves complete |
| validate | `23540890`, retry `23540912` | retry terminal `COMPLETED 0:0` | first attempt failed pre-evaluation from missing repository import context; reviewed v5 launcher corrected `cd`/`PYTHONPATH`; final validator passed 30 leaves and ten packages |

## Independent Read-Only Review

- Reviewer: independent read-only agent `iter009_review`.
- Reviewed source manifest and outcome: `pass` on `2026-08-11`; the reviewer confirmed all six
  original findings were corrected. A subsequent delta review caught a Bash `readonly` loop
  reassignment before submission; it was corrected and the final delta outcome was `pass`.
- Reviewed source lock: `development/spinup_forcing_coupling/slurm/iter009/iter009_source_manifest.sha256`
  (15 execution-source entries; mutable ledgers excluded). Static evidence: `git diff --check`,
  `bash -n` for all five submission/materializer scripts, and `sha256sum -c` all passed.
- A subsequent review of the validation-evaluator correction initially blocked two immutable
  decision-rule defects: transformed-arm log-probability screens used sampler rather than
  physical posterior values, and the selection comparator did not implement the less-than-10%
  tau tie-break. Both were corrected; re-review passed. The validator now emits the ten required
  site-arm packages, common-target R-hat/terminal-band evidence, the conditional selection rule,
  and report-only transformed-coordinate saturation tables. The unused original validation copy
  is preserved; reviewed `submit_validate_iter009_v2.slurm` is byte-identical to canonical source.
- The new closeout validator initially blocked because it searched broad strings rather than
  proving exact four-record field agreement and controlled-path ownership. It was strengthened
  to compare standardized identity, acceptance, decision, dependencies, and next state across
  the report, cumulative summary, registry, and handoff, and to require exact observed changed
  paths before and after the closeout commit. Re-review passed.

## Execution and Diagnostics

- Static validation: source-manifest, shell syntax, and diff checks passed before materialization.
- Preflight `23538732`: terminal `FAILED 1:0`, 11 s, 2 CPUs/10 GB; environment-only missing
  `pytest` before scientific/model execution. The one authorized minimal rerun `23538737` is
  terminal `FAILED 1:0`, 13 s, 2 CPUs/10 GB, before smoke execution with
  `ModuleNotFoundError: No module named 'model_ELM'`. User then explicitly approved one additional
  launcher-only correction, re-review, and third preflight submission. `23538751` is terminal
  `COMPLETED 0:0`; `smoke/preflight_result.json` records 8 pass results across ABBY/JERC and all
  four mechanisms, 32 walkers x 2 steps = 512 proposals.
- Campaign accounting is currently 46 submitted tasks before final validation: the nominal 33
  plus two explicitly approved extra preflight attempts and two explicitly approved six-leaf B
  application recoveries. This exceeds the original 42-task cap; the closeout integrity decision
  must therefore classify the user-approved exception explicitly rather than silently treating
  the cap as satisfied.
- The complete campaign source is already running; the evaluator-only source correction is
  independently reviewed and staged solely for the pending validation work unit.

## Validation, Evaluation, and Decision

- Iteration ID: `iter009`
- Status: `completed`
- Work type: `implementation`
- Objective: `ABBY and JERC sampler-geometry pilot`
- Bounded scope: `ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011`
- Overall acceptance result: `pass`
- Decision: `investigate_multimodality_nonidentifiability_likelihood_or_model_structure`
- Next state: `No next iteration is proposed; any follow-up requires a new approved package to investigate multimodality, non-identifiability, likelihood discontinuity, or model structure.`

All 30 final leaves are terminal `COMPLETED 0:0`, with required HDF, final raw chains, metadata,
hashes, diagnostics, and checkpoints. Validation `23540912` is terminal `COMPLETED 0:0` and
emitted all ten site-arm packages. Integrity and provenance passed, but no arm met every immutable
geometry qualification criterion: the best overlap screens occur in TIM, while its other required
screens still fail. The original 42-task cap was exceeded only through user-approved exception
attempts: final submitted count is 48, including the failed first validation attempt; this is
recorded as an exception rather than treated as cap satisfaction.

The complete arm-by-arm diagnostic interpretation, causal assessment, and proposed follow-up
experiments are in
[`summaries/iter009/ITER009_REPORT.md`](../summaries/iter009/ITER009_REPORT.md).
