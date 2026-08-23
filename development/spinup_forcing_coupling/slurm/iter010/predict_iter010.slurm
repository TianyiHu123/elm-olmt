#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --output=predict_%j.out
#SBATCH --error=predict_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly TOPOLOGY=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter010_topology/topology_decision.json
readonly RUN_DIR=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter010_predict
cd "${REPO_ROOT}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python development/spinup_forcing_coupling/slurm/iter010/predict_iter010.py --decision "${TOPOLOGY}" --output "${RUN_DIR}"
