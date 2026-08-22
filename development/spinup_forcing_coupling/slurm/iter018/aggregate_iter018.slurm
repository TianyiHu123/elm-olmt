#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=02:00:00
#SBATCH --job-name=sfc-i018-aggregate
#SBATCH --output=aggregate_%j.out
#SBATCH --error=aggregate_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
test -n "${SUBMISSION_CONFIG:-}"
source "${SUBMISSION_CONFIG}"
test "$(pwd -P)" = "${RUN_DIR}"
module load micromamba/2.0.2-2
micromamba run -n OLMT_puma python "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter018/aggregate_iter018.py" --root "${OUTPUT_ROOT}"
