# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan: `development/three_stage_surrogate/PLAN.md`
- Current/active locked SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Phase/alignment: progression item 5 GPP development; `aligned_with_scoped_deviation`
- Approved deviation: fixed published all-819 predicted-C/N inputs for both GPP fit and validation;
  evidence is `fixed_upstream_gpp_stage`, not end-to-end held out.

## Live State

- Latest iteration: `iter007`
- Active iteration: none
- Work type: `experiment`
- Status: `completed`
- Phase: `closed`
- Package state: `closed`
- Active job scope: none
- Active monitoring: none; fresh `squeue` found no active Iter007 job and `sacct` reconciled all
  268 allocations `COMPLETED 0:0`
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-11-02T22:28:22-07:00`

## Closed Iteration Result

- Objective/result: select the best pooled ABBY/JERC GPP MLP configuration from a locked
  24-candidate matrix using development-only evidence; `pass`.
- Decision: `configuration_selected_gate_pass`.
- Selected configuration: candidate 21; hidden layers `(64,32)`; activation `tanh`; alpha `1e-4`;
  otherwise frozen Adam controls; 4,929 parameters.
- Gate evidence: hourly R2 q10/RMSE q90/median absolute bias is
  `0.904205/4.260999/0.135299`; daily is `0.829424/2.675357/0.135299`. Every pooled gate passes.
- Ranking: final order `21,18,19,2,8,13`; candidate 18 also passes, but candidate 21 has the larger
  worst normalized margin (`0.063771` versus `0.056001`).
- Validation: all 120 selected leaves, 480 pooled metric rows, artifact hashes, linear quantiles,
  margins, paired baseline improvement, variability, ranking, and decision were independently
  reproduced. Fixed-test access and release authorization are false.
- Campaign-plan amendment recommendation: `none`.

## Accounting and Provenance

- Preflight `24494841`, smoke `24494873`, 192-leaf screen array `24494900`, screen aggregation
  `24506893`, 72-leaf finalist array `24507062`, and final aggregation/validation `24512103`
  completed `0:0`.
- Fresh reconciliation found no active Iter007 jobs and 268/268 allocations terminal with zero
  nonzero exits.
- One redundant `afterok:24506893` finalist submission was rejected before job-ID assignment with
  `Batch job submission failed: Job dependency problem`; unchanged locked material/resources were
  resubmitted without the unnecessary terminal dependency as `24507062`. No workload failure,
  scientific retry, or cancellation occurred.
- Source manifest: `3327dd9a11b306d3b3c04ddb4ca2d922ea889a73dcbfe72786d78c4b6aea1aff`.
- Finalist manifest: `f0a97d89040c1b9f2d0f82c31b7989b7796cda3fba0ff59272f2ba74b7dc24ad`.
- Selection report: `d90cf503ac52181213dee0ab91ed2518879208f84192a32292cc950d1314e745`.
- Final validation: `6edaf171f1c536081915bf4d9a9883b3174ee5b51a17299ac385c8703fadd728`.
- Closeout mode: committed no-push branch; expected parent
  `eab261a62f4ffcfb82436aa6afd179d0171654e3`; expected subject
  `Complete GPP configuration experiment`.

## Boundaries and Risks

- Candidate selection is development-only and does not authorize an all-819 fit, model artifact,
  uncertainty/SR handoff, stable release, catalog, or downstream publication.
- Fixed published C/N is in-sample upstream; this is not full-chain held-out evidence.
- Pooled metrics can mask site behavior; only two sites and a finite candidate matrix were tested;
  selection reused the Iter006/Iter007 development splits.
- External outputs remain on temporary unbacked `/xdisk`; no cleanup was authorized.

## Next Iteration Plan (Planning Only)

Freeze candidate 21 and test it on 20 newly generated balanced 655/164 development-member splits
that are distinct from the Iter006/Iter007 selection splits. Preserve the exact fixed-upstream
43-feature, physical-GPP, Adam, pooled hourly/daily metric, and immutable gate contracts. Retain
compact repeated-fit diagnostics and independently validate coverage, predictions, metrics, and
the gate. A pass may support a later separately planned all-819 release iteration; a failure must
stop with diagnostic evidence. Fixed-test use, release fitting/publication, SR handoff, and MCMC
remain out of scope. This proposal grants no runtime authority.

Fresh consolidated kickoff approval is required before any Iter008 implementation, directory
creation, scheduler action, retry, record mutation, or commit.

## Artifact References

- Iteration report: `development/three_stage_surrogate/iterations/iter007.md`
- Compact evidence: `development/three_stage_surrogate/summaries/iter007/`
- Registry: `development/three_stage_surrogate/registry.csv`
- Cumulative summary: `development/three_stage_surrogate/ITERATION_SUMMARY.md`
- Canonical scripts: `development/three_stage_surrogate/slurm/iter007/`
- External root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter007_abby_jerc_gpp_config`
