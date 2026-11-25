# iter003 compact closeout summary

- Closed: `2026-11-25T03:24:53-07:00`; status `completed`; work type
  `implementation | integration | numerical validation | bounded benchmark`.
- Objective: implement and validate a reusable site-specific PPE1 posterior combining the exact
  18-D prior, frozen target-free three-stage surrogate, immutable Iter002 observations, fixed
  flux/CN uncertainty, independently selected GPP/SR resolutions, and joint C/N likelihood.
- Decision: all ten gates pass; `four_observable_posterior_validated`. No candidate search,
  optimization, walker initialization, `emcee`, chain, PPE2 science, or Iter004 work occurred.
- Final package: config `0038e424...8bcc`, checksum manifest `492ad4fb...032d`, execution manifest
  `0b5f6513...2ba4`; plan `b302ee65...75ab`, aligned with no amendment.
- Architecture: general `load_three_stage_release()` delegates temporarily to the validated PPE1
  loader; immutable observation contexts preserve exact forcing-hour mappings; pure numerical
  kernels are separated from scalar/batch posterior orchestration and sampling-coordinate Jacobian
  handling. PPE2 requests against the PPE1 release fail before inference.
- Observation counts: ABBY GPP 15,437 hourly/514 daily and SR 26,264/1,095; JERC GPP
  19,844/699 and SR 51,162/2,114. Both sites pass daily/daily, hourly/hourly, daily/hourly, and
  hourly/daily with exact component isolation. Disabled C/N is explicitly zero.
- Arithmetic: eight independent Gaussian references and six independent joint-C/N references
  (ABBY/JERC × CV 0.20/0.30/0.50) pass `rtol=1e-12`, `atol=1e-10`; maximum normalized tolerance
  usage is 0.000194. Posterior component-sum maximum absolute error is zero. Prior support,
  conditional density, physical/sampler Jacobian, scalar/batch order, deterministic replay,
  nonpositive C/N handling, and target-free inference pass.
- Baseline daily/daily full-window components at the midpoint parameter vector are ABBY
  prior/GPP/SR/CN `24.323430/-3151.364059/-4591.367822/-2.957532` and JERC
  `24.323430/-3381.363805/-19704.520779/-14.475787`. These are validation values, not calibrated
  scientific posterior results.
- Performance: 72 warm cells, 24 cold measurements, five repeats/cell. Annual scalar medians span
  0.0711--0.2950 s; annual daily/daily is 0.0785 s ABBY and 0.0711 s JERC. Batch-16 improves all
  eight annual configurations. Maximum projected 1,024 evaluations is 302.06 s; benchmark peak is
  504888 KiB; no material blocker. Projections are estimates, not approved execution budgets.
- Jobs: `24811598` preflight failed a submitted hash transcription and `24811617` passed;
  `24811658` component failed on missing pytest and corrected `24811705` passed; `24811719`
  integrated passed but lacked complete Gate 5 references; authorized `24812674` passed corrected
  evidence; benchmark `24811738` and final `24812698` passed. All eight attempts are terminal and
  classified; zero of four shared scheduler retries were consumed.
- Independent package review initially blocked incomplete design evidence and passed after
  correction. Independent result review blocked missing CV 0.20/0.50 C/N references, then passed
  after all six site/CV cases were added. Final validation evidence SHA-256 includes posterior
  `cc21836e...e6ca`, references `deb2a5e0...1e4`, and benchmark `36ed26fd...45d`.
- Limitations: Iter015 daily surrogate errors use complete model days while some observation means
  use 18--23 hours; the 205 fixed-test members are not independent validation for the combined
  surrogate-plus-depth operator. Missing `pytest` remains unresolved in `OLMT_puma`; a later
  iteration must install/lock it or migrate to another supported test framework.
- Deferred debt: keep the PPE1-specific loader until the complete MCMC pipeline is finalized and a
  separate cleanup establishes general-loader migration and numerical equivalence.
- Next direction: planning-only **Initial Candidate Search and MCMC Pilot Planning** using the
  validated daily/daily, include-C/N, CV 0.30 baseline. No Iter004 initialization or execution is
  authorized without a fresh consolidated kickoff package and approval.
