# Spinup-Forcing Coupling Iteration Summary

Append one immutable section for each closed iteration. Each entry must include objective, locked
settings, quantitative evidence, gate outcome, and conclusion, and must agree with the iteration
report, `registry.csv`, and `handoff/CURRENT.md` on iteration ID, status, work type, objective,
bounded scope, overall acceptance result, and decision. Preserve prior entries.

## iter001 — Historical Forcing-Surrogate Offline Baseline

- Closed at: `2026-08-03T14:52:55-07:00`
- Status: `completed`
- Work type: `implementation`
- Summary path: `development/spinup_forcing_coupling/summaries/iter001`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Objective

Establish a reproducible nine-site historical forcing-surrogate offline baseline for `SR` before
coupling to the spinup surrogate. Registry/handoff label: Historical nine-site SR forcing-surrogate
offline baseline.

### Locked settings

- Cases: nine local pickles
  `{ABBY,JERC,OSBS,SOAP,RMNP,TALL,TEAK,WREF,YELL}_ppe6_I20TRCNPRDCTCBC`
- Target / split: `SR`; `random_time_window`; train fraction `0.8`
- Seeds: pilot `10001`; production `10001-10100` (exactly 100 eligible)
- Model controls: historical quick grid; three-fold CV; 12 workers at kickoff, amended to 4 workers
  for the 150 GB pilot/production path; complete declared 34-feature schema; direct forcing-output
  layout; pooled and per-site metrics; eight-repeat pooled permutation importance
- Site / resources: `development/hpc/puma.md`; Puma `standard` / `chopinsong`; preflight
  1 CPU / 5 GB / 15 min; amended pilot and replacement production 150 GB / 4–6 h / `N_JOBS=4`;
  aggregation 1 CPU / 5 GB / 1 h
- Exclusions: coupling; saved-artifact inference validation; feature selection; extra tuning;
  accuracy-driven retraining; post-result gate revision; no predictive-accuracy threshold
- Provenance: source manifest
  `1f71df1bf801b9fec152acdca063204554fbfe4fbb1d3d1562204d2bb10be7a6`; dependency manifest
  `e718a00fcccb361c5e70ca89dc51b558aa7dc7611d4e198ef31b357ca08fb1c9`; production config
  `ef9b837bcdeb85ea96438ac6e9321a37623aa13ac9156d9ed96d5c942c104246`; repository commit
  `2648998d4ceb08ecf72859a7d5200c0e3a5eb41d`
- Bounded scope label: Nine sites; SR; random_time_window; seeds 10001-10100; pooled/per-site
  metrics; eight-repeat pooled permutation importance; no coupling or saved-artifact inference

### Quantitative evidence

- Preflight `23467631`, composite pilot (`23473876` + validation `23475958`), and aggregation
  `23489654` all `COMPLETED 0:0`
- First production array `23476014`: leaves 1–15 `OUT_OF_MEMORY`; remaining cancelled under
  universal-defect authority; classified historical evidence
- Replacement production array `23476164`: all 100 leaves `COMPLETED 0:0`; exact-100 eligibility
  passed
- Aggregate SHA-256
  `b75510b4f1fc64109d5be942e93d4af1662bd1c7a2a07c565f065245ce69f0a3`; aggregate-validation SHA-256
  `63a0b23bf9337c762e4d6583eac4ce4ac67efc01ba904847a71666c6b6fc9611`
- Pooled overfitting warning fraction `0.0`
- Pooled test R2 mean/median `0.945275` / `0.945557`
- Pooled test RMSE mean/median `0.210745` / `0.209810`
- Pooled R2 gap mean/median `0.012502` / `0.012155`
- Pooled RMSE ratio mean/median `1.254273` / `1.244005`
- Top importance by mean held-out RMSE increase: `TOTSOMN`, `k_s4`, `FSDS`, `FSDS_anom_30d`,
  `rf_s3s4`

### Gate outcome

- Overall acceptance result: `pass`
- Work-unit gates: preflight, pilot (composite correction), production (replacement array), and
  aggregation all `pass`
- Functional/data-integrity gates only; predictive scores are characterization, not pass/fail
  thresholds

### Conclusion

Technical offline baseline validated; predictive quality characterized; coupling readiness not
established. Limitations: no saved-artifact inference validation; `/xdisk` retention is temporary
and unbacked. Next state: no next iteration is proposed.


## iter002 — Identity-Locked Forcing-Surrogate-v1 Release

- Closed at: `2026-08-05T11:31:01-0700`
- Status: `completed`
- Work type: `implementation`
- Summary path: `development/spinup_forcing_coupling/summaries/iter002`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Objective

Identity-locked forcing-surrogate-v1 full-data release with inference validation

### Locked settings

- Cases: nine sites; target `SR`; complete 34-feature Iter001 schema; quick grid; `N_JOBS=4`
- Amended release: full-data refit only; Iter001 100-seed aggregate baseline comparison is
  characterization only (not a gate); full-data 8-repeat in-sample importance
- Validate: manifest/fresh-process/negative gates/batch predict + ABBY operational predict
  (draw seed `10001`, spinup member 1)
- Site / resources: `development/hpc/puma.md`; preflight 1 CPU/5 GB/15 min; release 120 GB/10 h;
  validate 10 CPUs/~50 GB/1 h
