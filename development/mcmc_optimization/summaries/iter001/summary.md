# iter001 compact closeout summary

- Closed: `2026-11-23T00:56:47-07:00`; status `completed`; work type
  `implementation | validation | benchmark`.
- Objective: implement and validate the 18-parameter PPE1/PPE2 prior contract, validate target-free
  PPE1 ABBY/JERC coupled inference, and measure bounded coupled-surrogate throughput.
- Plan: `MCMC_OPTIMIZATION_PLAN.md` SHA-256 `46775c71...afc6`; aligned; no deviation or amendment.
- Prior result: PPE1 and PPE2 support, density, conditional normalization, inverse maps, sampling
  transforms, and Jacobians pass. Persisted inverse maps use serialization-aware `rtol=1e-10`,
  `atol=1e-12`; all other scientific tolerances remained unchanged. PPE2 scientific inference
  remains prohibited with the PPE1 surrogate.
- Interface result: published PPE1 `release_0001` manifest `4bdc91e2...543a`; ABBY/JERC target-free
  sequential inference, exact `hard_zero_v1`, finite unclipped SR, chunk equivalence, deterministic
  replay, schema/unit identity, invalid-input rejection, and PPE2 incompatibility rejection pass.
- Benchmark result: 18/18 ABBY/JERC x 48/720/8760-hour x batch 1/4/16 cells with five repeats;
  process peak 329336 KiB; batch accounting MaxRSS 1112544K. Linear surrogate-only projections are
  232.509 s for 1,024 and 22,705.939 s for 100,000 two-site 61,320-parameter-hour evaluations.
- Independent result review: `pass`; all seven acceptance gates pass. Recommendation `A`; decision
  `continue_existing_inference_path`; no concrete infrastructure blocker.
- Report hashes: prior `29bd1e2f...5c3b`; interface `7fc10ed5...e253`; benchmark
  `f7f15068...2176`; decision `705fe383...53fe`; final `4526f8b5...4e93`.
- Jobs: `24759169` FAILED harness, `24759238` COMPLETED recovery, `24773888` FAILED locked
  tolerance, `24773997` COMPLETED approved tolerance recovery, `24773889` COMPLETED interface,
  `24774027` COMPLETED benchmark, `24774088` COMPLETED final validation. No active job.
- Protected fixed-test data were not used. Published artifacts, historical records, and the plan
  remain unchanged. Output root is
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter001_dual_prior_coupled_preflight`.
- Limitation: no likelihood or posterior was evaluated; full posterior-call throughput must be
  rebenchmarked after a likelihood adapter exists. No next iteration is proposed or authorized.
