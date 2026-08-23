# iter008 - Single-site ABBY and JERC coupled SR MCMC diagnostics

## Status

- Iteration ID: `iter008`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter008_preflight`,
  `spinup_forcing_coupling_iter008_abby_campaign`,
  `spinup_forcing_coupling_iter008_jerc_campaign`, and
  `spinup_forcing_coupling_iter008_validate`
- Status: `completed`
- Phase: `closed`
- Objective label: `Single-site ABBY and JERC coupled/drop21_corr080 SR MCMC diagnostic campaign`
- Bounded scope label: `ABBY and JERC separately; coupled drop21_corr080; SR; 64x4000; seed 8008; raw-chain diagnostics; integrity-only`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter008`
- Forcing SHA-256: `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`
- Spinup SHA-256: `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-08T19:59:06-0700`
- Closed: `2026-08-09T14:56:00-0700`

## Finalized Plan

- Sequential ID and work type: `iter008`; `implementation`.
- Objective: demonstrate reproducible, diagnostically interpretable single-site SR MCMC
  results for ABBY and JERC using the locked coupled `drop21_corr080` framework before any
  further joint-site calibration.
- Hypothesis: isolated, longer, same-seed chains with raw-chain diagnostics will distinguish
  sampler limitation, likelihood limitation, and site-specific limitation without changing
  coupled artifacts or scientific inputs.
- Dependencies: immutable Iter002 forcing-surrogate-v1; immutable Iter012 `drop21_corr080`
  spinup state; the Iter007 cases and NEON v4 observations; Iter007 products as
  characterization-only baseline.
- Scope: separate ABBY and JERC campaigns, each `--fit-error`, 64 walkers x 4,000 steps,
  seed 8008, 16 worker processes; explicit raw-chain retention; adaptive postprocessing;
  site reports and paired validation.
- Exclusions: surrogate retraining, coupled interface/schema/feature/case/observation/prior
  changes, site weighting, joint MCMC, multi-variant campaigns, replicate ensembles, R-hat
  claims, and scientific hard gates.
- Gates: authoritative accounting; successful two-site preflight and bounded ABBY smoke;
  complete identity-locked chains and products; fail-closed provenance/checksum/schema
  validation; paired comparison and four-record agreement.
- Decision: classify as sampler-limited, likelihood-limited, site-specific model/data
  limitation, joint-calibration candidate, or inconclusive. Scientific quality metrics are
  diagnostic evidence, not pass/fail gates.
- Resources: Puma `chopinsong`/`standard`; preflight 2 CPUs/derived 10 GB/30 min; each
  campaign 1 node/16 CPUs/derived 80 GB/4 h/16 workers; validation 2 CPUs/derived 10 GB/1 h;
  recovery 2 CPUs/derived 10 GB/2 h.
- Retry/cancellation/stop: one minimal preflight correction; one scheduler/resource retry
  per site; one raw-chain-only recovery per site; cancellation only for recorded jobs under a
  proven universal pre-execution defect; stop after accounting, gates, decision, records,
  validation, and closeout.
- Expected evidence: raw chains and metadata/checksums, selection ledgers, standard products,
  diagnostic tables/plots/reports, paired report, summaries, registry, handoff, and validator.
- Authorization boundary: this finalized plan is covered by the approved consolidated package
  recorded below; no scope or locked-term change is authorized.

### Approved Contract Amendment

- User approval: `the amendment is approved. continue now`, `2026-08-09T13:51:32-0700`.
- Amendment: add the required two-site `--case` argument to the preflight dry-run; authorize
  one additional preflight-only rerun; increase the hard cap from 9 to 10 tasks. All other
  scope, resources, gates, retry/cancellation boundaries, and closeout terms remain unchanged.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response: `approved the complete package`; `2026-08-08T19:59:06-0700` |
