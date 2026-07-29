# Spinup Surrogate - Current Handoff (Iter012 closed)

## Live State

- Latest iteration: `iter012`
- Status: `completed`
- Phase: `closed`
- Last updated: `2026-07-29` on Puma
- Active Iter012 jobs: none
- Site profile: `development/hpc/puma.md`
- Native goal: Iter012 lifecycle completed by this authorized closeout snapshot

## Current Objective

Iter012 is the terminal spinup-surrogate development release. It publishes two trusted-source,
versioned `spinup-surrogate-v1` artifacts and preserves their Iter011 scientific evidence.

## Best Evidence So Far

- Recommended `drop32`: 32 features, Iter011 median validation R2 `0.827271 / 0.827497`,
  artifact SHA-256 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`.
- Compact `drop21_corr080`: 21 features, median validation R2 `0.801217 / 0.801178`,
  artifact SHA-256 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`.
- Both artifacts exactly reproduced seed 10001 before their full 900-row fits.
- Release jobs `23445281` and `23445296` and cross-validator `23445328` completed `0:0`.
- Cross-validation passed fresh-process loading, nine-case coverage, true batch inference,
  schema/range failure gates, sidecar identity, and forcing-bridge design-matrix compatibility.
- Target units and long names were recovered from same-source/version ELM history after all
  restart-component attributes were explicitly found empty.

## Current Risks or Blockers

- No active blocker.
- `/xdisk` is temporary, unbacked storage; copy release artifacts to durable storage if needed.
- Pickle loading is permitted only for trusted artifacts.
- The training domain is the recorded nine-case population. Out-of-range input produces warnings,
  not evidence of generalization.
- `drop21_corr080` remains a user-accepted compact tradeoff that failed the Iter011 median R2,
  minimum R2, and median RMSE-ratio gates.
- The forcing bridge validates only column order, shape, and dtype. No real forcing-surrogate
  artifact was trained or validated in Iter012.

## Next Action

Use `drop32` as the default final spinup artifact or `drop21_corr080` when its compactness
tradeoff is appropriate. Any real forcing-surrogate integration begins under a fresh objective
and runtime contract.

## Next Iteration Plan (Planning Only)

Iter012 is the terminal spinup-surrogate development release. No Iter013 experiment is proposed.
Future work, under a separate objective and runtime contract, may integrate a released spinup
artifact with a real forcing-surrogate artifact and validate actual forcing-target predictions.

## Next Session Start Protocol

1. Read this handoff, `development/spinup_surrogate/WORKFLOW.md`, and
   `development/spinup_surrogate/iterations/iter012.md`, plus `development/hpc/puma.md`.
2. Inspect current Git and scheduler state before diagnosing drift.
3. Verify artifact hashes and trusted provenance before loading either pickle.
4. Obtain a fresh finite runtime contract before any new scheduler or model execution.

## Artifact Paths

- Current report: `development/spinup_surrogate/iterations/iter012.md`
- Registry: `development/spinup_surrogate/registry.csv`
- Cumulative summary: `development/spinup_surrogate/ITERATION_SUMMARY.md`
- Canonical Iter012 scripts and validators: `development/spinup_surrogate/slurm/iter012/`
- Recommended artifact:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop32/surrogate_spinup/spinup_surrogate_iter012_drop32.pkl`
- Compact artifact:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl`
- Release sidecars and decision:
  `development/spinup_surrogate/summaries/iter012/`
- Metadata diagnostic:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter012_metadata_diagnostic/target_metadata_diagnostic.json`

## Files Modified in Repo (latest completed iteration)

- Public loader/CLI: `model_ELM/spinup_surrogate_artifact.py`,
  `predict_surrogate_spinup.py`
- Forcing bridge: `model_ELM/surrogate_NN_Forcing.py`
- Release and validation tooling: `development/spinup_surrogate/tools/`
- Iter012 Slurm and diagnostic sources: `development/spinup_surrogate/slurm/iter012/`
- Durable records: `README.md`, `development/spinup_surrogate/ITERATION_SUMMARY.md`,
  `development/spinup_surrogate/registry.csv`, this handoff, and the Iter012 report

## Latest Iteration Reference

See `development/spinup_surrogate/iterations/iter012.md` for the runtime contract, immutable
source provenance, independent reviews, full job ledger, failure classification, artifact hashes,
validation results, and release decision.
