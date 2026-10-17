# Iter009 ABBY Vertical-Soil-Carbon C:N Pool-Context Result

- Iteration ID: `iter009`
- Status: `completed`
- Work type: `implementation`
- Objective: Amend the Iter008 N/P-stress diagnostic by separating mean and temporal-variability figures, restoring observed SR context, and adding pool-C and realized pool-HR-per-C responses.
- Bounded scope: four exact ABBY vertical-soil-carbon C:N pickles; 400 members; 47 metrics; 74 response endpoints per parameter; 37,812 CSV rows; 17 figures; baseline-conditioned descriptive OAT only.
- Overall acceptance result: `pass`.
- Decision: Accept the validated amendment. Pool stocks and realized respiration per pool C respond differently to C:N perturbations; most notably, the `cn_s1` endpoint-bin contrast increases SOIL1C by `53.01%` while SOIL1 HR is nearly unchanged and SOIL1 HR/C falls `34.99%`.
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter009_abby_ctrlvertc_cn_pool_context/results`

## Quantitative evidence

- Preflight `24019322` and diagnostic `24019366` completed `0:0` on attempt one in `00:01:12` and `00:01:17`. Batch peak memory was 19.72 GB for each work unit against the 60 GB request. No retry or cancellation was used.
- Input manifest SHA-256 is `bb2836591c0857fb45a560cc1d7fdfb2d85053571394a85633f10855f982bf62`; validation receipt SHA-256 is `04bb75cefee96589f4b3d4b452633865dc6de92352b7dc6f9e9a7d08c58fe0bd`; output manifest SHA-256 is `afa885d5642b7cd886e5dfc05afd2575c803e91250c040604d23333fa5b95aae`.
- The published package contains exactly 4 parameter rows, 47 metric-definition rows, 400 member rows, 32,560 response rows, 4,800 ratio-support rows, one observation row, 37,812 CSV data rows, and 17 PNGs. All 4,800 ratios are supported; every member has 61,320 model hours.
- The contextual ABBY SR observation has 26,264 valid hours (`42.83%` of 61,320), mean `7.501337`, and population temporal standard deviation `2.627639` gC m-2 day-1.
- From the lowest to highest sampled-parameter-bin medians, matched soil-pool C, HR, and realized HR/C change by `+53.01%`, `-0.53%`, and `-34.99%` for `cn_s1`; `-3.90%`, `-4.76%`, and `-0.89%` for `cn_s2`; `-0.47%`, `-0.66%`, and `-0.18%` for `cn_s3`; and `+3.56%`, `+4.64%`, and `+1.04%` for `cn_s4`.
- Other matched-pool realized ratios include LITR1 HR/C `+38.50%` under `cn_s2` and LITR3 HR/C `+32.18%`/`+27.74%` under `cn_s3`/`cn_s4`. These are range-conditional endpoint-bin contrasts, not global, causal, prescribed-rate, or threshold estimates.

## Validation and interpretation

- Generator, exact artifact validator, and atomic-publication markers all passed. Manifest membership, hashes, schemas, counts, units, endpoint multiplicity, observation identity, ratio support, and absence of attempt-local staging were validated.
- All 17 full-resolution figures passed visual inspection. Mean and temporal-SD families are separated; observed SR mean and SD appear only on their corresponding rows; both new figures contain all eight ordered pools; zero `CWDC_HR` remains represented; and the four superseded mixed files are absent.
- The pool context supports a stock-versus-realized-rate distinction. In particular, greater SOIL1C under the `cn_s1` range is not accompanied by greater SOIL1 HR, whereas changes for the other matched soil pools are smaller and more nearly coherent. This complements, but does not turn into a causal explanation of, Iter008's microbial nutrient-satisfaction responses.
- Interpretation remains limited to the four separate baseline-conditioned ABBY OAT ensembles and their declared ranges. No interaction, PAWN/Sobol/global sensitivity, optimization, parameter recommendation, cross-site/configuration, whole-ecosystem limitation, or exact threshold claim is supported.
