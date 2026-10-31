# iter001 - Initialize ABBY and JERC surrogate input data

## Status

- Iteration ID: `iter001`
- Work type: `data_initialization`
- Run slug: `three_stage_surrogate_iter001_abby_jerc_data_init`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-10-27T00:40:17-07:00`
- Closed: `2026-10-27T05:39:17-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`
- Applicable campaign phase: Iter001 data initialization
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Sequential ID and work type: `iter001`; no-training data initialization.
- Evidence-derived objective: validate the declared ABBY/JERC transferred sources, materialize a
  compact and self-describing surrogate-input collection, create one deterministic global 819/205
  development/fixed-test split, and provide reusable preparation and validation tools.
- Inputs and trust assumptions: use only the exact declared parameter design, two transient
  pickles, two spinup-preprocessing NetCDFs, 84 ordered monthly forcing files per site, and exact
  `c260408` surface files. Preserve transferred pickles unchanged. Treat I1850 pickles, domain
  files, configurations, and preprocessing reports as provenance only.
- Bounded scope: implement and test reusable preparation/validation tools; prepare ABBY and JERC
  sequentially; independently validate sources, prepared files, manifests, and split; update
  lifecycle records and close out. Exclude surrogate fitting, feature/model selection, robustness,
  fixed-test evaluation, pickle mutation, source deletion, and inferred inputs.
- Acceptance gates: exact 18-parameter/1,024-member identity; exact site/member correspondence;
  explicit hourly 2018--2024 no-leap alignment with 61,320 rows per site; required finite forcing,
  surface, GPP, and SR values; positive finite C/N targets; lossless retained-source values; exact
  schemas/hashes; deterministic exhaustive disjoint 819/205 split; reusable and cross-record
  validators pass; no training.
- Site and operations: Puma using `development/hpc/puma.md`; one preflight, one sequential
  preparation job, and one independent full validation job. Two independent read-only review gates
  occur before preflight and before operational jobs. Up to three bounded correction/retry cycles
  are authorized separately for preflight and operational work within the locked scientific,
  resource, path, and acceptance contracts.
- Evidence and records: source, dataset, split, validation, and snapshot manifests; prepared
  NetCDFs; submitted scripts/configurations and job accounting; this report, summary, registry,
  handoff, and final cross-record validator.
- Approval boundary: approved by the user on `2026-10-27`; changes to inputs, schemas, scientific
  rules, gates, resource caps, output layout, or scope require a fresh consolidated package.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | User: `I approved with two revisions: 1. the subagent reviewer should be used before both preflight and operational runs. 2. increase the preflight correction to 3 and also give 3 correction/retry chance for operational runs. clear?`; recorded `2026-10-27T00:40:17-07:00`. |
| Kickoff goal, finite work-unit count, and stop conditions | Initialize and close no-training ABBY/JERC data initialization. Three sequential scheduler jobs: preflight, preparation, validation. Stop after terminal accounting, validation, records, one authorized commit, and a planning-only Iter002 proposal. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`; Iter001 data initialization; aligned; deviation none. |
| Confirmed HPC system and site profile | UA Puma, observed login host `wentletrap.hpc.arizona.edu`; `development/hpc/puma.md`; account `chopinsong`; partition `standard`; environment `OLMT_puma`; no GPU. |
| Approved output and storage policy | Create `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data` and run directory `runs/iter001_abby_jerc_data_init`; publish immutable component artifacts and appendable snapshot catalog; preserve sources and failure evidence; do not delete or overwrite sources. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact declared inputs and output schemas in this report; preserve source dtype and values; CF no-leap timestamp alignment; SHA-256 split with namespace `three-stage-surrogate-v1`, seed `2026`; all gates must pass. No training or target-based fixed-test analysis. |
| Lifecycle authority | Authorizes iteration records, repository implementation/tests/scripts, external directories and prepared artifacts, two read-only reviews, preflight, preparation, validation, monitoring/accounting, evaluation, records, closeout validation, and one scoped commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Preflight: one task, 20 GB, 1 hour. Preparation: one task, 80 GB, 8 hours. Validation: one task, 80 GB, 8 hours. Job-scoped supported monitoring through terminal `sacct`. Up to three correction/retry cycles in preflight and three in operational work, each followed by the applicable review and confined to locked inputs, schemas, gates, paths, scope, and resource caps. |
| Cancellation scope | Only recorded Iter001 jobs, when work leaves scope, threatens sources/outputs, is clearly runaway, or the user requests cancellation; reconcile terminal accounting afterward. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, and `job-limits`; bounded `scancel` under the recorded conditions. |
| Closeout branch | One scoped no-push closeout commit on `feature/three-stage-surrogate`. |