- Provenance: release-time source-manifest file SHA-256 `ea7ec3f35b452c78b21ac710079004dcd083867c95d4262342c6bc4a8bf46ab2`; memmap
  `01ef038fc41122b65fd40fe06fa2ee31ed9ffd5a16269cbb7a2880f7d4b5b7f6`; layout `a6ea4151c5be02e86d50dd8767cd579b8804c94803162f0246797487dd2dd2b0`; repository parent `ce2e252fefa1a200527d5cb4ecd20b62d6006f1c`
- Bounded scope: Nine sites; SR; full-data forcing-surrogate-v1; 8-repeat full-data importance; inference validation; ABBY operational predict; no live coupling

### Quantitative evidence

- Preflight `23491474` `COMPLETED 0:0`; amended release `23501708` `COMPLETED 0:0` (05:45:37;
  MaxRSS 95.31/120 GB); authoritative validate `23507103` `COMPLETED 0:0`
- Artifact SHA-256 `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; inference summary `44e493d65b770aedec83ef2d75978c2ff7857f49fe0c79550df848c87af3c20e`
- Full-data in-sample r2=`0.957720` rmse=`0.170592`
- Top importance (mean RMSE increase): `TOTSOMN`, `FSDS`, `k_s4`, `FSDS_anom_30d`, `rf_s3s4`

### Gate outcome

- Overall acceptance result: `pass`
- Work-unit gates: preflight pass; historical release fail (classified); amended release pass;
  validate pass
- Decision: Standalone forcing-surrogate-v1 artifact identity-locked and inference-validated; full-data importance characterized; live coupling readiness not established

### Conclusion

Standalone forcing-surrogate-v1 artifact identity-locked and inference-validated; full-data importance characterized; live coupling readiness not established Limitations: temporary `/xdisk` retention; no live coupling in Iter002. Next state:
Proposed iteration: `iter003` (planning only; dual-variant coupled spinup→forcing ELM comparison with MCMC-ready CLI).


## iter003 — Coupled Spinup–Forcing Dual-Variant ELM Comparison

- Closed at: `2026-08-05T20:30:09-0700`
- Status: `completed`
- Work type: `implementation`
- Summary path: `development/spinup_forcing_coupling/summaries/iter003`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Objective

Coupled spinup–forcing dual-variant ELM PPE SR comparison

### Locked settings

- Cases: nine sites `{ABBY,JERC,OSBS,SOAP,RMNP,TALL,TEAK,WREF,YELL}`; 100 PPE members;
  both spinup variants `drop32` and `drop21_corr080`; target `SR`
- Ladder: preflight → ABBY×5×both pilot (timeseries ON) → 9×100×both full (timeseries OFF)
  → validate/closeout; MCMC-ready CLI `predict_coupled_surrogate.py`; ELM compare; no skill
  floor
- Site / resources: `development/hpc/puma.md`; preflight 1 CPU/5 GB/30 min; pilot 60 GB/4 h;
  full array `1-9` 80 GB/8 h; validate 1 CPU/5 GB/1 h
- Provenance: forcing
  `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32
  `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; repository parent
  `7b70aa42d8d6b351255266690adcc0d97871d268`
- Bounded scope: Nine sites; both spinup variants; ABBY×5 pilot timeseries ON; 9×100×both full timeseries OFF; MCMC-ready CLI; ELM compare; no skill floor

### Quantitative evidence

- Preflight authoritative `23510375` `COMPLETED 0:0` (historical fail `23510366` classified);
  pilot authoritative `23510419` `COMPLETED 0:0` (historical fail `23510415` classified);
  full array `23510434` leaves 1–9 all `COMPLETED 0:0`; validate `23510503` `COMPLETED 0:0`
- Characterization (site-median of per-site member-medians): `drop32` median R²≈0.579
  KGE≈0.821; `drop21_corr080` median R²≈0.651 KGE≈0.816; Pearson r high (~0.93); negative
  R² at some sites (ABBY, WREF)
- Compact products: `iter003_site_metric_medians.csv`; `iter003_accounting.csv`;
  `iter003_decision.json`

### Gate outcome

- Overall acceptance result: `pass`
- Work-unit gates: preflight pass; pilot pass; full pass; validate pass (historical preflight
  and pilot fails classified under one-retry contract)
- Decision: Executable dual-variant coupled path demonstrated with ELM comparison evidence; predictive scores characterized; production MCMC readiness not established

### Conclusion

Executable dual-variant coupled path demonstrated with ELM comparison evidence; predictive scores characterized; production MCMC readiness not established. Limitations: temporary `/xdisk` retention; no skill floor; some sites negative R²; MCMC campaign not run. Next state:
Proposed iteration: `iter004` (planning only; MCMC integration of `predict_coupled_sr` primitive; no campaign).


## iter004 — Offline Forcing versus Coupled Dual-Variant Comparison

- Closed at: `2026-08-06T17:59:11-0700`
- Status: `completed`
- Work type: `implementation`
- Summary path: `development/spinup_forcing_coupling/summaries/iter004`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Objective

Offline forcing versus coupled dual-variant ELM PPE SR comparison

### Locked settings

- Cases: nine sites; 100 PPE members; arms offline (forcing-v1 + ELM restart), coupled
  `drop32`, coupled `drop21_corr080`; target `SR`
- Ladder: preflight → full array `1-9` timeseries ON → validate/closeout; four-figure plot
  package; no skill floor; MCMC deferred to `iter005`
- Site / resources: `development/hpc/puma.md`; preflight 2 CPUs / 30 min; full `--mem=20G` /
  4 h; validate 1 CPU / 1 h
- Provenance: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop32 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`; drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`;
  repository parent `6d8391443bbd0a2612e66e17c47414a896e2ab01`
- Bounded scope label: Nine sites; offline + drop32 + drop21_corr080; 9×100 timeseries ON; four-figure plot package; no skill floor

### Quantitative evidence

- Preflight `23515370` `COMPLETED 0:0`; full array `23515500` leaves 1–9 all `COMPLETED 0:0`;
  validate `23515820` `COMPLETED 0:0`
- Characterization (site-median of per-site member-medians): offline median R²≈0.850
  KGE≈0.862; drop32 median R²≈0.579 KGE≈0.821; drop21_corr080 median R²≈0.651 KGE≈0.816;
  Pearson r high (~0.93); coupled negative R² at ABBY and WREF
- Compact products: `iter004_site_metric_medians.csv`; `iter004_accounting.csv`;
  `iter004_decision.json`

### Gate outcome

- Overall acceptance result: `pass`
- Work-unit gates: preflight pass; full pass; validate pass
- Decision: Offline-versus-coupled comparison completed with metrics, timeseries, and plot package; predictive scores characterized; production MCMC readiness not established

### Conclusion

Offline-versus-coupled comparison completed with metrics, timeseries, and plot package; predictive scores characterized; production MCMC readiness not established. Limitations: temporary `/xdisk` retention; no skill floor; coupled lags offline;
MCMC campaign not run. Next state:
Proposed iteration: `iter005` (planning only; MCMC integration of `predict_coupled_sr`; no campaign).


## iter005 — Mean-Spinup Offline Baseline versus Iter004 Arms

- Closed at: `2026-08-06T19:42:02-0700`
- Status: `completed`
- Work type: `implementation`
- Summary path: `development/spinup_forcing_coupling/summaries/iter005`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Objective

Mean-spinup offline forcing baseline versus Iter004 arms

### Locked settings

- Cases: nine sites; 100 PPE members; new arm offline mean-spinup (forcing-v1 + site-mean
  ELM restart); Iter004 arms overlaid read-only; target `SR`
- Ladder: preflight → full array `1-9` timeseries ON → validate/closeout; two annotated
  plot types; joined medians CSV; no skill floor; MCMC deferred to `iter006`
- Site / resources: `development/hpc/puma.md`; preflight 2 CPUs / 30 min; full `--mem=20G` /
  4 h; validate 1 CPU / 1 h
- Provenance: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`;
  Iter004 reuse via `iter005_iter004_reuse.sha256`; repository parent
  `9a125ef3a703e1169e831f77a04636c344359024`
