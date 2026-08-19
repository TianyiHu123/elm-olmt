# iter015 - hybrid-init Iter011 configuration matrix at ABBY and JERC

Closeout identity: Iteration ID `iter015`; Status `completed`; Work type `implementation`; Objective `hybrid-init Iter011 configuration matrix at ABBY and JERC`; Bounded scope `1 preflight; 2 hybrid rebuilds; 36 64x8000 leaves; 1 analysis; 1 handoff validation; user-directed ELM-precal plot makeup`; Overall acceptance result `pass`; Decision `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`

## Status

- Iteration ID: `iter015`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter015_<work_unit>`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-08-18T15:28:00-07:00`
- Closed: `2026-08-18T19:20:00-07:00`

## Finalized Plan

- Sequential ID and work type: `iter015`; `implementation`
- Evidence-derived objective and optional hypothesis: rerun the Iter011 site-specific
  resolution × DE-scale matrix at ABBY and JERC using the Iter014 hybrid
  initialization-to-MCMC pipeline, then recommend a configuration per site or call the
  site inconclusive. Hypothesis: Iter014 `hybrid_high_l_maximin` (q=0.90) start clouds,
  not TIM, now set walker geometry and seed-to-seed behavior.
- Proposed upstream dependencies and trust assumptions: locked Iter002 forcing, Iter012
  `drop21_corr080`, frozen Iter012 Revision1 site ledgers, Iter014 JERC hybrid pool
  identity, NEON v4 observations, reusable `tools/` plot/diagnostic CLIs, `OLMT_puma`.
- Bounded scope, work units, and exclusions: 1 preflight, 2 hybrid rebuilds, 36 MCMC
  leaves, 1 analysis, 1 handoff validation; no TIM, no new search, no `rank_dominated`,
  no 32k production, no posterior promotion, no push.
- Tentative acceptance gates and decision rule: Iter011 paired non-domination with
  reported W/R̂/ESS; sites independent.
- Proposed site and resource envelope: Puma `chopinsong`/`standard`; 41 nominal / 52 cap.
- Expected evidence, artifacts, and record updates: collapsed `analysis/` tree plus Git
  summaries and four-record closeout.
- Fresh consolidated kickoff-approval boundary: approved `2026-08-18T15:28:00-07:00`.

The complete planning text is the `ITER015_PLAN_BEGIN` block copied from closed Iter014
into this report's kickoff package. Gates are immutable after this approval.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `approves the complete package`; `2026-08-18T15:28:00-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Execute Iter015 per `development/spinup_forcing_coupling/WORKFLOW.md` through authorized closeout. 41 nominal tasks, cap 52. Stop after terminal accounting, analysis, four-record validation, and the authorized closeout commit. |
| Confirmed HPC system and site profile | UArizona Puma; `development/hpc/puma.md`; host `junonia.hpc.arizona.edu`; repo `/xdisk/chopinsong/tianyihu/elm-olmt`; account `chopinsong`; partition `standard` |
| Approved output and storage policy | `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter015/` with `preflight/`, `pool_rebuild/{abby,jerc}/`, `production/{abby,jerc}/{hourly,daily}_{0.50,0.75,1.00}/seed_{9009,9010,9011}/`, `analysis/`; `/xdisk` temporary/unbacked |
| Locked dependencies, scope, exclusions, gates, and decision rule | hybrid q=0.90; `site_hybrid_pool_reuse_v1`; 36×`64x8000`; Iter011 decision rule; JERC pool must equal `40ac807e…` |
| Lifecycle authority | Prepare, independent review, preflight, submission, continuous monitoring, terminal accounting, analysis, durable records, handoff validation, one local closeout commit |
| Resources and retry boundaries | Preflight 4 CPUs / 30 min; rebuild 8 CPUs / 2 h; leaf 16 CPUs / 4 h; analysis 4 CPUs / 2 h; handoff 2 CPUs / 30 min. One preflight correction; one rebuild retry each; ≤6 leaf recoveries; one analysis retry; one handoff retry |
| Cancellation scope | Recorded Iter015 job IDs only; universal pre-execution defect or user emergency; config defect cancels only that array/leaf group |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; `scancel` only for recorded Iter015 IDs under the cancellation conditions |
| Closeout branch | One local closeout commit after handoff validation; no push |

## Upstream Dependencies and Source Lock