Correction authority does not permit changing the scientific contract, source inventory, prepared
schema, eligibility policy, split method, acceptance gates, output layout, resource caps, or
campaign direction. Such a change requires a new consolidated kickoff package. A correction cycle
may repair implementation, interface, path wiring, manifest construction, or numerical handling
needed to satisfy the already locked contract. A retry may resubmit the corrected reviewed work or
the unchanged work after scheduler/node/preemption failure. Every attempt is recorded and terminally
accounted. OOM or timeout cannot increase resources under this package.

## Declared Inputs and Evidence

| Input or dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Parameter list | Ordered parameter bounds and PFT flags | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params/NEON_ppe_vertc_parmfile` | 18 ordered rows | SHA-256 locked during preparation | Declared PPE design input. |
| Parameter names | Canonical names/order | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params/sobol18_1024_names.txt` | 18 names | SHA-256 locked during preparation | Must match parameter list, matrix columns, metadata, and both pickles. |
| Parameter matrix | Shared ABBY/JERC values | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params/sobol18_1024.txt` | 1,024 rows x 18 columns | SHA-256 locked during preparation | Same row must denote same member at both sites. |
| Parameter metadata | Sampling/transforms/C:N support | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/params/sobol18_1024_meta.json` | Owen-scrambled Sobol, seed 2026 | SHA-256 locked during preparation | Authoritative sampling metadata. |
| ABBY transient pickle | GPP, SR, target time, serialized parameter/member evidence | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/pkfiles/ABBY_ppe_vertc_I20TRCNPRDCTCBC.pkl` | transferred ELMcase | 18,586,982,454 bytes; SHA-256 locked in job | Preserve unchanged. |
| JERC transient pickle | GPP, SR, target time, serialized parameter/member evidence | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/pkfiles/JERC_ppe_vertc_I20TRCNPRDCTCBC.pkl` | transferred ELMcase | 18,586,982,454 bytes; SHA-256 locked in job | Preserve unchanged. |
| ABBY spinup preprocessing | Full-profile C/N targets and depth diagnostics | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/spinup_preprocessing/ABBY/ABBY_spinup_preprocessing.nc` | 1,024 members | 327,593 bytes; SHA-256 locked in job | Campaign-authoritative ABBY spinup source. |
| JERC spinup preprocessing | Full-profile C/N targets and depth diagnostics | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/spinup_preprocessing/JERC/JERC_spinup_preprocessing.nc` | 1,024 members | 327,593 bytes; SHA-256 locked in job | Campaign-authoritative JERC spinup source. |
| ABBY forcing | Raw named hourly forcing | `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/ABBY/1x1pt_ABBY/CLM1PT_data` | exactly `2018-01.nc`--`2024-12.nc` | 84 files; per-file hashes locked in job | Explicit site source; never scan the common parent. |
| JERC forcing | Raw named hourly forcing | `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/JERC/1x1pt_JERC/CLM1PT_data` | exactly `2018-01.nc`--`2024-12.nc` | 84 files; per-file hashes locked in job | Explicit site source; never scan the common parent. |
| ABBY surface | Site surface features | `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/ABBY/surfdata_1x1_NEON_ABBY_hist_2000_c260408.nc` | exact file | hash locked in job | Supplies `PCT_SAND`, `PCT_CLAY`, `ORGANIC`. |
| JERC surface | Site surface features | `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/JERC/surfdata_1x1_NEON_JERC_hist_2000_c260408.nc` | exact file | hash locked in job | Supplies `PCT_SAND`, `PCT_CLAY`, `ORGANIC`. |

## Prepared Data and Manifest Contract

- `common/parameters_v1.nc`: dimension `member=1024`; coordinates `member`, `sample_index`, and
  `ensemble_id`; each of the 18 original parameters stored as its own `(member)` variable.
- `sites/<SITE>/input_data_v1.nc`: dimensions `member=1024` and `time=61320`; the seven forcing
  variables stored under original names as `(time)`; `GPP` and `SR` as `(member,time)`;
  `TOTSOMC` and `TOTSOMN` as `(member)`; `PCT_SAND`, `PCT_CLAY`, and `ORGANIC` as scalar site
  features; explicit no-leap time and member identities.
