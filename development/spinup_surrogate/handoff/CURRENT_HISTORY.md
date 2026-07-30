# Spinup Surrogate Handoff History

This file holds historical or redundant material removed from the live
`handoff/CURRENT.md`. The detailed authoritative evidence remains in the iteration reports,
`ITERATION_SUMMARY.md`, registry, and site profile paths listed below.

## Archived historical sections

### Historical context through Iter009

- Iter006 settled the 45-feature `all_control` schema.
- Iter007 selected the compact `(8,)` tanh/Adam baseline.
- Iter008 selected `(32,)` tanh/LBFGS alpha 50/full45 with five-seed median validation R2
  `0.7935/0.7937`, absolute validation RMSE `4661.8/469.7`, RMSE ratio `0.9499/0.9561`, and
  zero warnings.
- Iter009 confirmed alpha-50/full45 as the eligible retained baseline; lower alpha improved
  R2 but warned on one of five seeds.

Detailed evidence: `iterations/iter006.md` through `iterations/iter009.md` and
`ITERATION_SUMMARY.md`.

### Historical Iter009 and Iter010 plans

The completed planning material is preserved in:

- `iterations/iter009.md` — proposed Iter010 matrix and gates;
- `iterations/iter010.md` — completed Iter010 plan, execution ledger, results, and planning-only
  next-iteration note.

These plans are provenance only and are not execution authority.

### Historical Puma migration state

The Perlmutter-to-Puma migration completed successfully. The nine case pickles were activated
under the recorded migration contract, with `.perlmutter.bak` backups retained. See the migration
record and `development/hpc/puma.md` for durable site rules.

### Historical Iter006 evidence and Iter007 scaffold notes

The former `Evidence (key metrics and failure signals)` and `What Changed in Iter007 Scaffold`
sections duplicated closed iteration reports. Their authoritative details remain in
`iterations/iter006.md`, `iterations/iter007.md`, and the cumulative summary.

### Historical risks and resource observations

Past memory, CPU-efficiency, cache, and migration observations remain in the relevant iteration
reports and site profile. They are not current blockers unless copied into the live handoff's
`Current Risks or Blockers` section.

### Historical plan and artifact references

External planning references:

- `/home/u32/tianyihu/.cursor/plans/iter007-mlp-tuning-4525e552.plan.md`
- `/home/u32/tianyihu/.cursor/plans/iter006-feature-settling-03e71a26.plan.md`

Closed-iteration artifact roots:

- `slurm/iter005/` through `slurm/iter009/`;
- `summaries/iter005/` through `summaries/iter009/`;
- `iterations/iter005.md` through `iterations/iter009.md`.

### Historical migration-cycle file list

The former migration-cycle file list is retained as provenance in the migration records. It is
not a live statement of files changed in the latest completed iteration.
