# iter017 - coupled optimization-pipeline consolidation and regression

Closeout identity: Iteration ID `iter017`; Status `planned`; Work type `implementation`; Objective `consolidate and end-to-end regress the coupled optimization pipeline before the separate nine-site operational campaign`; Bounded scope `1 preflight; 4 initialization/rebuild jobs; 12 optimization leaves; 4 reporting jobs; 1 handoff validation`; Overall acceptance result `pending`; Decision `pending`.

## Status

- Iteration ID: `iter017`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter017_<path>`
- Status: `planned`
- Phase: `preparing`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-20T19:16:22-07:00`
- Closed: `pending`

## Finalized Plan

The full plan in `iterations/iter016.md` and `handoff/CURRENT.md`, committed as `f222057`, is
finalized unchanged by the user approval. Iter017 consolidates the coupled three-stage pipeline:
initialization/rebuild, seeded optimization, and independent reporting. It is an
implementation/integrity regression, not a scientific calibration campaign.

The four approved paths are ABBY fresh daily/0.50, JERC ledger-rebuild hourly/0.75, and joint
ABBY+JERC fresh daily/0.50 and hourly/0.75. Each has seeds 9009--9011, 64 walkers, 2,000 steps,
and checkpoints at 1,000/2,000. Joint mode has one shared pool/vector and joint MAP, with
site-specific predictions and skills; `fit_error=true` must derive shared `sigma_SR` from all
sites and pass site-order invariance.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User approval | `approved the complete package`; plus use `development/hpc/puma.md` as the HPC operation guide; recorded `2026-08-20T19:16:22-07:00` |
| Finite scope and stop | 22 work units: 1 preflight, 4 initialization/rebuilds, 12 leaves, 4 reports, 1 handoff. Stop at validated Iter017 closeout; Iter018 is separate. |
| Site and output root | Puma `chopinsong`/`standard`; `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter017_pipeline_regression/`; only approved subdirectories; `/xdisk` unbacked. |
| Dependencies and exclusions | Existing forcing and `drop21_corr080` spinup artifacts, ABBY/JERC observations, `fit_error=true`, ordered schema; no retraining, refresh, tuning, TIM revert, promotion, nine-site run, push, PR, or merge. |
| Resources and concurrency | Preflight 4 CPU/30m; init/rebuild 8 CPU/4h; leaf 16 CPU/4h; report 4 CPU/2h; handoff 2 CPU/30m; max two three-leaf arrays concurrently. |
| Review and retries | Independent read-only review before preflight and after every code correction; one unchanged scheduler/resource retry per job/leaf; up to three revised-code correction/resubmission cycles each for preflight, an affected production/reporting path, and handoff. |
| Cancellation and outside-sandbox authority | Recorded Iter017 IDs only under approved conditions; `sbatch`, job-scoped `squeue`/`scontrol`/`sacct`/`seff`/`job-history`/`job-limits`, and bounded `scancel` approved. |
| Commit authority | One implementation/source-lock commit before preflight, amendable only for approved correction cycles, and one closeout commit. |

## Upstream Dependencies and Source Lock

- Repository parent: `f222057`; implementation/source-lock is the current
  repository `HEAD` recorded by the materializer in `package_identity.env`.
- Environment: `conda_envs/OLMT_puma.yml`, locked during preparation.
- Materialized YAML, submitted scripts, stage manifests, and source snapshots must be byte-identified before submission.
- Prepared reusable interfaces: `model_ELM/mcmc_artifacts.py` owns raw-chain
  persistence; `model_ELM/mcmc_diagnostics.py` owns post-burn selection;
  `model_ELM/optimization_config.py` validates the universal YAML contract;
  `run_optimization_campaign.py` is the stage adapter; and
  `report_optimization.py` is the independent aggregate reporter.
- Prepared canonical stage wrappers under `slurm/iter017/`, including the
  no-submit materializer and Puma-standard preflight, initialization, array,
  report, and handoff jobs. Four universal YAML examples and the README outline
  are under `examples/iter017/`.

## Acceptance Gates and Decision Rule

- Integrity gates: module/retirement records; adapter/YAML/static checks; generic-MCMC and forcing-training import compatibility; joint order invariance; all default outputs; standardized reports/exports; every draft example executed; terminal accounting and four-record validation.
- Sampler health, Tier-A count, model skill, and convergence are descriptive only.
- Any dependency, scope, gate, resource, or scientific-target change requires fresh authorization.

## Provenance and Job Ledger

| Work unit | Job IDs | State | Retry notes |
| --- | --- | --- | --- |
| preparation/source lock | `97c47b6` | review 1 blocked | adapter/provenance/preflight/report gaps recorded above |
| correction cycle 1 | `efa28c1` | review 2 blocked | order-invariance/source-identity/report-evidence gaps |
| correction cycle 2 | `46bc3ad` | review 3 blocked | submitted-copy/YAML/evidence-ledger gaps |
| correction cycle 3 | `02b6874` | review 4 blocked | materializer unmatched quote; fresh authority required |
| additional cycle 1 | `a6ed913a5c516ed2ce59d470215178e181dc96e7` | review 5 PASS_WITH_CONCERNS | quote-only repair; static checks passed |
| preflight | `23608697`, `23608738` | failed code | first missing `sys.path`; second relative `py_compile` paths; one additional retry remains |
| four path pipelines | pending | pending | contract limits |
| handoff validation | pending | pending | contract limits |

