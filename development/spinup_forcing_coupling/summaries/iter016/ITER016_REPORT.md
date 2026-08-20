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

### ABBY Tier-A MAP parameter matrix

Rows are physical parameters; columns are retained seeds. Values from `abby_map_inventory.json`.

| Parameter | 9009 | 9010 | 9011 | 9012 | 9013 | 9014 | 9015 | 9016 | 9017 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| k_l1 | 0.2054 | 0.2023 | 0.2020 | 0.2008 | 0.2021 | 0.2000 | 0.2006 | 0.2278 | 0.2175 |
| k_l2 | 0.1471 | 0.1491 | 0.1489 | 0.1493 | 0.1495 | 0.1456 | 0.1485 | 0.08694 | 0.1493 |
| k_l3 | 0.02793 | 0.02950 | 0.02877 | 0.02780 | 0.02817 | 0.02902 | 0.02971 | 0.02206 | 0.02870 |
| k_s1 | 0.07488 | 0.07294 | 0.07650 | 0.07564 | 0.07627 | 0.07851 | 0.07651 | 0.01072 | 0.07487 |
| k_s2 | 0.02523 | 0.02540 | 0.02606 | 0.02548 | 0.02582 | 0.02521 | 0.02591 | 0.02128 | 0.02566 |
| k_s3 | 7.173e-4 | 6.627e-4 | 6.745e-4 | 7.120e-4 | 6.965e-4 | 7.366e-4 | 7.421e-4 | 1.645e-3 | 7.180e-4 |
| k_s4 | 5.701e-5 | 5.675e-5 | 5.458e-5 | 5.554e-5 | 5.611e-5 | 5.661e-5 | 5.546e-5 | 6.776e-5 | 5.658e-5 |
| k_frag | 0.001999 | 0.001995 | 0.001975 | 0.001980 | 0.001990 | 0.001996 | 0.001989 | 0.001994 | 0.001970 |
| rf_l1s1 | 0.6322 | 0.6714 | 0.6522 | 0.6323 | 0.6441 | 0.6320 | 0.6398 | 0.3981 | 0.6513 |
| rf_l2s2 | 0.1006 | 0.1001 | 0.1004 | 0.1006 | 0.1006 | 0.1003 | 0.1002 | 0.1009 | 0.1003 |
| rf_l3s3 | 0.5989 | 0.6127 | 0.6162 | 0.6126 | 0.6106 | 0.6049 | 0.6124 | 0.7636 | 0.6158 |
| rf_s1s2 | 0.1008 | 0.1008 | 0.1008 | 0.1007 | 0.1042 | 0.1013 | 0.1007 | 0.1019 | 0.1008 |
| rf_s2s3 | 0.8997 | 0.8986 | 0.8987 | 0.8993 | 0.8999 | 0.8998 | 0.8992 | 0.8996 | 0.8997 |
| rf_s3s4 | 0.1012 | 0.1002 | 0.1003 | 0.1005 | 0.1003 | 0.1001 | 0.1006 | 0.1001 | 0.1003 |
| sigma_SR | 3.678 | 3.677 | 3.676 | 3.678 | 3.676 | 3.678 | 3.678 | 3.678 | 3.678 |
| MAP RMSE | 4.730 | 4.732 | 4.733 | 4.730 | 4.729 | 4.733 | 4.728 | 4.733 | 4.730 |

### JERC Tier-A MAP parameter matrix

Rows are physical parameters; columns are retained seeds only (`9009`, `9013`, `9016` excluded). Values from `jerc_map_inventory.json`.

| Parameter | 9010 | 9011 | 9012 | 9014 | 9015 | 9017 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| k_l1 | 0.5182 | 1.485 | 0.5231 | 0.5269 | 0.2032 | 0.2664 |
| k_l2 | 0.01812 | 0.01194 | 0.01818 | 0.01830 | 0.03955 | 0.01005 |
| k_l3 | 0.004051 | 0.003006 | 0.004184 | 0.004235 | 0.004252 | 0.004309 |
| k_s1 | 0.06259 | 0.1003 | 0.06318 | 0.06210 | 0.03943 | 0.09944 |
| k_s2 | 0.01907 | 0.02192 | 0.01910 | 0.01906 | 0.01781 | 0.01356 |
| k_s3 | 7.584e-4 | 1.273e-3 | 7.609e-4 | 7.573e-4 | 5.184e-4 | 3.003e-4 |
| k_s4 | 1.844e-4 | 2.000e-4 | 1.848e-4 | 1.846e-4 | 1.662e-4 | 1.561e-4 |
| k_frag | 9.020e-4 | 2.179e-4 | 9.157e-4 | 9.111e-4 | 1.465e-3 | 1.553e-3 |
| rf_l1s1 | 0.5345 | 0.2696 | 0.5354 | 0.5363 | 0.7288 | 0.5827 |
| rf_l2s2 | 0.4710 | 0.6148 | 0.4683 | 0.4670 | 0.2790 | 0.5528 |
| rf_l3s3 | 0.1005 | 0.1760 | 0.1003 | 0.1002 | 0.8093 | 0.2963 |
| rf_s1s2 | 0.7870 | 0.8364 | 0.7851 | 0.7867 | 0.2970 | 0.8996 |
| rf_s2s3 | 0.2113 | 0.2851 | 0.2095 | 0.2093 | 0.3300 | 0.3376 |
| rf_s3s4 | 0.4896 | 0.5524 | 0.4913 | 0.4905 | 0.7669 | 0.6818 |
| sigma_SR | 0.6670 | 0.6669 | 0.6668 | 0.6670 | 0.6661 | 0.6671 |
| MAP RMSE | 0.6674 | 0.6666 | 0.6674 | 0.6674 | 0.6677 | 0.6667 |

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