| Kickoff goal, finite work-unit count, and stop conditions | Single-site ABBY/JERC diagnostic MCMC; 4 nominal work units and amended hard cap 10; stop after terminal accounting, immutable integrity gates, diagnostic decision, durable records, cross-record validation, and one closeout commit |
| Confirmed HPC system and site profile | University of Arizona Puma; `development/hpc/puma.md` |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`; only the four Iter008 run directories; `/xdisk` is temporary/unbacked; raw outputs and large products remain outside Git |
| Locked dependencies, scope, exclusions, gates, and decision rule | Forcing SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; spinup SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; 64x4000/site, seed 8008, `--fit-error`; exact finalized plan above |
| Lifecycle authority | Initialization, preparation, source/configuration changes within scope, external directory creation, compute-node preflight, independent read-only review, submission, monitoring, accounting, evaluation, records, validation, retries within limits, and closeout |
| Resources and retry boundaries | Preflight 2 CPUs/derived 10 GB/30 min; campaigns 16 CPUs/derived 80 GB/4 h/16 workers; validation 2 CPUs/derived 10 GB/1 h; one minimal preflight correction, one scheduler/resource retry per site, one raw-chain-only recovery per site |
| Cancellation scope | Recorded Iter008 job IDs only, and only when a proven universal pre-execution defect invalidates affected work |
| Outside-sandbox authority | Locked `sbatch` and authorized retries; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the cancellation rule |
| Closeout branch | One bounded local closeout commit after final validation; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Iter002 forcing surrogate | Coupled `SR` | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | `forcing-surrogate-v1` | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | Iter002 release; current hash verified before approval |
| Iter012 drop21_corr080 | Coupled spinup | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` | `spinup-surrogate-v1` | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | Iter012 release; current hash verified before approval |
| ABBY/JERC cases and NEON v4 observations | Site targets and likelihood | Iter007 locked paths and case manifest | `SR:SR_err` validity mapping | hashes re-locked during preparation | Iter007 coupling and collocation evidence |
| Repository source | Implementation | `/xdisk/chopinsong/tianyihu/elm-olmt` | HEAD `88547e394af0cc53cf6fc97680032f8873538152` | clean tree at initialization | approved source lock |

- Environment identity: `OLMT_puma`; micromamba module/version to be recorded during preflight.
- Input hashes, sizes, manifests, submitted-copy identity, and configuration hashes will be
  recorded before submission.

## Acceptance Gates and Decision Rule

- Required completeness: terminal accounting for every submitted task; preflight pass; both
  complete raw chains and standard products; reports and selection ledgers; paired comparison;
  `summaries/iter008/`; and agreement among report, summary, registry, and handoff.
- Missing observation, schema, provenance, shape, artifact, or checksum evidence fails closed.
- Unavailable tau in the 32x20 smoke is reported and is not a failure; production postprocessing
  falls back to the declared discard/thin rule when tau is unavailable.
- Acceptance result is integrity-only. Acceptance does not claim scientific calibration quality.
- The decision report must select exactly one permitted diagnostic route: sampler-limited,
  likelihood-limited, site-specific model/data limitation, joint-calibration candidate, or
  inconclusive.
