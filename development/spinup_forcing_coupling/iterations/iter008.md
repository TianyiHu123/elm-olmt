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
- Next action: workflow stop condition reached; no next iteration is proposed or authorized.

## Proposed Next-Iteration Plan (Planning Only)

To be written only after Iter008 evaluation and closeout; no next iteration is authorized by
this report.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter008/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout commit verified