- Retain numeric source dtypes and values. Use NetCDF4 shuffle and deflate level 4 without lossy
  quantization; chunks `(1,8760)` for hourly targets, `(8760,)` for forcing, and `(256,)` for
  member variables when compatible with source shapes.
- GPP and SR retain the serialized postprocessed values and are recorded as `gC/m^2/day` under the
  established repository postprocessing contract. TOTSOMC is `gC/m^2`; TOTSOMN is `gN/m^2`.
  Forcing units are copied from source attributes.
- Reproduce the established forcing-loader contract by taking the arithmetic mean of the source
  records within each hour, remove February 29 from Gregorian forcing, and join by explicit
  timestamp to the ELM hourly 2018--2024 no-leap axis. Do not prefix-truncate or silently intersect.
- `member_split_1024_v1.json`: rank canonical ensemble IDs by
  `SHA256("three-stage-surrogate-v1|2026|<ensemble_id>")`; first 205 are fixed test and remaining
  819 are development; preserve ranked and numeric orders.
- `catalog.json` is the current index. Immutable source manifests and
  `dataset_snapshot_r0001.json` preserve the Iter001 baseline. Later authorized iterations may add
  sites or derived caches through new artifact identities and snapshot revisions without modifying
  validated existing artifacts.

## Acceptance Gates and Decision Rule

- Required completeness: every exact declared source exists; 18 ordered parameters; 1,024 common
  eligible members; 84 exact monthly forcing files per site; 61,320 aligned no-leap hours per site;
  every required output and manifest exists.
- Acceptance gates: parameter names/order/values and C:N support agree across sources; 0-based
  sample, 1-based member, and `gNNNNN` identities are bijective; required parameter, forcing,
  surface, GPP, and SR values are finite; C/N targets are finite and positive; parameters, targets,
  and surface reductions match sources exactly while forcing matches the declared hourly mean;
  hourly forcing aggregation, leap-day removal, and timestamp
  join are reproducible; units,
  schemas, shapes, chunks/compression, paths, sizes, and hashes are recorded; split is deterministic,
  exhaustive, disjoint, and exactly 819/205; reusable validator and final record validator pass;
  no training or target-based fixed-test analysis occurs.
- Decision rule: publish and close `completed` only if every gate passes and all jobs have terminal
  accounting. Otherwise preserve evidence, classify the failure, and use only remaining authorized
  correction/retry cycles without changing the contract; close failed or seek fresh approval when
  the contract cannot be met.
- Conditional metrics, ranking, or tie-breaker: no scientific ranking. The only ranking is the
  locked SHA-256 member split with ensemble ID as deterministic tie-breaker.
- Changes requiring fresh authorization: any source addition/substitution, schema or dtype policy
  change, eligibility change, split change, scientific transformation, gate change, output layout
  change, resource increase, fourth correction/retry in either phase, training, deletion, or push.

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| preflight | `preflight_iter001.slurm` / `77a1c6c8...` | submitted copy `77a1c6c8...`; config `93582015...`; manifest `c6e99b19...` | `surrogate_input_data/runs/iter001_abby_jerc_data_init`; `preflight_24430059.{out,err}`; no attempt-1/2 logs | locked inputs and environment | execution manifest `c6e99b19...`; base `174a7f6c...` plus bounded diff | attempt 1: `24428809`; attempt 2: `24428935`; attempt 3: `24430059` | attempts 1 and 2 `CANCELLED by 49065`, zero runtime/no node/requested `1M`; attempt 3 `COMPLETED`, `0:0`, `00:00:38`, 4 CPUs, MaxRSS `437484K`, ReqMem `20G` | Preflight passed all manifest, unit-test, environment, exact-inventory, and real-source checks. No preflight retries remain. |
| prepare | `prepare_iter001.slurm` / `1b3f60a3...` | submitted copy `1b3f60a3...`; config `93582015...`; manifest `c6e99b19...` | same run directory; `prepare_24430075.{out,err}`; `staging/prepare_attempt_1/package` | passing preflight and operational review | execution manifest `c6e99b19...` | `24430075` | `COMPLETED`, `0:0`, `00:02:24`, 16 CPUs, MaxRSS `54174240K`, ReqMem `80G` | Operational cycle 1 passed and produced the exact expected package; no correction/retry used. |
| validate | `validate_iter001.slurm` / `f010abc4...` | submitted copy `f010abc4...`; config `93582015...`; manifest `c6e99b19...` | same run directory; `validate_24430091.{out,err}`; published root | verified `staging/prepare_attempt_1/package` | execution manifest `c6e99b19...` | `24430091` | `COMPLETED`, `0:0`, `00:47:03`, 16 CPUs, MaxRSS `25579676K`, ReqMem `80G` | Independent validation passed and published snapshot `r0001` catalog last; no operational correction/retry used. |