- Any application, interface, schema, data, dependency, numerical, scope, resource-cap, or
  gate change requires a fresh consolidated approval.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter008.slurm`; source manifest | submitted copy `submit_preflight_iter008.slurm`; `submission_config.env`; byte-equal | Iter008 preflight directory; logs for `23524637`, `23524638`, `23527081` | locked inputs | HEAD `88547e3`; source manifest | `23524637`, `23524638`, `23527081` | `23527081` COMPLETED 0:0, 00:01:51, MaxRSS 8.64/10 GB; `PREFLIGHT_PASS` | prior two attempts classified; amendment used |
| ABBY campaign | `campaign_iter008.slurm`; source manifest | submitted copy/config byte-equal and revalidated | Iter008 ABBY directory; `campaign_23527105.{out,err}` | preflight `23527081` pass | HEAD `88547e3`; source manifest | `23527105` | `COMPLETED 0:0`, 00:24:50, MaxRSS 10.02/80 GB; `CAMPAIGN_PASS` | no retry used |
| JERC campaign | `campaign_iter008.slurm`; source manifest | submitted copy/config byte-equal and revalidated | Iter008 JERC directory; `campaign_23527106.{out,err}` | preflight `23527081` pass | HEAD `88547e3`; source manifest | `23527106` | `COMPLETED 0:0`, 00:49:39, MaxRSS 9.73/80 GB; `CAMPAIGN_PASS` | no retry used |
| validate | `validate_iter008.slurm`; source manifest | submitted copy/config byte-equal and revalidated | Iter008 validate directory; `validate_23527337.{out,err}` | both campaigns pass | HEAD `88547e3`; source manifest | `23527337` | `COMPLETED 0:0`, 00:00:24, MaxRSS 6.24/10 GB; `VALIDATE_PASS` | none |

## Independent Read-Only Review

- Reviewer: independent read-only agent `Averroes` (`019fe487-64e3-7142-9ba1-b56d69d74d8d`).
- Reviewed source hash: `iter008_source_manifest.sha256` after final provenance/config checks.
- Outcome: `pass`.
- Findings and primary-agent response: initial blocks on submitted-copy identity, provenance,
  strict validation, and handoff validator were corrected; final re-review confirmed all
  submitted copies, source/artifact/case manifests, bounds, provenance, and canonical config
  hashes pass. Amendment re-review by the same independent read-only agent also passed: the
  change is limited to the required two-site `--case` argument and refreshed identity.

## Execution and Diagnostics

- Static validation: `bash -n` pass; source-manifest `sha256sum -c` pass; AST parse pass;
  prior independent review pass; amended preflight review pass.
- Exact preflight submission command: `sbatch --parsable --export=ALL,SUBMISSION_CONFIG=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter008_preflight/submission_config.env ./submit_preflight_iter008.slurm`.
- Amended preflight rerun job: `23527081`, submitted from the verified run directory after
  passing amended independent review; immediate identity and terminal accounting passed.
- Preflight `23527081`: `COMPLETED 0:0`, elapsed 00:01:51, 2 CPUs, MaxRSS 8.64/10 GB;
  `PREFLIGHT_PASS`; collocation ABBY 26,280 / JERC 52,560; smoke ABBY 32x20 wrote the
  raw-chain package, selection ledger, standard products, and diagnostic report.
- ABBY `23527105`: identity matched; terminal `COMPLETED 0:0`, 00:24:50, 16 CPUs/80 GB/4 h,
  batch MaxRSS 10.02 GB, CPU 04:45:30; raw-chain hash
  `5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87`; standard products,
  diagnostics, selection ledger, and `CAMPAIGN_PASS` were written.
- JERC `23527106`: identity matched; terminal `COMPLETED 0:0`, 00:49:39, 16 CPUs/80 GB/4 h,
  batch MaxRSS 9.73 GB, CPU 09:26:30; raw-chain hash
  `34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080`; standard products,
  diagnostics, selection ledger, and `CAMPAIGN_PASS` were written.
- Preflight job `23524637` submitted from its verified run directory; immediate identity check
  matched Puma node `r7u01n1`, 2 CPUs/10 GB/30 min; terminal `FAILED 1:0`, elapsed 00:00:17,
  MaxRSS 8.68 MB. Failure classified as the authorized minimal preflight correction boundary:
  `OLMT_puma` has no `pytest`; no workflow preflight work ran.
- Corrected submitted script and source manifest revalidated; one authorized preflight rerun
  `23524638` submitted from the same verified directory; identity matched `r7u01n1`, 2 CPUs/
  10 GB/30 min; terminal `FAILED 1:0`, 00:00:38, MaxRSS ~6.19 GB. The compute-node log
  reports `optimize_surrogate_forcing.py: error: --case is required`; no collocation or smoke
  chain ran. The preflight retry boundary is exhausted.
- Validation `23527337`: identity matched; terminal `COMPLETED 0:0`, 00:00:24, 2 CPUs/10 GB/
  1 h, batch MaxRSS 6.24 GB, CPU 00:09.271; `VALIDATE_PASS` route `sampler-limited`; no
  validation retry used. All submitted jobs have terminal accounting; no campaign retry or
  cancellation used.
- Four-record precommit handoff validation: `python development/spinup_forcing_coupling/slurm/iter008/validate_iter008_handoff.py --phase precommit --expected-parent 88547e394af0cc53cf6fc97680032f8873538152 --expected-subject 'Close Iter008 single-site coupling diagnostics' --active-job-count 0`; result `ITER008_HANDOFF_VALIDATE_PASS`.
- Closeout commit identity: expected parent `88547e394af0cc53cf6fc97680032f8873538152`,
  subject `Close Iter008 single-site coupling diagnostics`; postcommit handoff validation
  passed with no active jobs and a clean worktree.

## Validation, Evaluation, and Decision

The complete scientific evaluation is
[`../summaries/iter008/iter008_comprehensive_mcmc_report.md`](../summaries/iter008/iter008_comprehensive_mcmc_report.md).
It reports site-level best-fit skill, every Iter007 diagnostic criterion, additional raw-chain
walker/parameter evidence, explicit good/bad judgments, all five route evaluations, the basis
for selecting `sampler-limited`, and falsifiable next experiments.

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | `23527081` terminal accounting, two-site collocation, ABBY smoke, `PREFLIGHT_PASS` | pass | preflight and smoke integrity gates pass |
| ABBY campaign | yes | `23527105` terminal accounting, raw-chain package, diagnostics, `CAMPAIGN_PASS` | pass | site-local integrity and output gates pass; scientific behavior remains diagnostic |
| JERC campaign | yes | `23527106` terminal accounting, raw-chain package, diagnostics, `CAMPAIGN_PASS` | pass | site-local integrity and output gates pass; scientific behavior remains diagnostic |
| validate | yes | `23527337` terminal accounting, paired comparison, `VALIDATE_PASS` | pass | paired integrity validation passes; diagnostic route is sampler-limited |

- Overall acceptance result: `pass` (integrity-only).
- Overall decision and closeout conclusion: `sampler-limited`; both chains are integrity-valid
  and reproducible, while measured acceptance/ESS/autocorrelation behavior is diagnostic only.
- Limitations: temporary `/xdisk` retention; no scientific quality gate.
- Next action: preserve the closed Iter008 evidence; the planning-only Iter009 proposal below
  requires a fresh consolidated kickoff package and explicit approval before initialization.

## Proposed Next-Iteration Plan (Planning Only)

### 1. Sequential ID and work type

- Sequential ID: `iter009`
- Work type: `implementation`
- Objective label: `ABBY and JERC sampler-geometry pilot`
- Proposed run slugs: `spinup_forcing_coupling_iter009_preflight`,
  `spinup_forcing_coupling_iter009_initialize`,
  `spinup_forcing_coupling_iter009_b_campaign`,
  `spinup_forcing_coupling_iter009_t_campaign`,
  `spinup_forcing_coupling_iter009_i_campaign`,
  `spinup_forcing_coupling_iter009_m_campaign`,
  `spinup_forcing_coupling_iter009_tim_campaign`, and
  `spinup_forcing_coupling_iter009_validate`.

### 2. Evidence-derived objective and hypothesis

Objective: determine whether Iter008's poor mixing is primarily caused by parameter scaling
and bounds, initial walker placement, or the default stretch proposal, while holding the
physical posterior fixed.

Evidence basis: Iter008 completed integrity-valid separate ABBY and JERC chains, but mean
acceptance was 0.178/0.102, maximum autocorrelation time was 508.8/482.7, only about 8--31
autocorrelation times were covered, and terminal walkers remained in separated log-probability
bands. The paired decision was `sampler-limited`; blindly extending the current geometry is not
the first action.

Hypothesis: one or more bounded geometry interventions will consistently improve acceptance,
terminal walker overlap, autocorrelation stability, and cross-seed agreement at both ABBY and
JERC without changing the likelihood, prior, scientific inputs, or physical posterior.

### 3. Proposed dependencies and trust assumptions

| Dependency | Role | Proposed lock / trust |
| --- | --- | --- |
| Preparation base | Repository parent | Clean HEAD `b086a212390af5f198a27799b92d8bc5ce09a321`; execution source will be locked by a reviewed manifest after authorized implementation |
| Iter002 forcing surrogate | Coupled `SR` | SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Iter012 `drop21_corr080` | Coupled spinup state | SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| ABBY observations | Likelihood target | NEON v4; SHA-256 `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` |
| JERC observations | Likelihood target | NEON v4; SHA-256 `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` |
| Iter008 ABBY raw chain | High-likelihood initialization source | SHA-256 `5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87` |
| Iter008 JERC raw chain | High-likelihood initialization source | SHA-256 `34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080` |
| ABBY/JERC cases and physical posterior | Fixed scientific contract | Same cases, site windows, `SR:SR_err` validity mapping, 14 physical parameters and bounds, IID Gaussian likelihood, and fitted site-specific `sigma_SR` as Iter008 |
| Puma environment | Runtime | `development/hpc/puma.md`; `chopinsong` / `standard` / `OLMT_puma`; exact package versions recorded by preflight |

The Iter009 initialization pools and bundles may be reused by a later convergence-length
experiment only while every posterior-defining input remains identical. A likelihood, prior,
bound, observation window, case, site input, or surrogate change invalidates the
`high-likelihood` designation and requires regeneration.

### 4. Bounded scope, work units, and exclusions

#### 4.1 Locked five-arm matrix

Each arm runs separate ABBY and JERC chains with 64 walkers, 8,000 steps, 15 free dimensions,
16 worker processes, unthinned retention, checkpoints at 2,000/4,000/6,000/8,000 steps, and
MCMC seeds 9009, 9010, and 9011. The matrix contains exactly 30 chains.

| Arm | Coordinates | Initialization | Proposal |
| --- | --- | --- | --- |
| `B` | physical | uniform-prior | explicit `StretchMove(a=2.0)` |
| `T` | transformed | same physical initial ensemble as `B` | explicit `StretchMove(a=2.0)` |
| `I` | physical | dispersed high-likelihood | explicit `StretchMove(a=2.0)` |
| `M` | physical | same physical initial ensemble as `B` | 80% `DEMove()` + 20% `DESnookerMove()` |
| `TIM` | transformed | same physical initial ensemble as `I` | 80% `DEMove()` + 20% `DESnookerMove()` |

The same three replicate seeds are used across sites and arms. Initialization and sampler RNG
streams are separated explicitly:

| Replicate | MCMC seed | Uniform-init seed | Maximin-selection seed |
| --- | ---: | ---: | ---: |
| 1 | 9009 | 19009 | 29009 |
| 2 | 9010 | 19010 | 29010 |
| 3 | 9011 | 19011 | 29011 |

#### 4.2 Transformation contract

- Apply the natural logarithm to the eight positive rate parameters: `k_l1`--`k_l3`,
  `k_s1`--`k_s4`, and `k_frag`.
- Apply a scaled logit to the six bounded `rf_*` fractions.
- Apply a scaled logit over the site-specific `[0, U]` interval to `sigma_SR`.
- Include the analytic Jacobian so the existing uniform physical-space prior is unchanged.
- Require physical-to-sampler-to-physical round-trip tests, analytic-versus-finite-difference
  Jacobian tests, and physical/transformed target equivalence. Do not clip or silently coerce
  invalid sampler coordinates.
- Retain both native sampler-space and physical-space chains. Physical coordinates are
  authoritative for cross-arm scientific comparison.

#### 4.3 Initialization preprocessing

The distinct post-preflight `initialize` work unit will, separately for ABBY and JERC:

1. Read the final half of the checksum-locked Iter008 unthinned raw chain.
2. Require finite log probability and in-bounds physical coordinates.
3. Remove exact repeated physical states before applying the likelihood percentile.
4. Retain the top 10% of unique states by log posterior.
5. Require at least 640 unique pool members and nonzero spread in every dimension.
6. Select 64 distinct positions per maximin seed in normalized physical-prior coordinates.
7. Require finite log posterior, strict bounds, uniqueness, full 15-dimensional rank, and a
   passing numerical condition check for every selected ensemble.
8. Write immutable per-site pool artifacts and per-site/per-seed initialization bundles with
   source step/walker indices, log probabilities, distances, ranks, metadata, and SHA-256.

The physical initialization bundle is authoritative. `B`/`T`/`M` share the corresponding
uniform bundle, and `I`/`TIM` share the corresponding high-likelihood bundle.

#### 4.4 Preflight and persistence

The bounded compute-node preflight verifies Puma/environment identity, all manifests and input
hashes, the exact 30-row matrix, transformation and Jacobian tests, target equivalence, and HDF
creation/reopen/continuation/finalization. It exercises the four unique execution mechanisms
(physical/stretch, transformed/stretch, physical/DE mixture, transformed/DE mixture) for both
sites with 32 walkers x 2 steps: 512 smoke proposals total. It makes no acceptance, tau, ESS,
skill, or convergence inference.

Every production leaf writes incrementally to an emcee HDF backend. Successful finalization
writes an immutable dual-coordinate `raw_chain.npz` containing both chains, raw log
probabilities, both initial states, parameter schema, transforms, bounds, Jacobian convention,
site, arm, seeds, move configuration, provenance, and hashes. A verified continuation finishes
at exactly 8,000 total steps; it never adds a second 8,000-step budget. A backend that already
contains 8,000 valid steps may undergo finalization-only recovery without resampling.

#### 4.5 Scheduler work units and layout

Use eight run directories under
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`, one for each proposed
slug. Each of the five arm-specific campaign parents is an unthrottled `--array=1-6` with an
explicit locked manifest:

```text
leaf_01_abby_seed9009
leaf_02_abby_seed9010
leaf_03_abby_seed9011
leaf_04_jerc_seed9009
leaf_05_jerc_seed9010
leaf_06_jerc_seed9011
```

The five parent arrays are submitted sequentially for identity verification and may overlap
after every parent passes its immediate check. There is no agent-imposed concurrency cap; Puma
schedules the approved maximum envelope.

#### 4.6 Exclusions

No likelihood, prior, physical bound, surrogate, observation, case, site window, coupled schema,
feature, or scientific-model change; no joint MCMC; no posterior-predictive campaign; no
Experiment 2 convergence-length confirmation; no Experiment 3 temporal-likelihood comparison;
no automatic proposal tuning; no arm selection by best log probability or predictive skill; and
no scientific adequacy or convergence claim from this pilot alone. Raw chains, HDF, logs,
NetCDF, full plots, and other large products remain outside Git.

### 5. Tentative integrity gates, geometry qualification, and decision rule

#### 5.1 Hard integrity gates

An integrity pass requires all submitted tasks to have authoritative terminal accounting and a
classified outcome; preflight and initialization to pass; every dependency, source, submitted
copy, configuration, matrix, and initialization identity to match; all 30 eligible chains to
contain exactly `(8000, 64, 15)` physical and sampler-space states with matching log
probabilities; transformation, provenance, finiteness, bounds, schema, and checksum validators
to pass; required diagnostic/report artifacts to exist; and the iteration report, cumulative
summary, registry, and handoff to agree after final validation. Missing or mismatched evidence
fails closed.

