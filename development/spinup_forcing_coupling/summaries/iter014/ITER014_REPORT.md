# Iter014 — JERC high-likelihood candidate-pool reconstruction

Decision: `partial_repair`

## Variant outcomes

| Pool rule | Geometry | MCMC | Mean acc | Cross-seed W | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| rank_dominated | fail (`cond≈1.72e7`) | skipped | — | — | `geometry_gate_failed` |
| hybrid_high_l_maximin | pass (`cond≈359`) | 3×64×8000 | 0.1898 | 0.4365 | `partial_repair` |

Control (Iter012 diversity): mean acc ≈0.1866; W ≈0.5484.

Hybrid seed acceptances: 0.0891 / 0.2211 / 0.2591. Diagnostic MCMC label:
`fixed_length_inconclusive`. No posterior promotion.

## Interpretation

Top-likelihood rank pools are scientifically infeasible under locked geometry gates
(ill-conditioned high-L ridge). Hybrid high-L+maximin rebuild improves seed agreement
versus the diversity control but does not clear repair thresholds (acc≥0.25 and W≤0.05).

## Artifact paths

- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014`
- Aggregate: `summaries/iter014/aggregate_result.json`
- Accounting: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling/spinup_forcing_coupling_iter014/accounting.csv`