- Bounded scope: Nine sites; mean-spinup offline 9×100 timeseries ON; overlay Iter004 three arms; two annotated plot types; joined medians CSV; no skill floor

### Quantitative evidence

- Preflight `23516340` `COMPLETED 0:0`; full array `23516376` leaves 1–9 all `COMPLETED 0:0`;
  validate `23516504` `COMPLETED 0:0`
- Characterization (site-median of per-site member-medians): offline_mean_spinup median
  R²≈-1.894 KGE≈0.438; Iter004 offline median R²≈0.850 KGE≈0.862; drop32 median R²≈0.579
  KGE≈0.821; drop21_corr080 median R²≈0.651 KGE≈0.816; Pearson r high (~0.925) for
  mean-spinup
- Compact products: `iter005_site_metric_medians.csv`; `iter005_accounting.csv`;
  `iter005_decision.json`

### Gate outcome

- Overall acceptance result: `pass`
- Work-unit gates: preflight pass; full pass; validate pass
- Decision: Mean-spinup offline baseline compared with Iter004 arms under locked plot/summary contract; predictive scores characterized; production MCMC readiness not established

### Conclusion

Mean-spinup offline baseline compared with Iter004 arms under locked plot/summary contract; predictive scores characterized; production MCMC readiness not established. Limitations: temporary `/xdisk` retention; no skill floor; mean-spinup offline lags member-restart offline and coupled arms on R²/KGE; MCMC campaign not run. Next state:
Proposed iteration: `iter006` (planning only; MCMC integration of `predict_coupled_sr`; no campaign).

## iter006

- Closed at: `2026-08-06T21:11:23-0700`
- Status: `completed`
- Work type: `implementation`

### Objective

MCMC three-mode spinup wiring (mean / member-restart / coupled)

### Locked settings

- Modes: `mean_spinup`, `member_restart`, `coupled` via `--spinup-mode`; coupled variants
  `drop32` / `drop21_corr080` (default `drop21_corr080`); historical default mean-spinup
- Ladder: preflight → ABBY validate smoke (dry-run + <=10 likelihood evals/mode) → closeout;
  no production campaign