Sampler quality remains scientific routing evidence, not an execution-integrity gate.

#### 5.2 Geometry qualification

An arm is `geometry-qualified` only when every condition holds for all six site-seed chains:

- mean acceptance is 0.20--0.50;
- at most 6 of 64 walkers have acceptance below 0.10;
- tau is finite for all 15 physical parameters;
- every parameter's 6,000-to-8,000-step relative tau change is at most 20%;
- `8000 / tau >= 20` for every parameter;
- rank-normalized split screening R-hat is at most 1.05 for every physical parameter and log
  probability;
- no deterministic terminal two-band partition has at least seven walkers per band and
  silhouette at least 0.5; and
- every pairwise cross-seed Wasserstein distance is at most 5% of the physical prior width for
  every parameter.

Split R-hat is a screening statistic because walkers within an emcee ensemble interact. Nominal
unthinned ESS is reported with its formula and units but is not a separate gate because it is
algebraically tied to length and tau. Physical boundary occupancy and transformed-coordinate
saturation are reported but do not fail geometry qualification by themselves.

#### 5.3 Selection and attribution

Among geometry-qualified arms, select lexicographically by: (1) lowest worst-case physical-space
tau over every parameter/site/seed; (2) if worst-case tau differs by less than 10%, lowest worst
split R-hat; (3) lowest worst cross-seed Wasserstein distance; and (4) fixed simplicity order
`B -> M -> T -> I -> TIM`. Best likelihood, MAP skill, RMSE, R2, KGE, and predictive scores cannot
select an arm.

