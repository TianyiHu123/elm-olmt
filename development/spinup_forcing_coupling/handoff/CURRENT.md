# Spinup-Forcing Coupling - Current Handoff

Closeout identity: Iteration ID `iter016`; Status `completed`; Work type `implementation`; Objective `multi-seed MAP ensemble operational experiment`; Bounded scope `1 preflight; 2 hybrid rebuilds; 2 production arrays (18 tasks); 1 analysis; 1 handoff validation`; Overall acceptance result `pass`; Decision `ABBY=equifinal_candidate_all_tier_a; JERC=equifinal_candidate_partial_tier_a`

## Live State

- Active iteration: none (Iter016 closed)
- Last closed iteration: `iter016`
- Status: `completed`
- Phase: `closed`
- Active job IDs: none
- Site profile: `development/hpc/puma.md`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter016`
- Last updated: `2026-08-19T18:00:00-07:00`

## Best Evidence So Far

- Iter016: 18/18 production leaves; ABBY 9/9 Tier A with MAP SR spread `0.005`; JERC 6/9 Tier A with spread `0.001`; both sites diagnostic `equifinal_candidate`.
- Reusable ensemble tools under `tools/` with README.
- Comprehensive report: `summaries/iter016/ITER016_REPORT.md`.

## Gate Result and Decision

- Overall acceptance: `pass` (integrity gates).
- Decision: `ABBY=equifinal_candidate_all_tier_a; JERC=equifinal_candidate_partial_tier_a`.
- No equifinality success gate; no posterior promotion.

## Current Risks or Blockers

- `/xdisk` products are temporary and unbacked.
- Analysis required one correction submission beyond nominal retry (tool schema vs production JSON); recorded in iteration report.
- Handoff submitter shares receipt filenames with analysis submitter — use direct `sbatch` for handoff or separate receipt paths in future iterations.

## Next Action

Read-only bootstrap for Iter017 kickoff when user approves a new consolidated package. No execution authority until kickoff approval.

## Next Iteration Plan (Planning-Only — Not Approved)

### Iter017 — MAP SR envelope from Tier-A inventory (proposal sketch)

- Work type: `validation` or `implementation` (TBD at kickoff)
- Objective: define and test an operational SR envelope rule from Iter016 Tier-A MAP inventory (no new MCMC unless approved)
- Dependencies: Iter016 `summaries/iter016/` MAP inventory JSON, equifinality diagnostics
- Exclusions: no TIM revert, no posterior promotion, no unauthorized re-run of 18-leaf production
- Status: `not_initialized` — requires user kickoff approval

## Next Session Start Protocol

1. Read this handoff, `WORKFLOW.md`, `iterations/iter016.md`, and `development/hpc/puma.md`.
2. Inspect Git and scheduler state before any submission.
3. Present consolidated kickoff package for Iter017 or other user-directed work.

## Artifact References

- Latest report: `development/spinup_forcing_coupling/iterations/iter016.md`
- Registry: `development/spinup_forcing_coupling/registry.csv`
- Cumulative summary: `development/spinup_forcing_coupling/ITERATION_SUMMARY.md`
- Summaries: `development/spinup_forcing_coupling/summaries/iter016/`
- Scratch output: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter016`
