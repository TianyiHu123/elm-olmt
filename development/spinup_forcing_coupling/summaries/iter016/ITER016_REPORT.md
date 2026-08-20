# Iter016 aggregate and decision report

## Closeout identity

- Iteration ID: `iter016`
- Status: `completed`
- Work type: `implementation`
- Objective: multi-seed MAP ensemble operational experiment at ABBY `daily/0.50` and JERC `hourly/0.75`
- Bounded scope: `1 preflight; 2 hybrid rebuilds; 2 production arrays (18 tasks); 1 analysis; 1 handoff validation`
- Overall acceptance result: `pass`
- Decision: `ABBY=equifinal_candidate_all_tier_a; JERC=equifinal_candidate_partial_tier_a`

## Integrity and provenance

Preflight `23594435` completed `0:0` (`00:03:10`) with `PREFLIGHT_PASS`. Hybrid pool rebuilds `23594478` (ABBY) and `23594479` (JERC) completed `0:0` with pool hashes matching Iter015 identities: ABBY `3627bb1d…`, JERC `40ac807e…`. Production arrays `23594502` and `23594503` submitted nine seeds each (`9009–9017`); all eighteen array tasks completed `0:0` with immutable packages (`raw_chain.npz`, `selection_ledger.json`, `production_result.json`, diagnostics). Elapsed per leaf ranged `01:03–01:54`.

Analysis `23595280` and retry `23595293` failed on reusable-tool schema mismatches (`best_physical_state` key; ELM baseline accessor). Authorized analysis correction `23595316` completed `0:0` (`00:04:14`) with `ANALYSIS_PASS leaves=18` after correcting `ensemble_common.py` (MAP from chain argmax) and `plot_ensemble_sr_overlay.py` (ELM baseline via `context[site]["case"]`). Source manifest entries for those two tools were updated in scratch preflight manifest only; repository commit at materialization remained `eca6014…`.

Tier A retention uses mean acceptance ∈ [0.20, 0.50] only. No equifinality success gate. No posterior promotion.

## Per-seed production evidence

### ABBY `daily/0.50`

All nine seeds pass Tier A. Mean acceptance spans `0.238–0.273`; saturation ≤ `0.019`; MAP RMSE `4.728–4.733` (spread `0.00509`).

| Seed | Acceptance | Tier A | MAP RMSE | MAP R² | Saturation | max τ-change |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| 9009 | 0.254 | pass | 4.730 | −2.240 | 0.012 | 0.299 |
| 9010 | 0.273 | pass | 4.732 | −2.243 | 0.010 | 0.349 |
| 9011 | 0.269 | pass | 4.728 | −2.236 | 0.016 | 0.306 |
| 9012 | 0.257 | pass | 4.731 | −2.241 | 0.010 | 0.325 |
| 9013 | 0.266 | pass | 4.733 | −2.244 | 0.017 | 0.385 |
| 9014 | 0.249 | pass | 4.730 | −2.239 | 0.014 | 0.372 |
| 9015 | 0.263 | pass | 4.729 | −2.238 | 0.019 | 0.352 |
| 9016 | 0.266 | pass | 4.731 | −2.242 | 0.012 | 0.410 |
| 9017 | 0.238 | pass | 4.729 | −2.239 | 0.012 | 0.263 |

### JERC `hourly/0.75`

Six of nine seeds pass Tier A. Excluded: `9009` (acceptance `0.089`), `9013` (`0.160`), `9016` (`0.192`). Retained MAP RMSE `0.667–0.668` (spread `0.00117`).

| Seed | Acceptance | Tier A | MAP RMSE | MAP R² | Exclusion / note |
| --- | ---: | --- | ---: | ---: | --- |
| 9009 | 0.089 | fail | — | — | acceptance below floor |
| 9010 | 0.221 | pass | 0.667 | 0.387 | retained |
| 9011 | 0.259 | pass | 0.667 | 0.387 | retained |
| 9012 | 0.213 | pass | 0.667 | 0.386 | retained |
| 9013 | 0.160 | fail | — | — | acceptance below floor |
| 9014 | 0.268 | pass | 0.668 | 0.386 | retained |
| 9015 | 0.209 | pass | 0.667 | 0.387 | retained |
| 9016 | 0.192 | fail | — | — | acceptance below floor |
| 9017 | 0.223 | pass | 0.667 | 0.387 | retained |