- Site / resources: `development/hpc/puma.md`; preflight 2 CPUs / 30 min; validate 1 CPU / 1 h
- Provenance: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`;
  drop32 `56bbd151103add74b5a0794e8d1bf4496c186d3a72e70b1b65c5ab247abd317e`;
  drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`;
  repository parent `542b7d3ce74bd3baa23c48b5b4638270be12cf86`
- Bounded scope: ABBY smoke; three MCMC spinup modes; coupled drop32/drop21_corr080; <=10 likelihood evals/mode; no production campaign

### Quantitative evidence

- Preflight `23516816` `COMPLETED 0:0` elapsed 00:00:34; MaxRSS ~2.47/10 GB
- Validate `23516840` `COMPLETED 0:0` elapsed 00:05:06; MaxRSS ~5.00/5 GB
- Smoke: 10 likelihood evals each for mean_spinup, member_restart, coupled; coupled drop32
  accept with 1 eval; missing-artifact negatives fail closed
- Compact products: `iter006_smoke_identity.json`; `iter006_accounting.csv`;
  `iter006_decision.json`
- Summary path: `development/spinup_forcing_coupling/summaries/iter006`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Gate outcome

- Overall acceptance result: `pass`
- Work-unit gates: preflight pass; validate pass
- Decision: MCMC can select and call locked coupling/offline primitives under each declared spinup mode; mean/member-restart paths still work; production campaign readiness not established

### Conclusion

MCMC can select and call locked coupling/offline primitives under each declared spinup mode; mean/member-restart paths still work; production campaign readiness not established. Limitations: temporary `/xdisk` retention; smoke obs fixture not NEON truth; validate near 5 GB ceiling; production campaign not run. Next state:
Proposed iteration: `iter007` (planning only; joint ABBY+JERC coupled/`drop21_corr080` SR MCMC; integrity-only gates).

## iter007

- Closed at: `2026-08-08T15:13:30-0700`
- Status: `completed`
- Work type: `implementation`

### Objective

Joint ABBY+JERC coupled/drop21_corr080 SR MCMC campaign

### Locked settings

- Cases: `ABBY_ppe6_I20TRCNPRDCTCBC`, `JERC_ppe6_I20TRCNPRDCTCBC`; mode coupled /
  `drop21_corr080`; vars `SR`; `--fit-error`; walkers×steps `64×500`
- Layout: flat campaign root (`best_params.txt`, `clm_params_best.nc`, `plots/`,
  `diagnostics/`); no `UQ_output/`
- Ladder: preflight → campaign → validate/closeout; integrity-only gates; one authorized
  resource retune; diagnostic-driven retune deferred
- Site / resources: `development/hpc/puma.md`; preflight 2 CPUs / ~10 GB / 30 min; campaign
  retuned 24 CPUs / ~120 GB / 12 h / `n_processes=16`; validate 2 CPUs / ~10 GB / 1 h
- Provenance: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`; drop21_corr080 `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`; obs ABBY `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2`;
  obs JERC `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f`; repository parent `4051e875bff93742bdf5ccfb69a94a9ce10468c1`
- Bounded scope: ABBY+JERC joint; coupled drop21_corr080; SR; 64x500; flat campaign layout; suggested diagnostics; integrity-only

### Quantitative evidence

- Preflight `23520801` `COMPLETED 0:0` elapsed 00:01:11; MaxRSS ~9.05/10 GB
- Campaign attempts: `23520817` TIMEOUT+OOM; `23523589` FAILED postprocess OOB;
  successful `23523645` `COMPLETED 0:0` elapsed 00:18:18; MaxRSS ~13.59/120 GB;
  `POSTPROCESS_FILTER kept=5120/5120`; mean acceptance 0.1197; approx ESS 93.8
- Validate `23523701` `COMPLETED 0:0` elapsed 00:00:11; `VALIDATE_PASS`
- Characterization: ABBY optimized_best RMSE 5.33 R² -3.12; JERC optimized_best RMSE 2.46
  R² -7.36; ABBY ΔlogL vs ELM-precal +1.42e5; JERC ΔlogL -4.47e7
- Compact products: `iter007_accounting.csv`; `iter007_decision.json`; skill/collocation/
  chain/posterior/delta_logL copies under `development/spinup_forcing_coupling/summaries/iter007`
- Summary path: `development/spinup_forcing_coupling/summaries/iter007`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Code bug / fix log (campaign)

- `23520817` TIMEOUT + OOM (16 CPUs / 80 GB / 12 h; mem 100%; CPU eff 0.07%; never
  `run_mcmc done`): emcee `Pool` pickled full ~GB ELM case objects into 16 workers. Fix:
  slim coupled arrays + `Pool(initializer=...)` in `coupled_surrogate.py` /
  `MCMC_forcing.py`; keep `n_processes=16`.
- `23523589` FAILED after `run_mcmc done` (24 CPUs / 120 GB; wall ~6 min; mem ~11 GB):
  OOB walkers retained because prior used a finite sentinel; postprocess hit
  `Parameters outside ensemble_pmin/pmax`. Fix: OOB → `-np.inf` and
  `POSTPROCESS_FILTER` (in-bounds + finite logp) before write/diagnostics in
  `MCMC_forcing.py`.
- `23523645` `CAMPAIGN_PASS` under the same sampler budget after both fixes
  (`POSTPROCESS_FILTER kept=5120/5120`).

### Campaign resource usage and recommended allocation (2-site)

| Job | Allocated | Wall | Memory used | CPU efficiency | Outcome |
| --- | --- | --- | --- | --- | --- |
| `23520817` | 16 CPUs / 80 GB / 12 h | 12:00:08 | 80.00 GB (100%) | 0.07% | TIMEOUT + OOM (pre-fix) |
| `23523589` | 24 CPUs / 120 GB / 12 h | 00:05:54 | 11.10 GB (9.3%) | 38.4% | MCMC OK; FAILED postprocess |
| `23523645` | 24 CPUs / 120 GB / 12 h | 00:18:18 | 13.59 GB (11.3%) | 20.4% | `CAMPAIGN_PASS` |

Recommended for the same 2-site shape (64×500, `n_processes=16`, after payload fix):
**16 CPUs / 32–40 GB / 1–2 h / 1 node**. The 24 CPU / 120 GB retune was oversized once the
pickle bug was fixed; do not re-request 80–120 GB unless slim payloads regress. Scale
walltime first when increasing `nsteps` or site count. Full detail:
`iterations/iter007.md` (Execution and Diagnostics).

### MCMC optimization summary report (campaign `23523645`)

Verdict: integrity pass for a joint ABBY+JERC coupled MCMC, but the fit is **not**
scientifically adequate. Optimization helps ABBY vs ELM-precal and hurts JERC; chain
mixing is weak. Posterior products are exploratory, not well-converged calibration.

#### Setup

- Mode: `--spinup-mode=coupled` / `drop21_corr080`; vars `SR`; shared parameter vector
  across ABBY+JERC; `--fit-error` on (`sigma_SR`)
- Sampler: 64 walkers × 500 steps; discard `nsteps//5` (=100), thin 5 → 5120 flat
  samples; 14 model parameters + 1 error parameter
