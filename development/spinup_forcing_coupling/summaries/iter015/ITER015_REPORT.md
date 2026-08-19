# Iter015 hybrid-init configuration matrix

## Integrity

All 36 immutable packages passed selection-ledger, chain, Jacobian, and plot gates.

## Site decisions

- ABBY: `inconclusive_seed_instability`; selected: none; eligible: hourly_1.00.
- JERC: `inconclusive_seed_instability`; selected: none; eligible: none.

## Six-configuration medians

| Site | Configuration | Acceptance | Saturation | Min steps/tau | Abs lag-24 | Sigma edge | Width | MAP RMSE | ELM RMSE |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ABBY | hourly/0.50 | 0.32781 | 0.4377 | 10.299 | 0.97265 | 0.0072115 | 0.34436 | 4.7212 | 6.6896 |
| ABBY | hourly/0.75 | 0.22542 | 0.47953 | 9.0653 | 0.97267 | 0.0066964 | 0.00050014 | 4.6986 | 6.6896 |
| ABBY | hourly/1.00 | 0.13538 | 0.52609 | 18.731 | 0.97265 | 0.0066964 | 0.46115 | 4.7213 | 6.6896 |
| ABBY | daily/0.50 | 0.26943 | 0.011975 | 10.361 | 0.9722 | 0 | 0.023529 | 4.7319 | 6.6896 |
| ABBY | daily/0.75 | 0.15761 | 0.017051 | 10.853 | 0.97256 | 0 | 0.052184 | 4.7294 | 6.6896 |
| ABBY | daily/1.00 | 0.059295 | 0.045998 | 10.984 | 0.97269 | 0 | 0.19631 | 4.7108 | 6.6896 |
| JERC | hourly/0.50 | 0.10292 | 0 | 8.7889 | 0.91641 | 0 | 0.34522 | 0.66744 | 1.5752 |
| JERC | hourly/0.75 | 0.22109 | 0 | 8.7041 | 0.91617 | 0 | 0.48541 | 0.66658 | 1.5752 |
| JERC | hourly/1.00 | 0.15427 | 0 | 8.6296 | 0.9176 | 0 | 0.89615 | 0.66771 | 1.5752 |
| JERC | daily/0.50 | 0.025031 | 0 | 8.9434 | 0.91868 | 0 | 0.10789 | 0.67285 | 1.5752 |
| JERC | daily/0.75 | 0.014557 | 0 | 8.9698 | 0.92022 | 0 | 0.081714 | 0.67358 | 1.5752 |
| JERC | daily/1.00 | 0.012262 | 0 | 8.9151 | 0.92071 | 0 | 0.11225 | 0.67331 | 1.5752 |
