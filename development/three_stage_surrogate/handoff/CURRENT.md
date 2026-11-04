# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Latest iteration locked plan SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Applicable campaign phase: progression item 6, SR development and configuration selection
- Planning alignment status: `aligned`
- Post-Iter008 plan revision: user authorized combining SR implementation and development-only
  configuration selection when the structure/smoke gate passes and the search contract is locked
  before production. The latest closed iteration remains governed by its recorded plan identity.

## Live State

- Active iteration: none; latest closed iteration is `iter008`
- Planning state: Iter009 proposal under interactive discussion; no kickoff or runtime authority
- Status: `completed`
- Phase: `closed`
- Work type: `implementation`
- Acceptance result: `pass`
- Decision: `gpp_release_published`
- Active job scope: none
- Active monitoring: none; every Iter008 job has authoritative terminal accounting
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-11-04T01:51:05-07:00`

## Completed Objective and Scope

Iter008 characterized Iter007 candidate 21 on 20 fresh synchronized balanced 655/164
development-member splits, published descriptive GPP uncertainty, fitted all 819 development
members, and released the artifact plus `gpp_predicted_for_sr.nc` after independent technical
validation. All 205 fixed-test members remained excluded. No performance gate was applied.

## Best Evidence and Decision

- Preflight `24512852`, all 20 robustness leaves under `24513943`, release fit `24520151`,
  diagnostic retry `24523514`, and corrected final `24523529` completed `0:0`.
- Fresh split manifest is `c3aa7c4b...c904`; 815 members appear four times and four appear five
  times; no validation set matches the prior Iter006/Iter007 design.
- All 20 robustness split and reload reports passed with zero convergence warnings and no
  fixed-test access. Aggregate evidence contains 240 metric rows and 84 uncertainty rows.
- Initial final job `24523438` and diagnostic job `24523491` failed and are preserved. Reviewed
  diagnosis localized the mismatch to scaler-stat dtype order; the corrected interface exactly
  mirrors scikit-learn's float32 transform path without changing model or science content.
- Stable artifact SHA-256: `67214897f16e536f450b34275e5fd19e435e4cc657048fc3194beca500928ec9`.
- Stable GPP handoff SHA-256: `c905fc60803405ba80b1ee7e4d7b489d1aeb3edc1b918ca2f07d8df9b0d198bb`.
- Release manifest SHA-256: `57cc18b063ab46a4cd07a3bd4e03ab1bfd05fb81894b097277d3c667135370d1`.
- All 13 release-manifest files match size and hash; validated, staging, and stable trees agree;
  catalog was written last and points to that exact manifest.
- Overall decision: `gpp_release_published`.

## Published Products

- Stable release:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/gpp_abby_jerc/release_0001`
- Artifact: `artifact/gpp_surrogate_artifact.pkl`
- Descriptive uncertainty: `uncertainty/gpp_uncertainty.nc`, `metric_distribution.csv`, and
  `uncertainty_estimates.csv`
- Downstream handoff: `handoff/gpp_predicted_for_sr.nc`
- Catalog:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/gpp_abby_jerc/catalog.json`
- Compact evidence: `development/three_stage_surrogate/summaries/iter008/`
- Full run evidence:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter008_abby_jerc_gpp_release`

## Risks and Interpretation

- `/xdisk` is temporary and unbacked; run, staging, and stable copies on the same filesystem are
  not independent backups.
- Evidence covers ABBY and JERC only. Published predicted C/N is fixed in-sample upstream input,
  and the all-819 GPP release predictions are in-sample.
- Robustness distributions describe the approved sampled splits; they are not a global or causal
  sensitivity claim and did not serve as a performance gate.
- No fixed-test use, SR fitting, full-chain uncertainty, observation, likelihood, or MCMC work was
  performed.
- Campaign-plan amendment recommendation: `none`.

## Explicit Terminal Declaration

Iter008 is complete and no job is active or unaccounted. Iter009 SR implementation and
configuration-selection planning is underway, but no complete proposal or consolidated kickoff
package has been approved. SR runtime work, full-chain uncertainty, likelihood/MCMC work, or any
later release requires the applicable consolidated kickoff approval.

## Next Session Start Protocol

1. Read `PLAN.md`, this handoff, `WORKFLOW.md`, and `iterations/iter008.md`.
2. Read `summaries/iter008/summary.md` and verify the stable catalog/release identities if needed.
3. Read `development/hpc/puma.md` before any scheduler work.
4. Treat all new work as planning-only until the user approves a new consolidated kickoff package.

## Closeout Identity

- Four-record validator: `development/three_stage_surrogate/slurm/iter008/validate_closeout_iter008.sh`
- Expected validator result: `ITER008_FOUR_RECORD_VALIDATE_PASS`
- Closeout mode: `committed`; expected parent `6bbbb779b6700da9e3dd0c010f1fe5c338829f89`;
  expected subject `Release GPP surrogate artifact`; no push authorized.
