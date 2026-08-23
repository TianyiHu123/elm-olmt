# Standard coupled-optimization examples

These files describe the supported manual three-stage pipeline. Copy a YAML and the three Slurm
templates to an external run root; do not submit the repository copies directly. Consult
`development/spinup_forcing_coupling/WORKFLOW.md` and the selected HPC profile before any run.

The YAML contains the shared scientific configuration. The optimization Slurm script contains the
explicit `#SBATCH --array` directive and its matching `SEEDS` list. Change both together when the
seed ensemble or concurrency changes. It is intentional that MCMC seeds are not in the YAML.

`submission_config.env.example` identifies the external campaign, pool, provenance manifests, and
resources used by the copied scripts. Build source and dependency checksum manifests before
submission, preserve the submitted copies beside their logs, and submit the three stages manually:
initialization, optimization array, then reporting after the array is terminal.