## Independent Read-Only Review

- Reviewer: read-only subagent `/root/iter001_preflight_review`.
- Reviewed source hash: first review `0f9993ef738f0185149c285671157167a9ba1809f5fd9623000899c8598b9659`;
  corrected review target `5f535c24fbb2d7cc3ff67f6bd092c61961b55e2d8d2639577db49885a9a5bdb3`.
- Outcome: first review `block`; refreshed review `pass_with_concerns` at
  `2026-10-27T00:58:07-07:00`.
- Findings and primary-agent response: first review blocked unversioned micromamba, missing runtime
  config/manifest identity enforcement, and non-retry-safe publication. Correction cycle 1 pinned
  `micromamba/2.0.2-2`, added canonical/submitted equality plus reviewed hash and execution-manifest
  checks to every job, made catalog-last hardlink publication resumable, independently reconstructed
  forcing with xarray and the split with hashlib, added aggregation/storage/publication tests, and
  unified operational cycle numbering. Two mandatory review gates remain: before preflight and,
  after passing preflight and any correction, before preparation/validation. Each correction
  requires refreshed review before submission.

The refreshed reviewer verified all original blockers resolved and recommended proceeding. The
primary agent accepts the nonblocking concerns because: partial publication from the same prepared
package is retry-safe, while any different-package recovery will stop for a recorded quarantine
plan rather than delete or overwrite evidence; forcing and split use independent reconstruction;
and reused lower-risk pickle/spinup/surface helpers remain bounded by independent source hashes and
exact prepared-value checks. Real-data validation covers the complete leap-day and site schema
contracts beyond the synthetic fixtures.

The first correction/retry-cycle-2 review blocked direct submission because removing the site
wrapper also removed its evidenced login-environment import, while each batch script called
`module` without initializing it. A first correction that sourced `/etc/profile` was blocked in the
second review because the site profile is not safe under `set -euo pipefail` and did not establish
`module` in the reviewed environment. All three scripts now bypass shell initialization and invoke
the approved environment through the absolute interpreter
`/home/u32/tianyihu/.local/share/mamba/envs/OLMT_puma/bin/python`, asserting both executable
presence and exact `sys.prefix` before work. The refreshed execution manifest is
`0f3a9a2d0c7cad3158ace496a1f44efe82e4209c8a44a9e664babd941231ec39`; canonical and external
copies are byte-identical. A third refreshed retry review is pending within the same correction
cycle; no retry job has been submitted.

The third refreshed retry review returned `pass_with_concerns`: the package and clean submission
mechanism are technically eligible, with the nonblocking requirement to record the exact attempt-2
command before submission. That command is
`env -u SBATCH_GET_USER_ENV /usr/bin/sbatch --parsable --export=ALL,ITER001_ATTEMPT=2,ITER001_CONFIG_SHA256=935820158b7a00ed75b8efc02108c11edfaebedba27fee06fe252db3b58a1f3d,ITER001_MANIFEST_SHA256=0f3a9a2d0c7cad3158ace496a1f44efe82e4209c8a44a9e664babd941231ec39 ./submit_preflight_iter001.slurm`
from the approved run directory with a non-login execution shell. Immediate identity inspection
must confirm account, partition, name, work directory, 20 GB, and one-hour limit before monitoring.

Attempt 2 was submitted exactly as reviewed as job `24428935`. Despite the clean command and parser
evidence, the live controller again recorded `ReqTRES=cpu=1,mem=1M,node=1,billing=1`. The identity
gate cancelled it before execution. Terminal accounting is `CANCELLED by 49065`, exit `0:0`, zero
elapsed, zero allocated CPUs, no node, and requested memory `1M`; no logs were created. Final
preflight correction/retry cycle 3 therefore replaces explicit total-memory directives with the
Puma-supported CPU-derived allocation: partition evidence reports `DefMemPerCPU=5120`; preflight
requests one task and four CPUs for exactly 20 GB, while the two operational scripts request one
task and 16 CPUs for their already approved 80 GB caps. Time, scientific contract, paths, schemas,
gates, and memory caps are unchanged. The resulting execution manifest is
`c6e99b1988a3e1f42d2708d251b3926260c70409d74b9e83caa823b771f341f2`; refreshed review is pending.

