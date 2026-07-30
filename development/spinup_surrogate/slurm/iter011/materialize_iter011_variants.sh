#!/bin/bash -e
# Materialize immutable variant-local Iter011 submission artifacts.

set -o pipefail

readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output
readonly MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter011/iter011_variants.tsv"
readonly CANONICAL="${REPO_ROOT}/development/spinup_surrogate/slurm/iter011/case.train_surrogate_spinup_iter011.slurm"

test -f "${MANIFEST}"
test -f "${CANONICAL}"
test "$(head -n 1 "${MANIFEST}")" = $'variant\talpha\tfeature_policy\tforcing_vars\tfeature_subset_policy\tapply_corr_filter\tcorr_threshold'
test "$(awk 'NR>1 {n++} END {print n+0}' "${MANIFEST}")" -eq 2

awk -F '\t' '
  NR == 1 {next}
  {
    if ($2 != "40") exit 2
    if ($4 != "PRECTmms,FSDS,TBOT,RH") exit 2
    if ($3 == "drop_flds_wind_psrf") {
      if ($5 != "strict" || $6 != "false" || $7 != "NA") exit 2
    } else if ($3 == "drop32_corr080_prioritydrop") {
      if ($5 != "eligible_pool" || $6 != "true" || $7 != "0.80") exit 2
    } else {
      exit 2
    }
    seen[$1]++
  }
  END {
    if (NR != 3 || length(seen) != 2) exit 2
    for (variant in seen) if (seen[variant] != 1) exit 2
  }
' "${MANIFEST}"

while IFS=$'\t' read -r variant alpha policy forcing subset apply corr; do
  [ "${variant}" = variant ] && continue
  run_dir="${OUTPUT_ROOT}/spinup_surrogate_iter011_${variant}"
  submitted="${run_dir}/submit_${variant}.slurm"
  config="${run_dir}/submission_config.env"
  mkdir -p "${run_dir}"
  if [ -e "${submitted}" ] || [ -e "${config}" ] || [ -e "${config}.tmp" ]; then
    echo "Refusing overwrite: ${run_dir}" >&2
    exit 2
  fi
  cp "${CANONICAL}" "${submitted}"
  {
    printf 'VARIANT=%s\n' "${variant}"
    printf 'MLP_ALPHA=%s\n' "${alpha}"
    printf 'FEATURE_POLICY=%s\n' "${policy}"
    printf 'FORCING_VARS=%s\n' "${forcing}"
    printf 'FEATURE_SUBSET_POLICY=%s\n' "${subset}"
    printf 'APPLY_CORR_FILTER=%s\n' "${apply}"
    printf 'CORR_THRESHOLD=%s\n' "${corr}"
  } > "${config}.tmp"
  mv "${config}.tmp" "${config}"
  bash -n "${submitted}"
  test "$(sha256sum "${submitted}" | awk '{print $1}')" = "$(sha256sum "${CANONICAL}" | awk '{print $1}')"
  printf '%s\t%s\t%s\t%s\t%s\n' \
    "${variant}" \
    "${submitted}" \
    "$(sha256sum "${submitted}" | awk '{print $1}')" \
    "${config}" \
    "$(sha256sum "${config}" | awk '{print $1}')"
done < "${MANIFEST}"