| Dependency | Role | Path | Version/schema | Size/hash | Trust and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Iter002 forcing SR | coupled likelihood | `.../iter002_release/surrogate_forcing/forcing_surrogate_iter002_sr.pkl` | trusted release | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` | prior campaigns |
| Spinup `drop21_corr080` | coupled spinup | `.../spinup_surrogate_iter012_drop21_corr080.pkl` | trusted release | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` | prior campaigns |
| ABBY Iter012 Revision1 ledger | hybrid rebuild input | `.../revision1/initialization/abby/artifacts/candidate_ledger.npz` | Iter012 Revision1 | `ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b` | frozen ledger |
| JERC Iter012 Revision1 ledger | hybrid rebuild input | `.../revision1/initialization/jerc/artifacts/candidate_ledger.npz` | Iter012 Revision1 | `25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d` | Iter014 locked |
| Iter014 JERC hybrid pool | JERC rebuild identity | `.../iter014/pool_rebuild/hybrid_high_l_maximin/artifacts/candidate_pool.npz` | Iter014 rebuild | `40ac807e17803316b1200b7caa316d2ee45dde3a82fa1570345b3da4e282e4df` | must reproduce |
| ABBY daily target | ledger-resolution target | Iter012 canonical | Iter012 | `bf9ade8b68bf7179cdb5c5712682dd1c343d510749efd7041cf0414ec4773bbd` | preflight |
| JERC hourly target | ledger-resolution target | Iter012/014 canonical | Iter012 | `26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196` | preflight |
| ABBY NEON v4 obs | likelihood obs | eval v4 | site obs | `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2` | prior campaigns |
| JERC NEON v4 obs | likelihood obs | eval v4 | site obs | `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` | prior campaigns |

- Repository commit: `4c83d7d25091ee290055190e63391670be764797`
- Bounded source manifest: `/xdisk/.../iter015/preflight/source_manifest.sha256` (`38ce1686314c84177f48c34c8eda00687b2b5b0fb8faf69fefbe3db3c3ff78b9`); working tree includes uncommitted `site_hybrid_pool_reuse_v1` engine/CLI and `slurm/iter015/` until closeout
- Dependency manifest: `a331654576331ee79e8617122269e90c91a010fc7527fbe8c2be786950f98d6a`
- Submission scaffold: `b9877ec847405bc9a7e025b7dcff1a81a9979687c909b694ea743dec658ba668`
- Environment identity: `OLMT_puma` / micromamba `2.0.2-2`

## Acceptance Gates and Decision Rule

- Required completeness: preflight pass; both hybrid rebuilds; 36 `CAMPAIGN_PASS` leaves; analysis package; handoff validation
- Acceptance gates: integrity/provenance; hybrid geometry; JERC rebuild hash; Iter011 interpretability and paired non-domination
- Decision rule: sites independent; `preferred_configuration_supported` / `default_configuration_retained` / `inconclusive_*`; W/R̂/ESS reported not veto; no posterior promotion
- Conditional comparative metrics: Iter011 core metrics and thresholds
- Changes requiring fresh authorization: matrix, hashes, exception, gates, resources, or scope