- Collocation: ABBY 26 280 hrs (2019-01-01–2021-12-31); JERC 52 560 hrs
  (2018-01-01–2023-12-31); skill rows use valid obs masks (ABBY 26 264; JERC 51 882)
- Products: `best_params.txt`, `clm_params_best.nc`, `plots/{pdfs,corner,predictions}/`,
  `diagnostics/`; compact copies under `summaries/iter007/`

#### Model skill after optimization (vs NEON obs; characterization only)

| Site | Series | n | RMSE | Bias | R² | KGE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| ABBY | optimized_best | 26264 | **5.33** | **−4.74** | **−3.12** | **−0.15** |
| ABBY | elm_precal | 26264 | 6.69 | −6.21 | −5.48 | −0.27 |
| JERC | optimized_best | 51882 | 2.46 | +2.36 | −7.36 | −0.87 |
| JERC | elm_precal | 51882 | **1.58** | **+1.43** | **−2.42** | **−0.16** |

ΔlogL (optimized − ELM-precal): ABBY **+1.42×10⁵** (improved); JERC **−4.47×10⁷** (much worse).

Interpretation:

- Shared-parameter joint fit pulls toward ABBY and degrades JERC relative to ELM
  ensemble-mean precal on the collocated window.
- Absolute skill remains poor at both sites (negative R²/KGE): MCMC does not produce an
  obs-matching SR series.
- Residuals are large and highly autocorrelated (lag-1 ≈ 0.999 ABBY, ≈ 0.993 JERC) with
  opposite mean signs (ABBY ≈ −4.7; JERC ≈ +2.4) → systematic structure, not white noise.
- Fitted `sigma_SR` MAP ≈ 3.66 (prior upper ≈ 3.68): observation-error inflation absorbs
  mismatch rather than explaining SR with parameters alone.
- Prior-edge occupancy diagnostic reported 0 for all parameters under its threshold;
  several `rf_*` posteriors remain broad (weakly identified from SR alone). MAP≠mean for
  some rates (e.g. `k_l1` MAP 0.52 vs mean 1.23).

#### MCMC diagnostics (detailed)

Targets below are practical guidance for a **scientifically usable** stretch-move emcee
posterior under this workflow. They were **not** Iter007 acceptance gates (integrity only).

