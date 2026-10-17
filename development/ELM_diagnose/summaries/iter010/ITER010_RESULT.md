# Iter010 ABBY C:N Carbon-Balance Result

- Status: `completed`; overall acceptance: `pass`.
- Direct model `HR` was used exactly as approved; no pool-HR reconstruction was used.
- Preflight `24025653` and diagnostic `24025871` completed `0:0` in `00:01:05` and `00:00:56`. Output manifest: `80afe70badeb0a0f7cd2e3bda3be4ca1ec5fceef8543891b47a39036590b5c3c`.
- The package contains exactly 39,542 CSV data rows and 21 PNGs; all 23 Iter009 core artifacts are byte-identical, all 400 closure ratios are supported, and all calculation, artifact, publication, and visual gates pass.

## Scientific result

No member lies within 5% of the absolute 1:1 balance. Median absolute closure errors are `8.91%`, `9.07%`, `8.91%`, and `8.79%` for `cn_s1`--`cn_s4`; `HR + delta_C` systematically exceeds declared `LITFALL` by about 151 gC m-2. The very high absolute-scale R-squared values reflect a nearly constant offset and do not establish closure.

Lowest-to-highest-bin contrasts show that direct HR accounts for about `88.6%`, `91.9%`, `101.2%`, and `87.4%` of the `cn_s1`--`cn_s4` input responses; storage change accounts for about `11.0%`, `7.3%`, `1.3%`, and `11.5%`. Thus direct HR descriptively tracks carbon-input response contrasts, with a non-negligible storage contribution for pools 1, 2, and 4.

Because the declared boundary is explicitly partial and absolute nonclosure is about 9%, this result does not demonstrate that historical or equilibrium HR is constrained solely by carbon entering the decomposition subsystem. It supports only baseline-conditioned response tracking within the four separate ABBY OAT ensembles.