The mandatory final preflight-cycle review returned `pass`. The exact attempt-3 command is
`env -u SBATCH_GET_USER_ENV /usr/bin/sbatch --parsable --export=ALL,ITER001_ATTEMPT=3,ITER001_CONFIG_SHA256=935820158b7a00ed75b8efc02108c11edfaebedba27fee06fe252db3b58a1f3d,ITER001_MANIFEST_SHA256=c6e99b1988a3e1f42d2708d251b3926260c70409d74b9e83caa823b771f341f2 ./submit_preflight_iter001.slurm`
from the approved run directory with `login=false`. The immediate identity gate must confirm one
task, four CPUs, effective 20 GB, account, partition, name, work directory, and one-hour limit. Any
mismatch requires cancellation and stop because preflight retry capacity is exhausted.

Attempt 3 was submitted at `2026-10-27T04:37:04-07:00` as job `24430059`. Its immediate live
identity passed: `NumTasks=1`, `NumCPUs=4`, `CPUs/Task=4`,
`ReqTRES=cpu=4,mem=20G,node=1,billing=4`, account `chopinsong`, partition `standard`, correct name
and work directory, and `TimeLimit=01:00:00`. It is pending for priority and under job-scoped
monitoring.

The first persistent watcher handle `8216` was stopped immediately after its state-extraction
expression produced an `awk` syntax error; its scheduler observations remained valid but it could
not detect terminal state. Corrected job-scoped watcher handle `48884` polls `squeue` and `sacct`
every 25 seconds, reports state changes, and exits only when the parent job has a recognized
terminal accounting state.

Watcher `48884` observed job `24430059` transition from pending to running on `r7u07n1` and then
terminated on authoritative parent accounting:
`24430059|3stage_i001_pre|COMPLETED|0:0|00:00:38|00:03.546|4||20G|r7u07n1`.
The batch step recorded `MaxRSS=437484K`. `seff` reports 4 CPUs, 38 seconds wall time, 427.23 MB
memory utilized, and 20.00 GB allocated. Standard output verifies all eight execution-manifest
entries, Python 3.11.15, six passing unit tests, and
`ITER001_PREFLIGHT_OK no_training=true attempt=3 sites=ABBY,JERC members=1024 parameters=18 forcing_months=84`.
The only stderr diagnostic is a nonfatal ArviZ future-warning plus `/usr/bin/time -v` resource
reports; both timed commands exited zero. The mandatory operational read-only review is next.

Operational cycle 1 command candidates are locked for review. Preparation:
`env -u SBATCH_GET_USER_ENV /usr/bin/sbatch --parsable --export=ALL,ITER001_OPERATIONAL_CYCLE=1,ITER001_CONFIG_SHA256=935820158b7a00ed75b8efc02108c11edfaebedba27fee06fe252db3b58a1f3d,ITER001_MANIFEST_SHA256=c6e99b1988a3e1f42d2708d251b3926260c70409d74b9e83caa823b771f341f2 ./submit_prepare_iter001.slurm`.
Validation, only after successful preparation:
`env -u SBATCH_GET_USER_ENV /usr/bin/sbatch --parsable --export=ALL,ITER001_PREPARE_CYCLE=1,ITER001_OPERATIONAL_CYCLE=1,ITER001_CONFIG_SHA256=935820158b7a00ed75b8efc02108c11edfaebedba27fee06fe252db3b58a1f3d,ITER001_MANIFEST_SHA256=c6e99b1988a3e1f42d2708d251b3926260c70409d74b9e83caa823b771f341f2 ./submit_validate_iter001.slurm`.
Both run from the approved run directory with `login=false`; non-submitting parser tests report one
node, one task, 16 CPUs, correct account/partition/name/log paths/exports, and eight-hour limits.

The mandatory independent operational review returned `pass` for manifest `c6e99b19...` and both
unchanged cycle-1 submissions. It verified preflight evidence, canonical/external equality,
fail-closed runtime locks, exact input and output contracts, sequential ABBY/JERC preparation,
independent validation, and catalog-last retry-safe publication. Preparation is eligible. This
review also covers validation after preparation cycle 1 has authoritative terminal success and the
expected `staging/prepare_attempt_1/package` is verified. Any preparation correction/retry,
package mismatch, or execution-material change requires refreshed review before validation.

Preparation operational cycle 1 was submitted at `2026-10-27T04:45:16-07:00` as job `24430075`
using the exact reviewed command. Immediate identity passed: `NumTasks=1`, `NumCPUs=16`,
`CPUs/Task=16`, `ReqTRES=cpu=16,mem=80G,node=1,billing=16`, correct account, partition, name, work
directory, and `TimeLimit=08:00:00`. It is pending for priority.