| Metric | Current reading | Implication | Target for a valid / usable MCMC optimization |
| --- | --- | --- | --- |
| Walkers × steps | 64 × 500 | Short production budget relative to measured τ | Enough that after burn-in, run length ≫ 50τ per chain and ESS is adequate (below); often 10³–10⁴+ steps once τ is known |
| Discard / thin | discard 100 (`nsteps//5`), thin 5 → 5120 flat | Fixed rule of thumb; not τ-adaptive | Discard ≳ 2–5τ (or until logp stable); thin ~τ/2 to τ; recompute after a pilot run |
| Mean acceptance fraction | **0.120** (min 0.044, max 0.186) | Proposals rarely accepted; chains mix slowly; some walkers nearly stuck | For emcee stretch move, commonly aim ~**0.2–0.5** (often ~0.25–0.4). Persistently ≪0.2 ⇒ step scale / prior / likelihood geometry issues or need longer adaptation |
| Mean / max autocorr time τ | **54.6 / 61.3** | Strong serial dependence; each walker yields few independent draws | Prefer stable τ estimate with run length ≳ **50τ** (ideally 100τ) before trusting τ or ESS |
| Steps / τ | ~500 / 55 ≈ **9** | Under-mixed: total length is only ~9 autocorrelation times | Target **≫ 50** (preferably ≥100) integrated steps per walker after reliable τ |
| Approx ESS | **~94** | ~94 effective samples for a **15-D** posterior → means/percentiles/predictive bands are noisy | Rule of thumb: **≳ few×10² to 10³+** ESS per parameter of interest (often **≳ 10× n_dim** as a floor; more for tight predictive intervals) |
| Flat samples kept | **5120 / 5120** in-bounds + finite logp | Prior/`POSTPROCESS_FILTER` fix worked; no OOB pollution in the successful run | Keep ≈ all post-burn thin samples in prior support; large discard of OOB samples ⇒ prior/likelihood bug |
| Log-prob / walker health | Acceptance spread 0.044–0.186; ESS low | Heterogeneous walker performance; posterior summaries not exchangeable with a well-mixed run | Walkers should have similar acceptance and overlapping traces; no large dead walkers; stable logp after burn-in |
| Residual lag-1 (skill side) | ≈ **0.999 / 0.993** | IID Gaussian likelihood badly misspecified; σ absorbs structure | For a well-specified likelihood, standardized residuals should be near-uncorrelated; else use correlated-error / robust / weighted likelihood |
| Site ΔlogL conflict | ABBY ≫ 0 vs ELM; JERC ≪ 0 | Joint shared params are not a single compromise that helps both sites | Valid multi-site calibration should not silently sacrifice one site; use weights, hierarchical offsets, or staged single-site then joint checks |
| `sigma_SR` vs prior | MAP near upper bound (~3.66 / ~3.68) | Error model saturated; parameter posterior may be compensating for structural bias | Prefer σ interior to prior with good residual diagnostics; bound-hitting σ ⇒ revisit model/obs/likelihood before trusting params |

Bottom line: the chain **ran and wrote integrity-valid products**, but acceptance, τ, steps/τ, and ESS indicate an **exploratory** posterior. Do not treat Iter007 MAP/mean/95% bands as converged scientific calibration.

#### Directions for MCMC improvement

1. **Mixing / budget** — Increase `nsteps` (and possibly walkers) from measured τ so length ≫ 50τ and ESS reaches O(10³)+ per parameter; retune discard/thin from a pilot. Walltime scales roughly with steps (~18 min baseline for 64×500 at 16 workers).
2. **Resolve site conflict** — Shared params fight (ABBY↑ / JERC↓). Consider site-weighted likelihood, hierarchical site offsets, leave-one-site checks, or separate-site posteriors before joint.
3. **Likelihood realism** — Homoscedastic independent-time `sigma_SR` mismatches lag-1≈1 residuals. Consider temporally correlated errors, robust likelihood, or downweighting dense hourly points.
4. **Identifiability** — Broad `rf_*` posteriors suggest weak constraint from SR alone; tighten priors, reduce free params, or add constraining variables if justified.
5. **Structural vs parametric** — Persistent negative R² and opposite site biases may be surrogate/coupling/obs issues not fixed by longer MCMC alone; use these diagnostics as the Iter008 baseline.
6. **Ops** — Same 2-site shape after pickle fix: **16 CPUs / 32–40 GB / 1–2 h**; scale walltime with `nsteps`, not memory.

### Gate outcome

- Overall acceptance result: `pass`
- Work-unit gates: preflight pass; campaign pass; validate pass
- Decision: Joint ABBY+JERC production MCMC campaign executed successfully through the locked coupled interface and wrote required products; diagnostic contents are characterization only; calibrated scientific adequacy not claimed

### Conclusion

Joint ABBY+JERC production MCMC campaign executed successfully through the locked coupled interface and wrote required products; diagnostic contents are characterization only; calibrated scientific adequacy not claimed. Limitations: temporary `/xdisk` retention; limited mixing (acceptance≈0.12,
ESS≈94); predictive skill poor vs obs; JERC optimized likelihood worse than ELM-precal;
no skill floors applied. See **MCMC optimization summary report** above for skill tables,
diagnostic targets, and improvement directions. Next state:
Proposed iteration: `iter008` (planning only; diagnostic-driven joint MCMC improvement under
locked coupled/`drop21_corr080` primitives).

## iter008 — Single-site ABBY and JERC coupled SR MCMC diagnostics

- Closed at: `2026-08-09T14:56:00-0700`
- Status: `completed`
- Work type: `implementation`
- Summary path: `development/spinup_forcing_coupling/summaries/iter008`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`

### Objective and bounded scope

Objective label: `Single-site ABBY and JERC coupled/drop21_corr080 SR MCMC diagnostic campaign`.
Bounded scope label: `ABBY and JERC separately; coupled drop21_corr080; SR; 64x4000; seed 8008; raw-chain diagnostics; integrity-only`.

Demonstrate reproducible, diagnostically interpretable single-site ABBY and JERC `SR` MCMC
results through the locked coupled `drop21_corr080` interface before further joint-site
calibration. The bounded scope was separate ABBY and JERC campaigns, `--fit-error`, 64 walkers
× 4,000 steps, seed 8008, 16 workers, retained raw chains, adaptive diagnostics, and
integrity-only acceptance; no scientific quality hard gate was applied.

### Locked settings and evidence

- Forcing artifact SHA-256: `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`.
- Spinup `drop21_corr080` artifact SHA-256:
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`.
- Preflight `23527081`: `COMPLETED 0:0`, `PREFLIGHT_PASS`; both-site collocation and ABBY
  32×20 smoke passed.
