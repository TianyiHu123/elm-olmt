# Iter017 coupled-optimization examples

These are the locked regression examples for the three manually submitted stages:

1. initialization or ledger rebuild;
2. seeded optimization; and
3. independent reporting.

Every file uses the same YAML sections: `shared`, `initialization`,
`optimization`, and `reporting`.  A stage reads only `shared` and its own
section, records the source hash in `stage_manifest.json`, and does not infer a
different configuration from a preceding job directory.

The report job writes its results below the submitted path root:

- `reports/best_parameters/parameter_sets.{csv,txt}` contains all seed MAP rows;
- `reports/best_parameters/clm_params/` contains one exact `clm_params_seed_*.nc`
  per seed, never a merged NetCDF;
- `reports/plots/physical_corner.png` is the aggregate physical-parameter plot;
- `reports/per_seed/` copies leaf diagnostics, default corner plots, and
  posterior time-series plots without changing the optimizer outputs; and
- `postprocess/stage_manifest.json` and `reports/report_manifest.json` record
  the reporting decision. If no seed is descriptive Tier A, the report is
  still written with `status: insufficient_retained`.

These example files are development records. After the four-path regression,
the tested commands and paths will be promoted to the repository README.
