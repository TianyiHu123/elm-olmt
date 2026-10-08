# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter012`
- Proposed iteration: none
- Status: `workflow_complete`
- Phase: `closed`
- Active job scope: none; jobs `24137742`, `24137829`, `24137929`, `24149109`, and `24149371` are terminally accounted `COMPLETED 0:0`.
- Active monitoring: none; all retained monitor outcomes and terminal handoffs are recorded in `iterations/iter012.md`.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-07T16:05:59-07:00`

## Iter012 Closeout Snapshot

- Objective: extend the Iter011 ABBY transient/spinup OAT package with six respiration-fraction ensembles while preserving the same baseline-conditioned descriptive methods and interpretation boundary.
- Scope: exactly 27 pickles/configs/parameter files/restart cases, 2,700 members, five transient means, three final-spinup totals, three constructed pathways, 103,114 primary CSV rows, and 11 figures.
- Acceptance: `pass`; all immutable input, calculation, artifact, visual, publication, review, accounting, resource, and record gates pass.
- Inputs: passing input manifest `2d041f0d3e952bc9c22bb757ca0533ded4baecd80d8b56daa998e9a0b3ae6977`; exact six additions `rf_l1s1`, `rf_l2s2`, `rf_l3s3`, `rf_s1s2`, `rf_s2s3`, and `rf_s3s4`, each sampled over `0.1--0.9`.
- Outputs: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter012_abby_ctrlvertc_oat_spinup/results`; output manifest `a24daac2c93c868182ed347e400938252f28a815645cb7cba41d7d61e01ec0ae`; exactly 103,114 rows and 11 PNGs.
- Execution: four preflights and one diagnostic completed `0:0`. Independent GNU-time measurement resolved allocation-pegged Slurm MaxRSS and supported right-sizing from 20 CPUs/100 GB to four CPUs/20 GB. Diagnostic process peak was `6408012K`, with no swaps.
- Review: `/root/iter012_review` passed final numerical, artifact, provenance, and visual review. It reproduced every score, rank, response bin, pathway row/curve, row count, and artifact hash; all 11 figures passed visual review.
- Result: `rf_s2s3` leads mean SR, HR, and LITFALL response spreads and ranks third for GPP and final-spinup decomposer C. `k_s4`, `k_s3`, and `k_s2` remain the leading stock-response parameters.
- Pathways: mean N-limited/potential and P-limited/potential ratios are `0.305316` and `0.401703`. P exceeds N in `2693/2700` cases; the seven exceptions are low-range `rf_s2s3` samples and are reported as sampled-range nonlinearity, not a threshold.
- Decision: accept only as baseline-conditioned, sampled-range descriptive OAT evidence. Constructed pathways remain distinct from direct model `HR`; no PAWN/Sobol/global-sensitivity, interaction, causal nutrient-limitation, tuning, threshold, recommendation, or cross-site/configuration conclusion is supported.
- Storage risk: `/xdisk` is temporary and unbacked; all attempts, logs, manifests, and published outputs are retained without overwrite or automatic backup.

## Records and Closeout

- Detailed report: `development/ELM_diagnose/iterations/iter012.md`
- Compact result: `development/ELM_diagnose/summaries/iter012/ITER012_RESULT.md`
- Cumulative summary: `development/ELM_diagnose/ITERATION_SUMMARY.md`
- Registry: one fixed-schema `iter012` row in `development/ELM_diagnose/registry.csv`
- Final validator: `development/ELM_diagnose/slurm/iter012/validate_iter012_closeout.sh`, SHA-256 `64c92e1053512de88626ca59a47b2216580309a94b4bb787b6149def0c47555a`; pass marker `ITER012_FOUR_RECORD_VALIDATE_PASS records=5 registry_rows=1 png=11 csv_rows=103114 transient_scores=135 spinup_scores=81 terminal_jobs=5 next_state=workflow_complete`.
- Closeout branch: exactly one scoped commit is authorized; no push. The commit identity is verified after creation and reported to the user rather than embedded in the committed records.

## Next State

The workflow is complete. No Iter013 plan is inferred. A future diagnostic iteration requires a new planning-only proposal and fresh consolidated kickoff approval.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter012.md`, its compact result, registry row, and `development/hpc/puma.md`.
3. Treat all Iter012 execution material, attempts, manifests, outputs, and closeout records as immutable provenance.
4. Do not resubmit any Iter012 job. Start only from a fresh planning-only proposal if the user requests another iteration.