- ABBY `23527105`: `COMPLETED 0:0`, 00:24:50, `CAMPAIGN_PASS`; raw-chain SHA-256
  `5eef997b62fadc8d41505627fdfd11fa86b409573da6192383476a0aa78b5d87`.
- JERC `23527106`: `COMPLETED 0:0`, 00:49:39, `CAMPAIGN_PASS`; raw-chain SHA-256
  `34a70beadf021acbc8ddeca160c80cb2c3bbf9b4926a3665402b0cefeb08c080`.
- Validation `23527337`: `COMPLETED 0:0`, 00:00:24, `VALIDATE_PASS`; paired route
  `sampler-limited`.
- Comprehensive skill, raw-chain, route-selection, hypothesis, and next-experiment report:
  [`summaries/iter008/iter008_comprehensive_mcmc_report.md`](summaries/iter008/iter008_comprehensive_mcmc_report.md).

### Gate outcome and conclusion

- Overall acceptance: `pass` (integrity-only).
- Decision: `sampler-limited`.
- Both site chains have complete shape/provenance/checksum/standard-product evidence. The
  paired diagnostics characterize limited mixing and low effective sample behavior; they do
  not claim calibrated scientific adequacy. The comprehensive report concludes that neither
  chain is converged; JERC has a useful best-fit prediction while ABBY remains poor, and
  likelihood and ABBY-specific limitations require controlled follow-up after sampler repair.
  `/xdisk` retention remains temporary and unbacked.

## iter009 — ABBY and JERC sampler-geometry pilot

- Iteration ID: `iter009`
- Status: `completed`
- Work type: `implementation`
- Summary path: `development/spinup_forcing_coupling/summaries/iter009`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Objective: `ABBY and JERC sampler-geometry pilot`
- Bounded scope: `ABBY/JERC sampler-geometry pilot; B/T/I/M/TIM; 30 chains; 64x8000; seeds 9009-9011`
- Overall acceptance result: `pass`
- Decision: `investigate_multimodality_nonidentifiability_likelihood_or_model_structure`
- Next state: `No next iteration is proposed; any follow-up requires a new approved package to investigate multimodality, non-identifiability, likelihood discontinuity, or model structure.`

### Evidence and conclusion

- Dependencies: forcing `8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e`, spinup
  `1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023`, ABBY observations
  `e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2`, and JERC observations
  `a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f` all matched locks.
- Preflight `23538751`, initialization `23538764`, all 30 final campaign leaves, and final
  validation `23540912` completed `0:0`. The first validation `23540890` failed before
  evaluation from a missing repository import context; the re-reviewed v5 launcher retry passed.
- The immutable evaluator verified 30 complete 64x8000 dual-coordinate chains and emitted ten
  site-arm packages. No arm qualified. TIM had the strongest overlap screens (ABBY/JERC maximum
  split R-hat `1.0317`/`1.02137`; width fractions `0.000713`/`0.002603`) but did not meet every
  required criterion, so no least-bad arm was selected.
- The original 42-task cap was exceeded through explicitly user-approved exception attempts;
  final submitted count was 48. This is an integrity accounting exception, not silent cap
  satisfaction. Raw products remain on temporary, unbacked `/xdisk`.
- Comprehensive arm-by-arm diagnostic implications, conclusion logic, and proposed next
  experiments: [`summaries/iter009/ITER009_REPORT.md`](summaries/iter009/ITER009_REPORT.md).
## iter010 - TIM terminal-partition topology diagnosis (2026-08-12)

