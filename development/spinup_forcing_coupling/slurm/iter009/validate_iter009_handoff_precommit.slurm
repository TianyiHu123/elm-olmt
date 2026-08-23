#!/usr/bin/env bash
# Compute-node pre-commit cross-record validation for the Iter009 closeout.
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:15:00
#SBATCH --job-name=sfc-i009-handoff-pre
#SBATCH --output=handoff_pre_%j.out
#SBATCH --error=handoff_pre_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
cd "${REPO_ROOT}"
module load micromamba/2.0.2-2
export PYTHONPATH="${REPO_ROOT}"
micromamba run -n OLMT_puma python development/spinup_forcing_coupling/slurm/iter009/validate_iter009_handoff.py \
  --phase precommit --expected-parent dff5da3373e9e61800e9a65fdd28fa0344066d5b \
  --expected-subject 'Close Iter009 sampler geometry pilot' --active-job-count 0 \
  --controlled-path development/spinup_forcing_coupling/ITERATION_SUMMARY.md \
  --controlled-path development/spinup_forcing_coupling/handoff/CURRENT.md \
  --controlled-path development/spinup_forcing_coupling/iterations/iter009.md \
  --controlled-path development/spinup_forcing_coupling/registry.csv \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/README.md \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/campaign_iter009.slurm \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/initialize_iter009.py \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/initialize_iter009.slurm \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/iter009_matrix.tsv \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/iter009_source_manifest.sha256 \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/materialize_iter009.sh \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/preflight_iter009.py \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/preflight_iter009.slurm \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/validate_iter009.py \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/validate_iter009.slurm \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/validate_iter009_handoff.py \
  --controlled-path development/spinup_forcing_coupling/slurm/iter009/validate_iter009_handoff_precommit.slurm \
  --controlled-path development/spinup_forcing_coupling/summaries/iter009/ITER009_REPORT.md \
  --controlled-path development/spinup_forcing_coupling/summaries/iter009/decision.json \
  --controlled-path development/spinup_forcing_coupling/summaries/iter009/iter009_accounting.csv \
  --controlled-path development/spinup_forcing_coupling/summaries/iter009/qualification_matrix.csv \
  --controlled-path development/spinup_forcing_coupling/summaries/iter009/worst_case_selection.csv \
  --controlled-path model_ELM/MCMC_forcing.py --controlled-path model_ELM/mcmc_geometry.py \
  --controlled-path optimize_surrogate_forcing.py --controlled-path tests/test_mcmc_iter009_geometry.py
