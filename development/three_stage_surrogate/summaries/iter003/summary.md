# Iter003 Closeout Summary

- Iteration/work type: `iter003` / `experiment`.
- Objective/result: select and freeze the ABBY/JERC spinup MLP configuration using 96 candidates
  and 20 shared development-only 655/164 splits; `pass`.
- Input boundary: immutable snapshot `r0001`; 819 development members; access to the 205 fixed-test
  members remained false.
- Frozen winner: candidate 74, `(64,32)`, `tanh`, alpha `10`, L-BFGS, `max_iter=800`, seed `42`.
- Primary evidence: winner median/mean/std/IQR/worst mean pooled validation log R2 is
  `0.8910/0.8539/0.07358/0.02875/0.6811`; baseline candidate 15 median is `0.8015`; winner paired
  primary mean delta is `+0.07655`.
- Site gate: winner ABBY C/N median log R2 is `0.8950/0.8885` and JERC is `0.8858/0.8845`;
  candidate-minus-baseline deltas are all positive (`+0.07224` to `+0.09391`).
- Stability: 27 of 40 target/split fits emitted nonfatal convergence warnings; this remains explicit
  evidence for release validation, not a reason to change the locked selection rule.
- Completeness: 42/96 candidates were eligible; all 96 array leaves completed `0:0`; aggregation
  and independent validation both selected candidate 74; no retries occurred.
- Evidence identities: aggregate `eae3ef79d12d49d5d2c2b9eef71b1699d1e15628f2c19ccab876ee5e8cab4ab7`;
  ranking `63c864b4539a939c625605bd714ac39e9a6739ffd15f060a98c7ebe4ff6c65ae`;
  validation `27f6a5431f09f77250c789c16bb60bec45265eed3618cbd17c3351f68a2d9d38`.
- Boundary: no model artifact, prediction NetCDF, fixed-test use, all-819 fit, release, GPP/SR work,
  campaign-plan edit, or push occurred.
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter003_abby_jerc_spinup_config`.
- Next direction: planning-only Iter004 all-819 development refit, artifact publication, and frozen
  predicted-C/N handoff; fresh consolidated approval required.