## Provenance and Job Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory and logs | Dependencies | Commit/source manifest | Job IDs | State | Retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| materialization | `materialize_iter015.sh` `456e521fe90db18a06bbf9f58581a350068016a5c0e4880dba825fb4ecda823d` | package identity `schema=spinup-forcing-coupling-iter015-package-v1` | `/xdisk/.../spinup_forcing_coupling_iter015/` | locked hashes | `4c83d7d` + source `38ce1686…` | none | materialized | 36 production submitters; 2 rebuilds; analysis + handoff in `analysis/` |
| preflight | `preflight_iter015.slurm` `88db43696d8cc28dcf224399c63c9b298c2482f85f03b2fe5a9fdf482fb48e38` | submitted copy byte-identical; config sha256 `9afaeb76731dd808286110ce6fad7e63a68c84e3bf3b6ce2aec98fa1ccab9ad5` | `.../preflight/`; logs `preflight_23589106.{out,err}` | source+dependency manifests | same | `23589106` | COMPLETED `0:0` `00:05:04` MaxRSS 12.86 GB | `PREFLIGHT_PASS` |
| pool_rebuild_abby | `rebuild_pool_iter015.slurm` `6986ccf465fe1229088958e20bed395c0fbf361ff3829293d043ad52f2656c83` | submitted copy byte-identical | `.../pool_rebuild/abby/` | frozen ABBY ledger | same | `23589146` | COMPLETED `0:0` `00:02:14`; pool `3627bb1d…` frozen | attempt 1 |
| pool_rebuild_jerc | `rebuild_pool_iter015.slurm` `6986ccf465fe1229088958e20bed395c0fbf361ff3829293d043ad52f2656c83` | submitted copy; `EXPECTED_POOL_SHA256=40ac807e…` | `.../pool_rebuild/jerc/` | frozen JERC ledger | same | `23589147` | COMPLETED `0:0` `00:02:02`; pool `40ac807e…` matched Iter014 | attempt 1 |
| 36 production leaves | `production_iter015.slurm` `9b7e5524547010aa140e70d3cf57e291e6b9ed3ad187001e0f077b028c9a2ca8` | submitted copies byte-identical; `--pool-reuse-policy site_hybrid_pool_reuse_v1` | `.../production/{site}/{res}_{scale}/seed_{seed}/` | site hybrid pool | same | ABBY `23589174-23589191`; JERC `23589195-23589212` | all 36 COMPLETED `0:0` `CAMPAIGN_PASS` | no recoveries |
| elm_precal_replot | `replot_elm_precal_iter015.slurm` | `analysis/replot/`; user-directed makeup | overlap-aligned `case.output['SR']` mean | same | `23589330` | COMPLETED `0:0` `00:23:16`; 36 figures + skill rows | not in locked source manifest |
| analysis | `analyze_iter015.slurm` `904c503fcb800d2a6ccd2d0ba78539800d2b4d583409a886ba8cb29933f983cd` | submitted copy byte-identical | `.../analysis/` | 36 `CAMPAIGN_PASS` | same | `23589325` FAILED `1:0`; `23589339` COMPLETED `0:0` `00:21:21` | first failed missing `elm_precal`; second after makeup |
| handoff_validation | `validate_iter015_handoff.slurm` `f0ba6827843514a106a72c24e7cd856439f7b53a82696c33700d1a09ad067fd2` | identity-checked equivalent of `submit_handoff.sh` via `submit_handoff_after_analysis.sh` (receipt-name collision with analysis) | `.../analysis/` | four records + accounting | same | `23589486` | COMPLETED `0:0` `00:00:22`; `ITER015_HANDOFF_VALIDATE_PASS` | attempt 1 |

## Independent Read-Only Review

- Reviewer: independent `generalPurpose` agent `de24b8ac-bc61-41cc-b71f-6910f2bdc39e`; read-only; no edits or jobs
- Reviewed source hash: source manifest `38ce1686314c84177f48c34c8eda00687b2b5b0fb8faf69fefbe3db3c3ff78b9`; HEAD `4c83d7d25091ee290055190e63391670be764797`
- Outcome: `pass_with_concerns`
- Findings and primary-agent response:
  1. Analysis does not re-compare saved daily maps to a rebuilt target. Production already requires `daily_index_maps.json` for daily leaves and writes the campaign maps; preflight locks ABBY daily target `bf9ade8b…`. Accepted as defense-in-depth, not a missing production flag. No rematerialization.
  2. Lag-24 masks non-finite MAP predictions and does not re-check MAP logp. Iter015 still computes hourly MAP residual lag-24; a fully non-finite prediction fails the residual-size/std gate. Production already reevaluates selected walkers. Accepted. No rematerialization.
- Residual noted risks (not blocking): freeze ABBY pool hash after rebuild; JERC pool identity is a runtime gate; analysis `CAMPAIGN_PASS` counts matching `.out` files; overwrite refuse if `production_result.json` exists without banner.

## Execution and Diagnostics

- Static validation: `bash -n` on Iter015 shell/Slurm scripts and `python3 -m py_compile` on pipeline, CLI, Iter015 Python, and reusable plot tools passed before materialization
- Preflight: `23589106` COMPLETED `0:0` `00:05:04`; `PREFLIGHT_PASS`; targets ABBY daily `bf9ade8b…` and JERC hourly `26e5caa0…` matched; reuse checks matched ledger vs campaign resolutions
- Exact submission commands: preflight `./submit.sh` → `23589106`; rebuilds `23589146`/`23589147`; 36 production leaves `23589174-23589191` and `23589195-23589212`; makeup `23589330`; analysis `23589325` then `23589339`
- Job identity checks: all recorded submissions matched contracted job names, account `chopinsong`, partition `standard`, CPU/time, workdir, stdin `/dev/null`
- Queue and terminal accounting: 41 official accounting rows (including one FAILED analysis); makeup addendum `analysis/replot/makeup_accounting.csv`
- Resource diagnostics: production wall ~50–85 min; makeup 12.4 GB / 40 GB; analysis 9.86 GB / 20 GB
- Failure, rejection, retry, or cancellation evidence: analysis `23589325` FAILED `1:0` missing `elm_precal` because coupled plots compared full-forcing ELM (61320) to overlap predictions (ABBY 26280, JERC 52560). Classified `application_gate`. User-directed makeup `23589330` aligned the ELM ensemble mean onto overlap indices, replotted all 36 `Predictions_SR_posterior.png` figures (originals saved as `.pre_elm_makeup.png`), and wrote `elm_precal` skill rows. Analysis then `23589339` COMPLETED. Canonical `submit_handoff.sh` shares analysis receipt names, so handoff used identity-checked `submit_handoff_after_analysis.sh` writing `handoff_submission_receipt_1.env`. Handoff `23589486` COMPLETED `0:0` `00:00:22`; `ITER015_HANDOFF_VALIDATE_PASS leaves=36 ABBY=inconclusive_seed_instability JERC=inconclusive_seed_instability`.

