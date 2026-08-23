# iter012 - Standard initialization and fixed production MCMC

Closeout identity: Iteration ID `iter012`; Status `completed`; Work type `implementation`; Objective `Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 and JERC hourly/0.75`; Bounded scope `Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation`; Overall acceptance result `pass`; Decision `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`

## Status

- Iteration ID: `iter012`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter012_<work_unit>`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-14T19:21:20-07:00`
- Closed: `2026-08-17T01:45:03-07:00`

## Finalized Plan

- Objective: implement a reusable initialization-to-production MCMC pipeline, then run fixed
  independent production inference for ABBY at `daily/0.75` and JERC at `hourly/0.75`.
- Scope: two isolated targets; two candidate-pool initialization leaves, one pool validation,
  six production leaves, two site evaluations, and one aggregate/handoff validation.
- Dependencies: Iter002 forcing surrogate, Iter012 `drop21_corr080` spinup surrogate, matching
  cases and NEON v4 observations, physical schema/priors/bounds/transforms/Jacobian, and
  `OLMT_puma`, all re-locked before compute. Iter008/009/011 chains and transferred states are
  excluded from initialization.
- Fixed inference: 14 physical parameters plus fitted `sigma_SR`; ABBY complete-day daily
  likelihood; JERC hourly likelihood; DEMove multiplier `0.75`; 80% DEMove / 20% DESnookerMove;
  seeds `9009`, `9010`, `9011`; 64 walkers x exactly 32,000 steps; checkpoints every 8,000.
- Initialization: `sobol_multistart_local_v1`, 8,192 scrambled states with deterministic
  expansion up to 65,536 only when required; 32 dispersed L-BFGS-B anchors, at most 512
  posterior evaluations per anchor; retain all evaluated states and require >=640 valid,
  exact-unique selected states, full rank, nonzero spread, condition number <=1e6, and robust
  stratum representation. Pool failure stops production without threshold changes or fallback.
- Hard gates: exact identity/provenance, target/pool agreement, valid initialization artifacts,
  finite in-bound 32,000-step HDF/raw chains, synchronized checkpoints/metadata, terminal
  accounting, complete evaluation artifacts, and durable-record agreement. Diagnostic outcomes
  are reported, not treated as integrity failures.
- Exclusions: joint production, mixed resolutions, annealed SMC, transferred states, automatic
  extension, alternate likelihoods, site weighting, dependency/target changes, pooled conclusions,
  configuration ranking, topology analysis, and automatic follow-up execution.
- Stop: after both site evaluations, aggregate/handoff validation, complete terminal accounting,
  classified failures, final validator pass, durable-record agreement, and one verified closeout
  commit.

## Consolidated Kickoff Package and Runtime Contract

| Field | Approved value |
| --- | --- |
| User response and approval timestamp | `The kickoff package is approved. outside sandbox authority is approved. Besides, make sure you know the hpc system you are on is development/hpc/puma.md .`; `2026-08-14` |
| Kickoff goal and finite work-unit count | Fixed initialization-to-production MCMC for ABBY `daily/0.75` and JERC `hourly/0.75`; 13 nominal tasks across six staged submissions; stop at complete evaluation and validated closeout. |
| Confirmed HPC system and profile | UArizona Puma; `development/hpc/puma.md`; account `chopinsong`; partition `standard`; repository root `/xdisk/chopinsong/tianyihu/elm-olmt`. |
| Approved output and storage | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012/` with `preflight/`, `initialization/{abby,jerc}/`, `pool_validation/`, `production/{abby,jerc}/seed_{9009,9010,9011}/`, `evaluation/{abby,jerc}/`, and `aggregate/`; large products remain outside Git; `/xdisk` is temporary and unbacked. |
| Resources | Preflight 2 CPUs/10 GB/30 min; initialization 16 CPUs/80 GB/4 h each; pool validation 4 CPUs/20 GB/1 h; production 16 CPUs/80 GB/8 h each; evaluation/aggregate 4 CPUs/20 GB/2 h. |
| Retry boundary | One minimal preflight correction/rerun; one unchanged scheduler/resource retry per initialization leaf; one compatible scheduler/resource recovery per production leaf; one unchanged retry per evaluation leaf; one unchanged aggregate retry; maximum 25 scheduler tasks. Application/code/schema/dependency/numerical/target/pool/scientific/scope failures stop for revised approval. |
| Cancellation | Only current Iter012 recorded job IDs, and only for a proven universal pre-execution defect that would make all affected work fail. |
| Lifecycle authority | Prepare, lock, review, materialize, submit, monitor, account, evaluate, update records, validate handoff, and make one local closeout commit. |
| Outside-sandbox authority | `sbatch` for locked submissions and allowed retries; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits` throughout monitoring/accounting; bounded `scancel` only under the cancellation rule. |
| Closeout branch | One local closeout commit authorized; no push. |

