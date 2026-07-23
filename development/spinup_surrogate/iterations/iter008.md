# iter008 - Global Correlation Pruning and LBFGS Regularization

## Status

- Iteration ID: `iter008`
- Run slug: `spinup_surrogate_iter008_<variant>`
- Status: `completed`
- Phase: `selection and closeout complete`
- Site profile: `development/hpc/puma.md`
- Started: `2026-07-22T21:43:40Z`
- Closed: pending

## Runtime Contract

| Field | Value |
| --- | --- |
| Run mode and stop conditions | One finite 18-variant, five-seed matrix (90 leaves). Stop after terminal accounting; stop immediately for application, code, or configuration failures. |
| HPC confirmed | Yes: UA Puma, using `development/hpc/puma.md`; user approved this contract on 2026-07-22. |
| Submission/monitoring authority | Authorized for implementation/test work, scaffolding, variant-local Slurm preparation, the locked matrix submission, continuous monitoring, aggregation, selection, and closeout. |
| Resource policy and caps | Puma `standard`, account `chopinsong`, one node/task, 10 CPUs (50 GB implied), 30 minutes, `N_JOBS=4`, `PRE_DISPATCH=n_jobs`, single-thread BLAS/OpenMP, per-task `XDG_CACHE_HOME`. |
| Closeout commit authority | Authorized: at most one closeout commit after all closeout artifacts are complete. |

The approval response was `approved` after a request explicitly naming the 18 variants / 90 leaves,
Puma profile, resource cap, one scheduler/resource retry boundary, continuous monitoring, and
closeout commit. Only one retry per leaf is allowed for a scheduler/resource interruption within
this cap. Any application, code, or configuration failure requires fresh authorization.

## Context and Objective

- Baseline: iter007 selected `s08_tanh_adam_a10_lr1e3` with the iter006 45-feature schema;
  median validation R2 is `0.5892` for both targets and median RMSE ratios are `1.0000` / `1.0008`.
- Hypothesis: stronger L2 regularization can make the high-R2 LBFGS approach eligible, and global
  correlation pruning may improve the compact Adam baseline without seed-specific schemas.
- Objective: test six locked models under three global feature policies without reopening feature
  selection or changing the nine-case scientific controls.

## Fixed Controls and Variant Matrix

- Cases: ABBY, JERC, OSBS, SOAP, RMNP, TALL, TEAK, WREF, YELL; all `ppe6_I20TRCNPRDCTCBC`
- Split: `by_member`, fraction `0.8`; targets `TOTSOMC,TOTSOMN`; seeds `10001-10005`
- Candidate pool: the exact iter006 `all_control` 45 features; variance filtering disabled.
- Feature policies: `full45`; global absolute-correlation `0.80` and `0.60` policies. Filtered
  policies use `eligible_pool`, so the candidate pool may be pruned. Filtering uses feature values
  only before a split, records `filter_scope=global_pre_split`, and never inspects targets.
- Pair removal: prefer dropping `WIND_*`, `PSRF_*`, or `FLDS_*`; otherwise retain the earlier
  canonical feature. Every dropped feature records its triggering pair and reason.
- Locked manifest: `development/spinup_surrogate/slurm/iter008/iter008_variants.tsv` (18 variants).

Models are the compact Adam baseline `(8,), tanh, adam, alpha=10, lr=1e-3` and `(32,), tanh,
lbfgs` at alpha `50, 100, 250, 500, 1000`; the recorded LBFGS learning rate is provenance-only.

## Decision and Retry Rules

- Eligibility: five readable stats files for each target and variant.
- Gates independently for each target: median validation R2 no more than `0.01` below control;
  minimum R2 no more than `0.02` below; R2 IQR no more than `0.02` above; median per-seed RMSE
  ratio no more than `0.02` above; zero overfit warnings. Report absolute validation RMSE.
- Rank full gate passers by mean cross-target median validation R2, then lower mean median RMSE
  ratio, then simpler architecture. If none passes, retain baseline `s08_tanh_adam_a10_lr1e3/full45`.