## Validation, Evaluation, and Decision

| Work unit | Complete and eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| preflight | yes | `PREFLIGHT_PASS`; locked target hashes | pass | reuse checks matched ledger vs campaign resolutions |
| pool rebuilds | yes | ABBY pool `3627bb1d…`; JERC `40ac807e…` | pass | JERC identity matched Iter014 |
| 36 MCMC leaves | yes | 36 `CAMPAIGN_PASS` | pass | no recoveries |
| ELM-precal makeup | yes | 36 `REPLOT_PASS`; ELM RMSE ABBY `6.6896`, JERC `1.5752` | pass | user-directed figure/skill repair after overlap-length skip |
| analysis | yes after makeup | `ANALYSIS_PASS`; both sites `inconclusive_seed_instability` | pass | Iter011 rule applied; no posterior promotion |

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `ABBY=inconclusive_seed_instability; JERC=inconclusive_seed_instability`; no configuration preferred; no posterior promotion
- Limitations: 64×8000 hybrid starts remain seed-unstable; ABBY unique non-dominated `daily/0.50` is not tau-eligible (`max_tau_change > 0.20`); JERC has no tau-eligible configuration; W/R̂/ESS are reported not veto (R̂/ESS fields null in aggregate); `/xdisk` is temporary/unbacked; coupled `case.output` must be overlap-aligned for ELM precal overlays
- Next action: planning-only Iter016 equifinal-ensemble proposal below; discuss and lock kickoff package before any execution

## Proposed Next-Iteration Plan (Planning Only)

This is planning-only. Do not initialize, scaffold, or submit until a fresh consolidated kickoff approval.

<!-- ITER016_PLAN_BEGIN -->
## Proposed Iter016 plan - multi-seed equifinal parameter ensemble for operational SR use

- Sequential ID: `iter016`
- Status: `not_initialized`
- Work type: `implementation`
- Run slug: `spinup_forcing_coupling_iter016_<work_unit>`

### Evidence-derived objective and hypothesis

- Objective: define and characterize a **multi-seed equifinal parameter ensemble** for operational SR use at ABBY and JERC. Treat Iter015 hybrid `64×8000` chains as **mode-discovery evidence**, not as a calibrated posterior. Publish one representative parameter set per retained seed/mode, plus local cloud geometry and an SR predictive envelope across modes.
- Hypothesis: JERC physical-corner plots and cross-seed width (0.345–0.896 on hourly configs vs Iter011 TIM ~0.003) reflect **parameter equifinality for soil decomposition**: different `(k, rf)` clusters can yield nearly identical MAP SR (~0.667 RMSE) because SR alone does not identify the cascade. Multiple MCMC seeds are a practical way to discover distinct high-likelihood modes; an operational product should retain those modes as an ensemble rather than collapse to one vector.
- Evidence basis: Iter015 integrity passed but both sites are `inconclusive_seed_instability`; JERC has no tau-eligible configuration, R-hat ~2, bulk ESS ~250, and seed 9009 remains unhealthy on `hourly/0.75` (acceptance 0.089); MAP skill is flat across the six-configuration matrix; ABBY `daily/0.50` shows low cross-seed width (0.024) and may represent a single well-agreed mode rather than JERC-style seed separation.

### Upstream dependencies and trust assumptions

| Dependency | Role | Path | Identity |
| --- | --- | --- | --- |
| Iter015 production leaves | read-only mode-discovery evidence | `.../spinup_forcing_coupling_iter015/production/` | 36 `CAMPAIGN_PASS` leaves |
| Iter015 summaries and analysis | paired metrics, corners, skill | `summaries/iter015/`, scratch `analysis/` | aggregate + per-leaf diagnostics |
| Iter002 forcing SR | coupled likelihood reference | Iter002 release pickle | `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e` |
| Spinup `drop21_corr080` | coupled spinup | Iter012 spinup release | `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023` |
| Iter015 frozen hybrid pools | provenance for walker geometry | ABBY `3627bb1d…`; JERC `40ac807e…` | Iter015 rebuild hashes |
| NEON v4 observations | SR target | eval v4 | ABBY `e5f7b679…`; JERC `a5507878…` |