## Approved Revised Package v2 - General Pipeline Canonical Rerun

### Trigger and authority

Package v1 reached six application-level `PRODUCTION_PASS` markers, but the interrupted session left
terminal accounting, evaluation, and closeout incomplete. Read-only recovery also identified that
the execution package retained redundant Iter012 Python adapters, did not expose frozen-pool
production through the established root `optimize_surrogate_forcing.py` entry point, wrote Slurm
logs into the repository root, treated unavailable tau as an execution error, omitted required
walker-level acceptance evidence, and lacked the promised final handoff validator.

Post-approval source-to-artifact reconciliation found an additional correctness defect. Package
v1's `run_fixed_production_chain` passed `de_move_scale=0.75` but omitted
`move_configuration="de_mixture"`, so all six raw-chain metadata files record
`move_configuration: "stretch"`. Package v1 therefore did not execute the locked 80% DEMove /
20% DESnookerMove kernel. Package v2 restores the predeclared kernel without changing the approved
scientific contract. Package v1 remains useful only as integrity-audited, misconfigured-sampler
legacy context and cannot be treated as equivalent reproduction evidence.

Authoritative `sacct` reconciliation on `2026-08-16` established that jobs `23570407--23570412`
all completed `0:0`. Elapsed times were `04:35:33`, `04:47:12`, `04:54:34`, `03:24:10`,
`03:33:53`, and `03:20:53`; peak batch RSS was approximately 5.75--10.29 GB. The twelve misplaced
stdout/stderr files were hashed, relocated to their matching Package v1 production leaves, hashed
again, and verified equal. The three superseded Python adapters were copied under Package v1
`provenance/superseded_adapters/`, recorded in `superseded_adapters.sha256`, and then removed from
the active repository.

On `2026-08-16`, the user confirmed that the active session is UArizona Puma and selected:

- Package v2 as canonical, with Package v1 retained as legacy corroborating evidence;
- output root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2`;
- external-only preservation of the exact superseded Iter012 Python adapters before repository
  removal;
- corrected evaluation of Package v1 into a separate legacy-comparison area under the v2 root; and
- hash-verified relocation of the twelve Package v1 production logs from the repository root into
  their matching external production leaves.

After reviewing the complete revised contract and the record-amendment policy, the user responded
`agreed. Are you ready to resume the iteration with the new package now?` at
`2026-08-16T17:20:00-07:00`. This authorizes Package v2 preparation, repository scripts/tests,
external directories, locked Slurm submissions, job-scoped monitoring/accounting, bounded
retries/cancellation, evaluation, durable-record updates, the stated cleanup, and one local
closeout commit. No push is authorized.

### Scope and unchanged scientific contract

Package v2 is a reproducibility and implementation-validation rerun, not a new scientific
experiment. It retains the Package v1 dependencies, separate ABBY `daily/0.75` and JERC
`hourly/0.75` targets, fresh Sobol plus bounded L-BFGS-B initialization, pool size 640, seeds
`9009--9011`, 64 walkers, exactly 32,000 steps, 80% `DEMove` plus 20% `DESnookerMove`, and every
diagnostic qualification threshold. No Package v1 state initializes Package v2.

The revised architecture is:

- `model_ELM/coupling_pipeline.py` provides iteration-neutral target, candidate-pool, walker
  selection, fixed-production, provenance, and safe-resume APIs;
- `initialize_pipeline.py` is the public general initialization CLI;
- `optimize_surrogate_forcing.py` is the public general production CLI, extended to consume and
  verify frozen candidate pools;
- Iter012 Slurm scripts are thin scheduler/configuration launchers that call those root entry
  points directly; and
- `model_ELM/iter012_target.py`, `initialize_iter012.py`, and `production_iter012.py` are removed
  after byte-identical external preservation and hash recording.

One invocation may contain multiple sites only under one common likelihood resolution. Package v2
therefore continues to run ABBY and JERC independently.

### Work units, resources, and retry boundary

Package v2 has 16 nominal tasks: one preflight, two initialization leaves, one pool validation,
six production leaves, two canonical site evaluations, two Package v1 legacy evaluations, one
aggregate/comparison, and one final handoff validation. Resources remain 2 CPUs/10 GB/30 minutes
for preflight; 16 CPUs/80 GB/4 hours per initialization; 4 CPUs/20 GB/1 hour for pool validation;
16 CPUs/80 GB/8 hours per production leaf; and 4 CPUs/20 GB/2 hours per evaluation, aggregate, or
handoff-validation task.

One minimal preflight correction/rerun and one unchanged scheduler/resource retry per eligible
leaf give a maximum of 31 scheduler tasks. Application, code, interface, schema, data, dependency,
numerical, target, scientific-gate, provenance, or scope failures stop for a revised package.
Cancellation is limited to recorded Package v2 job IDs and a proven universal pre-execution defect.

### Evidence and decision policy

Package v2 results are canonical. Package v1 receives terminal-accounting and artifact-integrity
audit plus corrected site evaluation, written only under Package v2's `legacy_comparison/` area.
Legacy findings may corroborate or contextualize the canonical result but cannot replace it or
override its immutable gates.

Every submitted configuration and script is hashed and closed before launch. Submissions use
absolute work-unit-local output/error paths and submit from the work-unit directory. Evaluation
records unavailable or unstable tau and returns `fixed_length_inconclusive` rather than failing;
it includes mean and per-walker acceptance. Aggregate compares canonical and legacy evidence
without pooling site conclusions. A separate final validator checks the iteration report,
iteration summary, registry, and handoff after record finalization.

## Upstream Dependencies and Source Lock

Dependency identity, paths, schemas, sizes, hashes, target fingerprints, environment identity,
and source manifests are recorded during preparation before preflight. The source lock is the
clean repository commit `6246e920c6329ee28bda4e813613628bbc3ac852` plus the bounded Iter012 source
manifest. The environment is `OLMT_puma` under the Puma profile.

## Acceptance Gates and Decision Rule

- Initialization freezes `search_contract.json`, candidate ledger/metadata, high-posterior
  pool/manifest, diversity diagnostics, initialization report, and hashes for each site.
- Every production leaf reconstructs and verifies exact target/pool identity, selects 64 unique
  walkers by seeded maximin allocation across retained strata, re-evaluates them, and records the
  complete selection ledger before opening its HDF backend.
- A site is `diagnostically_qualified` only if tau is stable to 20%, every parameter has >=50
  post-burn tau, split R-hat <=1.05, bulk and tail ESS >=400, and maximum normalized cross-seed
  Wasserstein <=0.05. Otherwise it is `fixed_length_inconclusive`; either result ends sampling.
- Evaluation retains required diagnostics, descriptive hourly prediction metrics, traces, corner
  plots, and observed/posterior-predicted hourly series, without scatter, topology, ranking, or
  non-domination packages.
- Any identity, provenance, completeness, or record mismatch is an integrity failure and stops the
  iteration under the approved retry boundary.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Job IDs | State |
| --- | --- | --- | --- | --- | --- |
| preflight | minimal correction rerun passed | `23570084` `COMPLETED 0:0` in `00:01:17` on `r7u01n2`; `PREFLIGHT_PASS`; `23570069` failed v4 output collision; prior `23569843` passed | `.../preflight/preflight_result_v5.json` | complete | revised marginal-strata/root-engine package |
| initialization ABBY/JERC | ABBY revised retry `23570107` and JERC `23570252` completed `0:0` and passed complete artifact gates; failed ABBY attempts preserved | generalized initialization engine retry | `.../initialization/{abby_retry_23569844_revised,jerc}/` | `23570107`, `23570252` (`23569844`, `23569633`, `23566851` prior) | complete |
| pool validation | both-site validation `23570353` completed `0:0`, `status=pass`; hashes and pool sizes verified | `submit_validate_pools_iter012.slurm` | `.../pool_validation/` | `23570353` | complete |
| Package v1 production ABBY/JERC seeds | all six leaves completed `0:0`; logs relocated with hash equality; raw metadata proves unintended `stretch` move | preserved submitted scripts and adapters | `.../production/{abby,jerc}/seed_{9009,9010,9011}/` | `23570407--23570412` | legacy misconfigured-sampler evidence; accounting complete |
| evaluation ABBY/JERC | pending preparation | pending | `.../evaluation/` | none | pending |
| aggregate/handoff | pending preparation | pending | `.../aggregate/` | none | pending |
| Package v2 preflight | locked package and absolute-log helper verified | `submit_preflight_iter012.slurm` and immutable config/receipt | `.../preflight/` | `23574254` | pending |

Package v2 preflight `23574254` was submitted at `2026-08-16T18:24:16-07:00` from the locked
preflight directory. Its receipt records config
`8d5411cd19ade461c7162490b2419802cbf41a24229233f066b67a9c6912cb89` and submitted script
`9e5e54d93c1b1aaa25b3eacd301cf0557caf3670a460cacfb09071b0fb6788f8`.
Immediate `scontrol` identity verification showed account `chopinsong`, partition `standard`,
2 CPUs/10 GB, 30-minute limit, exact work directory, and absolute local stdout/stderr paths.
Preflight `23574254` terminated `OUT_OF_MEMORY 0:125` after `00:01:55`; `seff` reports 10.00 GB,
99.99% of the locked allocation. Stdout completed both source and dependency manifest checks;
stderr contains one Slurm OOM-kill event and no application traceback. This is classified
`scheduler_resource`. The contract-authorized single unchanged retry is recorded in
`preflight/retry_authorization.env`, bound to receipt hash
`2a2ee6eefd0b6a2331327c4defa64fd933c765e36e6863a1c91096e8d8cd5c24`.
The unchanged retry `23574301` also terminated `OUT_OF_MEMORY 0:125`, after `00:01:30`, with
batch MaxRSS `10484892K` against the same 10 GB allocation. It produced no preflight result. The
approved preflight retry boundary is exhausted, no Package v2 job is active, and initialization
remains unsubmitted. Advancing requires a revised package with explicit resource and task-ceiling
authority.

The user approved the minimal preflight resource revision on `2026-08-16`. Revision1 uses the
separately locked root
`spinup_forcing_coupling_iter012_general_pipeline_v2/revision1/`, preserves the exhausted 10 GB
package at its parent, and changes only preflight allocation from 2 CPUs/10 GB to 4 CPUs/20 GB.
Walltime, source behavior, dependencies, fixtures, gates, downstream resources, and scientific
controls are unchanged. Exactly one revised preflight attempt is authorized with no retry, and the
overall Package v2 scheduler-task ceiling increases from 31 to 32.
Revision1 passed independent read-only review and materialized successfully. Its package identity
records source manifest `7ce581f0d736e9d82f7d7439c538c9c459ec41be5549178e917b728c515357bf`,
dependency manifest `540bf3d0816a3a6a103d4e2e5d83a19f43a4a5b58fead598f09b1a0d58365e2d`,
and submission scaffold `1d6d482b320a2c181fface19adae7c5e4c5bffe38b80033de3454899db6a5035`;
all manifest entries were reverified before submission.
Revision1 preflight `23574395` completed `0:0` in `00:03:00` with batch MaxRSS `17819484K`.
Stdout ended `PREFLIGHT_PASS`, stderr was empty, and `preflight_result.json` reports both target
fixtures, interleaved target state, prior-once/likelihood-sum, rejection fixtures, and overall
status `pass`.
Revision1 initialization ABBY `23574453` completed `0:0` in `00:35:29` with MaxRSS `9247936K`;
JERC `23574454` completed `0:0` in `00:30:09` with MaxRSS `9250096K`. Both stdout logs ended
`INITIALIZE_PASS`. Their transactional artifact manifests report `status: pass` and hash all six
required initialization artifacts.
Pool validation `23574678` completed `0:0` in `00:00:21` with `POOL_VALIDATION_PASS`. The durable
result reports both 640-member pool hashes and matching target identities; normalized condition
numbers are `1.1785851450301694` for ABBY and `1.1594670473745647` for JERC.
All six Revision1 production leaves completed `0:0` and emitted `FIXED_PRODUCTION_PASS`: ABBY
9009/9010/9011 jobs `23574707`/`23574706`/`23574708` ran
`05:55:51`/`05:55:35`/`05:39:55`; JERC jobs `23574709`/`23574710`/`23574711` ran
`04:43:46`/`04:27:04`/`04:19:28`. Each leaf has a hashed raw-chain package, validated selection
ledger, and terminal production result. Repeated empirical-training-range warnings accumulated in
localized stderr logs; they did not alter physical-bound checks or terminal status and are retained
as a pipeline usability finding.
Canonical evaluations ABBY `23575950` and JERC `23575951` completed `0:0` and committed
transactional artifacts with labels `fixed_length_inconclusive`. ABBY mean acceptance by seed is
`0.23890/0.23174/0.23753`, maximum rank-normalized split R-hat is about `1.018`, and maximum
cross-seed normalized Wasserstein distance is `0.00441`. JERC acceptance is
`0.18173/0.22123/0.15696`, maximum split R-hat is about `2.225`, and cross-seed distance is
`0.54843`, demonstrating material nonconvergence. Legacy-audit evaluations ABBY `23575952` and
JERC `23575953` completed `0:0` with the required `legacy_misconfigured_sampler` label.

## Independent Read-Only Review

- Historical Package v1 reviewer: authorized independent read-only `codex review --uncommitted`;
  its 2026-08-15 pass applies only to the superseded Package v1 source.
- Package v2 reviewer: independent read-only agent `b36774e0-34c7-4ed3-9221-7e8821b67f55`.
  The first 2026-08-16 review returned `BLOCK` with source-lock, recovery, ESS-gate,
  terminal-accounting, initialization-artifact, selection-ledger, multi-site-fixture,
  materialization, and stale-record findings. No Package v2 submission occurred. Corrections and
  repeated full re-review found additional transaction and submission-ledger races; each was
  corrected before execution. The final full review returned `PASS` with no remaining actionable
  P0--P3 findings. Static Python compilation, shell syntax, and `git diff --check` also pass.
- Package v2 materialization completed under the approved sibling root. The reviewed and
  rematerialized package identity records source manifest
  `6a7cacf18dac1403791f2466510d5fbf1a536f7e24e11b966ddecc38877f9739`, dependency manifest
  `540bf3d0816a3a6a103d4e2e5d83a19f43a4a5b58fead598f09b1a0d58365e2d`, and submission scaffold
  `b9a9dadc326cf04f01628884773e595ae366e9a0863ffee6297973dc0501e10e`.
  A generated retry-parser quoting defect was found before submission; the unused scaffold was
  removed, corrected, fully rematerialized, hash-verified, and re-reviewed `PASS`. No job existed
  during that correction.

## Execution and Diagnostics

- Static validation: `pass` (`git diff --check`, shell syntax, Python compilation); external materialization pass.
- Preflight correction: `23566810` failed `1:0` after 10s because its copied source manifest was stale; static checks passed. The authorized minimal correction refreshed the runtime-empty package and verified both manifests. Corrected preflight `23566829` submitted 2026-08-14T20:57:09-07:00 and completed `0:0` in 1:26 on `r7u01n1`; `PREFLIGHT_PASS` and both target midpoint evaluations passed.
- Failures/retries/cancellations: ABBY initialization `23566851` completed `FAILED 1:0` after 27s. Static and manifest checks passed; application traceback shows the initialization output guard rejected Slurm-created `initialize_23566851.out/.err` files. Classified as an application/code failure; no retry authorized under the current package and JERC remains unsubmitted.
- Revised continuation: the guard now permits scheduler `.out/.err` files while retaining scaffold/artifact refusal; revised preflight `23569607` completed `0:0` with `PREFLIGHT_PASS` on `r7u02n1`. ABBY retry `23569633` then failed `1:0` after 35:07 on `r6u01n1` because a NumPy integer in the initialization JSON payload was not serializable. Partial `candidate_pool.npz`, `candidate_ledger.npz`, `candidate_metadata.json`, and passing `search_contract.json` are preserved, but `initialization_report.json` is absent, so the initialization gate is not met.
- Approved generalized retry: reusable target construction and candidate-pool initialization now live in `model_ELM/coupling_pipeline.py`; `iter012_target.py` and `initialize_iter012.py` are compatibility/configuration adapters. The retry materializer preserves the failed attempt and uses `initialization/abby_retry_23569633`; static checks and independent review pass.
- ABBY retry `23569844` reached terminal `FAILED 1:0` after `03:02:13` on `r7u05n1`. The traceback
  is `RuntimeError: pool gate failed: 12106 robust strata exceed pool size 640`; `seff` reports
  8.65 GB of 80 GB used. Classify this as an application/pool-gate failure, not a
  scheduler/resource failure; no unchanged retry is authorized.
- Revised package approval: the user approved the revised package on `2026-08-15T19:41:27-07:00`.
  The corrected pool contract uses marginal parameter-bin strata (`15` parameters x `4` bins,
  at most `60` required representatives) while retaining the `640` pool, exact-unique,
  full-rank, condition-number, and nonzero-spread gates. Reusable walker selection and fixed
  production execution are in `model_ELM/coupling_pipeline.py`; Iter012 production is a thin
  configuration adapter. The revised ABBY attempt uses a new directory so failed artifacts stay
  preserved.
- Material design finding (recorded during active ABBY retry): the iteration objective was to
  build a reusable surrogate-optimization/initialization-to-production pipeline, but the
  execution package introduced Iter012-specific implementation surfaces, including
  `development/spinup_forcing_coupling/slurm/iter012/production_iter012.py`, despite existing
  root-level optimization functionality in `optimize_surrogate_forcing.py`. Iteration-specific
  files must remain thin configuration/scheduler adapters; reusable optimization, target,
  initialization, and production behavior belongs in root-level reusable engines/interfaces.
  This is a scope/architecture defect to audit and correct before any pool-validation or
  production submission. Do not silently fix the locked source or reinterpret the approved
  contract while `23569844` is active; preserve the current job and obtain the required revised
  approval before any material code/package change.
- Preflight retry `23569840` failed `1:0` after 17s because its configured `preflight_result_v3.json` already existed; no source or dependency check failed. The minimal correction advanced the output to `preflight_result_v4.json`, rematerialized the package, reverified both manifests, and submitted corrected preflight `23569843`.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| ABBY initialization/production/evaluation | yes | generic initialization and three 64x32000 `de_mixture` chains; canonical evaluation | implementation pass; `fixed_length_inconclusive` | max R-hat 1.01794; no posterior promotion |
| JERC initialization/production/evaluation | yes | generic initialization and three 64x32000 `de_mixture` chains; canonical evaluation | implementation pass; `fixed_length_inconclusive` | max R-hat 2.22410 and cross-seed distance 0.54843 |
| aggregate/handoff | aggregate complete; handoff pending | canonical/legacy aggregate `23575960` | aggregate pass | canonical Package v2 controls conclusions |

- Overall acceptance result: `pass` for the implementation/integrity contract.
- Overall decision and closeout conclusion: `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`.
- Limitations: `/xdisk` is temporary and unbacked; neither posterior is promoted; production
  empirical-range warnings are excessively repetitive.
- ABBY revised initialization `23570107` completed `0:0` after `00:38:44` on `r7u08n2` with
  16 CPUs/80 GB and 8.65 GB peak memory. Its complete artifact gate passed: `status=pass`,
  640 selected candidates, normalized rank 15, condition number 1.1957493726, nonzero
  normalized spreads, and `marginal_parameter_bins_v1` provenance in the report and contract.
- JERC initialization `23570252` completed `0:0` after `00:29:25` on `r7u04n1` with 16 CPUs/80 GB
  and 8.66 GB peak memory. Its complete artifact gate passed: `status=pass`, 640 selected
  candidates, normalized rank 15, condition number 1.1676396412, nonzero normalized spreads,
  and `marginal_parameter_bins_v1` provenance in the report and contract.
- Pool validation `23570353` completed `0:0` after `00:00:21` on `r7u01n2` with 4 CPUs/20 GB
  and 704.88 MB peak memory. Its result is `status=pass`; both pool hashes, target hashes,
  pool sizes 640, and condition numbers match the site contracts.

- Handoff validator identity: `development/spinup_forcing_coupling/slurm/iter012/validate_iter012_handoff.py`.
  Command: Slurm job `23575977` running `submit_validate_iter012_handoff.slurm` with
  `--aggregate .../revision1/aggregate/result/aggregate_result.json` and
  `--accounting .../revision1/accounting.csv`. Terminal accounting: `COMPLETED 0:0` in `00:00:15`.
  Output: `ITER012_HANDOFF_VALIDATE_PASS abby=fixed_length_inconclusive jerc=fixed_length_inconclusive`.

## Next state

Iter012 closeout originally recorded no next iteration because both canonical fixed-length
outcomes were inconclusive. On `2026-08-17` the user requested a Stage-A-only follow-up that
compares TIM and Iter012 initial clouds at ABBY and JERC. That planning-only proposal is
recorded below. `iter013` remains `not_initialized` until a fresh consolidated kickoff under
`WORKFLOW.md`.

<!-- ITER013_PLAN_BEGIN -->
## Proposed Iter013 plan - Stage A initialization-cloud comparison

- Sequential ID: `iter013`
- Status: `not_initialized`
- Work type: `validation`
- Objective: compare Iter009 TIM high-posterior start clouds with Iter012 production
  candidate-pool start clouds at ABBY and JERC, and test whether the Iter012 640/64 sets are
  high-posterior rank sets or diversity-dominated sets.
- Evidence basis: Iter012 JERC mixing collapsed relative to Iter011 `hourly/0.75` while MAP
  skill matched; Iter012 hypothesized initialization geometry rather than likelihood form.
  Iter011/009 TIM starts are transferred top-decile Iter008 chain states. Iter012 starts come
  from an independent Sobol plus L-BFGS-B search with marginal-quartile representation and
  maximin fill. ABBY is included as the geometry control because the same pool recipe did not
  split Iter012 ABBY seeds.
- Hypothesis: the TIM walker cloud is a compact high-posterior neighborhood, while the Iter012
  pool and walkers span near-full prior width; the Iter012 640/64 sets are not the top-k
  posterior states from the same search.

### Fixed targets and dependencies

- Re-lock the Iter012 Package v2 Revision1 site targets and the Iter009 TIM high-likelihood
  artifacts. Do not rebuild pools, replay MCMC, or change priors, bounds, transforms, surrogates,
  observations, or likelihood resolution.
- ABBY comparison uses the Iter012 daily target
  (`target_sha256=bf9ade8b68bf7179cdb5c5712682dd1c343d510749efd7041cf0414ec4773bbd`).
- JERC comparison uses the Iter012 hourly target
  (`target_sha256=26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196`).
- Forcing artifact SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`.
- Spinup `drop21_corr080` SHA-256
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`.
- Iter012 pools: ABBY `982350b16e17202acb4f2b82ab40c26e24c31dff159bb68dafbd6d8cc69a2d19`;
  JERC `32d2ba5fa7e21f60a9df38fa8bcc6d6fe06a08bcbfa3ba6ce4fdcb62e5afaf96`.
- Iter012 candidate ledgers: ABBY
  `ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b`; JERC
  `25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d`.
- TIM high-likelihood pools: ABBY
  `b19cbe90bdc746a4c2bf577fc2dc4877a32d89ee6bf77d76b6058c3f9085ad4a` (2,212 states, top-decile
  cutoff `-81162.4853383585`); JERC
  `fcd909188789ab97b222773fc21f2a60e401a730f16e95edeee1e7aac49140e8` (1,208 states, top-decile
  cutoff `-52719.034473135165`).
- TIM high-seed bundles 9009/9010/9011: ABBY
  `37f51011638e93ef1420d092d7f97bbd8e6bfa24342d205fcc09b9d5a9d8716a`,
  `49a32268e72a183414e2ba684717b1b7675c84f4ebf12b2ffd23df850c9f69cb`,
  `8c30198df99da7225f9c3235866c3020fef8d1e7a9349494149ddcfa11d14e0c`; JERC
  `394902f2c2378a6793196f226c7cf136872a2631012f559ba857c989c47bd8fe`,
  `86fa8a3a732be080454bb451ab025cf604c1c8c0a98ffbdce26ed2b46d3870d6`,
  `fa19ed47a533f540e88992c1eac6346f46478192ed85b1132222ac08599f063e`.
- Iter012 walker starts are the `selected_physical_states` in Revision1
  `production/{abby,jerc}/seed_{9009,9010,9011}/selection_ledger.json`.
- Physical parameter order remains
  `k_l1, k_l2, k_l3, k_s1, k_s2, k_s3, k_s4, k_frag, rf_l1s1, rf_l2s2, rf_l3s3, rf_s1s2, rf_s2s3, rf_s3s4, sigma_SR`.
- Use Iter012 site bounds, including site-specific `sigma_SR` upper bounds. Trust assumption:
  TIM physical states are in that same order and strictly in bounds; hash mismatch or order
  mismatch is an integrity failure, not a scientific result.

### Clouds, coordinates, and comparison methods

- Per site, compare four primary clouds: TIM high-L pool; TIM walker starts (per seed and the
  192-row union); Iter012 640-member pool; Iter012 walker starts (per seed and union).
- Add two Iter012-ledger counterfactual clouds: the unique states with the top 640 stored
  physical log posteriors, and the top 64 stored physical log posteriors.
- All geometry uses prior-normalized coordinates
  `(theta - pmin) / (pmax - pmin)` with the Iter012 site bounds. Do not compare stored TIM log
  posterior values with stored Iter012 log posterior values. TIM stored logp is Iter008 hourly
  chain posterior; Iter012 ABBY logp is daily.
- Geometry metrics, all in prior-normalized units: per-parameter mean, standard deviation, range,
  and 5–95 width; per-parameter 1D Wasserstein between each TIM cloud and each Iter012 cloud;
  centroid Euclidean distance; mean pairwise distance; mean nearest-neighbor distance;
  overlap fraction at Euclidean radius `0.05` from each TIM walker to the nearest Iter012 walker
  and to the nearest Iter012 pool member, and the reverse fractions.
- On JERC, highlight `k_s1`–`k_s4` versus `k_l1` and `rf_l3s3`. On ABBY, highlight `sigma_SR`.
- Common-target logp: reconstruct each Iter012 site target and re-evaluate TIM pool and TIM
  walker physical states under that target. Compare those values with stored Iter012 pool and
  walker physical log posteriors. Report 5/50/95 percentiles for each cloud and the median
  difference TIM walkers minus Iter012 walkers. Do not re-evaluate the full Iter012 search
  ledger except as needed to confirm stored pool/ledger logp identity.
- Rank-versus-diversity counterfactual: exact-row intersection of the Iter012 640 with the
  ledger top 640, and of each seed's 64 walkers with the ledger top 64. Report intersection
  counts, intersection fractions, and the max/mean normalized spread of actual versus top-k
  sets.
- Plots: one per-parameter overlay figure per site (violin or histogram) for the four primary
  clouds. No PCA scatter, no corner plot, and no observed-versus-predicted plot. Tables and JSON
  are the primary evidence.

### Classification and decision rule

Classify each site independently after integrity passes. Geometry classes are mutually exclusive
in this order:

1. `coincide` if the maximum per-parameter 1D Wasserstein between the TIM walker union and the
   Iter012 walker union is `<= 0.05` and at least 80% of TIM walkers have an Iter012 walker
   within Euclidean radius `0.05`.
2. `tim_nested_in_iter012_pool` if not `coincide`, at least 80% of TIM walkers have an Iter012
   pool member within radius `0.05`, and Iter012 walker mean pairwise distance is at least twice
   the TIM walker mean pairwise distance.
3. `separated` if fewer than 20% of TIM walkers have an Iter012 walker within radius `0.05` and
   the maximum per-parameter 1D Wasserstein between those walker unions is `> 0.05`.
4. `inconclusive_geometry` otherwise.

Separately classify Iter012 selection:

- `rank_dominated` if `|actual 640 ∩ top 640| / 640 >= 0.80`.
- `diversity_dominated` if that fraction is `< 0.50`.
- `mixed_rank_and_diversity` otherwise.

Also report the same intersection fractions for each seed's 64 walkers versus the ledger top 64.
These classes are descriptive. They do not promote a posterior, change the initializer, or
authorize MCMC.

### Bounded scope, work units, and exclusions

- Stage A only. No MCMC, no new candidate search, no pool regeneration, no TIM production replay,
  no DE-scale change, no likelihood or error-model change, no joint ABBY+JERC target, no
  initializer code change, and no automatic follow-up experiment.
- Proposed scheduler work: one compute-node preflight; one ABBY analysis leaf; one JERC analysis
  leaf; one aggregate/handoff validation: 4 nominal tasks.
- Preflight verifies artifact paths, hashes, parameter order, bounds, TIM-bundle membership in
  the TIM pool, Iter012 selection-ledger identity, and target fingerprints. It may run one
  midpoint posterior fixture per site. It must not re-evaluate TIM clouds or write scientific
  classifications.
- Each analysis leaf writes that site's geometry JSON, common-target logp JSON, top-k
  counterfactual JSON, overlay figure, and site classification.
- Aggregate concatenates both sites, writes the comparison table and report, and runs the
  four-record handoff validator after durable records exist.
- Exclude Iter009 uniform bundles, Iter012 Package v1 stretch-move chains, and any transferred
  chain states except the locked TIM high-L pools and high-seed bundles above.

### Proposed site, resources, retry, and stop boundary

- Proposed site: UArizona Puma; `development/hpc/puma.md`; account `chopinsong`; partition
  `standard`; environment `OLMT_puma`.
- Proposed output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter013/`
  with `preflight/`, `analysis/{abby,jerc}/`, and `aggregate/`. Large arrays remain outside Git;
  `/xdisk` is temporary and unbacked.
