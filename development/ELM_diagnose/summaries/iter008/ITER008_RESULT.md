# Iter008 ABBY Vertical-Soil-Carbon C:N Nutrient-Stress OAT Result

- Iteration ID: `iter008`
- Status: `completed`
- Work type: `implementation`
- Objective: Characterize how separate perturbations of `cn_s1`--`cn_s4` affect realized decomposition, microbial N/P demand satisfaction, plant N/P demand satisfaction, ecosystem carbon fluxes, and mineral nutrient cycling in the ABBY vertical-soil-carbon configuration.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 27 direct raw metrics; four accumulated satisfaction ratios; 58 response endpoints; 27,555 CSV rows; 11 figures; descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accepted the validated baseline-conditioned ABBY C:N OAT package. Increasing pool C:N reduces potential microbial nutrient demand and improves microbial demand satisfaction, especially for `cn_s3` and `cn_s4`, but does not broadly relieve plant demand or guarantee higher realized decomposition.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter008_abby_ctrlvertc_cn_oat/results`

## Quantitative evidence

- Preflight `24015245` and diagnostic `24015300` completed `0:0` on attempt one. Their elapsed times were `00:01:38` and `00:01:00`; peak memory was 19.71/60 GB and 4.17/60 GB. No scheduler/resource retry was consumed.
- Input manifest SHA-256: `2c90f754d843eba1b2610be2574862f17471689ba3a98d6140155986c1f7dc19`. Validation receipt SHA-256: `56fb4d944afb1cfd7e5bbd74b009fd88427a7488d02c49250c21c5238dfe257a`. Output manifest SHA-256: `9d5c8b07e560c1fa186a28d77f7ac35cd31d8009060e6f942714120f618ab49b`.
- The package contains exactly 4 parameter rows, 31 metric definitions, 400 member rows, 25,520 response rows, 1,600 ratio-support rows, and 11 PNGs: 27,555 CSV data rows total. All 1,600 ratios are supported; every member has 61,320 model hours.
- From the lowest to highest sampled parameter values, microbial N satisfaction changes by `+2.3%`, `+25.4%`, `+108.4%`, and `+118.6%` for `cn_s1`--`cn_s4`; microbial P satisfaction changes by `+22.2%`, `+33.7%`, `+96.1%`, and `+95.7%`.
- Potential N immobilization declines by `19.8%`--`66.7%`, and potential P immobilization declines by `43.3%`--`63.8%`. Actual immobilization generally also declines; only `cn_s4` produces small increases (`+4.4%` N and `+4.7%` P). The satisfaction increase therefore primarily reflects potential demand falling faster than realized immobilization.
- Plant N/P satisfaction changes only about `+0.6%`, `-3.6%`, `+1.4%`, and `+4.3%` for `cn_s1`--`cn_s4`. Direct HR changes by `+1.0%`, `-5.4%`, `-0.7%`, and `+4.6%`; SR follows nearly the same directions.
- All 11 figures passed visual review. Figure 8 uses direct model `HR`; Figure 9 includes all eight direct pool-HR outputs. No reconstructed `poolC * K`, potential/limited HR, heatmap, or excluded output was published.

## Descriptive interpretation

Within these separate sampled OAT ranges, raising soil-pool C:N can relieve microbial N/P demand mismatch, with the strongest response for pools 3 and 4. This relief is demand-driven: potential immobilization drops much more than actual immobilization. The nearly flat plant-satisfaction responses do not show broad transfer of that relief to plants.

Microbial satisfaction relief is not sufficient for greater realized decomposition. `cn_s2` and `cn_s3` improve microbial satisfaction while direct HR is lower or nearly unchanged, whereas `cn_s4` increases both satisfaction and HR modestly. `cn_s1` has a reproducible upper-range discontinuity across several responses; this is reported as descriptive model behavior, not a threshold.

These are baseline-conditioned, range-dependent responses from separately perturbed ensembles. They are not PAWN, Sobol, joint/global sensitivity, interaction, causal mediation, optimization, tuning, parameter recommendations, cross-site/configuration evidence, or proof of whole-ecosystem N limitation.
