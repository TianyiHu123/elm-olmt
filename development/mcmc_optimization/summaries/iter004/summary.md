# iter004 compact closeout summary

- Closed: `2026-11-26T01:18:00-07:00`; status `completed`; work type
  `implementation | integration | candidate search | sampling pilot | numerical validation`.
- Objective: validate a site-independent PPE1 candidate-search, diversified initialization,
  checkpoint/restart, and daily/daily four-observable `emcee` engineering pilot for ABBY and JERC.
- Plan: amended `MCMC_OPTIMIZATION_PLAN.md` SHA-256 `5ee74c52...60c0`; aligned. Iter001--003
  retain their historical plan identities.
- WU1 passed full-window Iter003 references, deterministic scalar/batch evaluation, exact physical/
  sampling target separation, recognized numerical rejection, and resources. The evidence-based
  scalar/batch-only tolerance is `rtol=1e-7`, `atol=1e-8`; strict reference and component-sum gates
  were not relaxed. Peak process RSS was `1.561 GiB`.
- Candidate search: Owen-scrambled 18-D Sobol Stage 1 generated 1,024 unique, finite, eligible
  candidates per site; Stage 2 was correctly unused. Search throughput was 4.572/s ABBY and
  2.601/s JERC. Physical posterior ranking excluded the sampling Jacobian.
- Initialization: both deterministic 256-member pools and 64-walker sets pass support, uniqueness,
  rank 18, spread, and replay. Pool condition numbers are 1.476/1.385 and walker condition numbers
  2.376/2.435 for ABBY/JERC. The fixed-seed 16-step uninterrupted versus 8+8 restart test is exact.
- Pilot: both sites stopped at the locked 128-step continuation gate. ABBY had 7,079/8,192
  (`0.8641357421875`) recognized out-of-support proposal rejections; JERC had 7,350/8,192
  (`0.897216796875`); maximum per-walker rejection was 1.0 for both. The fatal limits were 0.50
  overall and 0.90 per walker. No 256-step continuation occurred.
- Geometry and resources at failure remained valid: 64 unique states, rank 18, condition
  4.599/3.498, peak RSS 1.548/1.562 GiB, and projected 256-step time 0.201/0.164 h. Checkpoints are
  exactly steps 64 and 128 with hash-locked backend, ledger, target, and identity evidence.
- Diagnostics preserve all candidate, pool, walker, raw-chain, component, trace, bound-occupancy,
  representative GPP/SR residual, depth-adjusted C/N, covariance/bias, rejection, checkpoint, and
  performance evidence. Runtime storage is about 55.7 MB against 10 GiB. This is an exploratory
  engineering pilot with no posterior convergence or calibrated credible-interval claim.
- Independent package and result reviews pass. Diagnostics job `24827442` and final verification
  `24827522` completed `0:0`; final validation SHA-256 is `c344218b...6763`.
- All 16 submissions are terminal and reconciled; active or unaccounted jobs: zero. Final accounting
  SHA-256 is `20fe9fe7...84e8`. The approved absolute submission ceiling was reached exactly; no
  shared infrastructure retry was used.
- Decision: `iter004_validation_failed`. The fatal numerical gate cannot be reclassified as a
  nonfatal performance or mixing limitation.
- Missing `pytest` remains unresolved; Iter004 used 27 explicit `unittest` cases. Removal of
  `load_ppe1_coupled_release()` remains deferred until separately authorized full-pipeline cleanup.
- Iter005 is planning-only: audit proposal-level transformed/physical geometry and conditional
  support before proposing a corrected bounded pilot. Historical 500/4,000/8,000/32,000-step
  coupling runs do not justify a longer chain until the Iter004 fatal rejection mechanism is fixed.
  No Iter005 initialization, execution, push, or merge is authorized.
