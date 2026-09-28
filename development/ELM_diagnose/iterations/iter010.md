# iter010 - ABBY C:N carbon-balance diagnostic

## Status

- Iteration ID: `iter010`
- Work type: `implementation`
- Run slug: `elm_diagnose_iter010_abby_ctrlvertc_cn_carbon_balance`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-09-27T19:14:01-07:00`
- Closed: `2026-09-27T19:45:24-07:00`

## Finalized Plan

The complete planning block in `development/ELM_diagnose/iterations/iter009.md` and `handoff/CURRENT.md` at planning commit `77ffa89` is incorporated unchanged. Its normalized SHA-256 is `3b1bff17f52b8fc3999bf5f9b76303f79e3cc5e622d81d67fa78ffcfbbf7e269`.

- Objective: test whether weak historical direct-`HR` responses across the four separate ABBY `cn_s1`--`cn_s4` OAT ensembles track cumulative `LITFALL` input or changing eight-pool carbon storage.
- Calculations: `input_C=sum(LITFALL/24)`, `HR_C=sum(HR/24)`, `delta_C=C_end-C_begin` for `CWDC+LITR1C+LITR2C+LITR3C+SOIL1C+SOIL2C+SOIL3C+SOIL4C`, and `residual_C=input_C-(HR_C+delta_C)`.
- Implementation: create reusable `tools/oat_carbon_balance.py`; do not modify the nutrient-stress engine; preserve the four explicit pickles, 400 members, 61,320 hours, ten equal-count bins, native markers, explicit gaps, and baseline-conditioned OAT boundary.
- Artifacts: preserve and regression-check 37,812 Iter009 CSV rows and 17 figures; add 1,730 carbon-balance CSV rows and four figures; final contract 39,542 CSV rows and 21 PNGs plus manifests.
- Interpretation: 1:1 shows accounting closure only. Historical HR input tracking additionally requires small closure error, HR response following input response, and a small storage-change response. No equilibrium, causal, global-sensitivity, optimization, or cross-site claim.
- Work units: one bounded preflight and one diagnostic; staging then atomic publication; technical acceptance is independent of scientific direction.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | Exact response `Complete package approved`; `2026-09-27T19:14:01-07:00` |
| Goal and stop conditions | Complete initialization through validated closeout for exactly two compute work units; stop for a material decision, identity mismatch, failed immutable gate, exhausted authority, unavailable monitoring, explicit stop, or validated closeout. |
| HPC/profile | Puma host `wentletrap.hpc.arizona.edu`; `development/hpc/puma.md`; `standard/chopinsong`; `OLMT_puma`; validate `micromamba/2.0.2-2`. |
| Output/storage | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter010_abby_ctrlvertc_cn_carbon_balance`; `preflight/attempt_N`, `diagnostic/attempt_N`, atomic `results`; create exact layout, retain failed attempts, never overwrite/delete/auto-backup; `/xdisk` temporary and unbacked. |
| Lifecycle authority | Primary agent may implement, create approved paths, launch/wait for read-only review, submit, monitor, account, evaluate, update records, validate, and close out. |
| Resources/retries | Initial 12 CPUs/standard-derived 60 GB; 2 h preflight, 4 h diagnostic. One minimal preflight correction/rerun and one scheduler/resource retry per unit, capped at 16 CPUs/80 GB and 3 h/6 h. |
| Monitoring | Retained 300-second state-change detector with unchanged-output suppression; one materially different detached-tmux fallback if demonstrably lost; terminal job-scoped `sacct` required. |
| Cancellation | Recorded Iter010 job IDs only for identity mismatch, universal pre-execution defect, out-of-root writes, contract overrun, or explicit instruction. |
| Outside-sandbox authority | Approved locked `sbatch`; job-scoped `squeue`, `scontrol`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` under stated conditions. |
| Closeout | Exactly one scoped closeout commit; no push. |

## Declared Diagnostic Inputs and Evidence

| Parameter | Pickle SHA-256 |
| --- | --- |
| `cn_s1` | `fca486c11cf2a7c087195a7608b49d9b26c87c7369cd5a9418d6e44f4d9fcc1f` |
| `cn_s2` | `40589f8c95da4d12940dc99f1acfbe118721399e826283365fd628c3642c2297` |
| `cn_s3` | `b3d5d2aa40c48211551a16cd8db8ffca56430dc13f323087aeeffaf87ee525f1` |
| `cn_s4` | `c68eaafb6b0dbe54c5aa7eb604842ee36673228cb0357ecdd4b973ff35954ff6` |

- Each pickle is 4,121,205,317 bytes. Four config and four parameter-file hashes, control NetCDF `3876806b...1042e9`, environment `02283ec1...878bb`, Iter009 input manifest `bb283659...f982bf62`, and Iter009 output manifest `afa885d5...b95aae` were revalidated at kickoff.
- Output root was absent; repository was clean at commit `77ffa89`; current capacity fit the approved envelope.

## Acceptance Gates and Decision Rule

- Exact four inputs, direct `LITFALL`, direct `HR`, eight pools, 400 members, 61,320 hours, deterministic fixtures, correct integrations/endpoints/support, boundary audit, exact 39,542 CSV rows/21 PNGs, manifests, visual review, independent reviews, terminal accounting, and consistent records must pass.
- If `LITFALL` cannot establish the complete boundary, label the result partial and withhold the input-constraint conclusion without making scientific direction a technical failure.
- Any input, formula, artifact, gate, interpretation, resource-cap, retry, cancellation, or closeout change requires fresh approval.

## Provenance and Job Ledger

| Work unit | Canonical/submitted material | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| preflight | attempt_3 locked package | `24025653` | `COMPLETED 0:0`; 00:01:05; batch MaxRSS 20,613,164 K | terminal accounting complete; no scheduler retry |
| diagnostic | attempt_2 locked package | `24025871` | `COMPLETED 0:0`; 00:00:56; batch MaxRSS 20,623,812 K | terminal accounting complete; no retry |

## Independent Read-Only Review

- Reviewer: `/root/iter010_review` (read-only; active)
- Outcome: initial `block`; corrected attempt_3 re-review `pass_with_concerns`. All blocking dependency, boundary, support, fixture, validator, labeling, and non-evaluation-preflight findings were corrected. Remaining all-zero-input edge concerns are non-blocking because exact locked inputs are required and positive-input support is validated; final independent calculation review remains required.

## Execution and Diagnostics

- Static validation: `git diff --check`, both wrappers under `bash -n`, canonical/submitted attempt_3 byte identity, and pinned hashes pass.
- Preflight: job `24025653` completed `0:0` in `00:01:05`; `CARBON_BALANCE_PREFLIGHT_PASS`; input manifest `61b9fcad45de7271eada906e7a49739e40179d504e0ae203c15b1b0a80d79545`.
- Diagnostic: job `24025871` completed `0:0`; generator, exact validator, and atomic-publication markers pass; output manifest `80afe70badeb0a0f7cd2e3bda3be4ca1ec5fceef8543891b47a39036590b5c3c`.
- Terminal accounting: both jobs and their batch/extern steps are terminal `COMPLETED 0:0`.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`.
- Final review: independent reviewer passed all 33 artifact hashes, 39,542 CSV rows, 21 PNGs, all formulas/support/summary contrasts, 23 byte-identical Iter009 core artifacts, and all four new figures.
- Quantitative result: median absolute closure errors are `8.91%`, `9.07%`, `8.91%`, and `8.79%` for `cn_s1`--`cn_s4`; zero of 400 members are within 5%. HR accounts for approximately `88.6%`, `91.9%`, `101.2%`, and `87.4%` of the respective low-to-high input contrasts, while storage change accounts for `11.0%`, `7.3%`, `1.3%`, and `11.5%`.
- Decision: accept the technically valid partial-boundary diagnostic. Direct HR descriptively tracks litter-input response contrasts, but systematic roughly 9% absolute nonclosure and unresolved boundary transfers preclude the intended carbon-input-constraint or equilibrium conclusion.
- Next action: workflow complete; no next iteration proposed.

## Proposed Next-Iteration Plan (Planning Only)

No next iteration is proposed. Iter010 is closed; any further diagnostic requires a fresh complete plan and kickoff approval.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter010/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator passed
- [x] No job active or unaccounted
- [x] One scoped closeout commit created
