# Iter004 ABBY OAT Result

- Iteration ID: `iter004`
- Status: `completed`
- Work type: `implementation`
- Objective: Rank ABBY range-wide OAT responses for 13 carbon targets across 14 separately perturbed parameters.
- Bounded scope: 14 exact historical pickles; 1,400 members; 2018-2024 hourly means and population standard deviations; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted range-conditional descriptive OAT package; no global sensitivity, interaction, causal, tuning, or parameter-value claim.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter004_abby_oat/results`

## Quantitative evidence

- Preflight `23830156` and diagnostic `23830259` both completed `0:0` on their initial attempts; no retry was consumed.
- The input gate validated 14 exact ABBY pickles, 1,400 members, 61,320 common hourly samples per member, all required variables, native markers, and the deterministic calculation fixture.
- The published package contains 14 parameter rows, 1,400 member rows, 364 finite score rows, 40,040 curve rows, and 35 figures. The 35 figures comprise 26 response atlases, two heatmaps, and seven compensation plots.
- Input manifest SHA-256: `7c92ea9e0cd94b6657ea0926611ebbac6f4fe879947ee16826f1f0563d9b2082`.
- Output manifest SHA-256: `9d4308d04b68e49a816ebb23e6162703165a3dca9d810e4cc958f714ea86eca2`.
- Complete rankings and secondary Spearman direction evidence are in `sensitivity_scores.csv` (SHA-256 `cbdb7d6214f9d3e5a7b18319adac7e632ecd5b6c7b2b3690512f30a5b149fd2d`).

## Rank-one parameter by target and statistic

| Target | Mean leader (score %) | Temporal-std leader (score %) |
| --- | --- | --- |
| GPP | `leaf_long` (84.743) | `leaf_long` (84.628) |
| ER | `leaf_long` (86.899) | `leaf_long` (83.687) |
| SR | `leaf_long` (78.555) | `act25` (81.938) |
| HR_TOTAL | `leaf_long` (88.487) | `act25` (104.756) |
| LITFALL | `leaf_long` (86.955) | `act25` (50.288) |
| LITTER_SOIL_C_TOTAL | `k_s4` (2338.061) | `k_l2` (70.578) |
| LITR1C | `k_l1` (1284.482) | `k_l1` (377.366) |
| LITR2C | `k_l2` (1524.504) | `k_l2` (172.941) |
| LITR3C | `k_l3` (2272.211) | `k_l3` (107.834) |
| SOIL1C | `k_s1` (2333.894) | `k_s1` (508.344) |
| SOIL2C | `k_s2` (3533.887) | `k_s2` (153.503) |
| SOIL3C | `k_s3` (1871.716) | `k_s2` (68.768) |
| SOIL4C | `k_s4` (2536.987) | `k_s3` (1011.490) |

## Interpretation boundary

These rankings quantify response spread only over the declared, separately sampled ranges. `grpnow` and `kmax` varied across their member samples but scored zero in every target/statistic group. Neither that result nor the rankings establish global importance, interactions, causality, optimal values, or suitability for tuning.
