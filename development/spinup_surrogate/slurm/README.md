# Slurm Scripts

Keep iteration-specific Slurm scripts here:

- `iter001/`
- `iter002/`
- ...

Guidelines:

- Keep one canonical script per iteration and annotate variant usage.
- Prefer parameterized scripts with environment-variable variant selection, but require every
  production submission to materialize a self-describing, variant-local copy plus immutable
  configuration manifest directly under `<output-root>/UQ_output/<run-slug>/`.
- Submit that variant-local copy with root-level `slurm_%A_%a.out` and `slurm_%A_%a.err` paths;
  do not write production matrix logs to the shared `UQ_output` root or extra variant subfolders.
- Record canonical, submitted-copy, configuration, and log paths in `iterations/iterXXX.md`.
