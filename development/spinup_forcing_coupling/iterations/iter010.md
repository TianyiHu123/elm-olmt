# iter010 - TIM terminal-partition topology diagnosis

## Status

- Iteration ID: `iter010`
- Work type: `implementation`
- Run slugs: `spinup_forcing_coupling_iter010_{preflight,topology,predict,finalize}`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-12T19:06:17-07:00`
- Closed: 2026-08-12T20:05:00-07:00

## Finalized Plan and Consolidated Kickoff Package

- Objective: determine whether deterministic Iter009 TIM terminal two-means partitions are
  reproducible separated basins, a connected ridge, a broad/unimodal screen artifact, or
  inconclusive, analyzing ABBY and JERC separately.
- Hypothesis: genuine basins reproduce scalar and multivariate separation, temporal persistence,
  and corresponding group locations across all three seeds; intermediate paths support a ridge;
  overlap or unstable assignments support an artifact.
- Scope: six immutable TIM chains (ABBY/JERC x seeds 9009/9010/9011), each `(8000,64,15)`;
  terminal windows 500/1000/2000/4000; 1000-step rolling windows with 250-step stride over
  steps 4001--8000; late halves 4001--6000 and 6001--8000; 2048 deterministic colored draws
  per chain; five figures per chain and one three-seed synthesis per site.
- Exclusions: no new MCMC, continuation, resampling, changed posterior/likelihood/bounds,
  surrogate, observations, site windows, pooled clustering, interpolated paths, tempering,
  proposal tuning, or convergence-length study.
- Topology rule: classify each site exactly as `two_basin_supported`, `connected_ridge_supported`,
  `two_basin_declined`, or `inconclusive` from the four immutable requirements in CURRENT.md.
  Prediction is conditional only for `two_basin_supported`; otherwise emit a validated skip record.
- Integrity gates: terminal accounting; exact six-source identity/schema/shape/finiteness and
  provenance; deterministic metadata; complete figures/syntheses; immutable topology rule;
  complete conditional ledger or skip; comprehensive report and cross-record agreement.
- HPC/runtime: Puma, `chopinsong`/`standard`/`OLMT_puma`; preflight 2 CPUs/10 GB/30 min;
  topology 4 CPUs/20 GB/2 h; prediction 4 CPUs/20 GB/1 h; finalize 2 CPUs/10 GB/1 h.
  Three nominal tasks if prediction is skipped, four if triggered; hard cap eight including
  permitted retries. One minimal preflight correction/rerun and one unchanged scheduler/resource
  retry per substantive unit. Cancellation is limited to recorded Iter010 IDs for a proven
  universal pre-execution defect.
- Output root and layout: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`,
  with only the four named Iter010 run directories created; large outputs remain outside Git.
- Authority: exact user response `approved the full package`; lifecycle preparation through
  evaluation, records, validation, scheduler submission/monitoring/accounting, and one local
  closeout commit are authorized within this package; no push.

## Upstream Dependency Lock

The six Iter009 TIM `raw_chain.npz`, `backend.h5`, `raw_chain_metadata.json`, checkpoint manifests,
and selection ledgers are immutable inputs. Their paths and hashes are recorded in the preparation
manifest before submission. Iter002 forcing and Iter012 `drop21_corr080`, observations, cases,
physical bounds, parameter order, and posterior convention remain unchanged from Iter009.

Repository preparation parent: `879e376` (`Plan Iter010 TIM topology diagnosis`); source changes
are limited to `slurm/iter010/`, `summaries/iter010/`, this report, CURRENT, registry, cumulative
summary, and approved closeout metadata. Environment identity is `OLMT_puma` with the validated
Puma micromamba module recorded by preflight.

## Provenance and Job Ledger

| Work unit | Job IDs | State |
| --- | --- | --- |
| preflight | 23554607 | COMPLETED 0:0; `PREFLIGHT_PASS`; 13 s; 2 CPUs/10 GB |
| topology | 23554935 | COMPLETED 0:0; `TOPOLOGY_PASS`; 1:12; 4 CPUs/20 GB |
| predict | 23555136 | COMPLETED 0:0; `PREDICTION_SKIPPED`; 8 s; 4 CPUs/20 GB |
| finalize | 23555187 | COMPLETED 0:0; `FINALIZE_PASS`; 9 s; 2 CPUs/10 GB |

## Independent Read-Only Review

- Reviewer: independent read-only agents Epicurus, James, Herschel, and Parfit.
- Reviewed source hash: final Iter010 source files and submitted-copy SHA-256 identity after fixes.
- Outcome: pass after correction of hash/provenance enforcement, aggregation initialization,
  label ordering, and required trajectory/rolling evidence.
- Static evidence: `bash -n` all Slurm scripts, Python compile, JSON parse, and `git diff --check` pass.
- Preflight `23554607`: terminal `COMPLETED 0:0`, `PREFLIGHT_PASS`; all six raw/backend/metadata/
  checkpoint/selection hashes and site/seed/schema/log-prob provenance passed.
- Topology `23554935`: terminal `COMPLETED 0:0`, `TOPOLOGY_PASS`; ABBY and JERC both
  `two_basin_declined`; `prediction_required=false`; no conditional coupled evaluations.
- Prediction `23555136`: terminal `COMPLETED 0:0`, `PREDICTION_SKIPPED`; validated skip record
  reports zero evaluations because neither site supported two basins.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass` (integrity, provenance, and evidence completeness).
- ABBY topology: `two_basin_declined`; scalar separation, multivariate separation, and temporal
  persistence oppose in all three seeds; corresponding group locations support.
- JERC topology: `two_basin_declined`; scalar separation, multivariate separation, and temporal
  persistence oppose in all three seeds; corresponding group locations support.
- Conditional branch: validated `skipped`, zero evaluations, because neither site was
  `two_basin_supported`.
- Evidence: 32 PNG figures (five per chain plus one three-seed figure per site), six metric NPZ
  archives, topology decision/table, source manifest, final report, and prediction skip record.
- Interpretation: the forced terminal screen is declined as evidence for two physical basins at
  both sites. This does not establish convergence or posterior basin weights.
- Next route: replace the forced screen, reassess TIM/JERC, and propose Experiment 5 for ABBY
  acceptance/saturation, as the single planning-only route selected by the immutable table.

## Evaluation and Closeout

- Four-record validation command: `python development/spinup_forcing_coupling/slurm/iter010/validate_iter010_handoff.py`.
- Four-record validation output: `ITER010_HANDOFF_VALIDATE_PASS`.
- No active or unaccounted jobs; all four recorded jobs have terminal `COMPLETED 0:0` accounting.
- Closeout branch: one local commit authorized; no push.

The report, compact summaries, decision JSON, per-chain/site topology tables, figure metadata,
conditional prediction/skip evidence, accounting, cumulative summary, registry, and CURRENT must
agree exactly. Closeout requires no active or unaccounted job, complete classified evidence, passing
four-record validation, and the authorized single local commit.

## Closeout Checklist

- [ ] Iteration report finalized
- [ ] Required evidence copied to `summaries/iter010/`
- [ ] `ITERATION_SUMMARY.md` updated
- [ ] `registry.csv` updated
- [ ] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator passes
- [x] No job active or unaccounted
- [ ] Authorized closeout commit verified
