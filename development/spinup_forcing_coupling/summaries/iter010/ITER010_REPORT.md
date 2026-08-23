# Iter010 TIM terminal-partition topology diagnosis

## Closeout identity

- Iteration ID: `iter010`
- Status: `completed`
- Work type: `implementation`
- Objective: `TIM terminal-partition topology diagnosis`
- Bounded scope: `Six immutable TIM chains; ABBY/JERC; seeds 9009-9011; terminal/rolling topology diagnostics; conditional prediction skip`
- Overall acceptance result: `pass`
- Decision: `ABBY and JERC two_basin_declined; forced terminal screen declined as evidence for two physical basins; replace the screen, reassess TIM/JERC, and route to ABBY proposal-scale Experiment 5`
- Output root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/spinup_forcing_coupling`
- Summary path: `development/spinup_forcing_coupling/summaries/iter010`

## Question, inputs, and immutable construction

Iter010 asks whether the forced two-means terminal partitions in the six Iter009 `TIM` chains are
reproducible separated physical basins, a connected ridge, a broad/unimodal screen artifact, or
inconclusive. ABBY and JERC are evaluated separately. The source data are the six immutable
`raw_chain.npz` archives and their HDF, metadata, checkpoint, and selection-ledger provenance,
locked by `iter010_source_manifest.json`. Every chain has 8,000 steps, 64 walkers, and 15 physical
parameters. All source identities, shapes, bounds, parameter order, finiteness, site/seed fields,
and physical-log-posterior convention passed preflight.

The reference color is the deterministic lower/higher two-means assignment of each walker's
median physical log posterior over steps 7001--8000: blue is the lower-median group and orange is
the higher-median group. Terminal windows are 500, 1,000, 2,000, and 4,000 steps. Rolling windows
are 1,000 steps with stride 250 over steps 4001--8000. Late-half comparisons use steps 4001--6000
and 6001--8000. Corner and PCA figures use the same 32 equally spaced draws per walker from steps
4001--8000, exactly 2,048 draws per chain. Physical PCA coordinates are normalized by prior width.
No smoothing beyond the displayed histograms is used; KDE bandwidth factors are supporting
measurements only.

## Quantitative chain evidence

Positive `BIC2-BIC1` favors one Gaussian over the forced two-component approximation. Classifier
accuracy near 0.5, tiny prior-normalized centroid distance, unstable 2,000-versus-4,000-step
assignment, and frequent rolling reassignment all oppose separated physical basins.

| Site | Seed | Forced groups | BIC2-BIC1 | Classifier | Centroid distance | Assignment agreement | Occupancy change | Transitions | Max residence windows | Max standardized parameter difference |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ABBY | 9009 | 32 / 32 | 15.355 | 0.474 | 0.00193 | 0.859 | 0.109 | 184 | 13 | 0.291 |
| ABBY | 9010 | 36 / 28 | 14.560 | 0.473 | 0.00358 | 0.750 | 0.219 | 177 | 13 | 0.228 |
| ABBY | 9011 | 33 / 31 | 16.437 | 0.477 | 0.00300 | 0.797 | 0.031 | 196 | 13 | 0.324 |
| JERC | 9009 | 29 / 35 | 12.328 | 0.458 | 0.00238 | 0.781 | 0.000 | 194 | 10 | 0.255 |
| JERC | 9010 | 28 / 36 | 14.132 | 0.486 | 0.00589 | 0.891 | 0.047 | 196 | 13 | 0.341 |
| JERC | 9011 | 34 / 30 | 11.816 | 0.473 | 0.00666 | 0.625 | 0.500 | 170 | 13 | 0.287 |

Across seeds, corresponding group-location distances are only 0.00247 at ABBY and 0.00895 at
JERC in prior-width-normalized physical space. This supports reproducibility of the broad occupied
location, but it does not rescue the forced partition: all six chains oppose robust scalar
separation, physical multivariate separation, and temporal persistence.

These metrics test three different aspects of the proposed two-band interpretation:

  - Scalar separation: are there actually two populations of log-posterior levels?
  - Physical separation: do those labels correspond to different regions of the 15-dimensional parameter space?
  - Temporal persistence: do walkers remain in those groups over time?

  All metrics are computed separately for each site and seed. The common reference split is based on each walker’s median physical log posterior over steps 7001–8000.

  ## Metric-by-metric explanation

| Metric                                   | What it measures                                                | Interpretation                                                  |
|------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------|
| Forced groups                            | Number of walkers assigned to lower/higher terminal-log-posterior groups        | Shows balance only; it does not establish separation           |                                                   |
| BIC2−BIC1                                | Whether two Gaussian populations describe the 64 terminal medians better than one Gaussian after complexity penalty     | Negative favors two populations; positive favors one           |
| Classifier                               | Whether physical parameter vectors can recover the scalar group label      | Near 1 means physical separation; near 0.5 means overlap       |                                                               |
| Centroid distance                        | Distance between group-average physical parameter vectors after prior-width normalization     | Large means physically separated centers; near zero means nearly identical centers     |
| Assignment agreement                     | Stability of walker labels under different terminal windows     | Near 1 means stable labels; lower values mean window- sensitive labels          |
| Occupancy change                         | Change in the fraction of walkers assigned to the higher group between late-chain halves       | Near zero means stable aggregate occupancy; large means unstable occupancy      |
| Transitions                              | Total walker label changes between adjacent rolling windows     | Few changes suggest persistence; many changes suggest unstable labels                                                |
| Max residence windows                    | Longest uninterrupted run in one rolling group by any walker    | Large values show at least one persistent walker, but not necessarily persistent populations                             |
| Max standardized parameter difference    | Largest group-mean difference among the 15 parameters,measured in chain-standard-deviation units          | Large values indicate physical differentiation; values near zero indicate overlap     |


## Immutable topology synthesis

| Site | Scalar separation | Multivariate separation | Temporal persistence | Corresponding locations | Topology result |
| --- | --- | --- | --- | --- | --- |
| ABBY | oppose in 3/3 seeds | oppose in 3/3 seeds | oppose in 3/3 seeds | support across seeds | `two_basin_declined` |
| JERC | oppose in 3/3 seeds | oppose in 3/3 seeds | oppose in 3/3 seeds | support across seeds | `two_basin_declined` |

The formal result is therefore `two_basin_declined` at both sites. The occupied physical region is
reproducible, while the forced lower/higher labels are not robust scalar bands, separable physical
groups, or temporally persistent states. Iter010 does not claim that every posterior projection is
unimodal, nor does it mathematically prove connectedness; it declines the specific claim that the
Iter009 terminal screen established two physical basins.

## Figure construction and caption catalog

The following construction applies to every listed chain figure. Figure 1 plots all 64 physical
log-posterior traces, colored by reference assignment; read persistent color-separated levels as
basin support and repeated overlap/crossing as opposition. Figure 2 sorts terminal walker medians
and shows the forced threshold, group sizes, and group density/rug evidence; read a stable empty gap
as scalar support and overlap or window-sensitive gaps as opposition. Figure 3 is the 15-parameter
physical corner using the common 2,048 draws; read non-overlapping colored clouds as multivariate
support and overlapping clouds as opposition. Figure 4 is prior-width-normalized PCA with the same
draws and walker trajectories; read disconnected occupied clouds as basin support and intermediate
trajectories/overlap as opposition or ridge evidence. Figure 5 shows rolling assignments,
transitions, residence lengths, and occupancy; read stable labels and occupancy as persistence and
frequent reassignment as opposition. None of these figures alone establishes posterior weights,
stationarity, exchange, or mathematical convergence.

### ABBY seed 9009

- Figure `abby_seed9009_01_traces.png`: asks whether terminal colors occupy persistent physical-log-
  posterior levels. The 7001--8000 colors overlap across the full trace; implication: scalar basin
  persistence is opposed. It cannot identify physical separation alone.
- Figure `abby_seed9009_02_terminal.png`: asks whether the forced 32/32 split has a robust scalar
  gap. BIC2 exceeds BIC1 by 15.355 and the 2,000/4,000 assignment agreement is 0.859; implication:
  the forced threshold is unstable. It cannot establish multivariate topology.
- Figure `abby_seed9009_03_corner.png`: asks whether colors separate in 15-dimensional physical
  marginals and pairs. Classifier accuracy is 0.474 and the largest standardized difference is
  0.291; implication: physical groups overlap. Marginal overlap cannot prove every path connected.
- Figure `abby_seed9009_04_pca.png`: asks whether prior-normalized occupied space has disconnected
  clouds. Centroid distance is 0.00193 with intermediate trajectories; implication: no resolved
  basin separation. Two PCA coordinates cannot preserve every high-dimensional distinction.
- Figure `abby_seed9009_05_rolling.png`: asks whether assignments persist through time. Agreement is
  0.859, occupancy changes 0.109, and 184 rolling transitions occur; implication: persistence is
  opposed. Rolling windows are diagnostic summaries, not independent samples.

### ABBY seed 9010

- Figure `abby_seed9010_01_traces.png`: the 36/28 reference colors repeatedly overlap; scalar basin
  persistence is opposed, while physical topology remains a separate question.
- Figure `abby_seed9010_02_terminal.png`: BIC2-BIC1 is 14.560 and assignment agreement is 0.750;
  the forced scalar split is not robust across windows and cannot prove modes.
- Figure `abby_seed9010_03_corner.png`: classifier accuracy is 0.473 and the largest standardized
  difference is 0.228; colored physical clouds overlap, opposing multivariate separation.
- Figure `abby_seed9010_04_pca.png`: centroid distance is 0.00358 and occupied trajectories bridge
  the colors; no disconnected PCA support is observed, without claiming full-space proof.
- Figure `abby_seed9010_05_rolling.png`: occupancy changes 0.219 with 177 transitions and agreement
  0.750; assignments are temporally unstable, not posterior basin weights.

### ABBY seed 9011

- Figure `abby_seed9011_01_traces.png`: the 33/31 colors overlap through time; persistent scalar
  levels are not supported, and trace overlap alone cannot prove connectedness.
- Figure `abby_seed9011_02_terminal.png`: BIC2-BIC1 is 16.437 and agreement is 0.797; the forced
  threshold is window-sensitive and does not establish two scalar populations.
- Figure `abby_seed9011_03_corner.png`: classifier accuracy is 0.477 and the largest standardized
  difference is 0.324; physical groups overlap, opposing multivariate separation.
- Figure `abby_seed9011_04_pca.png`: centroid distance is 0.00300 with intermediate occupied
  trajectories; PCA does not resolve separated basins and cannot exclude subtler dimensions.
- Figure `abby_seed9011_05_rolling.png`: 196 transitions occur; although occupancy change is only
  0.031, agreement is 0.797, so the immutable temporal requirement is opposed.

### JERC seed 9009

- Figure `jerc_seed9009_01_traces.png`: the 29/35 colors overlap throughout the physical-log-
  posterior trace; persistent scalar levels are opposed.
- Figure `jerc_seed9009_02_terminal.png`: BIC2-BIC1 is 12.328 and assignment agreement is 0.781;
  the forced threshold is unstable and cannot establish physical modes.
- Figure `jerc_seed9009_03_corner.png`: classifier accuracy is 0.458 and the largest standardized
  difference is 0.255; overlapping physical clouds oppose multivariate separation.
- Figure `jerc_seed9009_04_pca.png`: centroid distance is 0.00238 with intermediate trajectories;
  no disconnected occupied regions are resolved in PCA, which is not full-space proof.
- Figure `jerc_seed9009_05_rolling.png`: occupancy change is 0.000 but agreement is 0.781 with 194
  transitions; stable aggregate occupancy does not mean stable walker assignments.

### JERC seed 9010

- Figure `jerc_seed9010_01_traces.png`: the 28/36 colors overlap through time, opposing persistent
  scalar bands without deciding full physical topology alone.
- Figure `jerc_seed9010_02_terminal.png`: BIC2-BIC1 is 14.132 and agreement is 0.891, just below the
  immutable 0.90 threshold; scalar separation is not robust.
- Figure `jerc_seed9010_03_corner.png`: classifier accuracy is 0.486 and the largest standardized
  difference is 0.341; physical groups overlap and do not support separated basins.
- Figure `jerc_seed9010_04_pca.png`: centroid distance is 0.00589 with intermediate trajectories;
  PCA supplies no disconnected-basin evidence and cannot certify stationarity.
- Figure `jerc_seed9010_05_rolling.png`: occupancy change is 0.047 but 196 transitions occur and
  agreement is 0.891; temporal persistence fails the all-criteria rule.

### JERC seed 9011

- Figure `jerc_seed9011_01_traces.png`: the 34/30 reference colors overlap through time; persistent
  scalar levels are opposed.
- Figure `jerc_seed9011_02_terminal.png`: BIC2-BIC1 is 11.816 and agreement is 0.625; the forced
  threshold is strongly window-sensitive and cannot establish two modes.
- Figure `jerc_seed9011_03_corner.png`: classifier accuracy is 0.473 and the largest standardized
  difference is 0.287; overlapping physical groups oppose multivariate separation.
- Figure `jerc_seed9011_04_pca.png`: centroid distance is 0.00666 with intermediate trajectories;
  no disconnected occupied clouds are resolved, without excluding all nonlinear structure.
- Figure `jerc_seed9011_05_rolling.png`: occupancy changes 0.500 with 170 transitions and agreement
  0.625; temporal persistence is decisively opposed.

### Three-seed site syntheses

- Figure `abby_three_seed_comparison.png`: compares GMM BIC, classifier/centroid separation, and
  assignment stability for ABBY seeds 9009--9011 using the same physical normalization and no
  smoothing. All three seeds oppose scalar, multivariate, and temporal separation while same-group
  locations reproduce within 0.00247 prior-normalized distance. Read consistency across all bars as
  site-level evidence; the figure cannot establish convergence or posterior weights.
- Figure `jerc_three_seed_comparison.png`: applies the identical construction to JERC seeds
  9009--9011. All three oppose scalar, multivariate, and temporal separation while same-group
  locations reproduce within 0.00895. The cross-seed consistency supports `two_basin_declined`,
  but the figure cannot prove every high-dimensional path connected.

## Secondary convergence implication

With the forced terminal screen declined, JERC retains the other Iter009 TIM criteria: mean
acceptance, low-acceptance walkers, stable tau, steps per tau, split R-hat, and cross-seed distance.
Its prescribed label is `convergence_supported_under_revised_iter009_diagnostics`. This is a
screening conclusion, not mathematical proof of stationarity or independent posterior draws.

ABBY does not receive that label. Its forced partition is also declined, but all three TIM/ABBY
chains retain mean acceptance near 0.146--0.148, below the immutable 0.20 floor, with marked
transformed-coordinate saturation. The conclusion is
`convergence_not_established_abby_acceptance_and_saturation`. A general cross-site TIM convergence
claim is therefore not made.

## Conditional prediction and equifinality

Neither site is `two_basin_supported`, so the conditional prediction branch is correctly
`skipped` with zero evaluations. Equifinality is `not_applicable_no_supported_basins`; neither
`equifinal_comparable` nor `distinct_solutions_unequal_support` is assigned. The skip cannot be
used to compare predictive support, basin weights, or calibrated scientific adequacy.

## Limitations

- The topology result declines the forced screen; it does not prove global unimodality or a unique
  connected posterior manifold.
- Ensemble walkers interact, so assignment counts and transition summaries are diagnostic rather
  than independent-binomial evidence.
- PCA and pairwise corners can miss nonlinear high-dimensional separation.
- Existing chain length is not extended, and thinning is not used to manufacture convergence.
- ABBY's acceptance/saturation problem remains unresolved and prevents a general TIM convergence
  conclusion.
- `/xdisk` products are temporary and unbacked; compact evidence does not replace raw archives.

## Routed next experiment

Exactly one route is selected: replace the forced terminal screen in downstream interpretation,
retain the revised JERC assessment, and run an ABBY-only, target-equivalent DE proposal-scale pilot
as Iter011. The complete planning-only Iter011 proposal is recorded unchanged in
`iterations/iter010.md` and `handoff/CURRENT.md`. Iter011 is not initialized and has no execution,
scheduler, retry, cancellation, commit, or directory-creation authority.

Next state: `Iter011 is not_initialized; its complete planning-only ABBY target-equivalent DE proposal-scale pilot is recorded in iterations/iter010.md and CURRENT.md, and execution requires a fresh consolidated kickoff package with explicit approval.`
