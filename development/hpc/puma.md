# Puma Site Profile

Use this profile for University of Arizona Puma Slurm operations. Record this path in the
iteration runtime contract before submission.

Official references:

- [Interactive Jobs](https://hpcdocs.hpc.arizona.edu/running_jobs/interactive_jobs/)
- [Batch Directives](https://hpcdocs.hpc.arizona.edu/running_jobs/batch_jobs/batch_directives/)
- [CPUs and Memory](https://hpcdocs.hpc.arizona.edu/running_jobs/cpus_and_memory/)
- [Monitoring Jobs and Resources](https://hpcdocs.hpc.arizona.edu/running_jobs/monitoring_jobs_and_resources/)
- [Batch Jobs and Slurm](https://uarizona.atlassian.net/wiki/spaces/UAHPC/pages/75989977)
- [HPC High Performance Storage](https://uarizona.atlassian.net/wiki/spaces/UAHPC/pages/75990091/HPC%2BHigh%2BPerformance%2BStorage)
- [Micromamba](https://hpcdocs.hpc.arizona.edu/software/popular_software/mamba/)

## Scheduler Operations

| Purpose | Command |
| --- | --- |
| Submit | `sbatch --export=ALL,<KEY=VALUE,...> <script>` |
| Queue state and pending reason | `squeue -j <job_ids>` |
| Detailed active-job state | `scontrol show job <job_id>` |
| Terminal accounting | `sacct -j <job_ids> --format=JobID,JobName,Partition,Account,AllocTRES,State,ExitCode,MaxRSS` |
| Readable job history | `job-history <job_id>` |
| Cancel | `scancel <job_ids>` |
| Efficiency report | `seff <job_id>` |
| Group limits and usage | `job-limits chopinsong` |

For a variant matrix, submit one job or array per variant and monitor the full job set
concurrently.

## Required Submission Inputs and Resource Semantics

The current CPU baseline uses account `chopinsong` and partition `standard`. Do not carry over
Perlmutter's `--qos=shared` or `--constraint=cpu`. Puma standard nodes provide 5 GB of memory per
requested CPU. For a CPU-limited job, request the CPU count and omit `--mem` and
`--mem-per-cpu`; Slurm derives total memory from the CPU count. For a memory-limited job, either
convert the required memory to CPUs using `ceil(total_GB / 5)` or request total memory with
`--mem` and let Slurm increase the CPU allocation to preserve the standard ratio. Do not set a
nonstandard `--mem-per-cpu` value: it can route the job to scarce high-memory nodes or produce an
unexpected allocation.

This documentation-only header shows the initial 10-CPU/50-GB shape selected for the next runtime
contract; an iteration-specific canonical script must still set job name, array range, log paths,
exports, and other run details:

```bash
#!/bin/bash -e
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
```

On a Puma standard node, the 10 requested CPUs imply 50 GB total memory. The current model keeps
`N_JOBS=4`; the additional allocated CPUs are the scheduling cost of meeting its measured memory
requirement and should be revisited after collecting Puma efficiency evidence.

Set GPU resources or a high-memory constraint only when the runtime contract explicitly requires
them. Confirm current account, partition, array, and user/group limits before submission.

## Environment and Storage

- Puma login nodes are for file and job management. Software modules are unavailable there, and
  login-node system Python is not the project runtime. To create, repair, or inspect `OLMT_puma`,
  first request a small standard-partition compute shell:

  ```bash
  interactive -a chopinsong -t 01:00:00 -n 1 -m 5gb
  ```

  Wait for the prompt to change from a login host such as `wentletrap` or `junonia` to a Puma
  compute-node hostname before loading modules or running environment commands. Use
  `interactive -h` when a different setup-session resource request is required.
- Once on the compute node, load micromamba and inspect the project runtime without relying on the
  login-node Python installation:

  ```bash
  module load micromamba
  micromamba env list
  micromamba run -n OLMT_puma python --version
  ```

  Create or repair the environment from `conda_envs/OLMT_puma.yml` only under explicit execution
  authority; environment installation is not a login-node task.
- The current environment is named `OLMT_puma`. Prefer this batch pattern, which does not depend
  on interactive shell activation:

  ```bash
  module load micromamba
  micromamba run -n OLMT_puma python <script> <arguments>
  ```

- The repository root for this temporary migration is fixed at
  `/xdisk/chopinsong/tianyihu/elm-olmt`. Future canonical and submitted scripts must use that
  literal path; do not derive it from `$0`, a copied script location, `SLURM_SUBMIT_DIR`, the
  current directory, or an environment override. Fail before loading the environment or touching
  outputs unless the fixed root contains the training entry point and required tracked controls:

  ```bash
  readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
  test -f "${REPO_ROOT}/train_surrogate_spinup.py"
  test -f "${REPO_ROOT}/development/spinup_surrogate/WORKFLOW.md"
  test -f "${REPO_ROOT}/development/hpc/puma.md"
  test -f "${REPO_ROOT}/conda_envs/OLMT_puma.yml"
  cd "${REPO_ROOT}"
  ```

  An iteration script must add early checks for its own tracked iteration record and canonical
  Slurm artifact. Record this fixed root, environment name, and output root in the provenance
  ledger.
- Use `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output` as the current default
  spinup-surrogate output root, with an exported output override supported by each new canonical
  script.
- `/xdisk` is temporary and unbacked. Check capacity and expiration before a new run and keep an
  external copy of irreplaceable inputs and results.
- `OLMT_puma` currently lives under the user's home micromamba root. Monitor the 50-GB home quota;
  relocation is deferred for this temporary migration.

## Transferred Spinup-Surrogate Data

The temporary Perlmutter-to-Puma mapping for the nine iter007 case pickles is deliberately narrow:

- `case.runroot` is rewritten to
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe`.
- `case.metdir` is rewritten per site to
  `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/<SITE>/1x1pt_<SITE>/CLM1PT_data`.
- `finidat`, `dependcase`, and unrelated historical path metadata remain unchanged. Restart lookup
  continues under `case.runroot/UQ/case.dependcase/gNNNNN/` using the basename of `case.finidat`.

Use `development/spinup_surrogate/migrate_case_pickles.py` only on a Puma compute node with a
confirmed runtime contract. Its inspect/apply modes validate the complete nine-case set, including
100 resolved restart files and 100 ensemble surface files per site, the observed 84-month forcing
sequences for ABBY/JERC/OSBS/SOAP/RMNP/TALL, the 72-month sequences for TEAK/WREF/YELL, required
NetCDF variables, stored spinup-cycle coverage, and compact pickle invariants. Apply stages and
reloads every pickle before activating any of them. It preserves each original as
`<case>.pkl.perlmutter.bak`; backups are never removed automatically. Recovery restores the
original set while preserving both backups and any already activated Puma pickles as staged files.

After the bounded compute-node contract is explicitly authorized, use the same ordered case list
for inspection and application:

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

Use the identical arguments with `--recover` instead of `--inspect` or `--apply` only to restore
the original set after interrupted activation. Do not remove backups as part of the utility run.

## Launch Convention

The spinup-surrogate workload is one Python process with internal joblib workers. Launch Python
directly through `micromamba run` inside the single-task Slurm allocation. Do not add `srun` solely
because the job is submitted through Slurm.

Use `srun` for multiple Slurm tasks, MPI ranks, or a future site requirement. Keep internal worker
counts and BLAS/OpenMP thread caps explicit and consistent with the iteration runtime contract.

## Puma Submission Guidance

During the 2026-07-18 migration, the site wrappers `/usr/local/bin/interactive` and
`/usr/local/bin/salloc` terminated before allocation with a `/bin/sg` segmentation fault. The
underlying `/usr/bin/sbatch` path worked. Interactive sessions remain appropriate when the wrapper
is healthy; verify the prompt hostname is a Puma compute node before loading modules.

Use a written, tracked Slurm script for large, multi-step, multi-CPU, or matrix jobs.
Submit it with `/usr/bin/sbatch`, and monitor it with `/usr/bin/squeue --job=<jobid>` and
`/usr/bin/sacct --jobs=<jobid>`. Use a one-line `/usr/bin/sbatch --wrap='...'` submission only for a
simple, bounded test or preflight; do not use `--wrap` as the production representation of a large
workflow.

### Variant-Local Submission Artifacts

For every production matrix variant, keep both its Slurm logs and its submitted, variant-specific
script under that variant's output directory, not directly under the shared `UQ_output` root. The
required layout is:

```text
<output-root>/UQ_output/<run-slug>/
  slurm_%A_%a.out
  slurm_%A_%a.err
  submit_<variant>.slurm
  submission_config.env
```

`submit_<variant>.slurm` is a pre-submit copy of the tracked canonical script. It must be
self-describing for the exact variant: either render the locked variables into the copy or source
the immutable `submission_config.env` beside it. Do not submit the repository canonical script
directly. The iteration report must record the canonical path/hash, submitted-copy path/hash,
configuration path/hash, exact `sbatch` command, and both log paths.

Before submission, create the variant directory and materialize the copy/configuration. Use the
variant directory as Slurm's working directory, and override `--output` and `--error` at submission
time so dynamic job IDs are resolved directly at that variant root. The following shape is
required; substitute the iteration's locked paths and variables:

```bash
readonly VARIANT_DIR="${OUTPUT_ROOT}/UQ_output/${RUN_NAME}"
readonly SUBMITTED_SCRIPT="${VARIANT_DIR}/submit_${VARIANT}.slurm"
readonly SUBMISSION_CONFIG="${VARIANT_DIR}/submission_config.env"
mkdir -p "${VARIANT_DIR}"

# Materialize a self-describing submitted copy and immutable locked configuration before sbatch.
cp "${CANONICAL_SCRIPT}" "${SUBMITTED_SCRIPT}"
# The new canonical script must load SUBMISSION_CONFIG, or the locked settings must be rendered
# into SUBMITTED_SCRIPT; record hashes for both artifacts in the iteration ledger.

/usr/bin/sbatch \
  --chdir="${VARIANT_DIR}" \
  --output="${VARIANT_DIR}/slurm_%A_%a.out" \
  --error="${VARIANT_DIR}/slurm_%A_%a.err" \
  --export="ALL,SUBMISSION_CONFIG=${SUBMISSION_CONFIG},VARIANT=${VARIANT},N_JOBS=${N_JOBS},PRE_DISPATCH=${PRE_DISPATCH}" \
  "${SUBMITTED_SCRIPT}"
```

The `#SBATCH --output` and `#SBATCH --error` lines in a canonical script are only safe defaults;
the explicit `sbatch` options above are authoritative for production variant submissions. Do not
put production matrix logs at the shared `UQ_output` root or in extra per-variant subdirectories.

Use this batch shape for a one-CPU/5-GB preflight (Puma derives 5 GB from one CPU; do not add a
memory directive to the normal CPU-limited form):

```bash
/usr/bin/sbatch \
  --account=chopinsong --partition=standard --nodes=1 --ntasks=1 --cpus-per-task=1 \
  --time=01:00:00 --job-name=puma-preflight \
  --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/puma_preflight_%j.out \
  --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/puma_preflight_%j.err \
  --wrap='set -e; cd /xdisk/chopinsong/tianyihu/elm-olmt; module load micromamba; \
    micromamba run -n OLMT_puma python /xdisk/chopinsong/tianyihu/elm-olmt/<tracked-script>'
```

Always use the literal repository root and `cd` there before launching Python. A nested script
invoked by absolute path does not necessarily get the checkout root on `sys.path`; it must
explicitly establish `/xdisk/chopinsong/tianyihu/elm-olmt` before importing repository modules.
Do not solve this with a copied checkout, `$0`, submit-directory discovery, or a repository-root
environment override.

## Pre-submit and Monitoring Checklist

1. Verify the canonical script and all resource directives are explicit.
2. Create and verify the variant-local submitted copy, configuration manifest, and root-level
   standard/error log paths, plus their SHA-256 hashes. If configuration is rendered into the
   copy, record that intentional difference from the canonical source rather than claiming
   byte-identical scripts.
3. Record the commit plus dirty-diff/source-manifest provenance.
4. Verify the Cursor plan references and required data paths are readable on Puma.
5. Show the exact `sbatch` command, including variant-local `--chdir`, `--output`, and `--error`,
   and obtain runtime-contract authority.
6. Record job IDs immediately after submission.
7. Use `squeue` while active and `sacct` after terminal state; record state, exit code, allocation,
   and memory evidence.
8. Use `seff` when diagnosing CPU efficiency or memory headroom.

## Failure Diagnostics

Capture accounting evidence and distinguish account/partition policy errors, resource exhaustion,
environment activation failures, launch-layout mismatch, storage/expiration failures, and
application failures. Only retry resource or scheduler failures once within the iteration's
declared caps. Code or configuration changes require fresh user authorization before retry.