Job-scoped watcher handle `14534` polls validation job `24430091` every 25 seconds and exits only
on recognized terminal parent accounting.

Job-scoped watcher handle `99981` polls preparation job `24430075` every 25 seconds and exits only
on recognized terminal parent accounting. Its first observation shows the job running on
`r4u06n1` with 16 allocated CPUs and 80 GB.

Watcher `99981` exited on authoritative terminal accounting:
`24430075|3stage_i001_prep|COMPLETED|0:0|00:02:24|01:44.470|16||80G|r4u06n1`;
batch `MaxRSS=54174240K`. `seff` reports 51.66 GB utilized of 80.00 GB. Standard output records
`PREPARE_SURROGATE_INPUT_OK` for `staging/prepare_attempt_1/package`. The verified 827 MB staging
package contains exactly the expected README, catalog, parameters, four manifests, two site
NetCDFs, and member split; ABBY/JERC NetCDF sizes are 438,515,369 and 427,530,711 bytes. No
execution material changed, so the prior operational review authorizes the recorded validation
cycle-1 command.

Validation operational cycle 1 was submitted at `2026-10-27T04:48:33-07:00` as job `24430091`
using the exact reviewed command. Immediate identity passed: `NumTasks=1`, `NumCPUs=16`,
`CPUs/Task=16`, `ReqTRES=cpu=16,mem=80G,node=1,billing=16`, correct account, partition, name, work
directory, and `TimeLimit=08:00:00`. It is pending for priority.

Watcher `14534` observed validation pending, running on `r4u06n1`, and then authoritative terminal
accounting:
`24430091|3stage_i001_val|COMPLETED|0:0|00:47:03|46:42.438|16||80G|r4u06n1`;
batch `MaxRSS=25579676K`. `seff` reports 24.39 GB utilized of 80.00 GB. Standard output records
`VALIDATE_SURROGATE_INPUT_OK sites=ABBY,JERC members=1024 hours=61320 development=819 fixed_test=205 publish=true`.
The published catalog points to snapshot `r0001` with SHA-256
`39b05495a57bfc9f323df67b47c0110dadfbf508b3159cde7ce1a6c59dfd187a`. All ten published package
files share their staging-file inodes, confirming retry-safe hardlink publication, and the compact
validation report records `result=pass` and `no_training=true`.

## Execution and Diagnostics

- Static validation: shell syntax, manifest hashes, submitted-copy equality, JSON syntax, and six
  compute-node unit tests pass.
- Preflight: attempts 1 (`24428809`) and 2 (`24428935`) were cancelled before execution because
  each live scheduler identity recorded `ReqMem=1M`, not the approved 20 GB. Final attempt 3 job
  `24430059` passed the live identity gate and completed successfully.
- Exact submission commands: attempt 1 used `sbatch --parsable --export=ALL,ITER001_ATTEMPT=1,ITER001_CONFIG_SHA256=935820158b7a00ed75b8efc02108c11edfaebedba27fee06fe252db3b58a1f3d,ITER001_MANIFEST_SHA256=5f535c24fbb2d7cc3ff67f6bd092c61961b55e2d8d2639577db49885a9a5bdb3 ./submit_preflight_iter001.slurm`; attempt 2 used the exact recorded clean command above. Both ran from the approved run directory.
- Job identity checks: attempts 1 and 2 matched account, partition, name, work directory, and
  one-hour limit, but failed the memory identity check
  (`ReqTRES=cpu=1,mem=1M,node=1,billing=1`). Attempt 3 passed with one task, four CPUs, and
  `ReqTRES=cpu=4,mem=20G,node=1,billing=4` plus all other locked identity fields.
- Queue and terminal accounting: attempt 1 is
  `24428809|3stage_i001_pre|CANCELLED by 49065|0:0|00:00:00|00:00:00|0||1M|None assigned`;
  attempt 2 is
  `24428935|3stage_i001_pre|CANCELLED by 49065|0:0|00:00:00|00:00:00|0||1M|1|None assigned`.
  Attempt 3 is
  `24430059|3stage_i001_pre|COMPLETED|0:0|00:00:38|00:03.546|4||20G|r7u07n1`;
  batch `MaxRSS=437484K`.
- Resource diagnostics: `scontrol show partition standard` reports `DefMemPerCPU=5120` and
  `SelectTypeParameters=NONE`; `scontrol show config` independently reports `DefMemPerCPU=5120`
  and `SelectTypeParameters=CR_CORE_MEMORY`.
