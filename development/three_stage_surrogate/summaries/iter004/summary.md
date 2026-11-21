# Iter004 Closeout Summary

- Iteration/work type: `iter004` / `implementation`.
- Objective/result: characterize frozen candidate 74 on 20 fresh development-only splits, publish
  its member-balanced spinup uncertainty component, refit on all 819 development members, and
  release the artifact plus predicted-C/N GPP handoff; `pass`.
- Input boundary: immutable snapshot `r0001`; 819 development members; zero access to the 205
  fixed-test targets or parameters; split seed `20261031`, file `7644ed38...ace0`, canonical design
  `0b343378...6ecb`.
- Robustness completeness: 20 synchronized 655/164 splits, 6,560 paired site/member/repetition
  observations, 168 metric rows, 80 same-member depth-dependence rows, and 22/40 nonfatal
  convergence warnings. Every development member appears four or five times.
- Repetition distributions are reported as minimum/median/maximum. Log R2 for ABBY C/N is
  `0.8584/0.8953/0.9102` and `0.8550/0.8890/0.9129`; JERC C/N is
  `0.5575/0.8796/0.9097` and `0.5510/0.8746/0.9110`. Log RMSE medians are ABBY
  `0.3522/0.3675` and JERC `0.3644/0.3759` for C/N.
- Cross-repetition pooled log R2 is ABBY `0.8931/0.8899` and JERC `0.8053/0.8011` for C/N.
  Cross-repetition log RMSE is ABBY `0.3611/0.3692` and JERC `0.4908/0.4996`.
- Member-balanced surrogate log-error summaries use occurrence weight `1/k`, normalized across
  819 members, and population `ddof=0`. ABBY C/N bias is `0.00466/0.00701`, covariance is
  `[[0.12981,0.12970],[0.12970,0.13562]]`, and correlation is `0.9775`. JERC bias is
  `0.00682/0.00892`, covariance is `[[0.24055,0.24197],[0.24197,0.24921]]`, and correlation is
  `0.9883`. Minimum eigenvalues are `0.00298/0.00287` for ABBY/JERC.
- Same-member surrogate/depth log-error correlation medians are ABBY `-0.164/-0.195` and JERC
  `-0.125/-0.125` for C/N; the full per-repetition diagnostic is retained and is not folded into
  the surrogate covariance.
- Release: artifact `9abb342d57bf81ce933f82a5750bb56df1eaeb721f55080e3766ba76fee8a809`;
  819-member predicted-C/N handoff
  `9e2d5be4809ee7c9053baf70ad7574ca0b5cc2afc4a15b6006663a0fb8fafdb5`; 14-file release
  manifest `69f840f7972d640e91b1693c2fcf71b984dae2e20fee9a07f05434af0591f2dc`.
- Publication: immutable stable package
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc/release_0001`;
  product catalog written last. Stable and run copies are distinct single-link inodes but remain on
  the same temporary, unbacked `/xdisk` filesystem and are not backups.
- Accounting: preflight `24479223`, successful robustness `24480121`, uncertainty `24480153`,
  release fit `24480174`, and validation `24480199` completed `0:0`. Robustness attempt 1
  `24479279` failed before fitting due to a development-position indexing bug; its exact source
  manifest and evidence are preserved, the bounded non-scientific correction passed re-review, and
  attempt 2 passed.
- Limitations: two sites; overlapping development validation sets; robustness models use 655 rather
  than final 819-member fits; all-development handoff predictions are in-sample; strong C/N error
  correlation; convergence warnings; surrogate-only uncertainty; temporary unbacked storage; no
  fixed-test, flux-stage, full-chain, observational, likelihood, or posterior evidence.
- Campaign-plan amendment recommendation: `none`.
- Next direction: planning-only Iter005 GPP input/interface materialization using published
  `release_0001`; fresh consolidated kickoff approval required.
