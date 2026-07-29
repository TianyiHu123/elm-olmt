# University of Arizona Puma Guide for This Repository

This is the repository-specific Puma profile for
`/xdisk/chopinsong/tianyihu/elm-olmt`. It combines reusable Puma operating guidance with
repository rules, workload-specific examples, and historical observations.

The labels below define scope:

- **SITE RULE**: Puma/Slurm behavior that should be rechecked against the official site
  documentation when it may have changed.
- **REPOSITORY RULE**: required for jobs launched from this checkout.
- **WORKLOAD RULE**: applies to a particular repository workload, currently spinup-surrogate.
- **EXAMPLE**: a template or command shape; substitute the active contract's values.
- **HISTORICAL**: an observed incident or migration fact, not a general execution default.

`development/spinup_surrogate/WORKFLOW.md` remains the canonical lifecycle policy. This file
provides the Puma mechanics that the workflow references. A runtime contract must still state the
active site, finite scope, resource cap, retry boundary, monitoring authority, and closeout
authority before scheduler or compute-node work begins.

## 1. Puma site baseline

### 1.1 Official references

The official site documentation is authoritative for changing site policy:

- [Interactive Jobs](https://hpcdocs.hpc.arizona.edu/running_jobs/interactive_jobs/)
- [Batch Directives](https://hpcdocs.hpc.arizona.edu/running_jobs/batch_jobs/batch_directives/)
- [CPUs and Memory](https://hpcdocs.hpc.arizona.edu/running_jobs/cpus_and_memory/)
- [Monitoring Jobs and Resources](https://hpcdocs.hpc.arizona.edu/running_jobs/monitoring_jobs_and_resources/)
- [Batch Jobs and Slurm](https://uarizona.atlassian.net/wiki/spaces/UAHPC/pages/75989977)
- [HPC High Performance Storage](https://uarizona.atlassian.net/wiki/spaces/UAHPC/pages/75990091/HPC%2BStorage)
- [Micromamba](https://hpcdocs.hpc.arizona.edu/software/popular_software/mamba/)

The repository profile records operational facts and conventions used by this project; agents
should verify account, partition, limits, and storage availability before a new runtime contract.

### 1.2 Login nodes, compute nodes, and scheduler use

**SITE RULE:** use Puma login nodes for source control, file management, job submission, and
monitoring. Do not use login-node Python as the project runtime. Load modules and run project
Python only inside an allocated compute-node shell or a Slurm batch job.

**REPOSITORY RULE:** large, long, multi-CPU, high-memory, or matrix workloads must run through
Slurm. Read-only inspection and static validation do not require a scheduler allocation, but
training, data generation, model runs, environment installation, and other compute work do.

**EXAMPLE: interactive setup allocation**

```bash
interactive -a <ACCOUNT> -t <HH:MM:SS> -n 1 -m 5gb
```

Wait for the prompt to change from a login host such as `wentletrap` or `junonia` to a Puma
compute-node hostname before loading modules or running project commands. Use `interactive -h` when
the setup allocation needs different options. If the wrapper fails, follow the historical-incident
guidance in Section 6.2 and do not silently run the workload on the login node.

### 1.3 Accounts, partitions, and resource semantics

The current repository deployment uses account `chopinsong` and partition `standard`. Confirm
these values and current group limits before submission; they are not a substitute for a runtime
contract.

**SITE RULE, as used by this repository:** Puma standard nodes provide approximately 5 GB of
memory per requested CPU. For a CPU-limited job, request the CPU count and normally omit both
`--mem` and `--mem-per-cpu`, allowing Slurm to derive the standard allocation. For a
memory-limited job, convert the required memory to CPUs with `ceil(total_GB / 5)` or use an
explicit total-memory request after confirming its placement semantics. Do not set a
nonstandard `--mem-per-cpu` value without a site-specific reason; it may route the job to scarce
high-memory nodes or produce an unexpected allocation.

Do not carry Perlmutter-only directives such as `--qos=shared` or `--constraint=cpu` into Puma
scripts. Request GPUs or a high-memory constraint only when the active runtime contract requires
them.

**EXAMPLE: generic CPU-limited header**

```bash
#!/usr/bin/env bash
#SBATCH --account=<ACCOUNT>
#SBATCH --partition=<PARTITION>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=<CPUS>
#SBATCH --time=<HH:MM:SS>
#SBATCH --output=job_%j.out
#SBATCH --error=job_%j.err
```

### 1.4 Scheduler command reference

Use the supported Puma command interface documented by UArizona HPC first. The monitoring
documentation lists the supported forms for `squeue`, `scontrol`, `scancel`, `job-history`,
`seff`, and `job-limits`: [Monitoring Jobs and Resources](https://hpcdocs.hpc.arizona.edu/running_jobs/monitoring_jobs_and_resources/).
Record job IDs and terminal accounting in the active workload record.

At session bootstrap, record command resolution with `type -a` or `command -v` for the Slurm
commands used by the workload. Do not replace the supported command interface with an absolute
`/usr/bin/<command>` path merely as a convention. An absolute binary is a fallback only when the
supported command is demonstrably malfunctioning or unavailable; record the failure, command
paths, timestamps, and resulting state when using that fallback.

| Purpose | Command shape |
| --- | --- |
| Submit | `sbatch --export=ALL,<KEY=VALUE,...> <script>` |
| Queue state and pending reason | `squeue --job=<JOB_ID>` |
| Detailed active-job state | `scontrol show job <JOB_ID>` |
| Terminal accounting | `sacct --jobs=<JOB_ID> --format=JobID,JobName,Partition,Account,AllocTRES,State,ExitCode,MaxRSS` |
| Readable job history | `job-history <JOB_ID>` |
| Efficiency report | `seff <JOB_ID>` |
| Group limits and usage | `job-limits <ACCOUNT>` |
| Cancel, only when authorized | `scancel <JOB_ID_OR_IDS>` |

### 1.5 Codex Slurm execution-context gate

Codex's default filesystem sandbox can run in a user namespace that drops supplemental HPC
groups or blocks Slurm connectivity. Before a Codex agent relies on any supported Slurm command,
verify its effective group and execution context:

```bash
id
id -Gn
```

For a job using this repository's current `chopinsong` account, the effective groups must include
`chopinsong`. If an authorized runtime contract selects another account, verify that the effective
groups include that account's required project group instead. If the required group is absent, the
Puma command wrappers used by `scontrol`, `sacct`, and `seff` can fail while attempting their group
transition. The sandbox can also produce Slurm connection, socket, controller, authentication, or
resource errors that do not occur in the host HPC context.

Once the default sandbox is known to lack the required project group or Slurm connectivity, route
all Slurm commands directly through the product's approved outside-sandbox execution context. Do
not keep probing Slurm inside the affected sandbox. A Slurm error produced there is
**observation-context failure**, not evidence that Puma's scheduler or controller has failed. In
particular, never use an in-sandbox `scontrol ping` result to diagnose scheduler health.

The primary agent must run read-only monitoring and post-job accounting outside the affected
user-namespace sandbox. This is a monitoring-context correction, not scheduler authority: it does
not authorize submission, cancellation, retries, configuration changes, or any other mutation.

Maintain reusable approval only for the read-only command families needed for normal monitoring:
`squeue --job=...`, `scontrol show job ...`, `sacct --jobs=...`, `seff <JOB_ID>`,
`job-history <JOB_ID>`, and `job-limits <ACCOUNT>`. Do not grant reusable approval for `scontrol`
generally. Keep `sbatch`, `scancel`, `scontrol` mutations, and other state-changing commands under
the runtime contract and their separate approval boundary. When the runtime contract authorizes
such an action, it must also state whether that command may be executed outside the sandbox.

Use commands according to job state:

| State or need | Command |
| --- | --- |
| Active or pending job, including an array | `squeue --job=<PARENT_JOB_ID> -r` |
| Detailed active-job configuration | `scontrol show job <PARENT_JOB_ID>` |
| Completed-job accounting, whole array | `sacct --jobs=<PARENT_JOB_ID> --format=JobID,JobName,State,ExitCode,Elapsed,TotalCPU,AllocCPUS,MaxRSS,AllocTRES` |
| Completed-job accounting, one leaf | `sacct --jobs=<JOB_ID>_<ARRAY_INDEX> --format=JobID,JobName,State,ExitCode,Elapsed,TotalCPU,AllocCPUS,MaxRSS,AllocTRES` |
| CPU and memory efficiency for one leaf | `seff <JOB_ID>_<ARRAY_INDEX>` |
| Readable terminal history | `job-history <JOB_ID_OR_ARRAY_ELEMENT>` |

Use the parent ID to reconcile every array element and overall terminal completeness. Use a
concrete element ID only for leaf-specific diagnosis or efficiency reporting.

`squeue` and `scontrol` reporting `Invalid job id specified` for a completed job is expected;
use `sacct`, `seff`, or `job-history` for terminal evidence. A successful query with a valid empty
result means that no matching job was found in that interface; a nonzero exit, timeout, malformed
response, or connection error leaves state unknown.

Record the exact query command, execution context, scope, timestamp, exit status, and response in
the workload ledger. Apply these evidence rules:

- A connection, controller, socket, authentication, group-transition, or resource error from the
  affected Codex sandbox is inadmissible as scheduler-health or job-state evidence. Repeat the
  exact job-scoped query through the approved outside-sandbox context without first diagnosing a
  Puma scheduler problem.
- If that outside-sandbox query succeeds, use its result as the authoritative scheduler evidence.
  If it fails, classify the observation as an authoritative query failure and preserve job state
  as unknown. Retry the same job-scoped query with bounded backoff at least once.
- Prefer a parent-job ID over a user-wide query. For an array, use `squeue --job=<JOB_ID> -r` to
  list its individual elements and `sacct --jobs=<JOB_ID>` for terminal accounting. If retries
  continue to fail, preserve the state as unknown and reconcile later using scheduler queries,
  job logs, and exact output-artifact validation.
- A query or transport failure is not a workload failure and must not consume a workload retry,
  authorize cancellation or resubmission, or support a completion claim. Classify a resource or
  scheduler job failure only from authoritative job-state or terminal-accounting evidence.

If an authorized `sbatch` invocation is accidentally attempted inside the affected sandbox and
returns an error or no parseable job ID, submission state is unknown. Before resubmitting, use
approved outside-sandbox `squeue` and `sacct` queries to prove that the attempted submission did not
create a matching job. This reconciliation is required to prevent duplicate jobs.

**Array monitoring example (Puma):** UArizona's array-job convention returns one parent ID from
`sbatch`; `squeue --job=<JOB_ID> -r` expands that parent into rows such as
`<JOB_ID>_<ARRAY_INDEX>`. Use the same parent ID for accounting:

```bash
job_id="3186754"

squeue --job="${job_id}" -r

sacct --jobs="${job_id}" \
  --format=JobID,JobName,State,ExitCode,Elapsed,AllocTRES,MaxRSS
```

This follows the [UArizona array-job example](https://hpcdocs.hpc.arizona.edu/running_jobs/batch_jobs/array_jobs/#example-jobs).
Record the parent ID, array range, per-element terminal states, and any retry evidence in the
workload record.

For arrays, monitor the parent job and inspect individual array elements when diagnosing a partial
failure. Use `squeue` while jobs are active and `sacct` after they reach terminal state. Do not
classify a job from queue state alone; record exit code, allocation, elapsed time, and memory.

## 2. Repository-wide Puma rules

These rules apply to any workload launched from this checkout, independent of whether it is a
spinup-surrogate run.

### 2.1 Fixed repository root and early validation

The repository root is fixed at:

```bash
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
```

Canonical and submitted scripts must use this literal path. Do not derive it from `$0`, a copied
script location, `SLURM_SUBMIT_DIR`, the current directory, or an environment override. Before
loading the environment or touching outputs, validate the repository controls needed by the
workload:

```bash
test -f "${REPO_ROOT}/train_surrogate_spinup.py"
test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"
test -f "${REPO_ROOT}/development/hpc/puma.md"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
cd "${REPO_ROOT}"
```

An iteration or workload script must add early checks for its own tracked record and canonical
artifacts. A Python utility launched by absolute path must explicitly put `REPO_ROOT` on
`sys.path` before importing repository modules.

### 2.2 Repository environment

The current repository environment is named `OLMT_puma`. Prefer direct invocation through
micromamba rather than relying on shell activation:

```bash
module load micromamba
micromamba env list
micromamba run -n OLMT_puma python --version
micromamba run -n OLMT_puma python <SCRIPT> <ARGUMENTS>
```

Environment creation or repair is compute-node work and requires explicit execution authority.
Do not install or repair the environment from a login node.

The environment currently uses a home-directory micromamba root. Monitor the home quota separately
from job memory, and do not relocate or recreate the environment as part of an experiment unless
that change has its own authorization and provenance record.

### 2.3 Storage and provenance

`/xdisk` is temporary and unbacked. Before a new workload, check capacity and retention/expiration
status, and keep an external copy of irreplaceable inputs and results. Do not treat a successful
Slurm completion as archival protection.

Every production workload should preserve, as applicable:

- the repository commit and dirty-diff/source-manifest state;
- the canonical script and its hash;
- the exact submitted script and configuration hashes;
- the exact submission command and log paths;
- job IDs, terminal state, exit code, allocation, elapsed time, and memory evidence.

### 2.4 Slurm script authoring and submission layout

**REPOSITORY RULE:** create or copy the self-describing submitted Slurm script into the
user-specified run, case, or variant directory before submission. Submit the copied script from
inside that directory. Do not submit the repository canonical script directly, and do not rely on
an absolute script path plus a different caller directory as a substitute for this procedure.

Canonical scripts must be human-readable and auditable. In particular:

- define one variable per line, especially when a later variable depends on an earlier one;
- do not combine dependent assignments in one `readonly` command;
- put long commands on multiple lines with one option per line;
- group the script into recognizable sections for directives, paths, validation, environment,
  provenance, and execution;
- include explicit `#SBATCH --output` and `#SBATCH --error` directives in every submission
  script. Use `%A_%a` for array jobs and `%j` for non-array jobs.

The Iter007 script
`development/spinup_surrogate/slurm/iter007/case.train_surrogate_spinup_iter007_mlp_tuning.slurm`
is the repository formatting example. Command-line output/error overrides may be used for a
special submission, but the script itself must remain self-describing.

The required submission shape is:

```bash
readonly RUN_DIR="<USER_SPECIFIED_RUN_OR_CASE_DIR>"
readonly SUBMITTED_SCRIPT="${RUN_DIR}/submit_<VARIANT>.slurm"
readonly SUBMISSION_CONFIG="${RUN_DIR}/submission_config.env"

mkdir -p "${RUN_DIR}"
cp "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
test -f "${SUBMITTED_SCRIPT}"
test -f "${SUBMISSION_CONFIG}"

cd "${RUN_DIR}"
test "$(pwd -P)" = "${RUN_DIR}"
sbatch --parsable \
  --export="ALL,SUBMISSION_CONFIG=${SUBMISSION_CONFIG}" \
  "./submit_<VARIANT>.slurm" </dev/null
```

Record the copied script path/hash, configuration path/hash, run directory, exact submission
command, and returned job ID immediately. Use `</dev/null` when the submission is performed from a
manifest-reading loop so `sbatch` cannot inherit the manifest's stdin.

The spinup-surrogate default output root is intentionally defined in the workload section below;
it is not a repository-wide output convention.

### 2.5 Workflow authority

Workload-specific lifecycle policy is defined by that workload's workflow document. For
spinup-surrogate work, `development/spinup_surrogate/WORKFLOW.md` is authoritative for runtime
contracts, authorization, retries, monitoring, failure handling, aggregation, selection, and
closeout.

This Puma profile defines site mechanics and repository execution constraints only. Agents must
read the applicable workflow document and workload record before execution and must not infer
lifecycle rules from this section.

## 3. Spinup-surrogate workload profile

Everything in this section is a **WORKLOAD RULE** for the current spinup-surrogate workflow, not a
general Puma requirement.

### 3.1 Current resource and execution shape

The current spinup-surrogate deployment uses:

- account `chopinsong`, partition `standard`;
- one node and one Slurm task;
- 10 CPUs, implying approximately 50 GB on the standard memory-per-CPU policy;
- a 30-minute production walltime shape, unless the active contract states otherwise;
- `N_JOBS=4` and `PRE_DISPATCH=n_jobs`;
- one-thread BLAS/OpenMP settings;
- task-local `XDG_CACHE_HOME` isolation.

`N_JOBS=4` is retained for compatibility with the legacy `GridSearchCV` path. The current fixed
parameter LBFGS path does not create fitting workers from `N_JOBS`, and the current permutation
importance loop is sequential. Increasing `N_JOBS` does not automatically make this workload use
all allocated CPUs.

Launch the workload as one Python process inside the single-task allocation. Do not add `srun`
solely because the job was submitted through Slurm. Use `srun` only for multiple Slurm tasks, MPI
ranks, or a separately authorized site requirement.

### 3.2 Spinup output root and cache isolation

The current spinup-surrogate default output root is:

```text
/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output
```

Each canonical script must support an explicit output override, and each production variant must
use a task-local cache directory rather than a shared cache. Do not infer this output root for
unrelated repository workloads.

### 3.3 Variant-local submission artifacts

For a production matrix variant, keep logs and the submitted copy under the variant's output
directory:

```text
<OUTPUT_ROOT>/UQ_output/<RUN_SLUG>/
  slurm_%A_%a.out
  slurm_%A_%a.err
  submit_<VARIANT>.slurm
  submission_config.env
```

The submitted script must be self-describing for exactly one locked variant. Either render locked
variables into the submitted copy or source an immutable `submission_config.env`. Do not submit the
repository canonical script directly. Record canonical and submitted paths/hashes, configuration
hash, exact `sbatch` command, and both log paths in the workload record.

**EXAMPLE: materialization and submission shape**

The following is a template, not a complete command until all placeholders are defined and the
configuration has been validated against the manifest:

```bash
readonly VARIANT_DIR="${OUTPUT_ROOT}/UQ_output/${RUN_SLUG}"
readonly SUBMITTED_SCRIPT="${VARIANT_DIR}/submit_${VARIANT}.slurm"
readonly SUBMISSION_CONFIG="${VARIANT_DIR}/submission_config.env"

mkdir -p "${VARIANT_DIR}"

cp "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
test -f "${SUBMISSION_CONFIG}"
test -f "${SUBMITTED_SCRIPT}"

cd "${VARIANT_DIR}"
test "$(pwd -P)" = "${VARIANT_DIR}"
job_id=$(
  sbatch --parsable \
    --export="ALL,SUBMISSION_CONFIG=${SUBMISSION_CONFIG},VARIANT=${VARIANT},N_JOBS=${N_JOBS},PRE_DISPATCH=${PRE_DISPATCH}" \
    "./submit_${VARIANT}.slurm" </dev/null
)
test -n "${job_id}"
echo "submitted variant=${VARIANT} job_id=${job_id} run_dir=${VARIANT_DIR}"
```

The submitted script itself must contain the authoritative output and error directives, for
example:

```bash
#SBATCH --output=slurm_%A_%a.out
#SBATCH --error=slurm_%A_%a.err
```

Place logs at the variant root, not at the shared output root or in an additional nested
per-variant directory. If a command-line output/error override is used, record the override and
verify that it still resolves inside the same run directory.

### 3.4 Spinup preflight example

Use a bounded one-CPU/approximately-5-GB allocation for a no-training preflight when authorized.
The time limit and tracked utility are workload-contract values. Materialize the tracked preflight
script into the user-specified preflight run directory and submit it from there:

```bash
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PREFLIGHT_DIR="<USER_SPECIFIED_PREFLIGHT_RUN_DIR>"
readonly PREFLIGHT_SCRIPT="${PREFLIGHT_DIR}/validate_<ITERATION>.slurm"

mkdir -p "${PREFLIGHT_DIR}"
cp "${REPO_ROOT}/<TRACKED_PREFLIGHT>" "${PREFLIGHT_SCRIPT}"
test -f "${PREFLIGHT_SCRIPT}"
cd "${PREFLIGHT_DIR}"
test "$(pwd -P)" = "${PREFLIGHT_DIR}"

job_id=$(
  sbatch --parsable \
    --account=chopinsong \
    --partition=standard \
    --nodes=1 \
    --ntasks=1 \
    --cpus-per-task=1 \
    --time=<PREFLIGHT_TIME> \
    --job-name=puma-preflight \
    "./validate_<ITERATION>.slurm" </dev/null
)
test -n "${job_id}"
echo "submitted preflight job_id=${job_id} run_dir=${PREFLIGHT_DIR}"
```

The copied preflight script must contain explicit `#SBATCH --output` and `#SBATCH --error`
directives, for example `puma_preflight_%j.out` and `puma_preflight_%j.err`.

The preflight must establish the fixed repository root before importing repository modules. A
preflight failure before training is an application/configuration failure unless the active
workflow contract explicitly provides a separate validation-only correction and retry.

### 3.5 Spinup monitoring and closeout

For a variant matrix, submit one job or array per variant and monitor the complete job set
concurrently. Use `squeue` while active and `sacct` after terminal state. Preserve per-leaf state,
exit code, allocation, elapsed time, MaxRSS, retry classification, aggregation evidence, selection
metrics, and closeout records. The retry and closeout rules come from the active
`WORKFLOW.md` contract, not from this resource example.

## 4. Puma migration workload example

This section is a **WORKLOAD EXAMPLE** for the temporary Perlmutter-to-Puma case migration. It is
not required for ordinary repository jobs or spinup-surrogate training.

### 4.1 Current migration mapping

For the nine migrated case pickles:

- `case.runroot` maps to
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe`;
- `case.metdir` maps per site to
  `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/<SITE>/1x1pt_<SITE>/CLM1PT_data`;
- `finidat`, `dependcase`, and unrelated historical path metadata remain unchanged;
- restart lookup continues under `case.runroot/UQ/case.dependcase/gNNNNN/` using the basename of
  `case.finidat`.

Use `development/spinup_surrogate/migrate_case_pickles.py` only on a Puma compute node with an
explicit migration contract. Its inspect/apply modes validate the complete nine-case set,
including resolved restart files, ensemble surface files, forcing sequences, required NetCDF
variables, spinup-cycle coverage, and pickle invariants. It preserves each original as
`<case>.pkl.perlmutter.bak`; backups are not removed automatically. Apply stages and reloads every
pickle before activating it. Recovery restores the original set while preserving backups and any
already activated Puma pickles as staged files.

### 4.2 Migration command example

The ordered case list is:

```bash
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly MIGRATION_CASES=ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,YELL_ppe6_I20TRCNPRDCTCBC
readonly MIGRATION_TOOL=${REPO_ROOT}/development/spinup_surrogate/migrate_case_pickles.py

micromamba run -n OLMT_puma python "${MIGRATION_TOOL}" \
  --inspect \
  --pickle-dir "${REPO_ROOT}/pklfiles" \
  --cases "${MIGRATION_CASES}" \
  --run-root /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe \
  --met-root /xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON

micromamba run -n OLMT_puma python "${MIGRATION_TOOL}" \
  --apply \
  --pickle-dir "${REPO_ROOT}/pklfiles" \
  --cases "${MIGRATION_CASES}" \
  --run-root /xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe \
  --met-root /xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON
```

Use identical arguments with `--recover` only to restore the original set after interrupted
activation. Do not remove backups as part of the utility run.

## 5. Pre-submit and monitoring checklist

Apply the relevant portions of this checklist after the runtime contract is active:

1. Confirm the session is on the intended Puma site and select this profile.
2. Confirm account, partition, CPU/memory shape, walltime, array scope, and retry boundary.
3. Verify the repository root and required tracked controls.
4. Verify the environment invocation and all workload-specific paths.
5. Run static checks and the authorized no-training preflight, if required.
6. Verify submitted copies, configuration manifests, log paths, and hashes.
7. Show and record the exact `sbatch` command before submission.
8. Record job IDs immediately after submission.
9. Monitor with `squeue` while active and `sacct` after terminal state.
10. Use `seff` when diagnosing CPU efficiency or memory headroom.
11. Preserve logs, accounting evidence, failure classification, and workload results.
12. Continue through aggregation and closeout when the active workflow contract requires it.

## 6. Failure classification and historical observations

### 6.1 Failure categories

Capture accounting evidence and distinguish:

- account, partition, or scheduler policy errors;
- resource exhaustion or timeouts;
- environment/module activation failures;
- repository-root or launch-layout mismatches;
- storage, quota, or expiration failures;
- application, code, or configuration failures;
- scientific validity rejections that do not block the iteration.

Retry only the resource or scheduler failure classes permitted by the active workload contract.
Application, code, configuration, and scientific-control changes require fresh authorization.

### 6.2 HISTORICAL: interactive-wrapper incident

During the 2026-07-18 migration, `/usr/local/bin/interactive` and `/usr/local/bin/salloc`
terminated before allocation with a `/bin/sg` segmentation fault. The underlying
`/usr/bin/sbatch` path worked. This is an observed incident, not a permanent claim that
interactive jobs are unavailable. If the issue recurs, capture the command and host evidence,
verify whether the wrapper is currently healthy, and use an explicitly authorized bounded batch
job when appropriate.

### 6.3 HISTORICAL: migration validation evidence

The migration validation observed 84 monthly forcing files for ABBY/JERC/OSBS/SOAP/RMNP/TALL and
72 monthly files for TEAK/WREF/YELL. These observations support the recorded migration provenance;
they are not general Puma storage or forcing guarantees.

### 6.4 HISTORICAL: spinup resource observations

Past spinup-surrogate leaves reached close to the standard memory ceiling while CPU efficiency was
low. This is why the current workload profile retains a memory-oriented 10-CPU shape and explicit
single-thread controls. Revisit the shape only with new accounting evidence and a new runtime
contract; do not infer that every repository job should request 10 CPUs.
