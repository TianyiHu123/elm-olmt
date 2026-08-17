# Iter012 — General-pipeline fixed production MCMC

Closeout identity: Iteration ID `iter012`; Status `completed`; Work type `implementation`; Objective `Reusable general-pipeline fixed production MCMC for ABBY daily/0.75 and JERC hourly/0.75`; Bounded scope `Package v2 canonical: two fresh pools; six 64x32000 chains; two canonical evaluations; Package v1 legacy audit/evaluation; aggregate and handoff validation`; Overall acceptance result `pass`; Decision `ABBY fixed_length_inconclusive; JERC fixed_length_inconclusive`

## Outcome

Package v2 demonstrated the reusable `initialize_pipeline.py` → `optimize_surrogate_forcing.py`
workflow with transactional artifacts, locked provenance, local Slurm logs, and separate canonical
and legacy evidence. The implementation and integrity gates passed. The fixed-length scientific
decision is inconclusive at both sites, so no posterior is promoted and no chain is rerun.

## Evidence

- Preflight attempts `23574254` and `23574301` exhausted the approved 10 GB allocation and ended
  `OUT_OF_MEMORY 0:125`. The approved Revision1 preflight `23574395` used 4 CPUs/20 GB, completed
  `0:0`, and emitted `PREFLIGHT_PASS`.
- Generic initialization ABBY `23574453` and JERC `23574454`, pool validation `23574678`, all six
  production leaves `23574706`–`23574711`, all four evaluations `23575950`–`23575953`, and
  aggregate `23575960` completed `0:0`.
- ABBY canonical: acceptance `0.23890/0.23174/0.23753`, max split R-hat `1.01794`, minimum bulk
  ESS `6518.63`, minimum tail ESS `3426.05`, max cross-seed distance `0.00441`.
- JERC canonical: acceptance `0.18173/0.22123/0.15696`, max split R-hat `2.22410`, minimum bulk
  ESS `241.33`, minimum tail ESS `1746.05`, max cross-seed distance `0.54843`.
- Package v1 is retained only as `legacy_misconfigured_sampler` comparison evidence.
- Handoff validator `23575977` completed `0:0` with
  `ITER012_HANDOFF_VALIDATE_PASS abby=fixed_length_inconclusive jerc=fixed_length_inconclusive`.

## Limitations and next state

Large empirical-range warning streams were localized correctly but should be deduplicated in a
future pipeline maintenance change. `/xdisk` remains temporary and unbacked.

No next iteration is proposed. This workflow is intentionally stopped because both canonical
fixed-length outcomes are inconclusive and JERC exhibits severe cross-seed nonconvergence. Any
ABBY continuation or JERC topology/likelihood investigation requires a fresh planning package and
explicit user approval.
