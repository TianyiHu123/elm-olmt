# MCMC Optimization Development

This directory contains the campaign plan, lifecycle policy, live handoff, and development records
for site-specific Bayesian calibration with the published three-stage ELM surrogate. The single
authoritative scientific contract is `MCMC_OPTIMIZATION_PLAN.md`. This scaffold does not initialize
an iteration or authorize implementation, repository Python, experiments, or scheduler activity.

## Scope and dependencies

The initial scientific baseline is the original 18-parameter PPE1 prior and the frozen ABBY/JERC
coupled three-stage surrogate `release_0001`. The surrogate predicts spinup TOTSOMC/TOTSOMN, then
GPP, then SR without true upstream ELM targets during inference. The completed upstream campaign
and its published artifacts remain immutable dependencies; this campaign does not retrain or edit
them.

PPE2 is an optional prior implementation target. It is scientifically inactive until a compatible
PPE2-trained and validated surrogate release and PPE2-specific uncertainty and depth products
exist. A prior switch alone cannot make the PPE1 release compatible with PPE2.

Reusable priors, likelihoods, inference adapters, MCMC machinery, diagnostics, configuration, and
tests belong under `model_ELM/`, repository-root entry points, and `tests/` as appropriate.
Iteration records, compact evidence, Slurm material, and campaign-specific development tools belong
here. This directory is a development record, not a standalone Python package.

## Structure

- `MCMC_OPTIMIZATION_PLAN.md`: user-approved scientific and engineering campaign contract. It is
  the only substantive campaign plan and changes only through separate user authorization.
- `WORKFLOW.md`: iteration lifecycle, authority, evidence, continuity, and closeout procedure.
- `handoff/CURRENT.md`: live state, locked plan identity, upstream dependencies, authority, and
  exact next action.
- `iterations/iterXXX.md`: exact approved plan, runtime contract, evidence, and decision for an
  initialized iteration. Create one only after consolidated kickoff approval.
- `registry.csv`: fixed-schema index of closed iterations; it has no row before the first closeout.
- `ITERATION_SUMMARY.md`: cumulative immutable closeout summaries.
- `summaries/iterXXX/`: compact decision evidence required by an approved iteration.
- `slurm/iterXXX/`: canonical iteration-specific preflight, execution, manifest, and validation
  material when runtime work is approved.
- `tools/`: reusable MCMC-campaign validation and analysis utilities. Keep one-off utilities with
  their iteration.
- `templates/`: scaffolds for iteration reports and the live handoff.

The `iterations/`, `summaries/`, `slurm/`, and `tools/` directories are created only when approved
work needs them. Their absence before Iter001 is intentional and is not missing campaign history.

## Session start and iteration lifecycle

At the start of every session:

1. Read `MCMC_OPTIMIZATION_PLAN.md` and verify its SHA-256 against `handoff/CURRENT.md`.
2. Read `handoff/CURRENT.md`, then `WORKFLOW.md`.
3. If an iteration exists, read its report in full and up to two preceding reports.
4. Read relevant registry rows, cumulative summaries, and compact evidence.
5. Read the proposed or approved profile under `development/hpc/` and inspect Git state.
6. Reconcile any recorded active scheduler scope using the workflow and selected profile.

New work begins as a planning-only proposal. The primary agent prepares one consolidated kickoff
package covering the scientific objective, locked identities, finite work units, immutable gates,
resources, runtime and scheduler authority, review, retry/cancellation boundaries, records, and
closeout branch. Only explicit approval of that complete package permits creation of
`iterations/iterXXX.md` and transition through preparation, independent read-only review,
compute-node preflight, execution, evaluation, and closeout. A closed iteration adds exactly one
registry row and one cumulative summary section and leaves a complete next planning-only proposal
or an explicit terminal declaration.

## Reusable kickoff goal

For Iter001, first finalize its planning-only proposal and request approval of the consolidated
package. For later iterations, recover the proposal from the latest closed report and handoff.

```text
/goal Start or resume the active or next MCMC optimization development iteration by following
development/mcmc_optimization/WORKFLOW.md. Begin at Section 4A and continue until the
workflow-defined stop condition is reached. Apply the monitoring-continuity gate before any
turn-ending response.
```

The goal names the lifecycle objective and stop boundary. It grants no initialization, execution,
scheduler, retry, cancellation, directory-creation, plan-amendment, or commit authority; those
must be stated in the user-approved consolidated kickoff package.
