#!/usr/bin/env bash
set -euo pipefail

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)"
readonly CAMPAIGN="${ROOT}/development/three_stage_surrogate"
readonly RUN_ROOT="/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter005_abby_jerc_gpp_baseline"
readonly PLAN_SHA256="9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128"
readonly PREPARED_SHA256="acd9a7bb7f47561e5aa81fe6ac72a55e1e0ab1b41837398f719eb9a9b8ec416b"
readonly ARTIFACT_SHA256="09820737baf9fa9c4760c35b7ce1cbc3c9e6b09eb4ed2f4143a7836416d5c31b"
readonly PREDICTIONS_SHA256="74b2b1334645238311370013f5f98bc87c6b5674cc723e3eb933027ccdee4024"
readonly METRICS_SHA256="5b7a40bfe1eecae9d4ef246c7899c7ad8c2a55483170f0211dab5a6d380f172d"
readonly VALIDATION_SHA256="a8c6ad338f5609ddba3e8822c72adcc71744bfcf3d8a84f7d177eb990d614d8a"
readonly DIAGNOSTICS_SHA256="a7c06f84dd6b732ea89bb9f78f7e3ba3001d9094013c9b64692fa9ef07f7ea7d"
readonly RECOMPUTED_SHA256="2678744366677ae6b9a1693cfcc36c3ff49e2efedf2aaba8f3fb9b23c34a0189"

if [[ "${1:-}" != "--active-job-count" || "${2:-}" != "0" || $# -ne 2 ]]; then
  echo "FAIL: expected --active-job-count 0" >&2
  exit 1
fi

readonly REPORT="${CAMPAIGN}/iterations/iter005.md"
readonly SUMMARY="${CAMPAIGN}/ITERATION_SUMMARY.md"
readonly HANDOFF="${CAMPAIGN}/handoff/CURRENT.md"
readonly COMPACT="${CAMPAIGN}/summaries/iter005/summary.md"
readonly EVIDENCE="${CAMPAIGN}/summaries/iter005/evidence.sha256"
readonly REGISTRY="${CAMPAIGN}/registry.csv"
readonly PREPARED="${RUN_ROOT}/runs/prepare/attempt_1/prepared/prepared_manifest.json"
readonly ARTIFACT="${RUN_ROOT}/runs/baseline/attempt_1/gpp_baseline_artifact.pkl"
readonly PREDICTIONS="${RUN_ROOT}/runs/baseline/attempt_1/predictions_physical_float32.dat"
readonly METRICS="${RUN_ROOT}/runs/baseline/attempt_1/metrics.csv"
readonly VALIDATION="${RUN_ROOT}/runs/validation/attempt_5/validation_report.json"
readonly DIAGNOSTICS="${RUN_ROOT}/runs/validation/attempt_5/reload_diagnostics.json"
readonly RECOMPUTED="${RUN_ROOT}/runs/validation/attempt_5/recomputed_metrics.json"

for path in "${REPORT}" "${SUMMARY}" "${HANDOFF}" "${COMPACT}"; do
  grep -q 'iter005' "${path}"
  grep -q 'implementation' "${path}"
  grep -q 'freeze_baseline' "${path}"
  grep -q 'pass' "${path}"
  grep -q 'fixed_upstream_gpp_stage' "${path}"
done
grep -q -- '- Status: `completed`' "${REPORT}"
grep -q -- '- Phase: `closed`' "${REPORT}"
grep -q -- '- Status: `completed`' "${HANDOFF}"
grep -q -- '- Phase: `closed`' "${HANDOFF}"
grep -q -- '- Active job scope: none' "${HANDOFF}"
grep -q "${PLAN_SHA256}" "${REPORT}"
grep -q "${PLAN_SHA256}" "${HANDOFF}"

readonly TMPDIR_ITER005="$(mktemp -d)"
trap 'rm -rf "${TMPDIR_ITER005}"' EXIT
awk '/^### Iter006 - ABBY\/JERC fixed-upstream GPP robustness$/{keep=1} /^## Four-Record Closeout Validation$/{keep=0} keep' "${REPORT}" |
  sed '${/^$/d;}' > "${TMPDIR_ITER005}/report_proposal"
sed -n '/^### Iter006 - ABBY\/JERC fixed-upstream GPP robustness$/,$p' "${HANDOFF}" > "${TMPDIR_ITER005}/handoff_proposal"
diff -u "${TMPDIR_ITER005}/report_proposal" "${TMPDIR_ITER005}/handoff_proposal"

[[ "$(grep -c '^iter005,' "${REGISTRY}")" -eq 1 ]]
grep '^iter005,' "${REGISTRY}" | grep -q ',completed,implementation,'
grep '^iter005,' "${REGISTRY}" | grep -q ',pass,Freeze baseline and perform fixed-configuration robustness'
grep '^iter005,' "${REGISTRY}" | grep -q 'summaries/iter005,committed'
grep '^iter005,' "${REGISTRY}" | grep -q 'validator=validate_closeout_iter005.sh'

[[ "$(sha256sum "${PREPARED}" | cut -d' ' -f1)" == "${PREPARED_SHA256}" ]]
[[ "$(sha256sum "${ARTIFACT}" | cut -d' ' -f1)" == "${ARTIFACT_SHA256}" ]]
[[ "$(sha256sum "${PREDICTIONS}" | cut -d' ' -f1)" == "${PREDICTIONS_SHA256}" ]]
[[ "$(sha256sum "${METRICS}" | cut -d' ' -f1)" == "${METRICS_SHA256}" ]]
[[ "$(sha256sum "${VALIDATION}" | cut -d' ' -f1)" == "${VALIDATION_SHA256}" ]]
[[ "$(sha256sum "${DIAGNOSTICS}" | cut -d' ' -f1)" == "${DIAGNOSTICS_SHA256}" ]]
[[ "$(sha256sum "${RECOMPUTED}" | cut -d' ' -f1)" == "${RECOMPUTED_SHA256}" ]]
grep -q "${PREPARED_SHA256}" "${EVIDENCE}"
grep -q "${VALIDATION_SHA256}" "${EVIDENCE}"

[[ "$(jq -r '.result' "${VALIDATION}")" == "pass" ]]
[[ "$(jq -r '.metric_rows_recomputed' "${VALIDATION}")" == "12" ]]
[[ "$(jq -r '.reload_equivalence_mode' "${VALIDATION}")" == "original_prediction_chunks" ]]
[[ "$(jq -r '.fixed_test_access' "${VALIDATION}")" == "false" ]]
[[ "$(jq -r '.spinup_execution' "${VALIDATION}")" == "false" ]]
[[ "$(jq -r '.validation_label' "${VALIDATION}")" == "fixed_upstream_gpp_stage" ]]

for job_id in 24485863 24485909 24485952 24488350 24488401 24488434 24488468 24488737; do
  grep -q "${job_id}" "${REPORT}"
done
grep -q '| validation | pooled | hourly | 20,112,960 | 0.911104 | 4.025672 | 2.151374 |' "${COMPACT}"
grep -q '| validation | pooled | daily | 838,040 | 0.860052 | 2.366163 | 1.393406 |' "${COMPACT}"
grep -q 'same hourly artifact' "${COMPACT}"
grep -q 'Campaign-plan amendment recommendation: `none`' "${REPORT}"
grep -q 'No campaign-plan amendment is proposed' "${HANDOFF}"

echo "ITER005_FOUR_RECORD_VALIDATE_PASS records=report,summary,registry,handoff result=pass decision=freeze_baseline active_jobs=0"
