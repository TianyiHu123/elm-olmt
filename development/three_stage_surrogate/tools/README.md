# Reusable Tools

Keep only reusable campaign-specific validation, analysis, and release utilities here. One-off
utilities remain with their iteration. Core surrogate implementation belongs in the repository's
normal source tree.

## Input-data tools

- `prepare_surrogate_input_data.py` validates declared sources and writes an attempt-local,
  no-training staging package with named-variable NetCDFs, source manifests, the locked global
  member split, and an immutable snapshot manifest.
- `validate_surrogate_input_data.py` independently reloads the declared sources, validates every
  prepared value and identity, checks the split and snapshot, and optionally publishes a passing
  package without overwriting existing artifacts.

Run these only through an iteration-approved Puma compute job. They intentionally preserve the
transferred pickles and do not fit, scale, select, or evaluate a surrogate.

## Closeout record tool

- `validate_closeout_records.py` cross-checks the Iter001 report, cumulative summary, registry,
  handoff, compact validation evidence, catalog, snapshot, and published artifact sizes. It accepts
  the independently observed active-job count and fails unless that count is zero.

This validator is static and reads only compact records and metadata; it does not load NetCDF or
pickle payloads, rerun data validation, mutate artifacts, or query the scheduler.
