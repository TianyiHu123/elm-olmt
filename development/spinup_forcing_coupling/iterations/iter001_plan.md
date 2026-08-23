# Iter001 Planning-Only Proposal - Historical Forcing-Surrogate Offline Baseline

## Planning Status and Authority Boundary

- Proposed iteration: `iter001`
- Proposed work type: `implementation`
- Status: planning only; not initialized
- Consolidated kickoff package: not approved
- Runtime and scheduler authority: none
- Closeout authority: proposed, not approved

This file records the user-developed Iter001 proposal. It is not the authoritative initialized
iteration report and does not grant initialization, Python, compute, scheduler, retry,
cancellation, directory-creation, commit, or closeout authority. Formal initialization must use
`iterations/iter001.md` only after the user approves one complete consolidated kickoff package.

## Goal and Bounded Scope

Establish a reproducible nine-site offline training baseline for the historical forcing surrogate
before any coupling with the spinup surrogate.

- Predict `SR` only.
- Validate offline training and characterize predictive behavior across seeded time-window splits.
- Do not couple to the spinup surrogate.
- Do not validate saved-artifact inference.
- Do not perform hyperparameter tuning beyond the locked historical quick grid.
- Do not perform feature filtering, ablation, candidate selection, performance-driven retraining,
  or post-result gate revision.
- Proposed lifecycle stop boundary: terminal accounting, aggregation, immutable gate evaluation,
  durable records, cross-record validation, and the approved closeout branch.

## Locked Data and Model Configuration

### Cases and target

Use these nine case pickles, with their exact paths, sizes, hashes, referenced forcing data,
restart data, schemas, and provenance to be locked during preparation:

1. `ABBY_ppe6_I20TRCNPRDCTCBC`
2. `JERC_ppe6_I20TRCNPRDCTCBC`
3. `OSBS_ppe6_I20TRCNPRDCTCBC`
4. `SOAP_ppe6_I20TRCNPRDCTCBC`
5. `RMNP_ppe6_I20TRCNPRDCTCBC`
6. `TALL_ppe6_I20TRCNPRDCTCBC`
7. `TEAK_ppe6_I20TRCNPRDCTCBC`
8. `WREF_ppe6_I20TRCNPRDCTCBC`
9. `YELL_ppe6_I20TRCNPRDCTCBC`

The only prediction target is `SR`.

### Split and seeds

- Split mode: `random_time_window`.
- Training fraction: `0.8`; the remaining `0.2` is the held-out test population.
- Runtime seed expression: `RANDOM_SEED=$((10000 + SLURM_ARRAY_TASK_ID))`.
- Pilot: array task `1`, seed `10001`.
- Production: full array `1-100%5`, seeds `10001-10100`.
- Production intentionally repeats pilot seed `10001`; pilot and production outputs must remain
  separate.

### Historical model and inputs

- Use the existing `--quick-grid` with three-fold cross-validation and 12 GridSearch workers.
- Raw forcing families: `PRECTmms`, `FSDS`, `FLDS`, `TBOT`, `RH`, `WIND`, and `PSRF`.
- Include all existing engineered features derived from those forcing families.
- Include all parameter columns supplied by the cases.
- Include historical spinup-state inputs `TOTSOMC` and `TOTSOMN`.
- Require exact parameter-name and parameter-order equality across all nine cases using
  `ensemble_parms`.
- Store the complete ordered feature schema in the memmap layout and result provenance.
- Do not change or filter the feature schema after results are observed.

## Proposed Implementation Scope

1. Remove the forcing trainer's hard-coded `UQ_output` path component. Make `--outputdir` the
   exact parent of `<run-name-or-case>/surrogate_forcing/`.
2. Update the forcing CLI help, forcing wrappers, relevant README material, examples, and tests to
   use that direct-output contract.
3. Do not change the spinup trainer or unrelated MCMC output layout.
4. Add train/test R2 and RMSE, R2 gap, RMSE ratio, overfitting warnings, and pooled and per-site
   diagnostics to the forcing result schema.
5. Add held-out permutation importance for every production seed, using eight repeats across the
   complete ordered input schema. Seed the permutation procedure reproducibly.
6. Aggregate feature importance by test-RMSE increase, test-R2 decrease, median rank, top-10
   frequency, and positive-importance frequency.
