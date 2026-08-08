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
