# Coupling Workflow Tools

Keep reusable validation, analysis, and release utilities here. Keep one-off utilities with their
iteration under `slurm/iterXXX/`.

## Iter002 release utilities

- `release_forcing_surrogate.py` — reproduction gate, full-data `forcing-surrogate-v1` build,
  and full-data in-sample permutation importance.
- `validate_iter002_release.py` — fresh-process load, batch inference, negative schema gates,
  and sidecar identity checks.

## Iter003 coupled evaluation

- `evaluate_coupled_surrogate.py` — PPE batch client over both spinup variants and the locked
  forcing artifact; writes per-member metrics, per-site median summaries, feedback plots, and
  optional NetCDF timeseries (`--save-timeseries`).

## Iter004 offline-versus-coupled comparison

- `evaluate_offline_coupled_comparison.py` — nine-site PPE client comparing offline
  forcing-v1 (ELM restart spinup) vs coupled `drop32`/`drop21_corr080`; writes metrics,
  timeseries NetCDF, and the locked four-figure plot package per site.

## Iter005 mean-spinup offline baseline

- `evaluate_mean_spinup_offline_comparison.py` — nine-site PPE client for offline
  forcing-v1 with site-mean ELM restart spinup; overlays Iter004 member-restart offline
  and coupled arms; writes metrics, timeseries NetCDF, and two annotated plot types per
  site (timeseries; SR vs member).

## Initialization cloud overlay (reusable)

- `plot_init_cloud_overlay.py` — prior-normalized violin overlays for candidate pools and
  MCMC walker unions; JSON spec with optional pairwise Wasserstein/overlap stats.
- `plot_init_cloud_overlay.slurm` — lightweight Slurm launcher (4 CPU / 20 GB / 30 min).

Cloud spec schema: `spinup-forcing-coupling-init-cloud-overlay-v1`.

Supported sources:

| Cloud kind | Typical source | Array key |
| --- | --- | --- |
| `pool_npz` | rebuilt or control `candidate_pool.npz` | `physical_states` |
| `tim_pool_npz` | Iter009 TIM high-L pool | `physical_chain` |
| `walker_union` | group of members | see below |

Walker union members: `selection_ledger` (`selected_physical_states`, 64×15) or
`tim_bundle` (`initial_state`, 64×15).

Outputs under `--output-dir`:

- `parameter_overlay.png`
- `cloud_stats.json`
- `init_cloud_overlay_manifest.json`

Local example:

```bash
micromamba run -n OLMT_puma python development/spinup_forcing_coupling/tools/plot_init_cloud_overlay.py \
  --spec /path/to/init_cloud_overlay.spec.json \
  --forcing-artifact /path/to/forcing_surrogate_iter002_sr.pkl \
  --spinup-artifact /path/to/spinup_surrogate_iter012_drop21_corr080.pkl \
  --output-dir /path/to/output \
  --overwrite
```

Iter014 hybrid reference:

- Spec: `.../iter014/production/hybrid_high_l_maximin/init_cloud_overlay.spec.json`
- Submit: `bash .../production/hybrid_high_l_maximin/submit.sh`
- Plot output: `.../iter014/pool_rebuild/hybrid_high_l_maximin/parameter_overlay.png`

Derived from `slurm/iter013/analyze_iter013.py` plotting utilities without Iter013 hash
locks or classification side effects.

## Fixed-length MCMC diagnostics and physical corners (reusable)

Shared Iter012/014 evaluation **core**, without iteration provenance gates or decision
labels. Closed evaluators under `slurm/iter012/` and `slurm/iter014/` are left unchanged.

- `fixed_length_mcmc_diagnostics.py` — library + CLI for τ, descriptive discard, rank
  split R̂, bulk/tail ESS, cross-seed normalized Wasserstein, transformed saturation,
  prior-edge occupancy, and the `skill()` helper used by both evaluators.
- `plot_physical_corner.py` — physical-coordinate matplotlib corners: pooled, optional
  seed-colored overlay, and optional per-seed plots (15 params including `sigma_SR`).
- `plot_physical_corner.slurm` — optional launcher; if `DIAGNOSTICS_SPEC` is set it runs
  diagnostics first, then the corner plotter.

These are **not** the production `plots/corner/corner_plot.png` files (14-param, thinned,
`corner` library). See `summaries/iter014/ITER014_REPORT.md` for that distinction.

Diagnostic spec schema: `spinup-forcing-coupling-fixed-length-mcmc-diagnostics-v1`.

```json
{
  "schema": "spinup-forcing-coupling-fixed-length-mcmc-diagnostics-v1",
  "case": "JERC_ppe6_I20TRCNPRDCTCBC",
  "resolution": "hourly",
  "expected_target_sha256": "<optional>",
  "chains": [
    {"label": "9009", "path": "/path/to/seed_9009/raw_chain.npz"},
    {"label": "9010", "path": "/path/to/seed_9010/raw_chain.npz"},
    {"label": "9011", "path": "/path/to/seed_9011/raw_chain.npz"}
  ]
}
```

Corner spec schema: `spinup-forcing-coupling-physical-corner-v1`.

```json
{
  "schema": "spinup-forcing-coupling-physical-corner-v1",
  "title": "JERC hybrid physical corner",
  "include_sigma_SR": true,
  "color_by_seed": true,
  "write_pooled": true,
  "write_per_seed": true,
  "subsample": 2000,
  "rng_seed": 14014,
  "chains": [
    {"label": "9009", "path": "/path/to/seed_9009/raw_chain.npz"},
    {"label": "9010", "path": "/path/to/seed_9010/raw_chain.npz"},
    {"label": "9011", "path": "/path/to/seed_9011/raw_chain.npz"}
  ]
}
```

Omit `discard` to use the same τ/20% rule as the evaluators.

Outputs under `--output-dir`:

| Tool | Files |
| --- | --- |
| diagnostics | `mcmc_diagnostics.json` |
| corner | `physical_corner.png`, optional `physical_corner_by_seed.png`, optional `physical_corner_<label>.png`, `physical_corner_manifest.json` |

Local example:

```bash
micromamba run -n OLMT_puma python development/spinup_forcing_coupling/tools/fixed_length_mcmc_diagnostics.py \
  --spec /path/to/mcmc_diagnostics.spec.json \
  --forcing-artifact /path/to/forcing_surrogate_iter002_sr.pkl \
  --spinup-artifact /path/to/spinup_surrogate_iter012_drop21_corr080.pkl \
  --output-dir /path/to/output \
  --overwrite

micromamba run -n OLMT_puma python development/spinup_forcing_coupling/tools/plot_physical_corner.py \
  --spec /path/to/physical_corner.spec.json \
  --output-dir /path/to/output \
  --overwrite
```
