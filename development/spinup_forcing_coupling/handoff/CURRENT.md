# Spinup-Forcing Coupling - Current Handoff

Closeout identity: Iteration ID `iter014`; Status `completed`; Work type `implementation`; Overall acceptance result `pass`; Decision `partial_repair`

## Live State

- Active iteration: `iter014`
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Objective: `JERC high-likelihood candidate-pool reconstruction`
- Bounded scope: `pool_rule API; rebuild eligible rules from frozen ledger; hybrid-only MCMC if A geometry-fails; evaluate; aggregate; handoff validation`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014`
- Last updated: `2026-08-18T15:21:00-07:00`

## Active Kickoff Package and Runtime Authority

- Package state: `closed` (revised geometry-gate scientific handling executed)
- Kickoff goal and stop boundary: Executed Iter014 through aggregate; overall decision `partial_repair`
- User response and approval timestamp: original `approved the complete package` `2026-08-17T19:48:15-07:00`; revision `approved the revised package` `2026-08-17T20:18:46-07:00`
- Confirmed HPC system and profile: UArizona Puma; `development/hpc/puma.md`
- Locked dependencies: ledger `25382a57…`; control pool `32d2ba5f…`; hybrid pool `40ac807e…`; target `26e5caa0…`
- Closeout branch: one local closeout commit authorized; no push

## Current Objective

Closed. High-likelihood pool reconstruction at JERC yielded `partial_repair` for
`hybrid_high_l_maximin` and `geometry_gate_failed` for `rank_dominated`.

## Best Evidence So Far

- Work type and bounded scope: implementation; revised package completed
- Headline evidence: A condition `1.72e7` fails geometry; hybrid condition ≈359 passes;
  hybrid mean acceptance `0.1898` (control `0.1866`); cross-seed W `0.4365` (control `0.5484`)
- Acceptance-gate result and decision: integrity pass; overall `partial_repair`; no posterior promotion

## Current Risks or Blockers

- `/xdisk` products are temporary and unbacked
- Remaining W and acceptance gaps vs `repair_supported` thresholds
- Iter015 is recorded as planning-only and is not initialized

## Next Action

1. Seek one approval of the complete Iter015 consolidated kickoff package recorded below.
2. Do not initialize, scaffold, or submit Iter015 until that approval.

## Next Iteration Plan (Planning Only)

This user-directed Iter015 package supersedes the original closeout note (JERC-only longer
and/or milder-quantile hybrid diagnostics). It is planning-only. Do not initialize, scaffold,
or submit until a fresh consolidated kickoff approval.

<!-- ITER015_PLAN_BEGIN -->
## Proposed Iter015 plan - hybrid-init Iter011 configuration matrix at ABBY and JERC

- Sequential ID: `iter015`
- Status: `not_initialized`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter015_<work_unit>`

### Evidence-derived objective and hypothesis

- Objective: rerun the Iter011 site-specific resolution × DE-scale matrix at ABBY and JERC
  using the Iter014 hybrid initialization-to-MCMC pipeline, then recommend a configuration
  per site or call the site inconclusive.
- Hypothesis: Iter014’s `hybrid_high_l_maximin` (q=0.90) start cloud, not TIM, now sets
  walker geometry and seed-to-seed behavior. Under that cloud, Iter011’s ABBY `daily/0.75`
  preference and JERC hourly tradeoff may or may not still hold.
- Evidence basis: Iter011 TIM selected ABBY `daily/0.75` and left JERC
  `inconclusive_metric_tradeoff`. Iter012 diversity-pool production was
  `fixed_length_inconclusive` at both sites (JERC W ≈ 0.548). Iter014 hybrid JERC
  `hourly/0.75` was `partial_repair` (W 0.437, mean acc 0.190; seed acc 0.089 / 0.221 /
  0.259). The hybrid cloud is a wide high-L shell, not a TIM neighborhood.

### Upstream dependencies and trust assumptions

