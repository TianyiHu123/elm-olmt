# University of Arizona Puma Profile for This Repository

This profile defines Puma site mechanics and repository-wide execution rules for
`/xdisk/chopinsong/tianyihu/elm-olmt`. It is intended for any current or future workflow in this
checkout.

The labels below define scope:

- **SITE RULE**: Puma or Slurm behavior that should be rechecked against official site
  documentation when it may have changed.
- **REPOSITORY RULE**: required for work launched from this checkout.
- **EXAMPLE**: a command shape or historical workload snapshot; it is not a default contract.
- **HISTORICAL**: an observed incident or result, not a permanent Puma guarantee.

The governing workflow document that directs readers to this Puma profile remains the canonical
lifecycle policy for that workload. This profile defines site mechanics and repository execution
constraints only; it does not define or broaden workload scope, scheduler authority, retry policy,
completion criteria, aggregation rules, selection rules, or closeout authority.

Obtain the governing workflow's required runtime approval before scheduler or compute-node work.

## 1. Puma site mechanics

### 1.1 Official references

Official UArizona HPC documentation is authoritative for changing site policy:

- [UArizona HPC Documentation](https://hpcdocs.hpc.arizona.edu/)
- [Running Jobs Overview](https://hpcdocs.hpc.arizona.edu/running_jobs/overview/)
- [Interactive Jobs](https://hpcdocs.hpc.arizona.edu/running_jobs/interactive_jobs/)
- [Batch Jobs Tutorial](https://hpcdocs.hpc.arizona.edu/running_jobs/batch_jobs/intro/)
- [Batch Directives](https://hpcdocs.hpc.arizona.edu/running_jobs/batch_jobs/batch_directives/)
- [Array Jobs](https://hpcdocs.hpc.arizona.edu/running_jobs/batch_jobs/array_jobs/)
- [CPUs and Memory](https://hpcdocs.hpc.arizona.edu/running_jobs/cpus_and_memory/)
- [Monitoring Jobs and Resources](https://hpcdocs.hpc.arizona.edu/running_jobs/monitoring_jobs_and_resources/)
- [Resource Optimization](https://hpcdocs.hpc.arizona.edu/running_jobs/resource_optimization/)
- [Job Limits](https://hpcdocs.hpc.arizona.edu/running_jobs/job_limits/)
- [HPC Storage](https://hpcdocs.hpc.arizona.edu/storage_and_transfers/storage/hpc_storage/)
- [Software Modules](https://hpcdocs.hpc.arizona.edu/software/modules/)
- [Micromamba](https://hpcdocs.hpc.arizona.edu/software/popular_software/mamba/)

Verify account access, partition availability, limits, and storage status before approving a new
runtime contract.

### 1.2 Login nodes, compute nodes, and scheduler use

**SITE RULE:** use Puma login nodes for source control, file management, job submission, and
monitoring. Do not use login-node Python as the project runtime. Load modules and run project
Python only inside an allocated compute-node shell or a Slurm batch job.

**REPOSITORY RULE:** large, long, multi-CPU, high-memory, sweep, matrix, training, data-generation,
model, or environment-installation workloads must run through Slurm. Read-only inspection and
static validation do not require an allocation.

**AGENT RULE:** agents must use bounded Slurm batch jobs by default. Do not use `interactive` or
`salloc` for agent-operated work unless the user explicitly requires an interactive allocation.
The following interactive example is for a human operator.

**EXAMPLE: human interactive setup allocation**

```bash
interactive -a chopinsong -t <HH:MM:SS> -n 1 -m 5gb
```

Wait for the prompt to change from a login host such as `wentletrap` or `junonia` to a compute-node
hostname before loading modules or running project commands. On Puma, the current `interactive`
helper submits through `srun`; direct `salloc` commands remain supported when more customization is
needed. Use `interactive -h` when the setup allocation needs different options. If the helper
fails, follow Section 4.1 and do not silently run the workload on the login node.

### 1.3 Repository account, partition, and resource semantics

The Puma defaults for this repository are:

```text
account: chopinsong
partition: standard
```

Use `chopinsong` and `standard` unless the user explicitly selects another authorized account or
partition for the active runtime contract. Confirm the selected account's project group and
current limits before submission.

**SITE RULE, as used by this repository:** Puma standard nodes provide 5 GB of memory per requested
CPU. For a CPU-limited job, request the CPU count and normally omit both `--mem` and
`--mem-per-cpu`, allowing Slurm to derive the standard allocation. For a memory-limited job,
either convert required memory to CPUs with `ceil(total_GB / 5)` or request total memory with
`--mem=<TOTAL>`. Do not specify both a CPU count and total memory for the latter shape; Puma's
scheduler derives the corresponding CPU allocation from the standard ratio.

Do not set a nonstandard `--mem-per-cpu` value without a site-specific reason; it may route the job
to scarce high-memory nodes or produce an unexpected allocation. Do not carry Perlmutter-only
directives such as `--qos=shared` or `--constraint=cpu` into Puma scripts. Request GPUs or a
high-memory constraint only when the active runtime contract requires them.

**EXAMPLE: generic CPU-limited header**

```bash
#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=<CPUS>
#SBATCH --time=<HH:MM:SS>
#SBATCH --output=job_%j.out
#SBATCH --error=job_%j.err
```

### 1.4 Scheduler operation and monitoring

Agents must run every Slurm-related read-only command outside the agent sandbox. This includes
`squeue`, read-only `scontrol` queries, `sacct`, `seff`, `job-history`, and `job-limits`. Do not
probe these commands inside the sandbox first and do not use an in-sandbox result as scheduler or
job-state evidence.

Outside-sandbox monitoring access is not scheduler authority. Submission with `sbatch`,
cancellation with `scancel`, retries, configuration changes, and other scheduler mutations still
require authorization from the governing workflow and active runtime contract.

Use the following command shapes:

| State or need | Command |
| --- | --- |
| Submit an authorized batch job | `sbatch --export=ALL,<KEY=VALUE,...> <script>` |
| Active or pending job, including an array | `squeue --job=<PARENT_JOB_ID> -r` |
| Detailed active-job configuration | `scontrol show job <PARENT_JOB_ID>` |
| Job accounting, whole array | `sacct --jobs=<PARENT_JOB_ID> --format=JobID,JobName,State,ExitCode,Elapsed,TotalCPU,AllocCPUS,MaxRSS,AllocTRES` |
| Job accounting, one leaf | `sacct --jobs=<JOB_ID>_<ARRAY_INDEX> --format=JobID,JobName,State,ExitCode,Elapsed,TotalCPU,AllocCPUS,MaxRSS,AllocTRES` |
| CPU and memory efficiency for one leaf | `seff <JOB_ID>_<ARRAY_INDEX>` |
| Readable terminal history | `job-history <JOB_ID_OR_ARRAY_ELEMENT>` |
| Group limits and usage | `job-limits <ACCOUNT>` |
| Cancel, only when authorized | `scancel <JOB_ID_OR_IDS>` |

`squeue` and `scontrol` reporting `Invalid job id specified` for a completed job is expected; use
`sacct`, `seff`, or `job-history` for terminal evidence. A successful query with a valid empty
result means no matching job was found in that interface. A nonzero exit, timeout, malformed
response, or connection error leaves state unknown.

If an outside-sandbox query fails, preserve job state as unknown and retry the same job-scoped
query with bounded backoff. A query or transport failure is not a workload failure and must not
consume a workload retry, authorize cancellation or resubmission, or support a completion claim.

## 2. Repository-wide Puma integration

### 2.1 Fixed repository root and generic early validation

The repository root is fixed at `/xdisk/chopinsong/tianyihu/elm-olmt`. Canonical and submitted
scripts must use this literal path. Do not derive it from `$0`, a copied script location,
`SLURM_SUBMIT_DIR`, the current directory, or an environment override.

Before loading the environment or touching outputs, validate the selected workload's governing
files:

```bash
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly PUMA_PROFILE="${REPO_ROOT}/development/hpc/puma.md"
readonly WORKFLOW_FILE="${REPO_ROOT}/<PATH_TO_WORKFLOW>"
readonly WORKLOAD_ENTRYPOINT="${REPO_ROOT}/<PATH_TO_ENTRYPOINT>"

test -f "${PUMA_PROFILE}"
test -f "${WORKFLOW_FILE}"
test -f "${WORKLOAD_ENTRYPOINT}"
test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"

cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
```

A workflow script must add early checks for its tracked record, configuration, manifest, and
canonical artifacts. A Python utility launched by absolute path must explicitly put `REPO_ROOT` on
`sys.path` before importing repository modules.

### 2.2 Repository environment

`OLMT_puma` is the Puma environment for this repository. Use it for repository Python workloads
unless the user explicitly authorizes a different environment for the active workflow.

Prefer direct invocation through micromamba rather than relying on shell activation:

```bash
readonly MICROMAMBA_MODULE="micromamba/<VALIDATED_VERSION>"
module load "${MICROMAMBA_MODULE}"
micromamba env list
micromamba run -n OLMT_puma python --version
micromamba run -n OLMT_puma python "${SCRIPT}" "${ARGUMENTS[@]}"
```

For a new workflow, record and pin the validated micromamba module version. Existing historical
scripts that load the site's default module remain provenance and should not be rewritten solely
to adopt this convention.

Environment creation or repair is compute-node work and requires explicit execution authority. Do
not install or repair the environment from a login node.

The environment currently uses a home-directory micromamba root. Monitor home quota separately
from job memory, and do not relocate or recreate the environment as part of a workload unless that
change has its own authorization and provenance.

### 2.3 Storage and provenance

`/xdisk` is temporary storage with allocations lasting up to 300 days. UArizona HPC storage is not
backed up. Storage snapshots may sometimes permit prompt recovery, but recovery is not guaranteed
and snapshots are not backups. Before a new workload, check capacity and expiration status, and
keep an external copy of irreplaceable inputs and results. Do not treat successful Slurm
completion as archival protection.

Every production workload should preserve, as applicable:

- the repository commit and dirty-diff or source-manifest state;
- the canonical script and its hash;
- the exact submitted script and configuration hashes;
- the exact submission command and log paths;
- the returned job IDs;
- terminal state, exit code, allocation, elapsed time, and memory evidence.

### 2.4 Slurm script authoring

Canonical scripts must be human-readable and auditable:

- define one variable per line, especially when a later variable depends on an earlier one;
- do not combine dependent assignments in one `readonly` command;
- put long commands on multiple lines with one option per line;
- group directives, paths, validation, environment, provenance, and execution into recognizable
  sections;
- include explicit `#SBATCH --output` and `#SBATCH --error` directives;
- use `%A_%a` for array jobs and `%j` for non-array jobs.

Command-line output or error overrides may be used for a special submission, but the canonical
script must remain self-describing and the override must be recorded.

### 2.5 Submitted-copy and run-directory layout

**REPOSITORY RULE:** create or copy a self-describing submitted Slurm script into the
user-specified run, case, or variant directory before submission. Submit the copied script from
inside that directory. Do not submit the repository canonical script directly.

The generic submission shape is:

```bash
readonly RUN_DIR="<USER_SPECIFIED_RUN_OR_CASE_DIR>"
readonly CANONICAL_SCRIPT="${REPO_ROOT}/<PATH_TO_CANONICAL_SCRIPT>"
readonly SUBMITTED_SCRIPT="${RUN_DIR}/submit_<RUN_NAME>.slurm"
readonly SUBMISSION_CONFIG="${RUN_DIR}/submission_config.env"

mkdir -p "${RUN_DIR}"
cp "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"

test -f "${SUBMITTED_SCRIPT}"
test -f "${SUBMISSION_CONFIG}"

cd "${RUN_DIR}"
test "$(pwd -P)" = "${RUN_DIR}"

job_id=$(
  sbatch --parsable \
    --export="ALL,SUBMISSION_CONFIG=${SUBMISSION_CONFIG}" \
    "./submit_<RUN_NAME>.slurm" </dev/null
)

test -n "${job_id}"
echo "submitted job_id=${job_id} run_dir=${RUN_DIR}"
```

Use `</dev/null` when submission occurs inside a manifest-reading loop so `sbatch` cannot inherit
the manifest's stdin.

Preserve the submission evidence listed in Section 2.3.

## 3. Generic job operation

### 3.1 Bounded preflight shape

When the governing workflow requires a no-workload or no-training preflight, materialize its
tracked script into a dedicated run directory and submit it from there:

```bash
readonly PREFLIGHT_DIR="<USER_SPECIFIED_PREFLIGHT_RUN_DIR>"
readonly TRACKED_PREFLIGHT="${REPO_ROOT}/<PATH_TO_TRACKED_PREFLIGHT>"
readonly PREFLIGHT_SCRIPT="${PREFLIGHT_DIR}/validate_<RUN_NAME>.slurm"

mkdir -p "${PREFLIGHT_DIR}"
cp "${TRACKED_PREFLIGHT}" "${PREFLIGHT_SCRIPT}"

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
    "./validate_<RUN_NAME>.slurm" </dev/null
)

test -n "${job_id}"
echo "submitted preflight job_id=${job_id} run_dir=${PREFLIGHT_DIR}"
```

The copied preflight must contain explicit output and error directives and establish the fixed
repository root before importing repository modules.

### 3.2 Submission reconciliation

If an authorized `sbatch` invocation returns an error or no parseable job ID, submission state is
unknown. Before resubmitting, use approved outside-sandbox `squeue` and `sacct` queries to prove
that the attempted submission did not create a matching job. Reconcile by job name, user,
submission window, script, and run directory to prevent duplicate jobs.

### 3.3 Array monitoring and accounting handoff

UArizona's array-job convention returns one parent ID from `sbatch`. Use that parent ID as the
`squeue` and `sacct` query selector. The governing workflow's recorded parent and approved array
scope remain the completeness criterion; a parent-ID query does not make the parent alone
sufficient evidence for an array.

For a long-running authorized job, the primary agent may use the following state-change detector
through one ongoing terminal-tool session. The detector observes only `squeue`: it reports compact
state changes and tells the agent when to inspect accounting. It does not determine workload
completion.

```bash
readonly JOB_ID="<PARENT_JOB_ID>"
readonly POLL_SECONDS=300
previous_snapshot=""

while true; do
  if ! raw_snapshot="$(squeue --job="${JOB_ID}" -r -h -o '%i|%T|%r' 2>&1)"; then
    printf '%s ACCOUNTING_CHECK_REQUIRED squeue_query_failed job_id=%s detail=%s\n' \
      "$(date -Iseconds)" "${JOB_ID}" "${raw_snapshot}" >&2
    exit 2
  fi

  if [[ -z "${raw_snapshot}" ]]; then
    printf '%s ACCOUNTING_CHECK_REQUIRED queue_empty job_id=%s\n' \
      "$(date -Iseconds)" "${JOB_ID}"
    exit 0
  fi

  snapshot="$({
    printf '%s\n' "${raw_snapshot}" |
      awk -F'|' '{ key = $2 "|" $3; count[key] += 1 } END { for (key in count) print key "|" count[key] }' |
      LC_ALL=C sort
  })"

  if [[ "${snapshot}" != "${previous_snapshot}" ]]; then
    printf '%s %s\n' "$(date -Iseconds)" "${snapshot}"
    previous_snapshot="${snapshot}"
  fi

  sleep "${POLL_SECONDS}"
done
```

`POLL_SECONDS=300` is an example scheduler-friendly throttle for this Puma command. Routine output
is grouped as `STATE|REASON|COUNT`. `ACCOUNTING_CHECK_REQUIRED` is an
observation-to-accounting handoff signal and never evidence of workload completion.

On that handoff, use the job-scoped accounting command from Section 1.4 and choose the next action
under the governing workflow. If the response is too large for the agent session, preserve it in
the authorized run or evidence directory and report its path, identity, and compact summary.

## 4. Historical Puma site observations

### 4.1 Interactive-wrapper incident

**HISTORICAL:** on 2026-07-18, the then-resolved `/usr/local/bin/interactive` and
`/usr/local/bin/salloc` commands terminated before allocation with a `/bin/sg` segmentation fault,
while `/usr/bin/sbatch` worked. This is not a permanent claim that interactive jobs are
unavailable. Current official documentation says Puma's `interactive` helper submits through
`/usr/local/bin/srun` and that direct `salloc` commands should work.

If the issue recurs, capture the command, host, time, and error; verify whether the wrapper is
currently healthy; and use an explicitly authorized bounded batch job when appropriate. Do not
fall back to running the workload on a login node.

## 5. Workload-specific examples

Everything in this section is an **EXAMPLE**, not a Puma or repository default. Resources, paths,
controls, and retry behavior must not be copied into a new workload without a governing workflow,
current evidence, and an explicit runtime contract.

### 5.1 Spinup-surrogate matrix example

The spinup-surrogate workflow is governed by
`development/spinup_surrogate/WORKFLOW.md`. Historical Iter010 through Iter012 Puma runs used:

- account `chopinsong` and partition `standard`;
- one node and one Slurm task;
- 10 CPUs, implying approximately 50 GB under the standard memory-per-CPU policy;
- a 30-minute production walltime shape;
- `N_JOBS=4` and `PRE_DISPATCH=n_jobs`;
- one-thread BLAS and OpenMP settings;
- task-local `XDG_CACHE_HOME` isolation.

The historical output root was:

```text
/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output
```

Each variant kept the submitted script, immutable configuration, and logs at its run root:

```text
<OUTPUT_ROOT>/UQ_output/<RUN_SLUG>/
  slurm_%A_%a.out
  slurm_%A_%a.err
  submit_<VARIANT>.slurm
  submission_config.env
```

The fixed-parameter LBFGS path did not create fitting workers from `N_JOBS`, and permutation
importance was sequential. Increasing `N_JOBS` therefore did not automatically use all allocated
CPUs. The workload launched one Python process inside one Slurm task; `srun` was not required.

**HISTORICAL:** some spinup-surrogate leaves approached the standard memory ceiling while CPU
efficiency remained low. The 10-CPU shape was retained for memory headroom, not as a general Puma
recommendation. Future spinup work must revisit resources only through its governing workflow and
new accounting evidence.

### 5.2 Perlmutter-to-Puma case-pickle migration example

The migration utility is:

```text
development/spinup_surrogate/migrations/perlmutter_to_puma_case_pickles.py
```

The historical mapping used:

- run root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe`;
- per-site meteorology root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/<SITE>/1x1pt_<SITE>/CLM1PT_data`.

The complete migration procedure, ordered case list, inspect/apply/recover commands, backup
behavior, and historical validation evidence are recorded in
[`development/spinup_surrogate/migrations/README.md`](../spinup_surrogate/migrations/README.md).
