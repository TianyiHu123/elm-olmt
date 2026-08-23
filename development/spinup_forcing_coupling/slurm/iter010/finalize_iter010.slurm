#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=01:00:00
#SBATCH --output=finalize_%j.out
#SBATCH --error=finalize_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly TOPOLOGY=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter010_topology/topology_decision.json
readonly PREDICTION=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter010_predict/conditional_prediction.json
readonly RUN_DIR=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter010_finalize
cd "${REPO_ROOT}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python development/spinup_forcing_coupling/slurm/iter010/finalize_iter010.py --topology "${TOPOLOGY}" --prediction "${PREDICTION}" --output "${RUN_DIR}"
