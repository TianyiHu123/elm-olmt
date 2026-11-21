# Iter001 Closeout Summary

- Iteration: `iter001`
- Work type: `data_initialization`
- Objective: initialize and validate reusable ABBY/JERC surrogate input data without training.
- Result: `pass`
- Decision: publish snapshot `r0001` and proceed to a planning-only Iter002 two-site prototype
  proposal; fixed-test members remain untouched.
- Scope boundary: no training or model selection occurred.
- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `347646addaad8cc8c99a72e6a89e1f1824f023eb5f2481065336e2d2215dda0c`
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_input_data`
- Catalog: `catalog.json` -> `manifests/dataset_snapshot_r0001.json`
- Sites and coverage: ABBY and JERC; 1,024 members and 61,320 no-leap hourly timestamps each.
- Parameters and split: 18 named parameter variables; deterministic namespace
  `three-stage-surrogate-v1`, seed 2026, 819 development and 205 fixed-test members.
- Prepared artifacts: `common/parameters_v1.nc`, `sites/ABBY/input_data_v1.nc`,
  `sites/JERC/input_data_v1.nc`, `splits/member_split_1024_v1.json`, three immutable source
  manifests, snapshot manifest, catalog, and README.
- Validation: `VALIDATE_SURROGATE_INPUT_OK`; exact schemas, dtypes, chunks/compression, values,
  forcing reconstruction, source identities, snapshot hashes, and publication passed.
- Source preservation: transferred ABBY/JERC transient pickles were read only and remain at their
  original paths; their recorded SHA-256 values are `65fac5b7...d1d82` and
  `cb808465...d3c5`.
- Scheduler accounting: preflight `24430059` completed `0:0`; preparation `24430075` completed
  `0:0`; validation `24430091` completed `0:0`. Preflight attempts `24428809` and `24428935`
  were cancelled before execution after immediate resource-identity rejection and are fully
  accounted.
- Limitations: only ABBY/JERC are initialized; no surrogate was trained; `/xdisk` is temporary and
  not archival storage; later sites and derived caches require new immutable artifacts and a new
  snapshot revision.
- Next direction: Iter002 planning-only proposal for a development-member-only ABBY/JERC direct
  three-stage prototype. Fresh kickoff approval is required.
