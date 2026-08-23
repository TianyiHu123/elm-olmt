#!/usr/bin/env bash
# Create the immutable Iter018 submitted-copy package; do not submit this script.
set -euo pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter018_operational_nine_site
readonly ITER_DIR="${REPO_ROOT}/development/spinup_forcing_coupling/slurm/iter018"
readonly FORCING="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl"
readonly SPINUP="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl"
readonly OBS_ROOT=/xdisk/chopinsong/chopinsong/CTSM_inputdata/lnd/clm2/neon_ncar/NEON/eval_files/v4
readonly COMMIT="$(git -C "${REPO_ROOT}" rev-parse HEAD)"

test "$(pwd -P)" = "${REPO_ROOT}"
test ! -e "${OUTPUT_ROOT}"
for file in "${ITER_DIR}"/* "${REPO_ROOT}/run_optimization_campaign.py" "${REPO_ROOT}/report_optimization.py"; do test -f "${file}"; done
mkdir -p "${OUTPUT_ROOT}"/{configs,preflight,aggregate,handoff,sites,source_snapshot}
cp "${ITER_DIR}/preflight_iter018.slurm" "${ITER_DIR}/preflight_iter018.py" "${OUTPUT_ROOT}/preflight/"
cp "${ITER_DIR}/validate_iter018_handoff.py" "${ITER_DIR}/validate_iter018_handoff.slurm" "${OUTPUT_ROOT}/handoff/"
cp "${ITER_DIR}/aggregate_iter018.py" "${ITER_DIR}/aggregate_iter018.slurm" "${OUTPUT_ROOT}/aggregate/"
cp "${ITER_DIR}"/*.slurm "${ITER_DIR}"/*.py "${ITER_DIR}/materialize_iter018.sh" "${OUTPUT_ROOT}/source_snapshot/"
cp "${REPO_ROOT}/run_optimization_campaign.py" "${REPO_ROOT}/report_optimization.py" "${REPO_ROOT}/initialize_pipeline.py" "${OUTPUT_ROOT}/source_snapshot/"

make_campaign() {
  local site="$1" resolution="$2" scale="$3"
  local name="${site,,}_${resolution}_0${scale#0.}"
  cat > "${OUTPUT_ROOT}/configs/${name}.yaml" <<EOF
shared:
  iteration_id: iter018_${name}
  sites: [${site}]
  cases: [${site}_ppe6_I20TRCNPRDCTCBC]
  variables: [SR]
  forcing_artifact: ${FORCING}
  spinup_artifact: ${SPINUP}
  observations:
    ${site}: ${OBS_ROOT}/${site}/${site}_cdo_merge.nc
initialization:
  mode: fresh
  resolution: ${resolution}
  pool_rule: hybrid_high_l_maximin
  high_l_quantile: 0.90
  pool_size: 640
  seed: 17017
optimization:
  likelihood_resolution: ${resolution}
  de_move_scale: ${scale}
  sampler_coordinates: transformed
  move_configuration: de_mixture
  nwalkers: 64
  nsteps: 8000
  checkpoint_interval: 2000
reporting:
  tier_a_acceptance_range: [0.20, 0.50]
  copy_leaf_products: true
EOF
  local root="${OUTPUT_ROOT}/sites/${site,,}"
  mkdir -p "${root}"/{initialization,optimization,reports}
  cp "${ITER_DIR}/initialize_iter018.slurm" "${root}/initialization/submit_initialize_iter018.slurm"
  cp "${ITER_DIR}/optimization_array_iter018.slurm" "${root}/optimization/submit_optimization_iter018.slurm"
  cp "${ITER_DIR}/report_iter018.slurm" "${root}/reports/submit_report_iter018.slurm"
  local campaign="${OUTPUT_ROOT}/configs/${name}.yaml"
  local source_manifest="${OUTPUT_ROOT}/source_manifest.sha256"
  local dependency_manifest="${OUTPUT_ROOT}/dependency_manifest.sha256"
  cat > "${root}/initialization/submission_config.env" <<EOF
RUN_DIR=${root}/initialization
SUBMITTED_SCRIPT=${root}/initialization/submit_initialize_iter018.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${root}/initialization/submit_initialize_iter018.slurm" | awk '{print $1}')
CAMPAIGN=${campaign}
CAMPAIGN_SHA256=$(sha256sum "${campaign}" | awk '{print $1}')
OUTPUT=${root}/initialization
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${source_manifest}
DEPENDENCY_MANIFEST=${dependency_manifest}
EOF
  cat > "${root}/optimization/submission_config.env" <<EOF
RUN_DIR=${root}/optimization
SUBMITTED_SCRIPT=${root}/optimization/submit_optimization_iter018.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${root}/optimization/submit_optimization_iter018.slurm" | awk '{print $1}')
CAMPAIGN=${campaign}
CAMPAIGN_SHA256=$(sha256sum "${campaign}" | awk '{print $1}')
PATH_ROOT=${root}
POOL=${root}/initialization/artifacts/candidate_pool.npz
SEEDS=(9009 9010 9011 9012 9013 9014 9015 9016 9017)
REPOSITORY_COMMIT=${COMMIT}
SOURCE_MANIFEST=${source_manifest}
DEPENDENCY_MANIFEST=${dependency_manifest}
EOF
  cat > "${root}/reports/submission_config.env" <<EOF
RUN_DIR=${root}/reports
SUBMITTED_SCRIPT=${root}/reports/submit_report_iter018.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${root}/reports/submit_report_iter018.slurm" | awk '{print $1}')
CAMPAIGN=${campaign}
CAMPAIGN_SHA256=$(sha256sum "${campaign}" | awk '{print $1}')
PATH_ROOT=${root}
SOURCE_MANIFEST=${source_manifest}
DEPENDENCY_MANIFEST=${dependency_manifest}
EOF
}

for site in ABBY SOAP YELL WREF; do make_campaign "${site}" daily 0.50; done
for site in JERC OSBS RMNP TALL TEAK; do make_campaign "${site}" hourly 0.75; done
sha256sum "${REPO_ROOT}/run_optimization_campaign.py" "${REPO_ROOT}/report_optimization.py" \
  "${REPO_ROOT}/initialize_pipeline.py" "${REPO_ROOT}/optimize_surrogate_forcing.py" \
  "${REPO_ROOT}/model_ELM/optimization_config.py" "${REPO_ROOT}/model_ELM/coupling_pipeline.py" \
  "${REPO_ROOT}/model_ELM/MCMC_forcing.py" "${REPO_ROOT}/model_ELM/mcmc_artifacts.py" \
  "${REPO_ROOT}/model_ELM/mcmc_diagnostics.py" "${ITER_DIR}"/* "${OUTPUT_ROOT}/configs"/*.yaml > "${OUTPUT_ROOT}/source_manifest.sha256"
for site in ABBY JERC OSBS SOAP RMNP TALL TEAK WREF YELL; do
  sha256sum "${REPO_ROOT}/pklfiles/${site}_ppe6_I20TRCNPRDCTCBC.pkl" "${OBS_ROOT}/${site}/${site}_cdo_merge.nc"
done > "${OUTPUT_ROOT}/dependency_manifest.sha256"
sha256sum "${FORCING}" "${SPINUP}" "${REPO_ROOT}/conda_envs/OLMT_puma.yml" >> "${OUTPUT_ROOT}/dependency_manifest.sha256"
cat > "${OUTPUT_ROOT}/preflight/submission_config.env" <<EOF
RUN_DIR=${OUTPUT_ROOT}/preflight
SUBMITTED_SCRIPT=${OUTPUT_ROOT}/preflight/preflight_iter018.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${OUTPUT_ROOT}/preflight/preflight_iter018.slurm" | awk '{print $1}')
CAMPAIGN_DIR=${OUTPUT_ROOT}/configs
SOURCE_MANIFEST=${OUTPUT_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${OUTPUT_ROOT}/dependency_manifest.sha256
EOF
cat > "${OUTPUT_ROOT}/aggregate/submission_config.env" <<EOF
RUN_DIR=${OUTPUT_ROOT}/aggregate
OUTPUT_ROOT=${OUTPUT_ROOT}
SUBMITTED_SCRIPT=${OUTPUT_ROOT}/aggregate/aggregate_iter018.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${OUTPUT_ROOT}/aggregate/aggregate_iter018.slurm" | awk '{print $1}')
SOURCE_MANIFEST=${OUTPUT_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${OUTPUT_ROOT}/dependency_manifest.sha256
EOF
cat > "${OUTPUT_ROOT}/handoff/submission_config.env" <<EOF
RUN_DIR=${OUTPUT_ROOT}/handoff
OUTPUT_ROOT=${OUTPUT_ROOT}
SUBMITTED_SCRIPT=${OUTPUT_ROOT}/handoff/validate_iter018_handoff.slurm
SUBMITTED_SCRIPT_SHA256=$(sha256sum "${OUTPUT_ROOT}/handoff/validate_iter018_handoff.slurm" | awk '{print $1}')
SOURCE_MANIFEST=${OUTPUT_ROOT}/source_manifest.sha256
DEPENDENCY_MANIFEST=${OUTPUT_ROOT}/dependency_manifest.sha256
EOF
echo "ITER018_MATERIALIZED root=${OUTPUT_ROOT} commit=${COMMIT}"
