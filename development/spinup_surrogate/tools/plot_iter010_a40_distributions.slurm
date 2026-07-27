#!/bin/bash
#SBATCH --job-name=iter010-a40-plots
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/iter010_a40_plots_%j.out
#SBATCH --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/iter010_a40_plots_%j.err

set -euo pipefail
cd /xdisk/chopinsong/tianyihu/elm-olmt
export MPLCONFIGDIR="/tmp/mplconfig_iter010_${SLURM_JOB_ID}"
mkdir -p "$MPLCONFIGDIR"
python development/spinup_surrogate/tools/plot_iter010_a40_distributions.py
