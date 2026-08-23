# iter018 - final nine-site operational coupled-optimization release

## Status

- Iteration ID: `iter018`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter018_operational_nine_site`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-21T19:17:05-07:00`
- Closed: `2026-08-22T19:51:19-07:00` (includes approved reporting-contract makeup)

## Finalized Plan

The complete `ITER018_PLAN_BEGIN/END` proposal in `iterations/iter017.md` was approved at
`2026-08-21T19:17:05-07:00`, with later approved concurrency, provenance, and report-guard
recoveries that did not change science, seeds, or acceptance gates.

- Objective: nine-site operational coupled-optimization release, then comprehensive
  coupling-development closeout and merge-readiness declaration (no merge).
- Daily/`0.50`: ABBY, SOAP, YELL, WREF. Hourly/`0.75`: JERC, OSBS, RMNP, TALL, TEAK.
- Fresh `q=0.90` hybrid pools; seeds `9009--9017`; 64 walkers × 8,000 steps.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| Approvals | Kickoff `2026-08-21T19:17:05-07:00`; concurrency `2026-08-22T15:37:00-07:00`; source-manifest recovery `2026-08-22T15:54:00-07:00`; provenance realignment `2026-08-22T16:15:00-07:00`; report-guard recovery `2026-08-22T18:49:00-07:00`; reporting-contract makeup `2026-08-22T19:17:00-07:00` |
| Goal and stop condition | Complete nine-site operational run through accounting, evaluation, four-record validation, comprehensive closeout, and merge-readiness declaration; no merge |
| HPC site | UArizona Puma; `chopinsong` / `standard`; `OLMT_puma`; `development/hpc/puma.md` |
| Output root | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter018_operational_nine_site/` |
| Resources | Preflight 4 CPU/30m; init 8 CPU/4h; leaf 16 CPU/4h; report/aggregate 4 CPU/2h; handoff 2 CPU/30m. Historical JERC/WREF `0-8%2`; remaining arrays submitted `0-8` |
| Commit authority | One preparation/source-lock commit before preflight and at most one closeout commit; no push, PR, or merge |

## Acceptance Gates and Decision Rule

Integrity requires terminal accounting, immutable pools, 81 complete leaves, nine standard
reports with Tier-A-only best-parameter/CLM exports plus SR MAP ensemble overlays, aggregate
evidence, handoff agreement, and four-record agreement. Decision `operational_release_ready`
requires every integrity gate. Per-site `all_tier_a` / `partial_tier_a` / `insufficient_retained`
is descriptive only.

## Provenance and Job Ledger

| Work unit | Job IDs | State | Notes |
| --- | --- | --- | --- |
| preflight | `23619814` | `COMPLETED 0:0` | `ITER018_PREFLIGHT_PASS campaigns=9` |
| initialization | `23619841`–`23619849`, `23619868` | all `COMPLETED 0:0` | nine fresh pools validated |
| optimization (historical `%2`) | JERC `23619996`; WREF `23620021` | 18/18 `COMPLETED 0:0` | leaf products pass |
| failed attempts | `23642777`–`23642783`; `23643001`–`23643007` | failed/cancelled | classified source-manifest then pool-provenance defects; recovered |
| optimization (remaining `0-8`) | OSBS `23643144` … YELL `23643150` | 63/63 `COMPLETED 0:0` | after provenance realignment |
| reports (initial) | ABBY `23651289`; JERC `23651290`; OSBS `23651291`; SOAP `23651292`; RMNP `23651293`; TALL `23651296`; TEAK `23651297`; WREF `23651306`; YELL `23651309` | all `COMPLETED 0:0` | superseded by makeup (all-seed best params) |
| reports (makeup) | ABBY `23651925`; JERC `23651926`; OSBS `23651927`; SOAP `23651928`; RMNP `23651929`; TALL `23651932`; TEAK `23651933`; WREF `23651934`; YELL `23651935` | all `COMPLETED 0:0` | Tier-A-only best params/corner + SR MAP ensemble |
| aggregate (makeup) | `23652320` | `COMPLETED 0:0` | `ITER018_AGGREGATE_PASS` |
| handoff (makeup) | `23652321` | `COMPLETED 0:0` | `ITER018_HANDOFF_PASS sites=9 leaves=81` |

## Execution and Diagnostics

- Report-guard defect: materializer scaffold `reports/` conflicted with overwrite check; fixed in
  `report_optimization.py` to refuse only prior reporting products.
- Reporting-contract makeup: best-parameter tables/NetCDFs and physical corner use Tier-A seeds
  only; full-seed audit retained in `all_seed_parameter_sets.csv` and `reports/per_seed/`;
  Tier-A MAP SR ensemble overlay vs obs + ELM precal written under
  `reports/plots/predictions/<site>/Predictions_SR_MAP_ensemble.png`. README optimization section
  updated to match. Handoff validator expects NetCDF count = retained Tier-A count.
- All 81 leaves have `production_result.json` status `pass`. All nine makeup reports emit
  Tier-A-only `clm_params_seed_*.nc` exports and `report_manifest.json` schema
  `coupled-optimization-report-v4`.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `operational_release_ready`
- Descriptive site statuses: ABBY/SOAP/YELL/WREF/TALL `all_tier_a`; JERC/OSBS/RMNP/TEAK
  `partial_tier_a`; none `insufficient_retained`
- Summary evidence: `development/spinup_forcing_coupling/summaries/iter018/`
- Next state: terminal declaration — coupling-framework development ends; no next iteration;
  merge is a separate user decision

## Proposed Next-Iteration Plan (Planning Only)

Terminal declaration: the spinup-forcing coupling-development line ends after this closeout. No
next iteration is proposed. Any merge is a separate user decision.

## Closeout Checklist

- [x] Iteration report, summary, registry, and handoff finalized and cross-validated
- [x] Required external products and accounting verified
- [x] Authorized makeup closeout commit verified
