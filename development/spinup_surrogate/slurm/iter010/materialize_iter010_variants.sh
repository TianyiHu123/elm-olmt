#!/bin/bash -e
# Materialize immutable variant-local iter010 submission artifacts; never overwrites a prior copy.
set -o pipefail
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt OUTPUT_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output
readonly MANIFEST="${REPO_ROOT}/development/spinup_surrogate/slurm/iter010/iter010_variants.tsv" CANONICAL="${REPO_ROOT}/development/spinup_surrogate/slurm/iter010/case.train_surrogate_spinup_iter010.slurm"
test -f "${MANIFEST}"; test -f "${CANONICAL}"; test "$(awk 'NR>1{n++} END{print n+0}' "${MANIFEST}")" = 15
awk -F '\t' 'NR==1 {next} {if ($1 !~ /^s32_tanh_lbfgs_a(40|42p5|45|47p5|50)_lr1e3_(full45|corr080_prioritydrop|drop_flds_wind_psrf)$/) exit 2; if ($2 !~ /^(40|42\.5|45|47\.5|50)$/) exit 2; seen[$1]++} END {if (NR!=16 || length(seen)!=15) exit 2; for (x in seen) if (seen[x]!=1) exit 2}' "${MANIFEST}"
while IFS=$'\t' read -r variant alpha policy forcing subset apply corr; do
  [ "${variant}" = variant ] && continue
  case "${policy}" in full45) test "${forcing}|${subset}|${apply}|${corr}" = 'PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF|strict|false|NA';; corr080_prioritydrop) test "${forcing}|${subset}|${apply}|${corr}" = 'PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF|eligible_pool|true|0.80';; drop_flds_wind_psrf) test "${forcing}|${subset}|${apply}|${corr}" = 'PRECTmms,FSDS,TBOT,RH|strict|false|NA';; *) exit 2;; esac
  run_dir="${OUTPUT_ROOT}/spinup_surrogate_iter010_${variant}" submitted="${run_dir}/submit_${variant}.slurm" config="${run_dir}/submission_config.env"; mkdir -p "${run_dir}"
  if [ -e "${submitted}" ] || [ -e "${config}" ] || [ -e "${config}.tmp" ]; then echo "Refusing overwrite: ${run_dir}" >&2; exit 2; fi
  cp "${CANONICAL}" "${submitted}"
  printf 'VARIANT=%s\nMLP_ALPHA=%s\nFEATURE_POLICY=%s\nFORCING_VARS=%s\nFEATURE_SUBSET_POLICY=%s\nAPPLY_CORR_FILTER=%s\nCORR_THRESHOLD=%s\n' "${variant}" "${alpha}" "${policy}" "${forcing}" "${subset}" "${apply}" "${corr}" > "${config}.tmp"; mv "${config}.tmp" "${config}"
  bash -n "${submitted}"; printf '%s\t%s\t%s\t%s\t%s\n' "${variant}" "${submitted}" "$(sha256sum "${submitted}"|awk '{print $1}')" "${config}" "$(sha256sum "${config}"|awk '{print $1}')"
done < "${MANIFEST}"
