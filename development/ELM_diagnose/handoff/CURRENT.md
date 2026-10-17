# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter013`
- Proposed iteration: none
- Status: `workflow_complete`
- Phase: `closed`
- Active job scope: none. Preflight jobs `24192660` and `24204148` and diagnostic job `24204180` are authoritatively terminal `COMPLETED 0:0`; preparations 1 and 3 were never submitted.
- Active monitoring: none. Sessions `92439`, `14410`, `9882`, and `58719` are historical and finished or handed off as recorded in `iterations/iter013.md`.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-10T15:58:15-07:00`

## Iter013 Closeout Snapshot

- Work type/status/acceptance: `implementation`; `completed`; `pass`.
- Objective: extend the Iter012 ABBY standard package with contextual NEON `GPP_DT`/`GPP_NT`, final-spinup eight-pool C:N and C:P response endpoints, and contextual soil C/N/C:N observations.
- Scope: exactly 27 mapped transient/restart OAT ensembles, 2,700 members, 61,320 hourly model samples/member, five transient endpoints, five final-spinup endpoints, three constructed pathways, 109,113 CSV rows, and 13 PNGs.
- Inputs: passing v6 manifest `808ec4f0870f13f6c947a65e9d466c3bb80cd036708bbb32648075bbd3863225`; exact 27 pickles/configs/parameter files/restart cases; control parameter NetCDF; ABBY SR and two GPP partitioning products; ABBY soil C/N/C:N table.
- Outputs: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter013_abby_ctrlvertc_oat_spinup_obs/results`; output manifest `99d84254e00f8bb0f49312ff99413a4b87b4249d0eadedb3b3dad53a7878539d`; generation, exact artifact validation, and atomic publication passed.
- Execution: preflight attempts 2 and 4 and diagnostic attempt 1 completed `0:0`; final diagnostic elapsed `00:07:33`, process peak `6413020K`, zero swaps. All scheduler work is terminally accounted.
- Observation support: SR 26,264 hours (42.83%); GPP_DT 15,771 (25.72%); GPP_NT 11,404 (18.60%), with 4,367 negative post-calendar values rejected. Model curves retain the full window; observations use independent support and never enter scoring.
- Result: all 2,700 C:N/C:P ratios and all 135 spinup scores are supported. `rf_s2s3` leads final-spinup C:N spread (166.2%); `k_s4` leads C:P (51.7%) and final-spinup C, N, and P totals.
- Review: `/root/iter013_review` independently reproduced all member ratios, 270 transient/spinup scores and ranks, response bins, observation semantics, counts, and hashes and visually inspected all 13 figures. Outcome `pass_with_concerns`; only minor readable heatmap/footer contrast and text-size concerns remain.
- Interpretation: baseline-conditioned, sampled-range descriptive OAT only. Soil observations are context-only with an accepted profile-versus-eight-pool boundary mismatch. No global sensitivity, interaction, causal limitation, threshold, optimization, tuning, recommendation, calibration, or cross-site/configuration conclusion is supported.
- Storage: `/xdisk` is temporary and unbacked; immutable attempts, logs, manifests, and results are retained without overwrite or automatic backup.

## Records and Closeout

- Detailed report: `development/ELM_diagnose/iterations/iter013.md`
- Compact result: `development/ELM_diagnose/summaries/iter013/ITER013_RESULT.md`
- Cumulative summary: `development/ELM_diagnose/ITERATION_SUMMARY.md`
- Registry: one fixed-schema `iter013` row in `development/ELM_diagnose/registry.csv`
- Final validator: `development/ELM_diagnose/slurm/iter013/validate_iter013_closeout.sh`, SHA-256 `2c24842dd3553c333f8767671192bff48d02b083cd86172bb3760ee22090d2f3`; pass marker `ITER013_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=13 csv_rows=109113 transient_scores=135 spinup_scores=135 terminal_jobs=3 next_state=workflow_complete`.
- Closeout branch: exactly one scoped closeout commit; no push.

## Next State

The Iter013 lifecycle is complete. No Iter014 plan is proposed. A future iteration requires a new planning-only proposal and fresh consolidated kickoff approval under `development/ELM_diagnose/WORKFLOW.md`.
