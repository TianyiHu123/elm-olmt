#!/usr/bin/env bash
#SBATCH --account=chopinsong
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:30:00
#SBATCH --job-name=sfc-i011-preflight
#SBATCH --output=preflight_%j.out
#SBATCH --error=preflight_%j.err
set -euo pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly CANONICAL_SCRIPT="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011/preflight_iter011.slurm"
test -n "${SUBMISSION_CONFIG:-}"; test -f "${SUBMISSION_CONFIG}"; cmp -s "${CANONICAL_SCRIPT}" "$0"
set -a; source "${SUBMISSION_CONFIG}"; set +a
test "${ITERATION_ID}" = iter011; test "${STAGE}" = preflight
test "$(git -C "${REPO_ROOT}" rev-parse HEAD)" = "${REPOSITORY_COMMIT}"
(cd "${REPO_ROOT}" && sha256sum -c "${SOURCE_MANIFEST}")
sha256sum -c "${DEPENDENCY_MANIFEST}"
module load "${MICROMAMBA_MODULE}"
cd "${REPO_ROOT}"
micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter011/preflight_iter011.py" \
  --output "${PREFLIGHT_OUTPUT}" --initialization-dir "${INITIALIZATION_DIR}"
for resolution in hourly daily; do
  for site in ABBY JERC; do
    for seed in 9009 9010 9011; do
      finite_dir="${PREFLIGHT_OUTPUT}/finite_${resolution}_${site,,}_seed${seed}"
      mkdir -p "${finite_dir}"
      obs_path="/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4/${site}/${site}_cdo_merge.nc"
      micromamba run -n "${MICROMAMBA_ENV}" python "${REPO_ROOT}/optimize_surrogate_forcing.py" \
        --workdir "${REPO_ROOT}" --outputdir "${finite_dir}" --flat-output \
        --case "${site}_ppe6_I20TRCNPRDCTCBC" --artifact "${FORCING_ARTIFACT}" --vars SR --obs "${obs_path}" \
        --obs-err-vars SR:SR_err --spinup-mode coupled --coupled-spinup-variant drop21_corr080 \
        --nwalkers 64 --nsteps 8000 --n-processes 2 --seed "${seed}" --fit-error \
        --sampler-coordinates transformed --move-configuration de_mixture --de-move-scale 1.00 \
        --likelihood-resolution "${resolution}" --initial-state "${INITIALIZATION_DIR}/${site,,}_high_seed${seed}.npz" \
        --smoke-likelihood-evals 1
      echo "FINITE_BUNDLE_PASS resolution=${resolution} site=${site} seed=${seed}"
    done
  done
done
test -f "${PREFLIGHT_OUTPUT}/preflight_result.json"
echo PREFLIGHT_PASS