The report separately attributes evidence: `B` qualification supports a default-geometry/run-
length explanation; `T` supports scaling/bound geometry; early-only `I` improvement supports
initialization/burn-in; `M` supports proposal limitation; `TIM` alone supports an interaction.
If no arm qualifies, select no least-bad winner and route toward multimodality,
non-identifiability, likelihood discontinuity, or model-structure investigation.

### 6. Proposed site, resources, review, retry, cancellation, and stop

| Field | Proposal |
| --- | --- |
| HPC / profile | University of Arizona Puma; `development/hpc/puma.md` |
| Account / partition / environment | `chopinsong` / `standard` / `OLMT_puma` |
| Preflight | 2 CPUs / Puma-derived 10 GB / 30 minutes |
| Initialize | 4 CPUs / Puma-derived 20 GB / 1 hour |
| Each of 30 campaign leaves | 16 CPUs / Puma-derived 80 GB / 4 hours / 16 workers |
| Validate/report | 4 CPUs / Puma-derived 20 GB / 2 hours |
| Maximum simultaneous campaign envelope | 480 CPUs / Puma-derived 2,400 GB; five unthrottled six-leaf arrays, subject to Puma scheduling |
| Nominal scheduler count | 33 tasks across eight submissions: preflight, initialize, 30 leaves, validate |
| Review | Independent read-only agent after preparation and before substantive submission; primary agent remains sole writer and scheduler operator |
| Retry | One minimal preflight-only correction/rerun; one unchanged initialize scheduler/resource retry; at most six campaign-leaf recoveries total and at most one per leaf; one unchanged validation scheduler/resource retry |
| Hard cap | 42 scheduler tasks including every permitted retry/recovery |
| Cancellation | Recorded Iter009 IDs only; a proven universal pre-execution defect may cancel all affected pending work, and a proven arm-specific defect may cancel only that arm's recorded array |
| Stop | After terminal accounting, immutable integrity evaluation, geometry qualification and selection/route, durable records, handoff validation, and the authorized closeout branch |

