# Iter009 sampler-geometry qualification report

Decision route: `investigate_multimodality_nonidentifiability_likelihood_or_model_structure`
Selected arm: `none`

## Immutable qualification matrix

| Arm | Site | Qualified | Worst split R-hat | Worst cross-seed width fraction |
| --- | --- | --- | ---: | ---: |
| B | ABBY | False | 2.66468 | 0.777247 |
| B | JERC | False | 4.58494 | 0.421616 |
| T | ABBY | False | 3.71179 | 0.503026 |
| T | JERC | False | 5.4533 | 0.378763 |
| I | ABBY | False | 1.74349 | 0.0212515 |
| I | JERC | False | 1.17066 | 0.00840954 |
| M | ABBY | False | 1.48017 | 0.441181 |
| M | JERC | False | 1.37898 | 0.477543 |
| TIM | ABBY | False | 1.0317 | 0.000713334 |
| TIM | JERC | False | 1.02137 | 0.00260268 |

## Interpretation

All geometry statistics use the physical posterior. Split R-hat is a screening statistic because ensemble walkers interact; nominal unthinned ESS is reported per leaf and is not an independent qualification gate. Boundary and transformed-coordinate saturation are report-only evidence. No likelihood, skill, or predictive metric participates in selection.