7. Add iteration-specific validation, aggregation, plotting, configuration, manifest, and Slurm
   material under `development/spinup_forcing_coupling/`.
8. Add targeted synthetic tests for split/seed behavior, direct output paths, metric and warning
   formulas, importance output, schemas, and aggregation invariants.

The primary agent is the sole writer, scheduler operator, decision maker, and closeout owner. A
different agent must perform the workflow-required independent review and remain read-only.

## Proposed Output Root, Layout, and Retention

The exact proposed external root is:

```text
/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling
```

Directory-creation authority would be limited to these new children:

```text
spinup_forcing_coupling_iter001_pilot/
spinup_forcing_coupling_iter001_baseline/
spinup_forcing_coupling_iter001_aggregate/
```

The pilot will create the shared feature memmap and layout. After they pass validation, the full
production array will reuse them read-only. Each production task will still create its own seeded
split, train its own model, and calculate its own metrics and importance.

Retain:

- the shared validated memmap and layout;
- the pilot seed-10001 trained model artifact and scalers;
- exactly 100 production per-seed JSON records;
- aggregation JSON and CSV tables;
- metric-distribution and feature-importance plots;
- submitted scripts, configurations, manifests, logs, and accounting evidence.

Production seeds write statistics and importance only; they do not retain 100 model artifacts.
Raw and large outputs remain outside Git. Puma `/xdisk` is temporary and unbacked; retention in
this root is not an archival or backup claim.

## Proposed Metrics and Overfitting Definitions

Record the following for every seed:

- pooled nine-site train/test R2 and RMSE;
- per-site train/test R2 and RMSE;
- pooled R2 gap, RMSE ratio, and overfitting warning;
- per-site R2 gaps, RMSE ratios, and overfitting warnings; and
- pooled held-out permutation importance for the complete input schema.

Use the existing spinup-surrogate overfitting definitions unchanged:

- `R2 gap = train R2 - test R2`;
- `RMSE ratio = test RMSE / train RMSE`;
- warn when `R2 gap > 0.15` and train R2 is above `0.6`; or
- warn when `RMSE ratio > 1.5`.

The production overfitting fraction is the number of warned production seeds divided by 100.
Aggregate the full distributions of R2, RMSE, R2 gap, and RMSE ratio rather than reporting only
the warning fraction. Feature importance remains pooled across the nine sites; separate per-site
permutation importance is excluded.

## Proposed Immutable Acceptance Gates and Decision Rule

### Pilot gate

The seed-10001 pilot passes only if:

1. its job reaches terminal `COMPLETED` state with exit code `0:0`;
2. exact cases, target, seed, split, input schema, and quick grid are verified;
3. pooled and per-site train/test R2 and RMSE are finite;
4. pooled and per-site overfitting diagnostics are computable;
5. pooled permutation importance is complete and finite for the locked feature schema;
6. the feature memmap and layout validate and are reusable read-only;
7. the pilot model artifact and scalers exist and pass identity/schema checks; and
8. expected configuration, provenance, logs, and output records validate.

The pilot does not run offline inference. Poor but finite scores remain baseline evidence and do
not block production. An operational or data-integrity gate failure stops before the production
array.

### Production and overall gate

The production baseline passes functionally only if:

1. exactly 100 eligible production records exist for seeds `10001-10100` with no missing or
   duplicate seed;
2. every record has matching dependency, source, configuration, seed, split, and ordered-schema
   provenance;
3. every record contains complete finite pooled and per-site metrics and overfitting diagnostics;
4. every record contains complete finite pooled permutation importance for the ordered schema;
5. the aggregate tables and plots validate; and
6. all jobs have authoritative terminal accounting and every failure is classified.

No numerical accuracy threshold is imposed. The decision distinguishes technical offline
training validation from predictive-quality characterization. Iter001 does not claim that the
surrogate is accurate enough for coupling and does not validate loading or inference from the
saved pilot artifact. The resulting distributions may support predeclared coupling-readiness
thresholds in later work.

## Proposed Puma Site and Resource Contract

- HPC system: University of Arizona Puma.
- Site profile: `development/hpc/puma.md`.
- Account: `chopinsong`.
- Partition: `standard`.
- Environment: `OLMT_puma`.
- Repository root: `/xdisk/chopinsong/tianyihu/elm-olmt`.
- Read-only planning snapshot: clean branch `feature/surrogate_coupling` at
  `2648998d4ceb08ecf72859a7d5200c0e3a5eb41d` on `junonia.hpc.arizona.edu`.

