# Iter012 ABBY Respiration-Fraction OAT Extension Result

- Status: `completed`; overall acceptance: `pass`.
- Scope: 27 separate ABBY vertical-soil-carbon OAT ensembles, 100 members each, extending Iter011 with `rf_l1s1`, `rf_l2s2`, `rf_l3s3`, `rf_s1s2`, `rf_s2s3`, and `rf_s3s4` over separate `0.1--0.9` ranges. Results are baseline-conditioned and range-dependent; they are not global-sensitivity, interaction, causal, tuning, threshold, or parameter-recommendation evidence.
- Inputs: exactly 27 transient pickles, 27 configs, 27 parameter files, and 27 restart cases with 2,700 final restart files. Transient coverage is 61,320 hourly samples/member for 2018--2024 noleap; spinup states are the final `0201-01-01` restarts.
- Outputs: exactly 103,114 primary CSV data rows and 11 PNGs. Input manifest `2d041f0d3e952bc9c22bb757ca0533ded4baecd80d8b56daa998e9a0b3ae6977`; output manifest `a24daac2c93c868182ed347e400938252f28a815645cb7cba41d7d61e01ec0ae`.
- Execution: preflights `24137742`, `24137829`, `24137929`, and `24149109`, plus diagnostic `24149371`, all completed `0:0`. Allocation-pegged Slurm MaxRSS readings prompted approved independent measurement and right-sizing. Reproducible GNU-time peaks near 6.41 GB supported a four-CPU/20-GB final shape; diagnostic peak was `6408012K`, with no swaps. Generation, artifact validation, and atomic publication passed.

## Methods and support

- Transient endpoints are arithmetic temporal means of direct model `SR`, direct model `HR`, direct model `GPP`, direct model `LITFALL`, and the sum of `CWDC`, `LITR1C`--`LITR3C`, and `SOIL1C`--`SOIL4C`. Flux units are `gC m-2 day-1`; transient decomposer stock is `gC m-2`.
- Final spinup C/N/P states sum every stored vertical element of the exact eight lowercase `_vr` decomposer pools. Units are `gC m-2`, `gN m-2`, and `gP m-2`.
- The descriptive screening score is `100 * (P95 - P05) / abs(ensemble median)`, ranked separately within each endpoint across the 27 declared ranges. All 135 transient and 81 spinup scores are supported.
- Observed SR is contextual only: mean `7.501337 gC m-2 day-1` over 26,264 valid hours (`42.83%` of the 61,320-hour model window). It is shown as a reference line and never enters scores or ranks.

## Range-conditional results

Transient leaders by response-spread score are:

| Endpoint | First | Second | Third |
| --- | --- | --- | --- |
| SR mean | `rf_s2s3` 73.4% | `act25` 65.3% | `leaf_long` 56.5% |
| HR mean | `rf_s2s3` 77.4% | `act25` 74.5% | `leaf_long` 66.6% |
| GPP mean | `leaf_long` 68.4% | `act25` 65.1% | `rf_s2s3` 61.6% |
| LITFALL mean | `rf_s2s3` 77.3% | `act25` 74.5% | `leaf_long` 63.4% |
| transient decomposer C | `k_s4` 3359.5% | `k_s3` 600.4% | `k_s2` 142.0% |

For final-spinup decomposer C, `k_s4` (1778.9%) and `k_s3` (360.8%) remain first and second, while `rf_s2s3` is third (156.9%). Final-spinup N is led by `k_s4` (2010.6%), `k_s3` (389.3%), and `k_s2` (105.7%), with `rf_s3s4` fourth (104.0%). Final-spinup P is led by `k_s4` (1944.6%), `k_s3` (382.2%), and `k_s2` (175.9%), followed by `rf_s3s4` (101.2%) and `rf_s2s3` (97.2%). These scores compare spread over different declared parameter ranges and are not derivatives or probability-weighted importance.

Among the six added respiration fractions, `rf_s2s3` has the largest flux response spreads and ranks first for mean SR, HR, and LITFALL, third for GPP, and third for final-spinup decomposer C. `rf_s3s4` is fourth for transient decomposer C and final-spinup N/P. These are baseline-conditioned sampled-range patterns, not evidence that changing a fraction alone will cause the same response outside these ensembles.

## Idealized decomposition pathways

The accumulated pathways are constructed diagnostics and remain distinct from direct model `HR`. Across all 2,700 parameter-member cases, mean member-level N-limited/potential and P-limited/potential ratios are `0.305316` and `0.401703`. P-limited/potential exceeds N-limited/potential in `2693/2700` cases (`99.74%`), not universally.

The six new-parameter means are:

| Parameter | Mean N/potential | Mean P/potential | P greater than N |
| --- | ---: | ---: | ---: |
| `rf_l1s1` | 0.354295 | 0.491135 | 100/100 |
| `rf_l2s2` | 0.338190 | 0.422546 | 100/100 |
| `rf_l3s3` | 0.376710 | 0.489796 | 100/100 |
| `rf_s1s2` | 0.375142 | 0.482229 | 100/100 |
| `rf_s2s3` | 0.360384 | 0.448841 | 93/100 |
| `rf_s3s4` | 0.273415 | 0.355015 | 100/100 |

The seven exceptions are all low-range `rf_s2s3` samples (`0.1008--0.1544`; normalized positions about `0.0010--0.0680`). This is sampled-range nonlinearity, not a confirmed threshold or causal transition. Pathway comparisons do not establish whole-ecosystem nutrient limitation.

## Validation and limitations

- Independent reviewer `/root/iter012_review` reproduced all 135 transient and 81 spinup scores, supports, rejection fields, ranks, all response bins, all 72,900 pathway rows and 810 pathway curves, exact row/figure counts, and every artifact hash.
- Visual review passed all 11 figures: each atlas has 27 populated panels in the intended 6x5 layout with three unused panels disabled; heatmaps, ranks, units, native markers, observed SR line, and pathway legend are legible. No compensation, litter-ratio, or standard-deviation family was unintentionally published.
- Puma `sacct` intermittently returned allocation-pegged MaxRSS. Repeated GNU-time measurements and no-swap evidence provide the applicable process-memory evidence; diagnostic peak was about 6.11 GiB under a 20-GiB allocation.
- `/xdisk` is temporary and unbacked. Observation support is partial and contextual. Separate OAT ranges are not probability distributions and do not measure interactions or global variance contributions.