## Ensemble inventory

Tier-A-retained MAP parameter sets are recorded in `abby_map_inventory.json` (9 entries) and `jerc_map_inventory.json` (6 entries with full `map_state` vectors). ELM precal skill is identical across seeds within each site (ABBY RMSE `6.690`, JERC RMSE `1.575`). Calibrated MAP beats ELM at both sites.

## Equifinality / convergence diagnosis

Two-layer diagnostics (MAP primary, subsampled post-burn clouds confirmatory) use thresholds: MAP Wasserstein converged `<0.05`, SR RMSE equivalence `≤0.01`, decomposition W equifinal `≥0.05`.

### ABBY

- MAP label: `equifinal_candidate`; cloud confirmation: `equifinal_candidate`
- MAP SR RMSE spread: `0.00509` (below SR equivalence band — skill-equivalent MAPs)
- Max pairwise MAP Wasserstein: `0.145`; max decomposition W: `0.155`
- Cloud between/within ratios remain ≤ `0.20` for all retained pairs — clouds overlap while MAP points remain separated in parameter space

Interpretation: ABBY shows **parameter-space multiplicity** with **near-identical SR skill** across seeds — consistent with Iter015 `daily/0.50` low cross-seed width (`0.024`) but now replicated across nine seeds.

### JERC

- MAP label: `equifinal_candidate`; cloud confirmation: `equifinal_candidate`
- MAP SR RMSE spread: `0.00117` among Tier-A seeds
- Max pairwise MAP Wasserstein: `0.336`; max decomposition W: `0.360`
- Several cloud pairs show between/within ratio > `1.0` (e.g. 9011–9015 `2.28`) — confirmatory clouds support equifinality among retained seeds

Interpretation: JERC retained ensemble reproduces Iter015 hourly/0.75 flat MAP SR (~0.667) with continued seed-health fragility (9009 still fails Tier A).

Artifacts: `abby_equifinality_diagnosis.json`, `jerc_equifinality_diagnosis.json`, SR overlays (`ensemble-sr-overlay-v2`, invalid timesteps masked with likelihood `_valid_mask`; makeup job `23595515`), physical-corner plots (or skip manifests when applicable).

## Site-specific rationale

**ABBY.** Nine-seed expansion under locked `daily/0.50` hybrid init confirms operational feasibility: every seed completes and passes Tier A. MAP SR skill is tightly clustered despite materially different MAP parameter vectors — the experiment supports treating ABBY MAP as an **SR-equivalent ensemble** for operational envelope purposes, not a single canonical parameter draw. Tau-change remains > `0.20` on every seed (same mixing-length limitation as Iter015 daily configs).

**JERC.** Six-seed Tier-A core matches Iter015 healthy seeds (9010, 9011) and adds four additional stable draws. Persistent low acceptance on 9009 and new failures on 9013/9016 show **seed-health filtering is required** before MAP inventory assembly. Among retained seeds, MAP SR is essentially flat — equifinal_candidate label is informational, not a success gate.

## Integrated conclusion

Iter016 establishes a **bounded operational procedure**: hybrid pool rebuild → fixed-config production arrays → Tier-A acceptance filter → per-seed MAP inventory → two-layer equifinality diagnostics. Integrity gates passed for all eighteen production leaves and the analysis package.

This is **experimental evidence for future operational policy**, not a promoted posterior or default configuration. Limitations: `64×8000` chains; SR-only likelihood; Tier A excludes Wasserstein; diagnostic labels are not veto gates; `/xdisk` scratch is unbacked.

## Next experiment routing (planning-only)

- Consider longer chains or milder DE scale only under a new kickoff package; do not infer from this closeout.
- Operational use should consume Tier-A MAP inventory JSON and SR overlay figures, not raw chains.
- A follow-on iteration might test ensemble aggregation rules (e.g. SR envelope from retained MAPs) — **not authorized here**.