Proposed resource envelope:

| Stage | Tasks | Resources per task | Wall time | Parallelism |
| --- | ---: | --- | --- | --- |
| Compute-node preflight | 1 | 1 CPU, 5 GB | 15 minutes | 1 |
| Pilot | 1 | 120 GB; 12 GridSearch workers | 4 hours | 1 |
| Production | 100 | 120 GB; 12 GridSearch workers | 4 hours | at most 5 leaves |
| Aggregation and plots | 1 | 1 CPU, 5 GB | 1 hour | 1 |

On Puma, pilot and production request total memory and allow Slurm to derive CPU allocation at the
site's standard memory-per-CPU ratio. Record terminal accounting for every task. Preserve detailed
efficiency evidence for the pilot and representative production leaves covering a typical task,
the highest-memory task, and the longest-running task for future resource sizing.

## Proposed Preflight, Retry, Stop, and Cancellation Boundaries

- Perform a bounded compute-node preflight for imports, environment identity, paths, manifests,
  synthetic fixtures, schemas, and launch behavior. It must not perform substantive model
  training, data generation, optimization, or evaluation.
- Permit one minimal preflight-only correction and one rerun.
- Pilot application, code, data, schema, numerical, OOM, or timeout failure stops before the
  production array and requires a revised package.
- Permit one same-scope retry of each affected production index only for a confirmed transient
  scheduler or node failure.
- A second production retry requires fresh user approval.
- Application, code, data, schema, numerical, OOM, or timeout failures do not authorize an
  automatic retry.
- Pilot or aggregation retries require fresh approval.
- Aggregate only after exactly 100 eligible production seeds exist.
- Permit cancellation only for recorded Iter001 job IDs when a proven universal pre-execution
  defect would invalidate all affected active tasks. Cancellation grants no fix or retry
  authority.
- Treat scheduler observation-context failures as unknown state and reconcile authoritatively;
  they are not workload failures.

The nominal scheduler-task count is 103:

```text
1 preflight + 1 pilot + 100 production leaves + 1 aggregation
```

One preflight correction/rerun and at most one authorized transient retry for every affected
production leaf produce a hard cap of 204 tasks under the proposed package. Tasks beyond this cap
require fresh approval.

## Expected Evidence, Artifacts, and Record Updates

- Locked dependency/source/environment manifest and hashes.
- Canonical and submitted Slurm scripts with byte-equality evidence.
- Immutable submission configurations and seed mappings.
- Independent read-only review record and reviewed source hash.
- Preflight result and terminal accounting.
- Pilot artifact/scalers, shared memmap/layout, metrics, importance, logs, and accounting.
- One hundred production JSON records and complete array accounting.
- Aggregate metric and importance tables plus plots.
- Resource-efficiency evidence for future sizing.
- `development/spinup_forcing_coupling/summaries/iter001/` compact decision evidence.
- Finalized `iterations/iter001.md`, `ITERATION_SUMMARY.md`, `registry.csv`, and
  `handoff/CURRENT.md` after an approved and executed iteration.
- Cross-record validator identity, command, output, and passing result.

## Proposed Closeout Branch

Authorize at most one local closeout commit after all jobs are terminal, aggregation and record
validation pass, and controlled paths are verified. The commit may include the forcing-trainer
improvements, relevant documentation/examples/tests, Iter001 scripts and tools, compact summaries,
and durable workflow records. It must exclude raw outputs, the memmap, model artifact, and logs.
No push is proposed.

## Fresh Consolidated Kickoff-Approval Boundary

Before initialization or execution, present the then-current complete package and obtain one
explicit user approval. The request must include:

> For this iteration, do you authorize the primary agent to execute outside the Codex sandbox:
> 1. sbatch for the locked submission and any resubmission already allowed by this contract;
> 2. job-scoped squeue, scontrol show job, sacct, seff, job-history, and job-limits commands
> throughout monitoring and terminal accounting, without another workflow-authority question;
> 3. scancel only for the current iteration's recorded job IDs and only under the cancellation
> conditions stated in this contract?

Approval must also cover preparation, exact external-directory creation, independent review,
preflight, production, evaluation, durable records, and the proposed local closeout commit. A goal,
this planning file, or remembered command approval grants none of those authorities.
