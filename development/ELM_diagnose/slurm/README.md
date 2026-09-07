# ELM Diagnostic Slurm Material

Keep iteration-specific canonical scripts, manifests, immutable configuration sources, and one-off validators under `iterXXX/` when an approved iteration requires scheduler execution.

For every authorized scheduler submission, materialize and submit only the locked local copy from its approved run directory, record its parsable job ID, verify job identity, and maintain terminal accounting in the iteration report and `handoff/CURRENT.md`.

Follow the selected profile under `development/hpc/` for site-specific directives, environment, storage, submission, monitoring, and accounting rules.
