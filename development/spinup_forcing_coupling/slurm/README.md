# Coupling Slurm Material

Keep iteration-specific canonical scripts, manifests, immutable configuration sources, and
one-off validators under:

- `iter001/`
- `iter002/`
- and so on.

For every authorized scheduler submission, including preflight and validators run through Slurm:

1. create the approved work-unit run directory;
2. materialize a self-describing submitted copy and immutable configuration there;
3. verify and record source/configuration identity, hashes, dependencies, resources, logs, and the
   exact submission command;
4. submit only that locked local copy from inside the run directory; and
5. capture the parsable job ID, verify job identity immediately, and maintain terminal accounting
   in `iterations/iterXXX.md` and live job state in `handoff/CURRENT.md`.

Follow the selected profile under `development/hpc/` for site-specific directives, environment,
storage, submission, monitoring, and accounting rules.