### Bounded scope, work units, and exclusions

Proposed work sequence (planning only; exact work units to be locked at kickoff):

1. **Do not operationalize parameters from Iter015 8k chains as a calibrated posterior.** Chains remain discovery evidence under incomplete mixing.
2. **Treat SR as the operational target and parameters as a set.** The deliverable is a documented equifinal ensemble and SR predictive envelope, not a single “best” vector per site.
3. **Build a per-site mode inventory from existing multi-seed runs.** For each site and locked operational configuration (to be chosen at kickoff; JERC evidence points to hourly hybrid; ABBY TBD), retain one representative parameter set per healthy seed (MAP or documented local representative) plus the associated local cloud from post-burn samples.
4. **Apply explicit seed-health gates before retention.** Exclude seeds with clearly unhealthy sampler behavior (e.g. JERC 9009 on `hourly/0.75`: acceptance 0.089, tau-change 0.548). Document exclusion criteria in the kickoff package.
5. **Test claimed equifinality before labeling a mode physical.** Require near-equal log-posterior and SR skill across retained modes, parameter separation in decomposition space, and either cross-seed recurrence or confirmation that a mode is not a single-short-chain artifact. Modes failing these tests remain “candidate modes under incomplete mixing.”
6. **Within-seed clustering is diagnostic only, not the primary product generator.** If clustering is used at all, apply it to **pooled post-burn samples across seeds** to name modes; do not emit separate operational products from within-seed clusters by default.
7. **If unique parameters are required later**, that is out of scope for this line unless additional constraints (stocks, other fluxes, tighter priors) are added in a separate iteration.

Tentative work units: mode-inventory analysis on Iter015 artifacts; equifinality and seed-health audit; ensemble manifest authoring; SR envelope plots; handoff validation. Optional bounded re-run only if kickoff proves existing leaves insufficient for mode labeling.

Exclusions: no TIM revert; no new search; no `rank_dominated`; no 36-leaf matrix rerun; no within-seed clustering as primary operational product; no posterior promotion; no claim of unique soil-decomposition parameters from SR alone; no reuse of Iter015 8k chains as fully mixed posterior evidence without explicit kickoff language.

### Tentative acceptance gates and decision rule

- Integrity: reproducible mode inventory from Iter015 artifacts; overlap-aligned ELM precal on any replotted SR figures.
- Operational gates: each retained mode documents MAP (or representative), log-posterior, SR skill vs ELM precal, and local cloud stats; excluded seeds have recorded health rationale; equifinality claims are either supported or explicitly downgraded to “candidate under incomplete mixing.”
- Decision rule (tentative): `ensemble_supported` if at least two healthy, SR-equivalent modes are documented per site; `partial_ensemble` if only one healthy mode survives gates; `inconclusive` if modes cannot be separated from mixing artifacts. This replaces the Iter011 configuration-selection rule for this iteration.

### Proposed site and resource envelope

- Primary path: **offline analysis** on existing Iter015 scratch and Git summaries; Puma not required unless kickoff adds validation reruns.
- If validation reruns are added: Puma `chopinsong`/`standard`; `OLMT_puma` / micromamba `2.0.2-2`; scope locked at kickoff.
- Retry/cancellation: standard bounded analysis retry; no large matrix unless explicitly approved.

### Expected evidence, artifacts, and record updates

- Git summaries under `summaries/iter016/`: per-site mode inventory, equifinality audit, seed-health exclusions, SR predictive envelope, ensemble manifest schema.
- Optional scratch under `spinup_forcing_coupling_iter016/` if kickoff adds reruns.
- Records: `iterations/iter016.md`, `ITERATION_SUMMARY.md`, `registry.csv`, `handoff/CURRENT.md`.

### Fresh consolidated kickoff-approval boundary

Planning only. Iter016 remains `not_initialized` until the user approves a complete consolidated kickoff package. Detailed operational configuration choice, seed-health thresholds, and ensemble schema will be discussed and locked at kickoff.
<!-- ITER016_PLAN_END -->

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter015/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Four-record validator identity, command, output, and passing result recorded
- [x] No job is active or unaccounted and every failure is classified
- [x] Authorized closeout branch satisfied: one verified commit or `validated_uncommitted`