- Proposed resources: preflight 4 CPUs / 20 GB / 30 min; each analysis leaf 16 CPUs / 80 GB / 4 h;
  aggregate/handoff 4 CPUs / 20 GB / 1 h.
- Proposed retry ceiling: one minimal preflight correction/rerun; one unchanged
  scheduler/resource retry per analysis or aggregate leaf; at most 8 scheduler tasks.
  Application, code, schema, dependency, numerical, target, hash, or scope failures stop for a
  revised package.
- Cancellation only for recorded Iter013 job IDs, and only for a proven universal pre-execution
  defect that would make remaining Iter013 work fail.
- Stop after both site analyses, aggregate/handoff validation, complete terminal accounting,
  classified failures, and durable-record agreement. Do not start MCMC or Stage B.

### Expected evidence, artifacts, and record updates

- External: hashed analysis JSON, overlay figures, `aggregate_result.json`, `accounting.csv`,
  and `ITER013_REPORT.md` under the approved output root, with compact copies in
  `development/spinup_forcing_coupling/summaries/iter013/`.
- Repository: `iterations/iter013.md`, canonical scripts under `slurm/iter013/`, registry row,
  `ITERATION_SUMMARY.md` append, and rebuilt `handoff/CURRENT.md` at closeout.
- Required completeness: both sites classified; all locked hashes verified; common-target TIM
  logp finite for every TIM pool and walker row; top-k counterfactuals present; no PCA plot.

### Fresh consolidated kickoff-approval boundary

This planning-only proposal does not authorize initialization, scaffolding, repository Python,
Slurm, retry, cancellation, or a closeout commit. It becomes executable only when included in
an approved consolidated kickoff package under `WORKFLOW.md`.
<!-- ITER013_PLAN_END -->

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter012/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized one-commit closeout branch satisfied
