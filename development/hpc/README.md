# HPC Site Profiles

The experiment workflow is site-neutral. Select one profile before Slurm or other scheduler
operations and record it in the iteration runtime contract.

Each profile must document:

1. Scheduler, submit, queue, accounting, and cancellation commands.
2. Required account, QOS, partition, constraint, node, CPU, memory, walltime, and accelerator
   settings.
3. Module or environment activation and repository/runtime roots.
4. Scratch/output-root convention and any data-staging requirements.
5. Resource semantics and local limits that affect experiment design.
6. Launch convention: direct single-process launch, `srun`, `mpirun`, or another launcher.
7. Pre-submit checks, monitoring commands, terminal accounting fields, and common failure
   diagnostics.

Profiles contain site facts only. They must not restate experiment lifecycle, iteration
tracking, promotion rules, or handoff policy; those belong in
`development/spinup_surrogate/WORKFLOW.md`.

Start with `perlmutter.md`. Add a new profile when supporting another HPC system, including a
non-Slurm system; document its equivalent submit, monitor, accounting, and cancellation
operations.
