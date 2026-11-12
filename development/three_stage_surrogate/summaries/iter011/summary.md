# Iter011 - SR capacity versus regularization

- Iteration/work type: `iter011` / `experiment`.
- Result: `pass`; decision `sr_capacity_regularization_configuration_selected`.
- Selected development candidate: B, `(96,48)`, `tanh`, alpha `0.01`, otherwise frozen Iter010
  Adam controls. This is not a release or production model.
- Design: five locked configurations, 20 new matched 655/164 development splits, 100 fits,
  fixed 44-feature inputs, and no fixed-test or upstream-model execution.

## Five-candidate pooled validation comparison

Values are mean across splits; parentheses give median. Bias is signed. Full quantiles, MAE,
train metrics, and split distributions are retained in the adjacent CSV files.

| ID | Hourly R2 | Hourly RMSE | Daily R2 | Daily RMSE | Daily bias |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 0.8023 (0.8024) | 0.9254 (0.9260) | 0.8199 (0.8200) | 0.8657 (0.8649) | 0.0108 (0.0030) |
| B | 0.8493 (0.8450) | 0.8031 (0.8207) | 0.8558 (0.8510) | 0.7692 (0.7877) | 0.0386 (0.0262) |
| C | 0.8029 (0.8012) | 0.9238 (0.9197) | 0.8206 (0.8194) | 0.8640 (0.8605) | 0.0168 (0.0183) |
| D | 0.8397 (0.8508) | 0.8286 (0.8162) | 0.8456 (0.8567) | 0.7961 (0.7846) | 0.0369 (0.0345) |
| E | 0.7986 (0.7957) | 0.9332 (0.9386) | 0.8095 (0.8059) | 0.8895 (0.8961) | 0.0415 (0.0355) |

## Site-specific validation for selected B

| Site | Hourly R2 | Hourly RMSE | Daily R2 | Daily RMSE | Daily bias |
| --- | ---: | ---: | ---: | ---: | ---: |
| ABBY | 0.8107 (0.8243) | 0.5827 (0.5831) | 0.8160 (0.8300) | 0.5628 (0.5638) | 0.0210 (0.0186) |
| JERC | 0.8099 (0.7968) | 0.9735 (0.9982) | 0.8165 (0.8028) | 0.9293 (0.9550) | 0.0562 (0.0542) |

## Paired interpretation and recommendation

- Weaker regularization is supported: B beat A in pooled daily RMSE on 18/20 matched splits
  (mean/median improvement `0.0965/0.0803`), and D beat C on 16/20
  (`0.0679/0.0588`), without a site-cost flag.
- Increased capacity is not supported: C versus A was nearly neutral (12/20 wins; mean RMSE
  improvement `0.0016`), while D lost to B (6/20 wins; mean improvement `-0.0270`). E was worse
  than both C and D, so the alpha-0.1 result is non-monotonic.
- B improves mean daily RMSE relative to A by 11.1% and D by 3.4%; its improvement is favorable
  in mean at both sites, but B beats D sitewise on only 11/20 ABBY and 12/20 JERC splits.
- B has a larger pooled daily train-validation RMSE gap (`0.4529`) than A (`0.1980`) and greater
  split variability, although it does not cross the locked poor-stability threshold. These results
  support B only as the preferred development candidate for a separately approved fresh robustness
  iteration; they do not establish release readiness or globally separate causal effects.

The full external evidence remains under the approved Iter011 output root. No next iteration is
authorized. Campaign-plan amendment recommendation: `none`.