- Iteration ID: `iter010`
- Status: `completed`
- Work type: `implementation`
- Objective: `TIM terminal-partition topology diagnosis`
- Bounded scope: `Six immutable TIM chains; ABBY/JERC; seeds 9009-9011; terminal/rolling topology diagnostics; conditional prediction skip`
- Overall acceptance result: `pass`
- Decision: `ABBY and JERC two_basin_declined; forced terminal screen declined as evidence for two physical basins; replace the screen, reassess TIM/JERC, and route to ABBY proposal-scale Experiment 5`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter010`
- Accounting: preflight `23554607`, topology `23554935`, conditional prediction `23555136`, and
  finalize `23555187` all reached terminal `COMPLETED 0:0`; no retry or cancellation occurred.
- Evidence: all six source identity/provenance families passed; 32 figures, six metric archives,
  topology decisions/tables, source manifest, comprehensive report, and validated zero-evaluation
  conditional skip are complete.
- Interpretation: scalar, multivariate, and temporal requirements oppose in every seed at both
  sites, while corresponding locations reproduce. JERC receives the revised convergence screening
  label; ABBY remains not established because acceptance/saturation fails. No general convergence,
  basin-weight, global-unimodality, or equifinality claim is made.
- Next state: `Iter011 is not_initialized; its complete planning-only ABBY target-equivalent DE proposal-scale pilot is recorded in iterations/iter010.md and CURRENT.md, and execution requires a fresh consolidated kickoff package with explicit approval.`
- Closeout: the 2026-08-13 corrective validator enforces exact cross-record agreement and externally
  verifies the selected follow-up commit against parent `ed42024d513f879d7dd88c998944b80f79b02ebe`,
  subject `Correct Iter010 closeout records`, controlled paths, and a clean tree.

## iter011 - TIM DE-scale and likelihood-resolution pilot (2026-08-14)

- Closeout identity: Iteration ID `iter011`; Status `completed`; Work type `implementation`;
  Objective `Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution pilot at ABBY and JERC`;
  Bounded scope `ABBY/JERC separately; hourly/daily likelihood; DEMove scales 0.50/0.75/1.00; seeds 9009-9011; 36 64x8000 chains`;
  Overall acceptance result `pass`; Decision `ABBY preferred_configuration_supported daily_0.75; JERC inconclusive_metric_tradeoff with no selected configuration`.
- Iteration ID: `iter011`; status: `completed`; work type: `implementation`.
- Objective and locked scope: Site-specific TIM DE-scale and hourly-versus-daily likelihood-resolution
  pilot at ABBY and JERC; hourly/daily likelihood evaluation only;
  DEMove scales 0.50/0.75/1.00; matching Iter009 TIM seed bundles 9009--9011; 36 immutable
  64-walker x 8,000-step chains. Hourly collocation, diagnostics, fitted `sigma_SR`, priors,
  transforms, and all upstream dependencies stayed locked.
- Overall acceptance result: `pass`. Preflight `23561067`, every campaign leaf in six six-leaf
  arrays, and aggregate `23565465` reached terminal `COMPLETED 0:0`. The final aggregate validated
  complete raw/HDF/checkpoint packages and emitted `AGGREGATE_PASS leaves=36` and `AGGREGATE_PASS`.
- Decision: ABBY `preferred_configuration_supported`, selecting `daily_0.75`; JERC
  `inconclusive_metric_tradeoff`, selecting none. The conclusion is site-specific; it is not a
  universal resolution or scale selection, nor authorization for production inference.
- Quantitative evidence: ABBY daily/0.75 combines acceptance 0.23671, saturation 0.013359, and
  minimum steps/tau 33.095. JERC's eligible hourly 0.75 and 1.00 retain a material trade-off;
  daily arms are tau-unstable with acceptance below the locked healthy range. Full seed-paired
  metric evidence is retained in `summaries/iter011/`.
- Provenance and limitations: v1--v4 aggregate failures were classified and preserved; v5 was
  independently reviewed before submission. `/xdisk` products are temporary and unbacked. Any
  ABBY production proposal or JERC follow-up is a new, separately approved iteration.

## iter012 - Reusable general-pipeline fixed production MCMC

Closeout identity: Iteration ID `iter012`; Status `completed`; Work type `implementation`; Objective `Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 and JERC hourly/0.75`; Bounded scope `Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation`; Overall acceptance result `pass`; Decision `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`

- Closed at: `2026-08-17T01:45:03-07:00`
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter012_general_pipeline_v2/revision1`
- Summary path: `development/spinup_forcing_coupling/summaries/iter012`

### Locked settings

- Separate ABBY daily/0.75 and JERC hourly/0.75 targets; 64 walkers × 32,000 steps; seeds
  9009–9011; transformed coordinates; `de_mixture`; frozen 640-member site pools.
- Package v1 is retained only as separately labeled misconfigured-sampler context.
- Revision1 source, dependency, and scaffold manifest hashes are
  `7ce581f0d736e9d82f7d7439c538c9c459ec41be5549178e917b728c515357bf`,
  `540bf3d0816a3a6a103d4e2e5d83a19f43a4a5b58fead598f09b1a0d58365e2d`, and
  `1d6d482b320a2c181fface19adae7c5e4c5bffe38b80033de3454899db6a5035`.

### Quantitative evidence

- Two 10 GB preflights ended `OUT_OF_MEMORY 0:125`; approved Revision1 preflight `23574395`
  completed `0:0` with `PREFLIGHT_PASS`. Initialization `23574453`/`23574454`, pool validation
  `23574678`, six production leaves `23574706`–`23574711`, evaluations `23575950`–`23575953`,
  and aggregate `23575960` all completed `0:0`.
- ABBY: acceptance `0.23890/0.23174/0.23753`; max split R-hat `1.01794`; minimum bulk/tail ESS
  `6518.63`/`3426.05`; cross-seed distance `0.00441`.
- JERC: acceptance `0.18173/0.22123/0.15696`; max split R-hat `2.22410`; minimum bulk/tail ESS
  `241.33`/`1746.05`; cross-seed distance `0.54843`.

### Gate outcome and conclusion

The implementation/integrity contract passed, but both fixed-length scientific outcomes are
inconclusive. No posterior is promoted and no rerun is authorized. On `2026-08-17` the user
requested a Stage-A-only `iter013` planning package that compares TIM and Iter012 initial
clouds at ABBY and JERC; that proposal is recorded in `iterations/iter012.md` and
`handoff/CURRENT.md` and remains `not_initialized` until a fresh consolidated kickoff.
`/xdisk` remains temporary and unbacked, and repetitive empirical-range warning logs are a
maintenance finding.
