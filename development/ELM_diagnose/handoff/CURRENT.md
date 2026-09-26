# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter006`
- Status: `completed`
- Phase: `closed`
- Active job scope: none. Preflight jobs `23856493`, `23856561`, and `23856771`, and diagnostic job `23861155`, are terminally accounted.
- Active monitoring: none. Detector sessions `12372` and `65404` are retired; the attempt-three preflight detector was not started before a recorded platform interruption.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-11T16:03:29-07:00`

## Closed Iteration Identity and Decision

- Iteration ID: `iter006`
- Work type: `implementation`
- Objective: Apply the complete Iter005 extended OAT diagnostic to the 14 corresponding JERC one-parameter ensembles with explicit site-generalized tooling.
- Bounded scope: 14 exact JERC pickles; 1,400 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated JERC range-conditional descriptive OAT and pathway/stoichiometry package under the approved explicit-gap support contract; no global sensitivity, interaction, causal, optimization, tuning, parameter-value, or cross-site claim.
- Closeout branch: one authorized scoped commit; no push.

## Authoritative Evidence

- Full report: `development/ELM_diagnose/iterations/iter006.md`.
- Compact result: `development/ELM_diagnose/summaries/iter006/ITER006_RESULT.md`.
- Published output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter006_jerc_oat_extended/results`.
- Input manifest SHA-256: `b10901c14c8d5689f1a704038860f51d79d9fa3ca663bfdef510555c9f5941f0`.
- Output manifest SHA-256: `256cc1e1318aaa3e2a2ceaa123fdb06f2fd9e7ff224f4950caea659e4571ec31`.
- Passing work: revised preflight `23856771 COMPLETED 0:0`; diagnostic `23861155 COMPLETED 0:0`; artifact validator passed 3,520,119 rows and 44 figures before atomic publication.
- Classified failures: preflight `23856493 FAILED 1:0` on abbreviated/full commit-SHA mismatch; preflight `23856561 FAILED 1:0` on the original all-members litter-denominator gate. The latter led to the user-approved explicit-gap contract; neither was a scheduler/resource failure.
- Review: independent read-only `/root/iter006_review`; corrected preparation material passed, and final results passed with only retained visual-quality concerns.
- Mean fluxes in gC m-2 day-1: potential/P-limited HR `3.961651`, N-limited HR `3.560783`, model SR `2.930035`, observed SR `1.326166`. Relative to model SR: `+35.21%`, `+35.21%`, `+21.53%`, and `-54.74%`; N limitation reduces potential HR by `10.12%`.
- Litter support: 1,363 supported and 37 rejected members per ratio; all rejections are `nonpositive_nutrient_total`. Observation coverage is 51,882/61,320 hours (`84.61%`).

## Risks and Next State

- Results are conditional on declared ranges and separate OAT ensembles. Observation context does not enter screening scores, incomplete observation support is not time-matched, and unsupported ratios are gaps rather than zeros.
- Heatmap annotation contrast is weak in some cells. Axis-offset notation magnifies machine-scale numerical scatter in effectively constant litter-ratio panels; do not interpret that display noise as sensitivity.
- `/xdisk` is temporary and unbacked. Allocation expiration remains unverified because the query is PI-only.
- Next state: workflow intentionally stopped after Iter006 closeout. No next iteration is proposed automatically.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter006.md`, its compact summary, and the Iter006 registry row.
3. Treat Iter006 code, Slurm material, outputs, summary, and registry evidence as immutable closed provenance.
4. If further work is desired, create a complete planning-only next-iteration proposal and obtain a fresh consolidated kickoff approval before initialization or execution.

## Proposed Next-Iteration Plan

No next iteration is proposed automatically. The workflow is intentionally stopped.