A campaign continuation requires a checksum- and metadata-verified HDF state and preserves every
locked scientific and sampler term. More than six affected leaves, or any application, numerical,
schema, dependency, scientific-input, provenance, or scope failure, stops for fresh approval.
Live `uquota`/capacity and `job-limits` evidence must be checked before submission; normal
scheduler throttling or pending state does not change the approved matrix.

### 7. Expected evidence, artifacts, records, and closeout

Each leaf must retain submitted material and manifests, HDF identity, final dual-coordinate raw
archive, initialization identity, checkpoint acceptance and tau tables, correct unthinned nominal
ESS, trace and terminal-log-probability evidence, boundary/saturation evidence, target-equivalence
audit, metadata/checksums, and a human-readable leaf report.

Validation creates ten site-arm three-seed packages with rank/split screening, pairwise
Wasserstein distances, tau trajectories, acceptance/stuck-walker tables, terminal-band results,
and overlaid seed marginals/traces. The global package contains a 5-arm x 2-site qualification
matrix, worst-case selection table, attribution/route, accounting table, machine-readable
decision, and comprehensive Iter009 report. Compact tables and selected plots go under
`summaries/iter009`; large artifacts remain in the external run directories.

Closeout finalizes `iterations/iter009.md`, appends `ITERATION_SUMMARY.md` and `registry.csv`,
rebuilds `handoff/CURRENT.md`, and runs a cross-record validator. After all gates pass, the
proposed closeout branch permits exactly one bounded local commit with expected subject
`Close Iter009 sampler geometry pilot`; raw/large outputs are excluded and no push is proposed.

### 8. Fresh consolidated kickoff boundary

This proposal and the preceding stepwise planning decisions grant no initialization,
implementation, external-directory creation, compute-node Python, reviewer delegation,
scheduler submission/monitoring/cancellation, retry, records mutation, or commit authority.
At kickoff, present this plan unchanged inside one consolidated package that states the exact
source lock and controlled paths; output and retention policy; final resource and task envelope;
preparation, independent review, preflight, initialization, submission, continuous monitoring,
terminal accounting, evaluation, records, validation, retry, cancellation, outside-sandbox, and
closeout authorities; and the one-commit/no-push branch. Obtain one explicit approval of that
complete package before initializing Iter009.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter008/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout commit verified
