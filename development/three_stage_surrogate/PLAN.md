# Three-Stage ELM Surrogate Development Plan

**Repository:** [TianyiHu123/elm-olmt](https://github.com/TianyiHu123/elm-olmt)
**Base branch:** `pmcpu`
**Development branch:** `feature/three-stage-surrogate`
**Development record:** `development/three_stage_surrogate/`
**Computing:** ELM PPE simulations on **NERSC Perlmutter**; subsequent surrogate development on **UA Puma**
**Status:** User-approved campaign-level plan; implementation details and iteration-specific rules are decided through the development workflow.

## Project context and workflow

Develop a **single pooled surrogate system for nine NEON forest sites**—in canonical order, **ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, and YELL**—using the same 1,024-member, 18-parameter Owen-scrambled Sobol PPE at each site. Begin implementation, tuning, robustness testing, and integration with **ABBY and JERC**. Introduce the other seven sites only after the complete three-stage structure and reusable inference path are ready.

Create a new Git branch from `pmcpu`; develop the implementation directly in the repository's established code locations (principally `model_ELM/` and root-level training scripts). Merge the tested implementation back to `pmcpu` after review. The branch provides isolation; `development/three_stage_surrogate/` is **not** a separate Python package.

The development folder should follow the conventions of [spinup_surrogate](https://github.com/TianyiHu123/elm-olmt/tree/pmcpu/development/spinup_surrogate), [spinup_forcing_coupling](https://github.com/TianyiHu123/elm-olmt/tree/pmcpu/development/spinup_forcing_coupling) and [ELM_diagnose](https://github.com/TianyiHu123/elm-olmt/tree/feature/ELM_diagnostics/development/ELM_diagnose): a concise `README.md`, project plan, development workflow/handoff, iteration records, cumulative summaries, and iteration-specific Slurm scripts and diagnostic tools as needed. Codex and the user will decide detailed iteration procedures separately; do not duplicate the older workflows' extensive operational rules in this plan.

**Data sequence and ownership:** The user owns completion of the ELM PPE simulations on Perlmutter and transfer of the required data to Puma. The user will identify the authoritative directories and necessary files under `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc`. The surrogate campaign consumes those declared inputs; it does not infer replacements from nearby directories. At the beginning of each iteration, validate the declared data identities, site/member correspondence, required schemas, and completeness before training or evaluation. Surrogate data preparation, development, robustness runs, and evaluation take place on Puma, using `development/hpc/puma.md` as the platform reference.

**Scope:** Deterministic surrogate construction, evaluation, and reusable inference only. Optimization, MCMC, likelihood design, uncertainty modeling, and comparison against NEON observations are outside this plan. MCMC is a future downstream use, so released inference must preserve and validate the 18-parameter order, bounds, transforms, and conditional C:N support recorded by the PPE design.

---

## 1. Overall surrogate structure

The system has **three sequential stages**, each trained on pooled site data:

1. **Spinup surrogate:** Predict `TOTSOMC` and `TOTSOMN` from the 18 PPE parameters and site-level surface/climatological features.
2. **GPP surrogate:** Predict hourly `GPP` from PPE parameters, site descriptors, engineered forcing/calendar features, and **predicted** spinup `TOTSOMC`/`TOTSOMN`.
3. **SR surrogate:** Predict hourly `SR` from PPE parameters, site descriptors, engineered forcing/calendar features, **predicted** spinup C/N, and **predicted** hourly GPP.

With member *m*, site *s*, and time *t*:

\[
(\widehat C_{s,m},\widehat N_{s,m})=f_{\mathrm{spinup}}(\theta_m,z_s)
\]

\[
\widehat G_{s,m,t}=f_{\mathrm{GPP}}(\theta_m,z_s,F_{s,t},\widehat C_{s,m},\widehat N_{s,m})
\]

\[
\widehat R_{s,m,t}=f_{\mathrm{SR}}(\theta_m,z_s,F_{s,t},\widehat C_{s,m},\widehat N_{s,m},\widehat G_{s,m,t})
\]

Here, \(\theta\) denotes the common 18-parameter PPE input, \(z\) denotes site properties/climatology, and \(F\) denotes hourly forcing and time features. ELM outputs are **supervised targets**; true ELM C/N or GPP values must not replace predicted upstream inputs in the normal downstream training or end-to-end prediction path.

The initial SR stage uses **same-hour predicted GPP**. Alternative lagged or rolling predicted-GPP features may be evaluated later using development members only.

### Features and data alignment

- Reuse the surface, climatological, hourly forcing, antecedent/rolling, and `sin_hour`/`cos_hour` features and inference-history behavior established by the existing spinup and coupled-surrogate procedures. Pin their exact source, ordering, units, and construction during data initialization rather than reinterpreting them independently for this campaign.
- Add **`sin_doy` and `cos_doy`** to both hourly stages, calculated from actual aligned forcing timestamps with the ELM **no-leap calendar**. Avoid assuming the record always begins on January 1 or at midnight.
- Include an explicit categorical site identity alongside the established physical site descriptors. The system targets new parameter vectors at the nine known sites, not inference for unseen sites.
- Keep a canonical parameter-name/order schema and explicit site/member/time identifiers. The same member ID must resolve to the **same parameter vector at every site**; account for the existing distinction between 0-based array positions and 1-based ensemble directories.
- Permit different forcing and target windows among sites when their available forcing data differ. Within one site, all eligible members must use the same validated timestamp axis for a given hourly stage. Record each site's model window, expected and valid row counts, and any explicit gaps; never silently truncate all sites to a common window.
- Reuse one feature-engineering implementation for training and inference, with consistent feature ordering, units, and timestamps.
- Support an end-to-end predictor that returns C/N, hourly GPP, and hourly SR from parameters plus site/forcing inputs, without needing ELM target outputs at inference. The hourly interface follows the existing forcing-surrogate procedure and accepts the ordered forcing history required to construct its antecedent/rolling features.

**Generalization target:** New PPE parameter vectors at the **nine modeled sites**, not unseen sites.

---

## 2. Training strategy

### 2.1 Shared global split

Create and save **one member-wise split manifest** for all sites and all three stages:

| Partition | Members | Use |
| --- | ---: | --- |
| Development | 819 (80%) | Training, feature/model selection, and robustness validation |
| Fixed test | 205 (20%) | Simple held-out evaluation after development choices are finalized |

These counts assume all 1,024 members are eligible. Create the split during the data-initialization iteration from the canonical PPE member identities using a recorded deterministic method and seed. If files are missing or members fail validation, first seek repair or replacement of the declared inputs. Resolve and document any change to the eligible-member population before finalizing the split; never silently create site-specific splits.

Within the development pool, all splitting, cross-validation, preprocessing, implementation, feature selection, tuning, and robustness work must respect **global PPE member identity** across sites and time rows. The 205 fixed-test members remain outside every fit and model-selection operation.

After the ABBY/JERC pipeline is frozen, use the 205 members once for a simple two-site end-to-end test. Do not select another model or configuration from those results. Reuse the same fixed member identities when the nine-site system is later evaluated; report this accurately as a **reused fixed test set**, not an entirely unseen first-look test for ABBY and JERC. The seven newly introduced sites' test targets remain previously unseen. If two-site test performance motivates later model changes, explicitly reclassify the 205-member set as an evaluation benchmark rather than a pristine final holdout, while continuing to exclude it from fitting and tuning.

Existing `by_member` behavior in the spinup and forcing trainers needs attention: the current spinup trainer partitions per case, and the forcing trainer selects the first member IDs per case. Replace or supplement those paths with a shared, explicit global member-manifest interface for the new pipeline.

### 2.2 Initial method: direct sequential training (`in_sample`)

Start with the simpler strategy discussed previously:

1. Fit spinup on the current training members using ELM C/N targets.
2. Predict C/N **on those same training members** with the fitted spinup surrogate.
3. Fit GPP using the predicted C/N features and true ELM GPP targets.
4. Predict GPP **on those same training members** through the fitted spinup → GPP chain.
5. Fit SR using predicted C/N, predicted GPP, and true ELM SR targets.

For unseen validation/test members, run the fully fitted chain without fitting any stage on those members.

This direct method is the **initial baseline**, not a guarantee of optimal generalization. Upstream models may predict their training members better than unseen members, which can create a downstream train/inference feature mismatch. Assess that effect through the end-to-end validation results.

### 2.3 Future alternative: cross-fitting (`out_of_fold` placeholder)

Leave a clear extension point for out-of-fold upstream prediction generation:

- **For GPP:** Train spinup on grouped folds and predict C/N for held-out members to construct GPP training features.
- **For SR:** Construct out-of-fold predictions of the **entire upstream spinup → GPP chain**, ensuring that the upstream models used for a member's training features did not train on that member. This may require nested cross-fitting.
- After generating downstream training features, fit full-training upstream models for validation and deployment.

Do **not** implement cross-fitting in the first version. Instead, separate **upstream feature generation** from the GPP/SR model-fitting interfaces, so a future `out_of_fold` generator can replace the initial `in_sample` generator without redesigning the stages. Expose the selected mode in configuration/artifact metadata; an unsupported mode should fail explicitly rather than silently revert to in-sample predictions.

### 2.4 Model fitting

Initially build on the existing MLP training and scaler infrastructure, with stage-specific model configurations. Use member-grouped validation for tuning, and ensure scalers or data-dependent feature selection do not learn from validation members. The existing row-based `GridSearchCV` splits and MLP internal early stopping warrant particular attention. Avoid repeated large hyperparameter searches inside every robustness repetition; establish candidate configurations using the development pool, then compare reproducibly.

The hourly nine-site training matrix may be very large. Retain or adapt memory-aware data preparation/memmap approaches without accidentally using legacy feature matrices populated with **true** ELM spinup inputs.

---

## 3. Robustness testing and evaluation

### Development-only robustness

Within the 819 development members, perform repeated **80/20 member-wise train/validation splits** (approximately **655 training / 164 validation members** per repetition), synchronized across sites and stages.

Require **20 repetitions** for the selected configuration, with any expansion to **50** treated as a separately planned resource decision. In each repetition, train the **complete three-stage chain** from its training members and evaluate end-to-end on its unseen validation members. Save the member lists/seeds, configurations, metrics, and enough provenance to compare repetitions. The 205-member fixed test pool must not enter these experiments. Do not repeat large hyperparameter searches inside the robustness repetitions.

### Metrics and diagnostics

Evaluate `TOTSOMC` and `TOTSOMN` at member/site level, and GPP/SR at both **hourly** and **daily-aggregated** resolution. Initially follow the established surrogate evaluation approach and report results **per site** and **pooled**, explicitly recording each site's time coverage because sites may have different forcing windows. Any later site-weighting rule, cross-site decision metric, or worst-site gate must be defined in the applicable iteration plan before results are examined.

Use conventional predictive **R²**, RMSE, MAE, and bias as primary metrics; correlation may be an additional diagnostic. Note that some existing surrogate functions label *squared correlation* as R²: distinguish that from `r2_score` when building the unified evaluation.

Inspect training–validation gaps and **end-to-end error propagation** (spinup → GPP → SR). Optionally compare downstream predictions obtained with true upstream inputs as a **diagnostic only**, not a deployment score or normal training method.

### Fixed-test evaluation

After feature choices, hyperparameters, and the upstream-prediction strategy are selected using development data, train the frozen ABBY/JERC chain on all **819 development members**, then perform the simple two-site evaluation on the **205 fixed test members**. Save the models, feature schema, split manifest, sitewise/pooled scores, predictions, and provenance. Do not reuse older released models unless their training-member provenance proves that all fixed-test members were excluded.

When the other seven sites are introduced, continue to use only the 819 development identities for further fitting, tuning, and robustness work. The later nine-site fixed-test evaluation reuses the same 205 member identities under the disclosure above.

Cross-fitting, if explored later, should be compared to the direct method on matched **development validation splits**, not chosen using final-test performance.

---

## 4. Proposed code and development structure

### 4.1 Main repository implementation

Work directly in the existing source tree **on the new development branch**:

| Existing area | Proposed work |
| --- | --- |
| `model_ELM/surrogate_NN_Spinup.py` | Reuse spinup preparation/fit/predict; integrate explicit global member splitting and suitable model interfaces. |
| `model_ELM/surrogate_NN_Forcing.py` | Reuse forcing loading/features and hourly modeling; implement consistent timestamp-based DOY features and predicted-upstream input handling. |
| `model_ELM/surrogate_forcing_multicase.py` | Reuse pooled multi-case preparation where suitable. |
| `model_ELM/spinup_surrogate_artifact.py`, `model_ELM/forcing_surrogate_artifact.py` | Reuse compatible artifact schema/validation concepts. |
| `model_ELM/coupled_surrogate.py` | Review existing spinup → SR inference for reusable interfaces, while preserving existing behavior. |
| Repository-root `train_surrogate_*.py` scripts | Preserve existing entry points; add a dedicated pipeline training/evaluation CLI if useful. |
| `tests/` | Add focused pipeline, global-split, upstream-feature, and inference tests. |

Possible **new reusable modules within `model_ELM/`**, subject to Codex's review of existing functionality:

- **Global member split/manifest support**, shared by stages.
- **Three-stage pipeline orchestration**, for sequential fit and inference.
- **Upstream prediction feature generation**, initially direct/in-sample, with an OOF extension interface.
- **Common pipeline evaluation and bundle serialization**, where existing utilities are insufficient.

These are *responsibility boundaries*, not a mandatory list of new files or class names. Prefer reusing existing functions and avoiding unnecessary wrappers or duplicate abstractions.

### 4.2 Development records only under `development/`

Model the new workflow folder on the two previous projects:

```text
development/three_stage_surrogate/
├── README.md
├── PLAN.md
├── WORKFLOW.md
├── ITERATION_SUMMARY.md
├── registry.csv
├── handoff/
│   └── CURRENT.md
├── iterations/
│   └── README.md
├── summaries/
│   └── README.md
├── slurm/
│   └── README.md
├── tools/
│   └── README.md
└── templates/
    ├── current-handoff.md
    └── iteration.md
```

This folder holds **iteration records, HPC job scripts, diagnostics, and development-specific tools**, not the core surrogate library. Initialize it in a `not_initialized` / `pre_kickoff` state without an `iter001.md`, `slurm/iter001/`, or `summaries/iter001/` directory. Create iteration-specific material only after approval of that iteration's complete kickoff package. Add optional shared folders such as `configs/`, `manifests/`, or `schemas/` only when an approved iteration produces genuinely reusable material that does not belong in the main source tree.

### 4.3 Suggested development progression

1. **Branch and project scaffold:** Create the branch from `pmcpu`; initialize the development records in the pre-kickoff state; inspect/reuse existing surrogate code.
2. **Iter001 data initialization:** After the user identifies the transferred ABBY/JERC inputs, validate and record the exact PPE design, parameter/member mapping, restart targets, site-specific forcing/GPP/SR time axes, established feature inputs, units, schemas, coverage, and eligible members. Create the deterministic 819/205 split and a reusable no-training data-contract validator. Do not train a surrogate in this iteration.
3. **Two-site prototype:** Build the direct three-stage chain on ABBY/JERC using only development members; establish cross-fitting-ready interfaces and deterministic end-to-end inference.
4. **Two-site tuning and robustness:** Settle feature/model choices within the development pool and complete the required 20 synchronized robustness repetitions.
5. **Two-site fixed test:** Freeze and refit the selected chain on all 819 development members, then perform the simple 205-member ABBY/JERC test without tuning from its results.
6. **Nine-site expansion:** As the user supplies the remaining transferred sites, extend and validate the data contract without changing established ABBY/JERC identities; then scale preparation, fitting, and development-only robustness to all nine sites.
7. **Nine-site fixed-test evaluation and release:** Refit the frozen nine-site chain on the 819 development members, evaluate the reused 205-member fixed test with the required disclosure, and produce reusable deterministic model artifacts.
8. **Integration:** Review implementation and tests, then merge validated code from the development branch back to `pmcpu`.

A later **cross-fitting experiment** can be added as a separate development iteration if validation suggests meaningful train/inference mismatch.

---

## Expected outcome

A reproducible, pooled nine-site **spinup → GPP → SR** surrogate that accepts new PPE parameter vectors and site forcing inputs, supplies predicted upstream features throughout, and has documented robustness and held-out performance. The first implementation uses **direct in-sample sequential training**, while keeping the architecture open to **out-of-fold cross-fitting**. Code lives in the normal repository source tree; the dedicated development folder preserves the experiment history.
