#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly MANIFEST=${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter010/iter010_source_manifest.json
readonly RUN_DIR=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter010_preflight
cd "${REPO_ROOT}"
test "$(pwd -P)" = "${REPO_ROOT}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python development/spinup_forcing_coupling/slurm/iter010/preflight_iter010.py "${MANIFEST}" | tee "${RUN_DIR}/preflight_result.json"