| Dependency | Role | Path | Identity |
| --- | --- | --- | --- |
| Iter002 forcing SR | coupled likelihood | `.../spinup_forcing_coupling_iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Spinup `drop21_corr080` | coupled spinup | `.../UQ_output/spinup_surrogate_iter012_drop21_corr080/surrogate_spinup/spinup_surrogate_iter012_drop21_corr080.pkl` | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| ABBY Iter012 Revision1 ledger | hybrid rebuild input | `.../iter012_general_pipeline_v2/revision1/initialization/abby/artifacts/candidate_ledger.npz` | `ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b` |
| JERC Iter012 Revision1 ledger | hybrid rebuild input | `.../iter012_general_pipeline_v2/revision1/initialization/jerc/artifacts/candidate_ledger.npz` | `25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d` |
| Iter014 JERC hybrid pool | JERC rebuild identity check | `.../iter014/pool_rebuild/hybrid_high_l_maximin/artifacts/candidate_pool.npz` | `40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df` |
| ABBY daily target | ledger-resolution target | Iter012 canonical | `bf9ade8b68bf7179cdb5c5712682dd1c343d510749efd7041cf0414ec4773bbd` |
| JERC hourly target | ledger-resolution target | Iter012/014 canonical | `26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196` |
| ABBY NEON v4 obs | likelihood obs | eval v4 | `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` |
| JERC NEON v4 obs | likelihood obs | eval v4 | `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` |
| Reusable analysis tools | overlay, diagnostics, corner | `development/spinup_forcing_coupling/tools/` | `plot_init_cloud_overlay.py`, `fixed_length_mcmc_diagnostics.py`, `plot_physical_corner.py` |
| Environment | execution | Puma | `OLMT_puma` |

- Trust: ledgers and artifacts are frozen trusted products. ABBY hourly and JERC daily
  campaign targets are built at preflight and hashed then; they have no Iter012 ledger.
  Characterization appendix may read Iter011/012/014 summaries; they are not Iter015 matrix
  leaves.
- Locked exception `site_hybrid_pool_reuse_v1`: one hybrid pool per site is reused across
  that site’s six configs. Walker selection uses the site pool; MCMC uses the campaign
  resolution. Pool target SHA and campaign target SHA may differ when resolution ≠ ledger
  resolution. They must match for ABBY daily and JERC hourly. Recorded and fail-closed.

### Bounded scope, work units, and exclusions

- Matrix: ABBY and JERC separately; hourly and daily; DEMove `0.50 / 0.75 / 1.00`; seeds
  `9009 / 9010 / 9011`; 64 walkers × 8,000 steps; checkpoints every 2,000; 80% DEMove /
  20% DESnookerMove; 16 workers; 14 physical parameters + fitted `sigma_SR`. Daily
  likelihood: complete-day map, 24 valid hourly pairs/date, mean the same indices, fitted
  `sigma_SR` with no `sqrt(24)`.
- Initialization: rebuild `hybrid_high_l_maximin` (`high_l_quantile=0.90`) from the frozen
  site ledger. No new Sobol/L-BFGS search. JERC rebuilt pool must equal Iter014 hash
  `40ac807e…`; mismatch stops. Freeze the new ABBY hybrid pool hash after rebuild, before
  MCMC. Rerun all 36 leaves; do not reuse Iter014 chains.
- Work units (41 nominal scheduler tasks): 1 preflight; `pool_rebuild_abby` and
  `pool_rebuild_jerc`; 12 arrays × 3 seeds = 36 leaves
  `production_{abby,jerc}_{hourly,daily}_{0.50,0.75,1.00}_seed{9009,9010,9011}`; 1 analysis
  job; 1 handoff-validation job (logs only).
- Staging: preflight → both rebuilds (parallel) → identity freeze → all 12 production
  arrays unthrottled → analysis only after 36 `CAMPAIGN_PASS` → records → handoff
  validation → authorized closeout.
- Exclusions: TIM / Iter008/009/011 transferred starts; `rank_dominated`;
  `diversity_maximin` production; new search; 32k production; adaptive extension / early
  stop; joint ABBY+JERC; mixed-resolution targets; likelihood / DE-mixture / prior / bound /
  Jacobian / surrogate / observation changes; posterior promotion; W as a selection veto;
  `physical_corner_by_seed` or per-seed physical corners; separate `evaluation/` or
  `handoff_validation/` scratch trees; push.

### Acceptance gates and decision rule

- Integrity (hard): provenance/identity of locked deps; hybrid geometry (`cond ≤ 1e6`, full
  rank, 640 unique, nonzero spread); JERC rebuild hash; finite in-bound 8,000-step HDF/raw
  chains; synchronized checkpoints/metadata; daily-map provenance where used;
  `site_hybrid_pool_reuse_v1` recorded on every leaf; terminal accounting; complete
  analysis/plot/decision package; four-record agreement. Sampler outcomes are not integrity
  failures.
- Interpretability: a config is eligible only if all three seeds have finite
  `max_tau_change ≤ 0.20`.
- Core comparison metrics (Iter011, immutable): `mean_acceptance`, `saturation`,
  `min_steps_per_tau`, `abs_resid_lag24`, `sigma_upper_edge`,
  `max_cross_seed_width_fraction`.
- Healthy / material thresholds (Iter011, immutable): acceptance 0.20–0.50 (material 0.03);
  saturation ≤ 0.05 (material 0.10); steps/τ tier crossing at 20/50 or 20% relative; lag-24
  0.05; sigma-edge 0.20 unless both ≤ 0.10; width-fraction threshold crossing at 0.05.
  Paired matching-seed rule: all three seeds same sign, material median, no materially
  opposite seed.
- Reported, not used to veto: from `tools/fixed_length_mcmc_diagnostics.py`, normalized
  Wasserstein, rank-normalized split R̂, bulk/tail ESS, descriptive discard, and
  `fixed_length_inconclusive` labels. Skill (RMSE, R², KGE, bias) per seed and pooled for
  MAP, posterior median, and `elm_precal`. Skill cannot override MCMC diagnostics or the
  Iter011 rule.
- Decision (sites independent): integrity plus interpretability plus a unique non-dominated
  config that materially improves at least one core metric and worsens none.
  - `preferred_configuration_supported`: unique non-dominated eligible config that dominates
    `hourly/1.00`
  - `default_configuration_retained`: unique non-dominated eligible config is `hourly/1.00`
  - `inconclusive_metric_tradeoff`: multiple non-dominated configs
  - `inconclusive_no_unique_preference`: unique winner does not dominate `hourly/1.00`
  - `inconclusive_seed_instability`: no tau-stable eligible config, or winner is not
    tau-stable
- No posterior promotion. A supported config is evidence for a future production proposal
  only.
- Appendix (characterization only): Iter011 TIM six-config tables; Iter012 diversity
  `ABBY daily/0.75` and `JERC hourly/0.75`; Iter014 JERC hybrid `hourly/0.75`. Not matrix
  leaves.

### Site, resources, preflight, review, retry, cancellation, and stop

- Site: UArizona Puma; `development/hpc/puma.md`; account `chopinsong`; partition
  `standard`; env `OLMT_puma`.
- Preflight: 4 CPUs / 30 min (20 GB derived). Absolute-path imports; locked hashes; dry
  hybrid rebuild geometry both sites; daily-map smoke; walker-selection smoke; one finite
  likelihood eval per site × resolution; record `site_hybrid_pool_reuse_v1`. 4 CPUs is a
  justified lift from a 2 CPU / 10 GB draft: Iter012 preflight OOM’d at 10 GB.
- Review: independent read-only reviewer before compute-node preflight. `block` requires
  correction and re-review.
- Retry: one minimal preflight correction/rerun; one unchanged scheduler/resource retry per
  rebuild; at most six production recoveries total and one per leaf from compatible
  8,000-step state; one unchanged analysis retry; one unchanged handoff-validation retry.
  Application/code/schema/dependency/numerical/scientific/gate/scope failures stop for a
  revised package. Hard cap 52 tasks (41 + 11 retries).
- Cancellation: only recorded Iter015 job IDs. Proven universal pre-execution defect that
  would fail remaining work in the same locked round, or explicit user emergency.
  Configuration defect: cancel only that array. Isolated leaf failure does not cancel the
  matrix.
- Stop: terminal accounting of the locked set; every non-completion classified; analysis
  and gate evaluation done; four records agree; handoff validator passes; authorized
  closeout branch satisfied. Or: blocked failure, exhausted retries, or user stop.

### Expected evidence, artifacts, and record updates

Scratch root (create only this layout):
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter015/`