- A complete gate failure is a scientific rejection; independent variants continue. One retry per
  leaf only for scheduler/resource interruption. No aggregation or selection with incomplete variants.

## Provenance and Job Ledger

| Item | Evidence |
| --- | --- |
| Canonical training script | `slurm/iter008/case.train_surrogate_spinup_iter008.slurm`; SHA-256 `c3fe108a05984aa601d113d967f6174b6fd3f17badebb2120849f04801a084f8` |
| Manifest | `slurm/iter008/iter008_variants.tsv`; 18 locked names; SHA-256 `4fbc66c8e2f0b35069ed100e148e9beb644823c5b00682e0c58eb9c21d1ea63c` |
| Compute validation | `slurm/iter008/validate_iter008_global_filter.slurm`; SHA-256 `b12dcf11dcdefe1e56f1cfdb92f23fd91cf60b4f214913a1bbd5d29253196999`; source `eb06ee9ebb3d0698d30e99e4155957ed96506021`; dirty iter008 scaffold |
| Variant-local artifacts | Required per variant: `UQ_output/<run_slug>/submit_<variant>.slurm`, `submission_config.env`, `slurm_%A_%a.out`, and `slurm_%A_%a.err` |
| Source state | pending compute validation and pre-submit source manifest |

All submitted copies have canonical SHA-256 `c3fe108a05984aa601d113d967f6174b6fd3f17badebb2120849f04801a084f8`.
Their configuration hashes are recorded below; each is at
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_surrogate_iter008_<variant>/submission_config.env`.

| Variant | Config SHA-256 |
| --- | --- |
| `s08_tanh_adam_a10_lr1e3_full45` | `5a2c1bb4df93cd892a97da24a0adab541ccf61771438acb03b393bc600ca28c1` |
| `s08_tanh_adam_a10_lr1e3_corr080_prioritydrop` | `619f5c047f7e1ca9de41d3e1ec8ceef3f44708afb203be71aa96dd5a88d42347` |
| `s08_tanh_adam_a10_lr1e3_corr060_prioritydrop` | `64a1364743faf80dc94f58908856a6205f60a3f083b794a05ab986c3cc1ca244` |
| `s32_tanh_lbfgs_a50_lr1e3_full45` | `89c6418edd7332fc4538d3f6de6ad34ccb6a0a068177bf40de251a0caf98e3e7` |
| `s32_tanh_lbfgs_a50_lr1e3_corr080_prioritydrop` | `135c274c90d2e7cae0d81b33ee985091056561331089ec0e29c91eea37079ebd` |
| `s32_tanh_lbfgs_a50_lr1e3_corr060_prioritydrop` | `62f1d6737c1980e7fce017bba724904f950146024aee42503c69b0aa4551b8c4` |
| `s32_tanh_lbfgs_a100_lr1e3_full45` | `fb25c9d816b8f9eb5b4d84ea0d7b6884fc6c1d08cd8048c1f7885f47eca602c3` |
| `s32_tanh_lbfgs_a100_lr1e3_corr080_prioritydrop` | `b13708de91cf18ddc84bd3ae7253f7accca2074398a1e83b6419a3dfe7656cc7` |
| `s32_tanh_lbfgs_a100_lr1e3_corr060_prioritydrop` | `25da76a73181eeb7fde68237ac0aed51b8c61356db14f30696ebcfc2b87c347c` |
| `s32_tanh_lbfgs_a250_lr1e3_full45` | `ca3213f1fec8ce7df483a5838234bed67417c2576891b066d547eebecb392b5b` |
| `s32_tanh_lbfgs_a250_lr1e3_corr080_prioritydrop` | `7ae4f5739ec7d694d1bee10a084d381155032fd9d9b6e5ae2d37598499f703cb` |
| `s32_tanh_lbfgs_a250_lr1e3_corr060_prioritydrop` | `702c5c52a8f73a1ec5c7de2177c68e0964f96c288c1601a9eb1439beaad07ba9` |
| `s32_tanh_lbfgs_a500_lr1e3_full45` | `be3c6519beb9e4671f47bc385593bcd8445ce631ae143acc75f00b450331eac2` |
| `s32_tanh_lbfgs_a500_lr1e3_corr080_prioritydrop` | `ab3c6a4e8b07ea8c7f98705799582ea650bf97c2cd24369e1798c2bb6729c631` |
| `s32_tanh_lbfgs_a500_lr1e3_corr060_prioritydrop` | `b3e343858d2f93f990ab2686c998b93b523678727de88b2c6cccbf117d4b6aeb` |
| `s32_tanh_lbfgs_a1000_lr1e3_full45` | `81cf49d84a6eed8d76bb25fd0fecadf5526779c891dc85fa9b1433884c9bb650` |
| `s32_tanh_lbfgs_a1000_lr1e3_corr080_prioritydrop` | `0482f476b61e50a6ebb548f5aa4c0ec4076133da72574cc385fe4dfa1b32b87f` |
| `s32_tanh_lbfgs_a1000_lr1e3_corr060_prioritydrop` | `e4e34e7de9701c9b82b3f91fe7cc98975a46b66c19cb7d16535036d0ce84bdc6` |

## Execution and Diagnostics

- Static checks: `py_compile` and `bash -n` passed on 2026-07-22.
- Login-node Python lacks NumPy, as expected under the Puma profile; the synthetic invariant test is
  therefore scheduled only as a bounded compute-node validation. It does not load cases or train a model.
- Validation job `23362319` submitted with `/usr/bin/sbatch --parsable --output=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter008_validate_%j.out --error=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/spinup_iter008_validate_%j.err development/spinup_surrogate/slurm/iter008/validate_iter008_global_filter.slurm`; terminal `FAILED`, exit `1:0`, elapsed `00:00:10`, MaxRSS `51328K`.
- Failure classification: application/configuration failure, not scheduler/resource. The validator ran by absolute path and failed before its invariant checks with `ModuleNotFoundError: No module named 'model_ELM'`. Preserve logs and stop: retrying or adding the fixed repository root to `sys.path` requires fresh authorization.
- Fresh authorization: the user authorized exactly this import-path fix and a rerun of only the
  same bounded validation job on 2026-07-22. No training-matrix submission is included.
- Rerun provenance: validator SHA-256 `9bd6a05bf389d981c540c30e9a58367020324f5b1aab3517b99578a55ad20a53`;
  canonical Slurm SHA-256 unchanged (`b12dcf11dcdefe1e56f1cfdb92f23fd91cf60b4f214913a1bbd5d29253196999`);
  source `eb06ee9ebb3d0698d30e99e4155957ed96506021`, dirty iter008 scaffold.
- Rerun job `23362351` submitted under that narrow authorization; monitoring to terminal accounting.
- Rerun result: `23362351` `COMPLETED`, exit `0:0`, elapsed `00:00:35`, MaxRSS `406084K`.
  Its compute-node log reports `iter008 global feature-filter invariants passed`.
- Pre-submit checks: 18 manifest rows and 18 variant roots; every copied script/config passed
  `bash -n`; the canonical feature pool contains 45 columns; `/xdisk` had 2.6 TB free.
- Submitted arrays (each `1-5`): `s08_tanh_adam_a10_lr1e3_full45=23362388`,
  `s08_tanh_adam_a10_lr1e3_corr080_prioritydrop=23362389`,
  `s08_tanh_adam_a10_lr1e3_corr060_prioritydrop=23362398`,
  `s32_tanh_lbfgs_a50_lr1e3_full45=23362399`,
  `s32_tanh_lbfgs_a50_lr1e3_corr080_prioritydrop=23362400`,
  `s32_tanh_lbfgs_a50_lr1e3_corr060_prioritydrop=23362401`,
  `s32_tanh_lbfgs_a100_lr1e3_full45=23362402`,
  `s32_tanh_lbfgs_a100_lr1e3_corr080_prioritydrop=23362403`,
  `s32_tanh_lbfgs_a100_lr1e3_corr060_prioritydrop=23362404`,
  `s32_tanh_lbfgs_a250_lr1e3_full45=23362405`,
  `s32_tanh_lbfgs_a250_lr1e3_corr080_prioritydrop=23362406`,
  `s32_tanh_lbfgs_a250_lr1e3_corr060_prioritydrop=23362407`,
  `s32_tanh_lbfgs_a500_lr1e3_full45=23362408`,
  `s32_tanh_lbfgs_a500_lr1e3_corr080_prioritydrop=23362409`,
  `s32_tanh_lbfgs_a500_lr1e3_corr060_prioritydrop=23362410`,
  `s32_tanh_lbfgs_a1000_lr1e3_full45=23362411`,
  `s32_tanh_lbfgs_a1000_lr1e3_corr080_prioritydrop=23362412`, and
  `s32_tanh_lbfgs_a1000_lr1e3_corr060_prioritydrop=23362413`. All commands used the required
  variant-local `--chdir`, stdout/stderr roots, and `SUBMISSION_CONFIG` export.
- Terminal accounting: all 90 leaves completed with exit `0:0`; elapsed range `00:01:31` to
  `00:02:56`. No retry was used or needed.
- Artifact validation: each of the 18 manifest variants has exactly five readable stats JSONs.
  Canonical aggregation script `slurm/iter008/aggregate_iter008.slurm` passed `bash -n` and has
  SHA-256 `d3b5cf7a20c935c00166bf3b6e8ed44bb53b50245bfbea577485891231e7daee`.
- Aggregation job `23362489` submitted with variant manifest validation, Puma `standard`, 10 CPUs,
  and a 30-minute cap; monitoring to terminal accounting.
- Aggregation result: `23362489` `COMPLETED`, exit `0:0`, elapsed `00:00:17`.

## Closeout Checklist

- [x] Compute-node global-filter invariant validation passed (`23362351`; the failed `23362319` diagnostic retained)
- [x] Variant-local scripts/configs materialized and hashes recorded
- [x] Locked matrix submitted and monitored to terminal accounting
- [x] Summary/stability artifacts copied to `summaries/iter008/`
- [x] `ITERATION_SUMMARY.md` updated with objective, settings, evidence, and conclusion
- [x] `registry.csv` and `handoff/CURRENT.md` finalized
- [x] One authorized closeout commit created

## Results and Decision

All 18 summaries and 18 stability reports are present. Schemas were seed-invariant: full45
retained 45 features, `corr080_prioritydrop` 25, and `corr060_prioritydrop` 21.

| Variant | Median R2 (C/N) | Validation RMSE (C/N) | RMSE ratio (C/N) | Decision |
| --- | --- | --- | --- | --- |
| s08 Adam full45 | 0.5892/0.5892 | 6758.3/676.4 | 1.0000/1.0008 | pass |
| s08 Adam corr080 | 0.5500/0.5499 | 7588.3/759.7 | 1.0052/1.0062 | reject: R2 median/min |
| s08 Adam corr060 | 0.5215/0.5215 | 7482.4/749.2 | 1.0047/1.0057 | reject: R2 median/min/IQR |
| LBFGS alpha 50 full45 | 0.7935/0.7937 | 4661.8/469.7 | 0.9499/0.9561 | pass, selected |
| LBFGS alpha 50 corr080 | 0.7896/0.7906 | 4719.5/472.6 | 0.9531/0.9539 | pass |
| LBFGS alpha 50 corr060 | 0.7726/0.7724 | 4866.4/487.2 | 0.9542/0.9552 | pass |
| LBFGS alpha 100 full45 | 0.6908/0.6905 | 5861.8/586.9 | 0.9727/0.9737 | pass |
| LBFGS alpha 100 corr080 | 0.6796/0.6798 | 5966.2/597.3 | 0.9817/0.9826 | pass |
| LBFGS alpha 100 corr060 | 0.6584/0.6583 | 6183.6/619.2 | 0.9894/0.9904 | reject: warnings 0.2/0.2 |
| LBFGS alpha 250 (all policies) | 0.5490-0.5667 | 7364.2-7788.4 / 737.1-779.8 | 0.9913-1.0147 | reject: R2 median/min |
| LBFGS alpha 500 (all policies) | 0.4198-0.4935 | 9190.6-9989.1 / 919.7-1000.7 | 1.0115-1.0274 | reject: R2; some RMSE ratio |
| LBFGS alpha 1000 (all policies) | 0.2438-0.3895 | 10395.6 / 1041.2 | 1.0283/1.0293 | reject: R2 and RMSE ratio |

Selected `s32_tanh_lbfgs_a50_lr1e3_full45`: mean cross-target median validation R2 `0.7936`,
the highest full-gate passer, ahead of alpha-50 corr080 (`0.7901`) and corr060 (`0.7725`). It
improves markedly on the iter007 baseline without warnings. The next iteration requires a new
runtime contract.

## Proposed Iter009 Plan (Planning Only)

- Retained baseline: `s32_tanh_lbfgs_a50_lr1e3_full45` with the full45 schema. Correlation-pruned
  arms are not proposed because all three alpha-50 policies ranked below full45.
- Hypothesis: the sharp improvement at LBFGS alpha 50 can be refined by a narrow regularization
  sweep without reopening feature policy or architecture.
- Tentative matrix: `(32,), tanh, lbfgs, full45` at alpha `25`, `35`, `50` (control), `65`, and
  `75`; five seeds `10001-10005`, for 25 proposed leaves. Keep the nine cases, `by_member` split,
  `0.8` train fraction, `TOTSOMC,TOTSOMN`, stats-only output, and disabled variance/correlation
  filtering.
- Tentative gates, independently per target against the iter008 selected baseline: median R2 not
  more than `0.01` below (`0.7935/0.7937`); minimum R2 not more than `0.02` below
  (`0.6820/0.6820`); R2 IQR not more than `0.02` above (`0.0646/0.0612`); median per-seed RMSE
  ratio not more than `0.02` above (`0.9499/0.9561`); zero warnings. Rank passers by mean
  cross-target median R2, then lower mean median RMSE ratio, then lower alpha.
- Tentative Puma shape: `standard` / `chopinsong`, 10 CPUs (50 GB implied), 30 minutes,
  `N_JOBS=4`, per-task `XDG_CACHE_HOME`, variant-local scripts/configs, read-only reviewer
  subagent, and bounded no-training preflight. One validation-only retry is separate from one
  scheduler/resource retry per matrix leaf; application/code failures after preflight stop.
- Expected artifacts: `iterations/iter009.md`, `slurm/iter009/` controls and manifest,
  variant-local output roots, `summaries/iter009/`, and a refreshed `CURRENT.md`/registry record.
- Authorization boundary: this is an evidence-derived proposal only. A new runtime contract is
  required before any iter009 scaffold, code change, submission, or execution.

## Preventive Refinement

The first compute-node validator job (`23362319`) stopped before testing because an absolute-path
Python launch set its import path to the validator directory, not the repository root, causing
`ModuleNotFoundError: model_ELM`. Future absolute-path repository utilities must explicitly prepend
the fixed Puma checkout root `/xdisk/chopinsong/tianyihu/elm-olmt` to `sys.path` before importing
repository modules. Before any production matrix submission, run a bounded compute-node preflight
that imports the utility and executes its no-training invariants; classify a failure as an
application/configuration failure and request narrow authorization before retrying.

Post-closeout workflow refinement: the validator was promoted to reusable
`tools/validate_global_feature_filter.py`, and the locked matrix manifest was moved under
`slurm/iter008/`. The submitted variant-local copies and their recorded hashes remain the
execution provenance.
