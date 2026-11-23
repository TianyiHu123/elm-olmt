# Puma MCMC Worktree Overlay

This workload profile applies all site, Slurm, environment, storage, submitted-copy, monitoring,
and accounting rules in `development/hpc/puma.md`. It supersedes only that profile's fixed
repository-root clause for the MCMC optimization worktree:

```bash
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt-mcmc
```

Iter001 scripts must verify the physical path, `feature/mcmc-optimization` branch, locked campaign
plan hash, base commit, and execution-manifest source hashes before invoking repository Python.
No environment override or alternate checkout is permitted. The shared Puma profile remains
unchanged and all its other rules continue to apply.