```text
preflight/
pool_rebuild/{abby,jerc}/
production/{abby,jerc}/{hourly,daily}_{0.50,0.75,1.00}/seed_{9009,9010,9011}/
analysis/
  {abby,jerc}/{hourly,daily}_{0.50,0.75,1.00}/
    parameter_overlay.png
    physical_corner.png
    mcmc_diagnostics.json
  aggregate_result.json
  site_decisions.json
  six_configuration_*.csv
  paired audits
  ITER015_REPORT.md
  accounting.csv
  handoff_validate.out/.err
```

- Per-seed production (already in each leaf): `plots/pdfs/<param>.png`,
  `plots/corner/corner_plot.png`, `plots/predictions/<SITE>/Predictions_SR_posterior.png`
  with `elm_precal`.
- Cross-seed plots (reusable tools only):
  - `tools/plot_init_cloud_overlay.py` → pool + 3-seed walker starts
  - `tools/plot_physical_corner.py` with `write_pooled=true`, `color_by_seed=false`,
    `write_per_seed=false` → one pooled `physical_corner.png`
  - `tools/fixed_length_mcmc_diagnostics.py` → per-seed and cross-seed MCMC metrics
- Git: `iterations/iter015.md`; `summaries/iter015/` compact tables/JSON/report/12
  overlay+corner PNGs; `ITERATION_SUMMARY.md`; `registry.csv`; `handoff/CURRENT.md`;
  `slurm/iter015/`. Chains stay on `/xdisk` (temporary, unbacked).