- Failure, rejection, retry, or cancellation evidence: no attempt-1 output/error files exist and no
  node was assigned. The direct `/usr/bin/sbatch --test-only -vv` parser reports `mem: 20G` for the
  byte-identical submitted script. The original command resolved `sbatch` to the site
  `/usr/local/bin/sbatch` wrapper in a login shell with failing startup-module commands. Preflight
  correction/retry cycle 2 therefore uses `env -u SBATCH_GET_USER_ENV /usr/bin/sbatch` from the run
  directory with `login=false`. Two retry reviews rejected unsafe module initialization variants;
  all runtime scripts now use and verify the absolute approved OLMT_puma interpreter without
  sourcing shell profiles. Scientific code, config, resources, gates, and artifact contracts
  remained unchanged. The refreshed manifest and submitted copies passed the third retry review
  with concerns, but the live controller still reduced the request to `1M`; attempt 2 was cancelled
  without execution. Final correction cycle 3 uses four CPUs and Puma's 5120 MB/CPU default to
  preserve the 20 GB cap and requires refreshed review.
- Final record validator: `development/three_stage_surrogate/tools/validate_closeout_records.py`;
  command `python3 development/three_stage_surrogate/tools/validate_closeout_records.py --active-job-count 0`;
  output `ITER001_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff snapshot=r0001 sites=ABBY,JERC members=1024 split=819/205 active_jobs=0`.

Initialization completed at `2026-10-27T00:42:56-07:00`: the approved report, handoff, repository
iteration directories, external output root, and run directory were created. No Python, scheduler,
or data-preparation work occurred during initialization.

Preparation reached the first review gate at `2026-10-27T00:48:11-07:00`. Shell syntax, JSON
syntax, submitted-copy equality, execution-manifest checks, and `git diff --check` passed. The
execution manifest SHA-256 is `0f9993ef738f0185149c285671157167a9ba1809f5fd9623000899c8598b9659`.

The first review blocked without execution. Preflight correction cycle 1 completed at
`2026-10-27T00:55:45-07:00`; corrected execution-manifest SHA-256 is
`5f535c24fbb2d7cc3ff67f6bd092c61961b55e2d8d2639577db49885a9a5bdb3`. Canonical and external
scripts, configuration, and manifest are equal. No job has been submitted.

Refreshed read-only review passed with concerns at `2026-10-27T00:58:07-07:00`; the concerns and
proceeding rationale are recorded above. Preflight attempt 1 is now eligible for submission.

Preflight attempt 1 was submitted at `2026-10-27T00:58:27-07:00` as job `24428809`, captured
directly from `sbatch --parsable`. Login-shell module warnings preceded the returned ID and are not
job-state evidence; the batch job independently loads and verifies the pinned module.

The immediate identity gate found `ReqMem=1M` instead of 20 GB while the job was still pending, so
the approved mismatch condition was applied and attempt 1 was cancelled before execution. Terminal
accounting shows zero elapsed time, zero allocated CPUs, no node, and exit code `0:0`; no job logs
were created. Direct parser evidence confirms the unchanged submitted script requests 20 GB. This
is classified as a submission-interface failure and consumes preflight correction/retry cycle 2.

The submission process itself exports `SBATCH_GET_USER_ENV=1`. A direct parser check inherited it,
so the locked retry command explicitly removes that variable with
`env -u SBATCH_GET_USER_ENV /usr/bin/sbatch`. The exact clean-command parser output omits
`get-user-env` and retains the approved account, partition, 20 GB, one-hour limit, paths, name, and
exports.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | attempt 3 output, terminal accounting, and `seff`; attempts 1 and 2 preserved as cancelled identity mismatches | pass | Final CPU-derived attempt passed every declared lightweight environment, source, manifest, and unit-test gate. |
| prepare | yes | job `24430075` terminal accounting, logs, `seff`, and exact attempt-1 staging inventory | pass | Preparation completed zero-exit and produced the reviewed package identity without correction. |
| validate | yes | job `24430091` terminal accounting, logs, `seff`, validation report, catalog/snapshot, published inventory and inode equality | pass | Independent source reconstruction and every declared artifact, schema, value, split, and publication gate passed. |

- Overall acceptance result: `pass`.
- Overall decision and closeout conclusion: publish immutable ABBY/JERC snapshot `r0001`; Iter001
  completed without training or fixed-test use. Proceed only to the planning-only Iter002 proposal
  below, subject to fresh kickoff approval.