## Independent Read-Only Review

- Review 1 (`/root/iter017_review`) on source lock `97c47b6`: **BLOCK**.
  Findings: the adapter emitted `SITE=/path` instead of the optimizer's
  required `SITE:/path`; incomplete submitted-copy/dependency provenance;
  a stale source-lock identifier in live records; preflight did not cover the
  approved imports, dependency/source identities, or joint order invariant;
  and reporting/handoff did not require the full standard product contract.
  No reviewer edits, Python, or scheduler activity occurred.
- Review 5 (`/root/iter017_review`) on
  `a6ed913a5c516ed2ce59d470215178e181dc96e7`: **PASS_WITH_CONCERNS** for
  materialization/preflight. Scope was the quote-only correction; `bash -n`,
  `git diff --check`, clean-tree inspection, canonical/copied manifests,
  joint-order check coverage, import checks, and YAML-driven reporting were
  confirmed. No reviewer edits, Python, or scheduler activity occurred.

## Execution and Diagnostics

- Static validation: shell syntax and diff checks passed before review.
- Preflight code-correction cycle 1: opened after review 1, before any job
  submission. The correction will record changed files, rationale, source-lock
  identity, and re-review outcome here before materialization.
- Cycle 1 changes: `run_optimization_campaign.py` now emits the documented
  `SITE:path` observation mapping; `materialize_iter017.sh` now records all
  locked artifacts, observations, case pickles, ledger, environment, campaign,
  and submitted-script identities; every stage wrapper validates its copied
  script and applicable campaign/source/dependency manifests before Python;
  preflight imports retained public boundaries; reporting requires terminal,
  finite, bounded leaf products; and handoff requires all three seeds and CLM
  NetCDF exports per path. Rationale: address every review-1 BLOCK finding.
- Preflight code-correction cycle 2: opened after re-review 2. It adds
  compute-node reversed-site `build_coupling_target` identity comparison,
  canonical-to-snapshot byte comparison plus snapshot manifest, imported
  runtime-closure hashing, mandatory site-specific posterior products, and
  per-seed health/skill/log-likelihood evidence in the report manifest.
  Rationale: address every review-2 BLOCK finding before any submission.
- Preflight code-correction cycle 3: adds explicit canonical-to-copy `cmp`
  checks and a submitted-copy manifest; makes reporting consume its YAML
  retention/copy settings; copies collocation, residual, and likelihood tables
  into `reports/per_seed`; and records all correction-source identities above.
  Rationale: address every review-3 BLOCK finding.
- Additional minimal preflight correction cycle 1, authorized by the user after
  cycle 3: repair the single unmatched quote in the submitted-copy manifest
  command, then repeat static validation and independent review. No scope,
  dependency, resource, or runtime configuration changes are authorized.
- Additional minimal preflight correction cycle 2: preflight `23608697` passed
  manifest/static checks but failed at import because an absolute-path Python
  entrypoint lacked the required `REPO_ROOT` `sys.path` bootstrap. Add that
  bootstrap, rematerialize the preflight submitted copy, re-review, then
  resubmit only this failed preflight work unit.
- Additional minimal preflight correction cycle 3: preflight `23608738` passed
  the manifest, import, and environment gates but `py_compile` used relative
  filenames from the submitted preflight directory. Anchor the compile list to
  `REPO_ROOT`, refresh only the preflight source package, re-review, and submit
  the final additional preflight retry.
- Review 7 (`/root/iter017_review`) on
  `ec05d3f6486a58168d6906c97cf275726952eb70`: **PASS_WITH_CONCERNS** for the
  final additional preflight retry. It confirmed the literal-root compile list,
  existing import bootstrap, static checks, and unchanged prior gates. No
  reviewer edits, Python, or scheduler activity occurred.
- Review 6 (`/root/iter017_review`) on
  `12f4d738a1177541cf0bf3eb793e9584e934490d`: **PASS_WITH_CONCERNS** for the
  preflight retry. The literal root-path bootstrap resolves the observed import
  error; shell/diff checks and the prior integrity gates remain valid. No
  reviewer edits, Python, or scheduler activity occurred.

## Validation, Evaluation, and Decision

- Overall acceptance result: pending.
- Overall decision: pending.
- Limitation: 2,000-step regression chains cannot establish convergence or posterior validity.

## Proposed Next-Iteration Plan (Planning Only)

No Iter018 plan is authorized here; it needs a separate proposal and fresh kickoff approval.

## Closeout Checklist

- [ ] Iteration report finalized
- [ ] Required evidence copied to `summaries/iter017/`
- [ ] `ITERATION_SUMMARY.md` and `registry.csv` updated
- [ ] `handoff/CURRENT.md` rebuilt and validator passed
- [ ] No job is active or unaccounted; authorized closeout commit verified
