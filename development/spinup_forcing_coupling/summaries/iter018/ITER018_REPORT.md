# Iter018 Operational Closeout Report

## Closeout identity

- Iteration ID: `iter018`
- Status: `completed`
- Work type: `implementation`
- Objective: final nine-site operational coupled-optimization release with comprehensive
  coupling-development closeout and merge-readiness declaration
- Bounded scope: 1 preflight; 9 initializations; 9 arrays / 81 leaves; 9 reports; 1 aggregate;
  1 handoff validator
- Overall acceptance result: `pass`
- Decision: `operational_release_ready`; descriptive site statuses below; no posterior promotion;
  coupling-development line terminal; merge is a separate user decision
- Closed at: `2026-08-22T20:35:00-07:00` (includes seed-colored physical-corner makeup)
- Output root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter018_operational_nine_site`
- Summary path: `development/spinup_forcing_coupling/summaries/iter018`

## 1. Comprehensive Iter001–Iter018 development narrative

The spinup-forcing coupling line built a reproducible path from standalone surrogates to a
site-local operational optimization release:

1. **Iter001–002**: Historical then identity-locked forcing-surrogate baselines (nine-site SR).
2. **Iter003–006**: Coupled spinup–forcing comparison arms and MCMC wiring modes
   (mean / member-restart / coupled).
3. **Iter007–008**: Joint then single-site production MCMC diagnostics; evidence classified as
   primarily sampler-limited.
4. **Iter009–011**: Sampler-geometry and TIM DE-scale / likelihood-resolution pilots; site-specific
   configuration evidence without universal promotion.
5. **Iter012–014**: Reusable initialization→production pipeline, TIM-vs-init-cloud diagnosis, and
   high-likelihood hybrid pool reconstruction.
6. **Iter015–016**: Hybrid-init configuration matrix and multi-seed MAP ensemble operational
   procedure at ABBY/JERC.
7. **Iter017**: End-to-end consolidation of the three-stage optimization pipeline (initialize /
   optimize / report) with integrity regression; deliberately non-promoting short chains.
8. **Iter018**: Final nine-site operational release using the locked pipeline, publishing
   site-local MAP-candidate products and closing the development line.

## 2. Released architecture, interfaces, and examples

Locked reusable surfaces (production source lineage through Iter017 `70506cc` and Iter018
runtime packages):

- `model_ELM/coupling_pipeline.py`, `optimization_config.py`, `mcmc_artifacts.py`,
  `mcmc_diagnostics.py`
- Stage adapters: `run_optimization_campaign.py`, `report_optimization.py`,
  `initialize_pipeline.py`
- Manual examples: `examples/optimization/`
- Iteration adapters: `development/spinup_forcing_coupling/slurm/iter018/`
- Site profile: `development/hpc/puma.md`
- Lifecycle policy: `development/spinup_forcing_coupling/WORKFLOW.md`

Iter018 late corrections:

- `report_optimization.py` scaffold-aware overwrite guard so materializer `reports/` directories
  (submit script + config) do not block reporting.
- Reporting-contract makeup (`coupled-optimization-report-v4`): Tier-A-only
  `parameter_sets.{csv,txt}` / `clm_params_seed_*.nc` / physical corner; full-seed audit table;
  Tier-A MAP SR ensemble overlay vs obs + ELM precal; README optimization section updated;
  handoff validator expects NetCDF count = retained Tier-A count.

## 3. Site and cross-site operational evidence

| Site | Config | Tier-A seeds | Descriptive status |
| --- | --- | --- | --- |
| ABBY | daily / 0.50 | 9/9 | `all_tier_a` |
| SOAP | daily / 0.50 | 9/9 | `all_tier_a` |
| YELL | daily / 0.50 | 9/9 | `all_tier_a` |
| WREF | daily / 0.50 | 9/9 | `all_tier_a` |
| JERC | hourly / 0.75 | 1/9 | `partial_tier_a` |
| OSBS | hourly / 0.75 | 4/9 | `partial_tier_a` |
| RMNP | hourly / 0.75 | 8/9 | `partial_tier_a` |
| TALL | hourly / 0.75 | 9/9 | `all_tier_a` |
| TEAK | hourly / 0.75 | 2/9 | `partial_tier_a` |

Machine-readable tables: `site_decisions.csv`, `seed_metrics.csv`, `evaluation_summary.json`.
External aggregate/handoff receipts:
`aggregate/iter018_operational_summary.json`, `handoff/handoff_validation.json`.

Tier-A retention and skill metrics remain descriptive. Retained seeds are operational MAP
candidates only.

## 4. Reproducibility identities

- Dependency manifest digest: `99cf0a1569ee9d8dd74b0b9506cd79a91f5bea455bf3338d4834e7445ad4d4eb`
- Pool-locked source-manifest digest at initialization/optimization:
  `12d25e63fd33126c73f2d6cd9a3390243b10ee305ed04a2e2d9af3dc78da7524`
- Final source-manifest file digest after seed-colored corner makeup:
  `0a40b003f41fdd436f77d0cced56424a2cb53062c2be50aa4433a4dfa67a3afd`
- Repository commit pinned in site submission configs: `eeec519de0dc400fab499fe6fa676caee27b931c`
- Optimization arrays: JERC `23619996`, WREF `23620021`; remaining sites
  `23643144`–`23643150` (submitted `--array=0-8`)
- Corner makeup reports: `23652955`–`23652967`
- Corner makeup aggregate `23653056`; handoff `23653095` (`ITER018_HANDOFF_PASS sites=9 leaves=81`)

## 5. Limitations and storage-retention risk

- `/xdisk` products are temporary and unbacked; raw chains/plots/NetCDF must be curated or copied
  if long-term retention is required.
- High concurrency (`0-8`, no parent-array cap) produced micromamba lock warnings; not a terminal
  failure after provenance realignment.
- Mid-iteration source-manifest edits without matching pool provenance caused a classified
  failure/recovery cycle; immutable pools were preserved.
- Descriptive Tier-A / skill outcomes are not posterior validation or cross-site ranking.

## 6. Merge-readiness declaration

The coupling-development line is **merge-ready from a technical integrity standpoint**:

- Reusable pipeline interfaces and examples exist and were operationally exercised at nine sites.
- Iter018 integrity gates passed (`operational_release_ready`).
- Durable records and external receipts agree on nine complete site packages.

**Merge, push, and PR remain out of scope for Iter018** and require an explicit separate user
decision. This report ends the spinup-forcing coupling-development iteration sequence with a
terminal declaration: no next iteration is proposed.
