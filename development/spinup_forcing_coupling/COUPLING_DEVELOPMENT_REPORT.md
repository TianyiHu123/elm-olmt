# Spinup--Forcing Coupling Development Report

## Purpose and final status

This is the integrated, human-readable record of the completed
development/spinup_forcing_coupling line. It condenses Iter001--Iter018 into
the decisions that changed the work, while linking reports that retain the full
metric tables, raw-chain diagnostics, scheduler receipts, and artifact identities.

The work delivered a reproducible, HPC-exercised workflow that couples a spinup
surrogate to a historical forcing surrogate and uses MCMC to construct
site-local soil-BGC parameter MAP candidates for soil respiration (SR). The
final Iter018 release is technically operational_release_ready: nine site
packages and 81 optimization leaves passed integrity and handoff validation.
This is deliberately narrower than posterior validation, scientific
calibration, or cross-site parameter ranking.

The authoritative terminal state remains the [handoff](handoff/CURRENT.md).
See [WORKFLOW.md](WORKFLOW.md) for lifecycle and authority policy, and
[Iter018's closeout](summaries/iter018/ITER018_REPORT.md) for detailed final receipts.

---

# Part I -- Development narrative

## 1. What the final workflow enables

For a supported site and a locked target/configuration, a user can:

1. optimize key soil biogeochemistry (BGC) parameters for ELM with an MCMC
   workflow driven by the coupled spinup--historical surrogate;
2. evaluate optimization behavior with auditable MCMC diagnostics and evaluate
   the optimized SR simulation with model-skill metrics;
3. produce a standard visual package: parameter-distribution/corner plots,
   MCMC posterior and diagnostic traces, and optimized SR time-series and
   ensemble overlays against observations and ELM precalibration;
4. retain only clearly identified, seed-level MAP candidates for operational
   use, while labeling non-retained or inconclusive outcomes explicitly; and
5. obtain a reproducible handoff containing locked inputs, HPC accounting,
   artifacts, reports, and cross-record validation.

The reusable surfaces are coupling_pipeline.py, optimization_config.py,
mcmc_artifacts.py, mcmc_diagnostics.py, and the three stage adapters
initialize_pipeline.py, run_optimization_campaign.py, and
report_optimization.py. Examples live in examples/optimization/.

## 2. Coupled-surrogate optimization pipeline

~~~mermaid
flowchart LR
    subgraph Inputs[Locked site inputs]
        F[Historical forcing<br/>and site observations]
        S[Spinup surrogate<br/>state for PPE members]
        P[Prior bounds for soil<br/>BGC parameters]
    end

    subgraph Coupling[Coupled surrogate model]
        D[Compose forcing + parameters<br/>+ spinup-state design matrix]
        CS[Historical forcing surrogate<br/>conditioned on spinup state]
        SR[Predicted soil respiration]
    end

    subgraph Optimize[Three-stage optimization workflow]
        I[1. Initialize<br/>candidate pool and walkers]
        M[2. Optimize<br/>multi-seed MCMC]
        R[3. Report<br/>evaluate and retain]
    end

    subgraph Products[Validated products]
        C[Parameter distributions,<br/>posterior traces, diagnostics]
        T[SR time series and<br/>MAP ensemble overlays]
        N[Tier-A MAP parameter files<br/>and validated handoff]
    end

    F --> D
    S --> D
    P --> I
    D --> CS --> SR
    F --> I
    SR --> I --> M --> R
    R --> C
    R --> T
    R --> N
~~~

## 3. Development path at a glance

~~~mermaid
flowchart LR
    A[Standalone forcing surrogate<br/>Iter001-002] --> B[Coupled prediction and<br/>MCMC interface<br/>Iter003-006]
    B --> C[First production MCMC<br/>and diagnosis<br/>Iter007-008]
    C --> D[Sampler geometry and<br/>site-local configuration<br/>Iter009-011]
    D --> E[Reusable initialization<br/>and pool repair<br/>Iter012-015]
    E --> F[Operational procedure<br/>and regression<br/>Iter016-017]
    F --> G[Nine-site operational<br/>release<br/>Iter018]
~~~

| Stage | Iterations | Main outcome, including decisive quantitative change | What it enabled next |
| --- | --- | --- | --- |
| 1. Foundation | Iter001--002 | Inference-validated nine-site forcing surrogate; pooled held-out R² 0.945 and RMSE 0.211 | Real coupled prediction input |
| 2. Coupling bridge and MCMC transition | Iter003--006 | Coupled drop21_corr080 improved over mean-spinup: median R²/KGE about 0.651/0.816 versus -1.894/0.438; Iter006 enabled all three MCMC modes | First bounded production MCMC |
| 3. First MCMC evidence | Iter007--008 | Complete campaigns, but low initial acceptance 0.1197 and approximate ESS 93.8 identified sampler limitations | Controlled sampler and initialization experiments |
| 4. Configuration diagnosis | Iter009--011 | JERC acceptance/steps-per-tau improved from 0.058--0.137 / 7.37 in the initial B arm to 0.245--0.251 / 53.25 with TIM; final hourly/0.75 had 0.349 / 63.01 | Fixed, site-local targets for pipeline testing |
| 5. Pipeline and pool repair | Iter012--015 | Reusable initializer; pure-rank pool condition about 1.72e7 versus feasible hybrid about 359 | Bounded MAP-ensemble procedure |
| 6. Operationalization | Iter016--017 | Tier-A MAP inventory: ABBY 9/9 and JERC 6/9; all four regression paths passed without promoting zero-retention tests | Nine-site release |
| 7. Release and closeout | Iter018 | 81/81 leaves and nine validated site packages; five sites retained 9/9 Tier-A seeds | Terminal handoff; merge remains separate |

## 4. Stage 1 -- establish the forcing-surrogate foundation (Iter001--002)

**Goal.** Create a reproducible nine-site historical SR forcing-surrogate
baseline, then identity-lock the artifact and validate fresh-process inference.

**Result and evidence.** Iter001's replacement 100-seed production completed
after a classified memory failure in the original array. Its pooled held-out
test R² mean was 0.945 and RMSE mean was 0.211. Iter002 completed full-data
release and fresh-process inference validation; full-data characterization was
R² 0.958 and RMSE 0.171.

**Conclusion and lead-in.** The forcing artifact was a validated upstream
dependency, not yet a coupled model. That distinction allowed Iter003 to
compare actual coupled paths to ELM rather than only test interfaces. Full
baseline evidence is in [ITERATION_SUMMARY.md](ITERATION_SUMMARY.md).

## 5. Stage 2 -- build the coupled bridge and transition MCMC to it (Iter003--006)

**Goal.** Build the bridge from the spinup surrogate to the historical forcing
surrogate, show that a member-specific coupled state improves on the previous
mean-spinup surrogate, and then make the coupled predictor usable by the
existing MCMC optimizer.

**Result and evidence.** Iter003--004 completed the nine-site coupled bridge
and demonstrated both coupled spinup variants. The site-median-of-member-median
R²/KGE was about 0.579/0.821 for drop32 and 0.651/0.816 for drop21_corr080.
The comparison that motivated coupling was the older mean-spinup path: Iter005
measured it at R² about -1.894 and KGE about 0.438. Thus the coupled
drop21_corr080 path improved median R² by about 2.55 and KGE by about 0.38
relative to mean-spinup, although it still did not equal the member-restart
offline comparator and coupled ABBY/WREF had negative R².

Iter006 was deliberately a transition iteration rather than another model
comparison: it added three selectable MCMC spinup modes and passed ten
likelihood evaluations for each mean-spinup, member-restart, and coupled mode,
including fail-closed missing-artifact checks.

**Conclusion and lead-in.** The coupled bridge was real model functionality,
not a schema-only connection: it materially outperformed mean-spinup and made
spinup-state information available to MCMC. Iter006 then enabled the existing
MCMC machinery to optimize through the coupled surrogate before
production-scale sampling.

## 6. Stage 3 -- first production MCMC and diagnosis (Iter007--008)

**Goal.** Run the first coupled SR campaigns at ABBY and JERC, retain raw
chains, and diagnose their behavior rather than equating integrity with
scientific convergence.

**Result and evidence.** Iter007's successful joint 64-by-500 campaign retained
all 5,120 postprocessed samples, with mean acceptance 0.1197 and approximate
ESS 93.8. MAP skill was poor at ABBY (RMSE 5.33; R² -3.12) and JERC
(RMSE 2.46; R² -7.36). Iter008 then completed separate 64-by-4,000 campaigns
and validators for both sites; its raw-chain assessment was sampler-limited.

**Conclusion and lead-in.** Coupled MCMC could run reproducibly and create
audit-ready artifacts, but complete products did not establish mixing,
convergence, or scientific adequacy. The route shifted to sampler geometry,
initialization, and site-specific likelihood configuration. See the
[Iter008 comprehensive diagnostic report](summaries/iter008/iter008_comprehensive_mcmc_report.md).

## 7. Stage 4 -- diagnose geometry and select only site-supported settings (Iter009--011)

**Goal.** Separate coordinate, initialization, proposal mixture, terminal
geometry, DE-scale, and hourly/daily likelihood effects.

**Result and evidence.** Iter009 ran 30 chains over five geometry arms. TIM was
strongest but no arm met every immutable qualification screen; maximum split
R-hat was 1.032 at ABBY and 1.021 at JERC. Iter010 declined the two_basin
interpretation at both sites: all six forced screens favored one Gaussian
(BIC2-BIC1 from 11.816 to 16.437), had near-chance physical classifiers
(0.458--0.486), and had 170--196 rolling assignment transitions.

Iter011 completed 36 immutable chains. ABBY daily/0.75 had acceptance 0.23671,
saturation 0.01336, and minimum steps/tau 33.10, supporting it as a
site-specific future setting. JERC daily arms had acceptance 0.027--0.084 and
short effective run lengths; hourly 0.75 and 1.00 remained non-dominated, so
the correct outcome was inconclusive_metric_tradeoff rather than a forced pick.

**Conclusion and lead-in.** The workflow selected a setting where evidence
supported one (ABBY) and preserved an inconclusive result where it did not
(JERC). ABBY daily/0.75 and JERC hourly/0.75 became fixed targets for reusable
pipeline testing. Full evidence: [Iter009](summaries/iter009/ITER009_REPORT.md),
[Iter010](summaries/iter010/ITER010_REPORT.md), and
[Iter011](summaries/iter011/ITER011_REPORT.md).

## 8. Stage 5 -- build the reusable pipeline and repair initialization geometry (Iter012--015)

**Goal.** Replace iteration-specific sampling logic with a reusable
initialize-to-production pipeline, test it at ABBY/JERC, and identify why
high-diversity starts did not reproduce the strongest earlier geometry.

**Result and evidence.** Iter012 constructed frozen 640-member pools and
completed six 64-by-32,000 chains. ABBY had acceptance 0.232--0.239, maximum
split R-hat 1.018, and cross-seed distance 0.004; JERC had acceptance
0.157--0.221, maximum split R-hat 2.224, and cross-seed distance 0.548. Both
fixed-length outcomes were therefore inconclusive.

Iter013 found TIM and Iter012 initialization clouds separated at both sites:
walker Wasserstein was 0.490 at ABBY and 0.541 at JERC, with zero walker
overlap. Common-target median log probability favored TIM by +2,216 and
+31,578. Iter014 showed that a pure rank-dominated JERC high-likelihood pool
was geometry-infeasible (condition number about 1.72e7), while the hybrid
high-likelihood/maximin pool passed geometry (about 359) but only partially
repaired mixing. Iter015's 36-chain matrix remained inconclusive_seed_instability
at both sites.

**Conclusion and lead-in.** Pool construction became a first-class scientific
and operational control. The hybrid pool was retained because it improved
feasibility without falsely promoting a posterior, enabling a conservative
multi-seed MAP inventory. Full evidence: [Iter012](summaries/iter012/ITER012_REPORT.md),
[Iter013](summaries/iter013/ITER013_REPORT.md),
[Iter014](summaries/iter014/ITER014_REPORT.md), and
[Iter015](summaries/iter015/ITER015_REPORT.md).

## 9. Stage 6 -- operationalize a MAP ensemble and regress the pipeline (Iter016--017)

**Goal.** Turn hybrid initialization into a conservative multi-seed procedure,
then exercise the same interfaces end to end before nine-site expansion.

**Result and evidence.** Iter016 completed all 18 leaves. ABBY retained 9/9
Tier-A seeds with MAP RMSE spread 0.00509; JERC retained 6/9 with spread
0.00117 after excluding seeds 9009, 9013, and 9016 for acceptance below 0.20.
The small SR spread alongside different parameter vectors was recorded as a
descriptive equifinality candidate, not posterior evidence.

Iter017 tested four initialize--optimize--report paths using short 64-by-2,000
chains. Its validator emitted ITER017_HANDOFF_PASS paths=4; every report had
zero Tier-A seeds and was correctly marked insufficient_retained. This was a
successful safeguard rather than a scientific failure.

**Conclusion and lead-in.** The operating procedure and reporting gates worked
on both retained and non-retained outcomes. With interfaces regression-tested,
Iter018 applied the locked process at nine sites. See
[Iter016](summaries/iter016/ITER016_REPORT.md) and
[Iter017](summaries/iter017/ITER017_REPORT.md).

## 10. Stage 7 -- nine-site operational release and closeout (Iter018)

**Goal.** Run the locked process at nine sites, publish Tier-A-only MAP
candidate products, and reconcile implementation, reports, aggregate, and
handoff into a terminal record.

**Result and evidence.** One preflight, nine initializations, 81 optimization
leaves, nine reporting makeups, one aggregate, and one handoff validator
completed. All 81 leaves reached COMPLETED 0:0; the final validator emitted
ITER018_HANDOFF_PASS sites=9 leaves=81. Five sites had 9/9 Tier-A seeds and
four retained a subset (1--8 of nine).

**Conclusion.** The final decision is operational_release_ready. Tier-A seeds
are site-local operational MAP candidates, not posterior draws, calibrated
uncertainty, or a site ranking. The development line is terminal; merge, push,
or PR is a separate user decision.

## 11. How authority, automation, failure, and recovery worked

The workflow combines human scientific control with agentic work under a
bounded contract. A planning proposal did not authorize compute, scheduler
actions, retries, or commits. The human supplied goals and approved complete
runtime packages; the agent reconciled evidence, prepared reproducible work,
monitored approved jobs, and closed records.

~~~mermaid
flowchart TD
    Start([Development need or question])

    subgraph Human[Human decisions and authority]
        H1[Define objective, scientific scope,<br/>and desired output]
        H2[Review consolidated kickoff package<br/>and grant bounded authority]
        H3[Resolve material scope changes,<br/>unapproved retries, or merge decision]
    end

    subgraph Agent[Agentic work under the approved contract]
        A1[Read handoff, workflow, prior records,<br/>HPC profile, Git, and artifact state]
        A2[Prepare plan: scope, gates, resources,<br/>evidence, and stop conditions]
        A3[Lock inputs, manifests, scripts,<br/>and run configuration]
        A4[Independent read-only review]
        A5[Bounded HPC preflight]
        A6[Approved submission, monitoring,<br/>and terminal accounting]
        A7[Evaluate evidence and preserve diagnostics]
        A8[Cross-validate handoff, records,<br/>summary, registry, and report]
    end

    Start --> H1 --> A1 --> A2 --> H2 --> A3 --> A4 --> A5
    A5 --> Check{Preflight and<br/>contract checks pass?}
    Check -- Yes --> A6 --> A7 --> Close{Acceptance and cross-record<br/>validation pass?}
    Check -- No --> Failure[Preserve and classify<br/>failure evidence]
    A7 --> Close
    Close -- No --> Failure
    Failure --> Change{Correction already authorized<br/>and within scope?}
    Change -- Yes --> A3
    Change -- No --> H3 --> A2
    Close -- Yes --> A8 --> End([Validated handoff and closeout])
~~~

| Iteration | Observed failure | Bounded response and evidence | Why it matters |
| --- | --- | --- | --- |
| Iter001 | First production array had 15 out-of-memory leaves | Classified shared resource defect; replacement 100-leaf array completed and exact-100 eligibility passed | Prevented partial results being presented as the baseline |
| Iter007 | Parallel workers timed out/OOM; later postprocessing retained invalid walkers | Slimmed shared arrays, initialized workers correctly, fixed invalid-walker handling, then completed the campaign | Separated infrastructure/code failures from sampler evidence |
| Iter012 | Two 10-GB preflights OOM; a pool gate exposed unsuitable geometry | Used approved resource correction, validated pools, and investigated geometry in Iter013--015 | Preserved reproducibility instead of silently rerunning |
| Iter015--016 | ELM-precal reporting omission and reusable analysis schema mismatches | Preserved failed jobs, corrected only approved reporting/analysis steps, and revalidated artifacts | Tested reporting contracts rather than assuming them |
| Iter018 | Materialized report scaffolds conflicted with report output | Added a scaffold-aware guard; reran reports, aggregate, and handoff | Final claims rest on the corrected reporting contract |

---

# Part II -- Technical evidence ledger

## 12. Decisive quantitative evidence

This table keeps only stage-changing measurements. It does not replace the
full per-seed tables, diagnostic plots, or raw artifacts in the linked reports.

| Stage | Key measurement | Result | Interpretation |
| --- | --- | --- | --- |
| Foundation | Iter001 pooled held-out SR | R² mean 0.945; RMSE mean 0.211 | Baseline forcing-surrogate characterization |
| Foundation | Iter002 full-data artifact | R² 0.958; RMSE 0.171; fresh-process validation passed | Locked, usable dependency |
| Coupling bridge | Iter003 drop21_corr080 / offline median R², KGE | about 0.651, 0.816 / about 0.850, 0.862 | Coupled path worked but lagged offline comparator |
| First MCMC | Iter007 joint 64x500 campaign | acceptance 0.1197; approximate ESS 93.8 | Technically complete, diagnostically weak |
| Geometry | Iter009 TIM maximum split R-hat, ABBY/JERC | 1.032 / 1.021 | Strongest arm still failed complete qualification |
| Topology | Iter010 forced BIC2-BIC1 | +11.816 to +16.437 across six chains | Declined evidence for two physical basins |
| Configuration | Iter011 ABBY daily/0.75 | acceptance 0.23671; saturation 0.01336; min steps/tau 33.10 | Supported ABBY-specific setting |
| Pipeline | Iter012 JERC fixed run | acceptance 0.157--0.221; R-hat 2.224; distance 0.548 | Fixed-length result inconclusive |
| Initialization | Iter013 TIM vs Iter012 walker W, ABBY/JERC | 0.490 / 0.541; zero overlap | Initial-cloud geometry mattered |
| Pool repair | Iter014 rank / hybrid condition number | about 1.72e7 / about 359 | Pure rank failed; hybrid was partial repair |
| MAP procedure | Iter016 Tier-A inventory | ABBY 9/9; JERC 6/9 | Operational candidate ensemble, not posterior promotion |
| Regression | Iter017 | Four paths passed; zero Tier-A seeds in short chains | Correctly prevented promotion |
| Release | Iter018 | 81/81 leaves; handoff pass for nine sites | Complete operational integrity evidence |

## 13. Final nine-site release status

| Site | Locked configuration | Tier-A seeds | Descriptive status |
| --- | --- | ---: | --- |
| ABBY | daily / 0.50 | 9/9 | all_tier_a |
| SOAP | daily / 0.50 | 9/9 | all_tier_a |
| YELL | daily / 0.50 | 9/9 | all_tier_a |
| WREF | daily / 0.50 | 9/9 | all_tier_a |
| JERC | hourly / 0.75 | 1/9 | partial_tier_a |
| OSBS | hourly / 0.75 | 4/9 | partial_tier_a |
| RMNP | hourly / 0.75 | 8/9 | partial_tier_a |
| TALL | hourly / 0.75 | 9/9 | all_tier_a |
| TEAK | hourly / 0.75 | 2/9 | partial_tier_a |

Tier-A retention and skill metrics are descriptive. A retained seed is an
operational MAP candidate, not a posterior-validation label.

## 14. Detailed evidence and reproducibility references

| Material | Location |
| --- | --- |
| Cumulative objectives, contracts, accounting, and conclusions | [ITERATION_SUMMARY.md](ITERATION_SUMMARY.md) |
| Closed-iteration index | [registry.csv](registry.csv) |
| Iteration-level records | [iterations/](iterations/) |
| Detailed MCMC diagnosis | [Iter008 comprehensive report](summaries/iter008/iter008_comprehensive_mcmc_report.md) |
| Geometry, topology, and configuration evidence | [Iter009](summaries/iter009/ITER009_REPORT.md), [Iter010](summaries/iter010/ITER010_REPORT.md), [Iter011](summaries/iter011/ITER011_REPORT.md) |
| Pipeline, pool, and operations evidence | [Iter012](summaries/iter012/ITER012_REPORT.md), [Iter013](summaries/iter013/ITER013_REPORT.md), [Iter014](summaries/iter014/ITER014_REPORT.md), [Iter015](summaries/iter015/ITER015_REPORT.md), [Iter016](summaries/iter016/ITER016_REPORT.md), [Iter017](summaries/iter017/ITER017_REPORT.md) |
| Final release report | [Iter018](summaries/iter018/ITER018_REPORT.md) |

## 15. Limits and correct reuse

- Raw products under /xdisk are temporary and unbacked; curate or copy them for
  long-term retention.
- The workflow establishes technical integrity, reproducibility, and a bounded
  operational MAP-candidate process. It does not establish a validated
  posterior, parameter uncertainty, universal sampler setting, or cross-site ranking.
- ABBY and JERC conclusions remain independent. When metrics conflicted, the
  durable result is explicitly inconclusive rather than a universal winner.
- A future run must begin from the handoff and workflow, form a new approved
  runtime contract, and treat site configurations, inputs, pools, and scheduler
  authority as fresh decisions.

## 16. Closing statement

The development line demonstrates an agentic research workflow that can move
from a scientific objective to reproducible artifacts, controlled HPC
execution, quantitative diagnosis, classified recovery, and validated handoff
without collapsing implementation success into a scientific claim. Iter018 is
the terminal technical release; any merge decision is separate.
