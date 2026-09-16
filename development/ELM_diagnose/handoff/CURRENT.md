# ELM Diagnostic - Current Handoff

## Live State

- Active iteration: none
- Most recent closed iteration: `iter007`
- Status: `completed`
- Phase: `closed`
- Active job scope: none. Preflight jobs `23882414`, `23882462`, and `23882524`, and diagnostic job `23882574`, are terminally accounted.
- Active monitoring: none; all retained monitor handles ended and job-scoped accounting is complete.
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-09-15T19:19:52-07:00`

## Closed Iteration Identity and Decision

- Iteration ID: `iter007`
- Work type: `implementation`
- Objective: Apply the complete Iter005/Iter006 extended OAT diagnostic to 13 ABBY vertical-soil-carbon one-parameter ensembles with explicit dynamic parameter mapping.
- Bounded scope: 13 exact ABBY vertical-soil-carbon pickles; 1,300 members; 13 standard targets; one SR observation; seven compensation mappings; eight-pool potential/N/P-limited HR; four litter ratios; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted validated standalone ABBY vertical-soil-carbon range-conditional descriptive OAT and pathway/stoichiometry package; no PAWN/Sobol/global sensitivity, interaction, causal, optimization, tuning, parameter-value, cross-configuration, or cross-site claim.
- Closeout branch: one authorized scoped commit; no push.

## Authoritative Evidence

- Full report: `development/ELM_diagnose/iterations/iter007.md`.
- Compact result: `development/ELM_diagnose/summaries/iter007/ITER007_RESULT.md`.
- Published output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter007_abby_ctrlvertc_oat_extended/results`.
- Input manifest SHA-256: `bf459adab7ce1ed4400ba14a4b217381ecad812510c94164992d54bfe887fd49`.
- Output manifest SHA-256: `61a85ab5395a10865996faea1ad425229a594439e53d210941798b45688935ce`.
- Passing work: preflight `23882524 COMPLETED 0:0`; diagnostic `23882574 COMPLETED 0:0`; hardened validator passed 3,268,682 rows and 44 figures before atomic publication.
- Classified failures: preflight `23882414` and `23882462` failed before Python on the mistyped pinned postprocessing digest. Attempt two also corrected a latent newline-sensitive parameter reader. After explicit authorization, the corrected final retry passed.
- Review: independent read-only `/root/iter007_review`; preparation, retry, launch, artifacts, calculations, and corrected pathway metrics passed final review.
- Mean fluxes in gC m-2 day-1: potential, P-limited, N-limited, model SR, observed SR, and actual model HR_TOTAL are `11.782900`, `3.834530`, `2.865373`, `1.342808`, `7.501337`, and `0.785350`. The first three and observed SR differ from model SR by `+777.48%`, `+185.56%`, `+113.39%`, and `+458.63%`; N limitation reduces potential HR by `75.68%`.
- Observation coverage is 26,264/61,320 hours (`42.83%`). All four litter ratios retain 1,300 supported and zero rejected members.
- `decomp_depth_efolding` has `0.30%`--`0.57%` flux-summary response spreads and ranks 8th--11th for aggregated soil-C summaries over its sampled range.

## Risks and Next State

- Results are conditional on declared ranges and separate OAT ensembles. Observation context does not enter screening scores and is not exactly time matched. Constructed HR pathways are not actual model HR.
- Heatmap annotation contrast is weak in low-valued cells. Axis-offset notation magnifies machine-scale scatter in effectively constant litter-ratio panels; numerical tables are authoritative.
- `/xdisk` is temporary and unbacked. Allocation expiration remains unverified because the query is PI-only.
- Next state: workflow intentionally stopped after validated Iter007 closeout; no next iteration is proposed automatically.

## Resume Protocol

1. Read this handoff and `development/ELM_diagnose/WORKFLOW.md`.
2. Read `development/ELM_diagnose/iterations/iter007.md`, its compact result, and the Iter007 registry row.
3. Treat Iter007 execution material, reports, manifests, results, and registry evidence as immutable closed provenance.
4. Begin any new work at WORKFLOW Section 4A with a new sequential plan and fresh authority.

## Proposed Next-Iteration Plan (Planning Only)

No next iteration is proposed automatically.