- Limitations: only ABBY/JERC are initialized; the other seven planned sites are absent; no
  surrogate has been trained or evaluated; the two cancelled preflight submissions reveal that
  explicit `--mem` was not preserved by this submission path, so future Puma scripts should use the
  reviewed 5 GB/CPU allocation rule; `/xdisk` is temporary and not archival storage.
- Campaign-plan amendment recommendation: `none`
- Next action: present the Iter002 planning-only proposal and await fresh consolidated kickoff
  approval; do not create Iter002 scaffold or run training automatically.

## Proposed Next-Iteration Plan (Planning Only)

- Proposed sequential ID: `iter002`.
- Work type: `implementation`.
- Campaign-plan identity, applicable phase, alignment, and proposed deviation:
  `development/three_stage_surrogate/PLAN.md`, SHA-256
  `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`, progression item 3
  (two-site prototype), `aligned`, deviation `none`.
- Evidence-derived objective and optional hypothesis: implement a deterministic ABBY/JERC direct
  `in_sample` spinup -> GPP -> SR prototype that enforces the global development-member boundary,
  uses predicted upstream C/N and same-hour predicted GPP, and proves one reusable end-to-end
  inference path. Hypothesis: existing surrogate/scaler components can be composed behind shared
  data and feature-schema interfaces without redesigning the three stages.
- Proposed inputs, upstream dependencies, identities, and trust assumptions: consume only catalog
  snapshot `r0001`, its immutable source manifests, named NetCDFs, and split manifest from the
  Iter001 output root; preserve parameter/site/member/time identities and treat the 205 fixed-test
  IDs as forbidden at loader boundaries. Reuse compatible code in `model_ELM/` and root training
  entry points only after source-contract inspection; do not reuse an artifact whose training
  membership is unproven.
- Bounded scope, work units, and exclusions: inspect and reuse existing model interfaces; implement
  shared snapshot/split loading, feature ordering, actual-timestamp no-leap `sin_doy`/`cos_doy`,
  explicit site identity, direct predicted-upstream feature generation, deterministic three-stage
  fit/predict orchestration, bundle provenance, and focused tests. Run one fixed smoke prototype on
  the first 64 ranked development members for fit and the next 16 ranked development members for
  smoke validation, using the 2018 hourly window and fixed non-tuned model settings. Exclude all
  fixed-test access, hyperparameter/feature selection, robustness repetitions, release claims,
  other sites, observations, optimization, MCMC, and scientific performance thresholds.
- Tentative acceptance gates and decision rule: exact snapshot and split identity; zero fixed-test
  reads; synchronized member/site/time grouping; fitted scalers see fit members only; GPP consumes
  predicted C/N and SR consumes predicted C/N plus predicted same-hour GPP; one deterministic
  end-to-end inference round trip; artifact reload reproduces predictions within declared numeric
  tolerance; finite outputs and complete provenance; unit/integration tests and independent
  validator pass. Accept the prototype if interface and leakage gates pass; record smoke metrics as
  descriptive evidence only and do not select or reject architecture from them.
- Proposed site, output root, resources, preflight, review, monitoring, retry, cancellation, and stop boundaries:
  Puma `chopinsong/standard`; proposed output root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/three_stage_surrogate/iter002_abby_jerc_prototype`;
  preflight one task/4 CPUs/20 GB/1 hour, prototype one task/16 CPUs/80 GB/8 hours, validation one
  task/8 CPUs/40 GB/2 hours; independent read-only reviews before preflight and operational work;
  proposed three bounded correction/retry cycles separately for preflight and operational work;
  job-scoped monitoring through terminal accounting; cancellation only for recorded scope/resource
  violations, runaway behavior, threatened inputs/outputs, or user request. Stop after validation,
  records, the approved closeout branch, and a planning-only Iter003 proposal.
- Expected evidence, artifacts, and record updates: locked config/source manifest, global-member
  exclusion evidence, feature schema, fixed smoke member lists, stage/bundle artifacts, predicted
  upstream audit, deterministic reload/inference report, descriptive smoke metrics, tests,
  submitted scripts and accounting, Iter002 report/summary/registry/handoff, and four-record
  validation.
- Authorization boundary: fresh approval of one complete kickoff package is required; do not
  create the next report or iteration-specific scaffold automatically.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter001/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment and any advisory plan-amendment recommendation recorded consistently
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized one-commit closeout branch satisfied at the expected parent and subject;
  post-commit identity and controlled paths verified externally without a circular self-hash