### Proposed consolidated kickoff package and runtime contract (pending approval)

| Field | Proposed value |
| --- | --- |
| Kickoff goal, finite work-unit count, stop | Execute Iter015 per `development/spinup_forcing_coupling/WORKFLOW.md`: authorized scaffolding, independent review, preflight, two hybrid rebuilds, 36 MCMC leaves, one analysis, records, handoff validation, authorized closeout. 41 nominal tasks, cap 52. Stop at the stop conditions above. Do not stop while jobs or closeout remain open. |
| HPC system and profile | Confirm: this session is UArizona Puma; `development/hpc/puma.md`; repo `/xdisk/chopinsong/tianyihu/elm-olmt`; account `chopinsong`; partition `standard`. |
| Output and storage | Exact root and layout above. Creation authorized only for that layout. `/xdisk` temporary/unbacked. |
| Locked dependencies, scope, exclusions, gates, decision | As in this plan. |
| Lifecycle authority | Prepare, independent review, preflight, submission, continuous monitoring, terminal accounting, analysis, durable records, handoff validation, and the closeout branch below. |
| Resources | Preflight 4 CPUs / 30 min; rebuild 8 CPUs / 2 h each; each leaf 16 CPUs / 4 h / 16 workers (80 GB derived); analysis 4 CPUs / 2 h; handoff validation 2 CPUs / 30 min. |
| Retry | As above. Application/code/schema/dependency/numerical/scientific/gate/scope changes require a revised package. |
| Cancellation | Recorded Iter015 IDs only; universal pre-execution defect or user emergency; config defect cancels only that array. |
| Outside-sandbox | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, and `job-limits`; `scancel` only for recorded Iter015 IDs under the cancellation conditions. |
| Closeout branch | Proposed: one local closeout commit after the handoff validator passes; no push. |

### Fresh consolidated kickoff-approval boundary

This planning-only proposal grants no initialization, scaffolding, repository Python,
scheduler, retry, cancellation, or commit authority for Iter015. Those require one approval
of the complete package, including HPC confirmation and the seven runtime-contract items
(outside-sandbox `sbatch` / monitoring / bounded `scancel`). Omitted items are declined.
Any later change to matrix, hashes, exception, gates, resources, or scope needs a revised
package.
<!-- ITER015_PLAN_END -->

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter014.md`, and `development/hpc/puma.md`.
2. Treat Iter014 as closed. The Iter015 package above is planning-only.
3. Initialize a successor only after one approval of that complete consolidated kickoff
   package.

## Artifact References

- Current report: `development/spinup_forcing_coupling/iterations/iter014.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter014/`
- Canonical scripts: `development/spinup_forcing_coupling/slurm/iter014/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014`
