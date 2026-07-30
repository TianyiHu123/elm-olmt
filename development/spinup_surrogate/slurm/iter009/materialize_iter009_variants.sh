#!/bin/bash -e
# Materialize the locked iter009 variant-local scripts and immutable configurations.

set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output
readonly MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter009/iter009_variants.tsv"
readonly CANONICAL="${REPO_ROOT}/development/spinup_surrogate/slurm/iter009/case.train_surrogate_spinup_iter009.slurm"
test -f "${MANIFEST}"
test -f "${CANONICAL}"
test "$(awk 'NR > 1 { count++ } END { print count + 0 }' "${MANIFEST}")" = 15
test "$(head -n 1 "${MANIFEST}")" = $'variant\talpha\tfeature_policy\tforcing_vars\tfeature_subset_policy\tapply_corr_filter\tcorr_threshold'
awk -F '\t' '
  NR == 1 { next }
  {
    key = $2 SUBSEP $3
    seen[key]++
    if ($1 != "s32_tanh_lbfgs_a" $2 "_lr1e3_" $3) exit 2
    if ($2 != 25 && $2 != 35 && $2 != 50 && $2 != 65 && $2 != 75) exit 2
    if ($3 == "corr080_prioritydrop") {
      if ($4 != "PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF" || $5 != "eligible_pool" || $6 != "true" || $7 != "0.80") exit 2
    } else if ($3 == "drop_flds_wind_psrf") {
      if ($4 != "PRECTmms,FSDS,TBOT,RH" || $5 != "strict" || $6 != "false" || $7 != "NA") exit 2
    } else if ($3 == "full45") {
      if ($4 != "PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF" || $5 != "strict" || $6 != "false" || $7 != "NA") exit 2
    } else exit 2
  }
  END {
    if (NR != 16 || length(seen) != 15) exit 2
    for (key in seen) if (seen[key] != 1) exit 2
  }
' "${MANIFEST}"

while IFS=$'\t' read -r variant alpha feature_policy forcing_vars feature_subset_policy apply_corr_filter corr_threshold; do
  if [ "${variant}" = variant ]; then continue; fi
  case "${alpha}" in 25|35|50|65|75) ;; *) echo "Invalid alpha: ${alpha}" >&2; exit 2 ;; esac
  case "${feature_policy}" in full45|corr080_prioritydrop|drop_flds_wind_psrf) ;; *) echo "Invalid feature policy: ${feature_policy}" >&2; exit 2 ;; esac
  run_dir="${OUTPUT_ROOT}/spinup_surrogate_iter009_${variant}"
  submitted="${run_dir}/submit_${variant}.slurm"
  config="${run_dir}/submission_config.env"
  mkdir -p "${run_dir}"
  if [ -e "${submitted}" ] || [ -e "${config}" ] || [ -e "${config}.tmp" ]; then
    echo "Refusing to overwrite existing iter009 submission artifact in ${run_dir}" >&2
    exit 2
  fi
  cp "${CANONICAL}" "${submitted}"
  {
    printf 'VARIANT=%s\n' "${variant}"
    printf 'MLP_ALPHA=%s\n' "${alpha}"
    printf 'FEATURE_POLICY=%s\n' "${feature_policy}"
    printf 'FORCING_VARS=%s\n' "${forcing_vars}"
    printf 'FEATURE_SUBSET_POLICY=%s\n' "${feature_subset_policy}"
    printf 'APPLY_CORR_FILTER=%s\n' "${apply_corr_filter}"
    printf 'CORR_THRESHOLD=%s\n' "${corr_threshold}"
  } > "${config}.tmp"
  mv "${config}.tmp" "${config}"
  bash -n "${submitted}" "${config}"
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "${variant}" "${submitted}" "$(sha256sum "${submitted}" | awk '{print $1}')" \
    "${config}" "$(sha256sum "${config}" | awk '{print $1}')"
done < "${MANIFEST}"
