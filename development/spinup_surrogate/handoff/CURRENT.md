# Spinup Surrogate - Current Handoff

## Current Objective

Evaluate multi-case NN behavior (`by_member`) and determine whether forcing-derived climatology features become informative when case diversity is introduced.

## Best Variant So Far

`tuned_nn` (tied with `no_clim` and `reduced_clim`) in iter001 single-case runs.

## Evidence (iter001, single-case, 100 seeds)

For `TOTSOMC` medians:

- `baseline`: `r2_val=0.6056`, `rmse_ratio=0.9412`, warning frac `0.30`
- `tuned_nn`: `r2_val=0.6383`, `rmse_ratio=0.9202`, warning frac `0.41`
- `rf_constrained`: `r2_val=0.5942`, `rmse_ratio=1.2891`, warning frac `0.95`

`TOTSOMN` shows the same ranking pattern.

## What Changed in Latest Iteration

- Added feature filtering + diagnostics in spinup training.
- Ran five variants across 100 seeds each.
- Generated and copied summary JSON files into `development/spinup_surrogate/summaries/iter001/`.
- Added fail-fast iteration workflow with required provenance, debug bundle, and handoff bootstrap rules.

## Open Risks / Unknowns

- Baseline has lower warning fraction but weaker median `r2_val`.
- Current setup is single-case; non-parameter features are mostly constant and removed by variance filter.
- Need confirmation that improvements hold under broader case/site diversity.
- Multi-case (9-case) runs need materially larger memory than previous single-case jobs.

## Next Iteration Plan (iter002)

1. Keep split mode `by_member`, train fraction `0.8`, and targets `TOTSOMC,TOTSOMN`.
2. Use 9-case multisite list (ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL).
3. Run seeds `10001-10030` (30 seeds).
4. Run NN-only variant matrix for forcing/surface attribution:
   - `multi_all` (`feature_set=all`)
   - `multi_params_surface` (`feature_set=params_surface`)
   - `multi_params_clim` (`feature_set=params_clim`)
   - `multi_params_only` (`feature_set=params_only`)
5. Use canonical script path `development/spinup_surrogate/slurm/iter002/` and default scratch run roots `.../spinup_surrogate_iter2_<VARIANT>`.
6. Compare retained-feature diagnostics + permutation importance and standard validation metrics (including `IQR = p75 - p25`).
7. Apply fail-fast policy: if any variant blocks after retry, cancel remaining active/pending iter002 jobs, mark iter002 failed, and switch to debug handoff.

## Next Session Start Protocol

1. Load `development/spinup_surrogate/handoff/CURRENT.md`.
2. Load `development/spinup_surrogate/iterations/iter001.md`.
3. Create and review `development/spinup_surrogate/slurm/iter002/case.train_surrogate_spinup_iter2_multicase.slurm`.
4. Create/update `development/spinup_surrogate/iterations/iter002.md` before first submission.
5. Before each submit, checksum-check canonical vs submitted script and log provenance (`commit hash`, checksums, job IDs/states).
6. Submit variant jobs in parallel by default and monitor all variant jobs concurrently.
7. If any variant is blocked after one retry, cancel remaining active/pending iteration jobs and produce debug handoff.

## Ready/Blocked Status for Next Iteration

Ready to run iter002. Resource policy resolved to explicit values from the successful 9-case multisite reference run.

## Required User Decisions Before Execution (if any)

None for resource policy. Use explicit baseline:

- `#SBATCH --mem=42GB`
- `#SBATCH --time=00:05:00`

Reference used:
`/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter1_multisite_baseline/case.train_surrogate_spinup_iter1.slurm`

## Artifact Paths

- Canonical iter002 script root: `development/spinup_surrogate/slurm/iter002/`
- Iteration report: `development/spinup_surrogate/iterations/iter002.md`
- Scratch outputs (iter002): `/pscratch/sd/t/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter2_<VARIANT>`
- Repo summaries (iter002): `development/spinup_surrogate/summaries/iter002/`
- Prior iteration summaries: `development/spinup_surrogate/summaries/iter001/`

## Files Modified in Repo (latest cycle)

- `.cursor/skills/spinup-surrogate-iteration/SKILL.md`
- `.cursor/skills/spinup-surrogate-handoff/SKILL.md`
- `.cursor/skills/perlmutter-slurm-jobops/SKILL.md`
- `development/spinup_surrogate/iteration_loop.md`

## Failure Debug Bundle Reference (required when latest iteration status is `failed`)

N/A (latest completed iteration is `iter001` success).
