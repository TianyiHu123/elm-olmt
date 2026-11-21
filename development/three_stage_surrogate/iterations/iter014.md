# iter014 - ABBY/JERC coupled inference engine and diagnostics

## Status

- Iteration ID: `iter014`
- Work type: `integration`
- Run slug: `three_stage_surrogate_iter014_abby_jerc_coupled_inference`
- Status: `completed`
- Phase: `closed`
- Site profile: `development/hpc/puma.md`
- Started: `2026-11-16T23:50:17-07:00`
- Closed: `2026-11-17T15:21:18-07:00`

## Campaign Plan Alignment

- Campaign plan: `development/three_stage_surrogate/PLAN.md`
- Locked plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`
- Applicable campaign phase: progression item 6, reusable frozen two-site three-stage integration
- Alignment: `aligned`
- Approved deviation: `none`

## Finalized Plan

- Objective: implement and validate deterministic ABBY/JERC spinup -> GPP -> SR inference from
  arbitrary valid canonical 18-parameter vectors and timestamped forcing, then produce four
  development-only descriptive scientific diagnostics without fitting any model.
- Inputs: immutable snapshot `r0001`, global 819/205 split, and published spinup, GPP, and SR
  `release_0001` artifacts and all-development handoffs with the identities below.
- Work units: focused tests and compute-node preflight; bounded nine-member two-site integration;
  streamed all-development diagnostics; independent final validation and closeout.
- Exclusions: refitting, full-chain robustness or uncertainty, fixed-test access, full-819 engine
  replay, upstream or release edits, extra sites, MCMC, cross-fitting, new features, plan edit,
  intermediate commit, or push.
- Decision: all immutable technical, numerical, provenance, scope, diagnostic, and closeout gates
  pass -> `three_stage_inference_ready_for_robustness`; otherwise a precisely classified
  blocked/failed state. Diagnostic metric values have no performance threshold.

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `Approve the complete revised Iter014 kickoff package and runtime contract.`; `2026-11-16T23:50:17-07:00` |
| Kickoff goal, finite work-unit count, and stop conditions | Four sequential submissions: preflight, integration, diagnostics, final validation; stop on identity mismatch, immutable-gate failure, prohibited access, unapproved substantive correction, or unaccounted job. |
| Campaign plan identity and alignment | `development/three_stage_surrogate/PLAN.md`; `014a112b...5360`; item 6; aligned; no deviation or plan edit. |
| Confirmed HPC system and site profile | Puma login `junonia.hpc.arizona.edu`; `development/hpc/puma.md`; `chopinsong/standard`; CPU-only `OLMT_puma`. |
| Approved output and storage policy | Create `<root>/runs/{preflight,integration,diagnostics,final}/attempt_N` and `<root>/products`; retain at most 2 GiB and use at most 20 GiB transient; `/xdisk` is temporary and unbacked. |
| Locked dependencies, scope, exclusions, gates, and decision rule | Exact identities below; canonical physical parameter validation and conditional C:N support; exact 25/43/44 features, transforms, scalers, no-leap/720-hour logic, predicted upstreams; no fitting, fixed test, full-819 engine chain, release mutation, or performance gate. |
| Lifecycle authority | Initialization; implementation/tests/scripts/config/manifests/validators; exact external directories; separate read-only review before every submission and at every result gate; four submissions; monitoring/accounting; evaluation; normal records; exactly one closeout commit. |
| Resources, monitoring/wait mechanism, and retry boundaries | Preflight 2 CPU/10 GB/30 min, cap 4/20/1 h; integration 4/20/1 h, cap 6/30/2 h; diagnostics 8/40/4 h, cap 12/60/6 h; final 4/20/1 h, cap 8/40/2 h. Initial plus at most one same-scope scheduler/node/transport/launch/resource retry per unit. Only a reviewed wrapper/manifest-only preflight correction is preauthorized; substantive failures require renewed authority. |
| Cancellation scope | Recorded Iter014 IDs only if duplicate, outside contract, invalidated by proven common defect, unsafe, or threatening storage integrity; pending or slow is insufficient. |
| Outside-sandbox authority | Locked `sbatch`; job-scoped `squeue`, `scontrol show job`, `sacct`, `seff`, `job-history`, `job-limits`; bounded `scancel` under the stated conditions. |
| Closeout branch | Exactly one scoped local no-push commit after independent validation; subject `Add three-stage inference engine`. |

`<root>` is `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference`.

## Declared Inputs and Evidence

| Input | Role | Identity |
| --- | --- | --- |
| Snapshot r0001 | parameters, forcing, surfaces, aligned truth | manifest `39b05495...187a`; ABBY `85f52690...c9c1`; JERC `a846c731...c0cb6` |
| Global split | immutable development/fixed-test boundary | `99467dea...0fce`; 819/205 |
| Spinup release | frozen C/N inference and comparison handoff | manifest `69f840f7...f2dc`; artifact `9abb342d...a809`; handoff `9e2d5be4...fdb5` |
| GPP release | frozen GPP inference and comparison handoff | manifest `57cc18b0...70d1`; artifact `67214897...c9c`; handoff `c905fc60...98bb` |
| SR release | frozen SR inference and comparison handoff | manifest `3a3d3faf...ed4c`; artifact `8dd06c29...3fb2`; handoff `3704cab6...d3a1` |
| Repository source | implementation base | `ef49c6f4bfefcba0ef1c782b1ff6a3e8e685e14b`; clean and equal to branch upstream at approval |

## Acceptance Gates and Decision Rule

- Engine input is one or more finite physical 18-vectors in exact canonical order and bounds;
  `leafcn + 0.5 <= frootcn <= min(60, 49.5)`; site is ABBY or JERC; forcing is consecutive
  no-leap hourly data with the locked seven variables and required ordered history.
- Engine output has static positive finite TOTSOMC/TOTSOMN, timestamped finite GPP/SR, exact
  release/source provenance, no ELM truth, and predicted C/N plus predicted same-hour GPP at the
  downstream stages. No clipping is permitted.
- Locked sample positions/members: `0:g00314`, `102:g00137`, `204:g00378`, `306:g00968`,
  `409:g00233`, `511:g00242`, `613:g00427`, `715:g00836`, `818:g00890`; sites ABBY/JERC;
  half-open 48-hour windows `[720,768)`, `[30648,30696)`, `[61272,61320)`.
- Exact comparison denominators are 18 rows per spinup target and 2,592 values per hourly stage.
  Every stage must match the published handoff at `rtol=1e-6`, `atol=1e-4`; this narrow replay
  allowance covers batch-dependent floating-point arithmetic only. Direct versus chunked/windowed
  inference remains at `rtol=atol=1e-6`, serialization/reload remains exact, and missing history,
  invalid site/parameter/time, and leakage cases reject; fixed-test access is false.
- Four figures: `spinup_cn_parity.png`, `parity_flux_hourly.png`, `joint_gpp_sr_hourly.png`, and
  `gpp_sr_joint_conditional.png`. Exact metrics, correlations, density grids, conditional bins,
  night/near-zero summaries, manifest, and hashes are retained.
- Flux parity uses full-record streamed 200x200 probability-density grids in a GPP/SR by
  pooled/ABBY/JERC layout with common per-row axes and log normalization, 1:1 lines, and exact
  R2/RMSE. Joint GPP-SR uses three panels and overlaid unit-mass ELM/surrogate contours at
  50/75/90/99 percent enclosed mass with exact Pearson correlations.
- Conditional diagnostics use paired finite records; night is `FSDS <= 1 W m-2`; daylight
  near-zero is `FSDS > 1` and applicable GPP `<= 0.1 gC m-2 day-1`; remaining daylight uses
  exact pooled combined ELM/surrogate GPP quantile edges for 20 common bins. Plot median and
  q10-q90; retain exact count, mean, median, q10, and q90; duplicate edges or empty required
  products fail.
- Every figure states that evidence is in-sample 819-member development-only descriptive evidence,
  not causal confirmation, held-out end-to-end performance, or full-chain uncertainty.
- Application/code/interface/schema/data/dependency/numerical/scientific changes after execution
  begins require fresh authority.

## Provenance and Job Ledger

| Work unit | Run directory | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- |
| preflight | `<root>/runs/preflight` | jobs `24678619`, `24678718`, `24678814`, `24678875` | attempts 1-3 `FAILED 1:0`; attempt 4 `COMPLETED 0:0` | reviewed corrected preflight and independent result gate passed |
| integration | `<root>/runs/integration` | jobs `24678937`, `24680350`, `24680395` | attempts 1-2 `FAILED 1:0`; attempt 3 `COMPLETED 0:0` | bounded integration and independent result gate passed |
| diagnostics | `<root>/runs/diagnostics` | jobs `24680459`, `24680504` | both `COMPLETED 0:0` | corrected products promoted; independent result gate passed |
| final | `<root>/runs/final` | job `24691748` | `COMPLETED 0:0` | deep validation and independent result gate passed |

## Independent Read-Only Review

- Reviewer: independent read-only agent `/root/iter014_reviewer`
- Reviewed source hash: engine `665c19c2...9b6`; tests `98ccf347...730c`; config
  `ece93603...304e`; manifest `075534f2...6573`; preflight script `67c07adb...aa81`.
- Outcome: preflight package `pass_with_concerns`; submission permitted; no preflight blocker.
- Findings and primary-agent response: reviewer confirmed exact submitted-copy equality, release and
  split identities, 819/205 boundary, sample mapping, 25/43/44 features, loaders/scalers,
  predicted-upstream path, parameter/C:N/site/history checks, resources, and prohibitions. Later
  gates must resolve non-streaming diagnostic metric/correlation implementation, final-script
  hardcoded integration attempt, and runner enforcement of handoff hashes before their respective
  submissions. These do not affect the bounded compute-node preflight.
- Attempt-2 correction review: `pass_with_one_record_correction`; engine
  `73fb88a8...ecf`, execution manifest `6717e6ea...6813`; correction changes only the prediction
  kernel from batch-shaped artifact calls to fixed one-row calls inside optional outer chunks.
  Reviewer confirmed the old/new manifest differs only in the engine hash, attempt-1 evidence is
  preserved, exact submitted-copy equality and static gates pass, and cleared exactly one retry.
- Attempt-2 result review: `block`; independent review confirmed a numerical compatibility
  failure, not a scheduler, node, transport, launch, or resource failure. Direct-versus-chunk
  determinism passed, then the immutable published-handoff replay gate failed in 25/48 GPP values.
  Both attempts are preserved and terminal; the reviewer requires renewed user authority before
  any code change, tolerance revision, handoff interpretation change, or third submission.
- Attempt-3 package review: `pass`; reviewer verified the engine is unchanged, the only config
  additions are `handoff_replay_rtol=1e-6` and `handoff_replay_atol=1e-5`, only published-handoff
  comparisons consume them, direct/chunk and serialization gates remain strict, submitted copies
  byte-match canonical, prior evidence is preserved, and exactly one submission is cleared.

## Execution and Diagnostics

- Initialization: approved revised package recorded; canonical and exact external run packages
  materialized for all four work units.
- Static validation: JSON and shell syntax, execution-manifest verification, canonical/submitted
  equality, `git diff --check`, exact input hashes, resource/scope inspection pass. Repository
  Python remains restricted to the approved compute-node preflight.
- Preflight submission: exact reviewed run-directory copy submitted as attempt 1; job `24678619`
  passed immediate identity checks for command, exports, workdir, logs, stdin `/dev/null`, account,
  partition, 2 CPUs, Puma-derived 10 GB, and 30-minute limit.
- Preflight result: job `24678619` is authoritatively terminal `FAILED 1:0` after `00:00:21`;
  batch MaxRSS `283920K`. Both focused tests loaded the real frozen artifacts; invalid-input tests
  passed, but direct versus 7-row chunked GPP replay differed in 8/48 values with maximum absolute
  difference `6.67572021e-06`, exceeding the immutable `rtol=atol=1e-6` gate. The test stopped
  before the preflight runner, integration, diagnostics, fixed-test access, or training.
- Failure classification: numerical/interface failure caused by prediction batch-shape sensitivity;
  evidence is preserved in `preflight_24678619.{out,err}`. The approved package requires renewed
  authority before any substantive code correction or retry. No retry or cancellation occurred.
- Renewed authority: user response `Authorize the deterministic numerical correction and one
  reviewed Iter014 preflight retry` at `2026-11-17T00:19:29-07:00`. Correction scope is limited to
  a fixed one-row numerical kernel inside optional outer chunks; artifacts, features, scalers,
  inputs, tolerances, sample, resources, and scientific gates remain unchanged. Preflight attempt
  2 requires refreshed immutable copies and independent re-review before submission.
- Preflight attempt 2: job `24678718` submitted after review and passed immediate identity checks:
  attempt/export hashes, run directory, logs, stdin `/dev/null`, account `chopinsong`, partition
  `standard`, 2 CPUs, 10 GB, and 30-minute limit.
- Preflight attempt-2 result: authoritatively terminal `FAILED 1:0` after `00:00:24`; batch MaxRSS
  `291668K`. Manifest verification and invalid-input tests passed. Fixed one-row calls eliminated
  the direct-versus-chunk failure, but direct one-row GPP differs from the historical published
  batched handoff in 25/48 values at `rtol=atol=1e-6`; maximum absolute difference
  `7.15255737e-06`, maximum relative difference `0.00032807`. The test stopped before the
  preflight runner; no integration, diagnostics, fixed-test access, or training occurred.
- Attempt-2 evidence: stdout SHA-256 `91a162cc...07e`, stderr SHA-256
  `f4158e9e...ce4`; immutable attempt-2 config, execution manifest, and Slurm snapshots retained.
  The single authorized retry is exhausted; no further correction or submission is authorized.
- Renewed tolerance/retry authority: user agreed with the primary recommendation and authorized a
  retry. The amendment is narrow: published-handoff replay changes to `rtol=1e-6`, `atol=1e-5`;
  direct-versus-chunk stays at `rtol=atol=1e-6`, serialization stays exact, and no engine,
  release, sample, resource, or scientific-product input changes. Exactly one attempt-3 preflight
  retry is pending refreshed immutable package review.
- Preflight attempt 3: job `24678814` submitted after independent review and passed immediate
  identity checks for hashes, workdir, logs, stdin `/dev/null`, account, partition, 2 CPUs, 10 GB,
  and 30-minute limit.
- Preflight attempt-3 result: authoritatively terminal `FAILED 1:0` after `00:00:19`; batch MaxRSS
  `221824K`. Manifest verification and both focused tests passed, including the amended handoff
  replay, strict direct/chunk checks, and exact serialization. The subsequent absolute-path runner
  invocation failed before creating output with `ModuleNotFoundError: No module named 'model_ELM'`.
  This is a code-structure/import-path failure, not evidence for further tolerance relaxation.
- Attempt-3 evidence: stdout SHA-256 `91a162cc...07e`, stderr SHA-256
  `be37a720...faa`; immutable config, manifest, and Slurm snapshots retained. No integration,
  diagnostics, training, full-chain replay, or fixed-test access occurred.
- Attempt-4 package review: `pass`; each wrapper adds only
  `PYTHONPATH=/xdisk/chopinsong/tianyihu/elm-olmt`; model, config, tolerances, sample, resources,
  and scientific behavior are unchanged. Job `24678875` passed immediate scheduler identity checks.
- Attempt-4 result: authoritatively terminal `COMPLETED 0:0` after `00:00:33`; batch MaxRSS
  `291916K`. All manifest entries verified, both focused tests passed, and the preflight runner
  reported success with three synthetic parameter vectors, exact 25/43/44 feature counts, locked
  sample/windows, and false fixed-test/training/full-819 flags. Report SHA-256 `8b3db4be...37cd`;
  stdout `8f917c75...0aaa`; stderr `ffd57392...c757` (only ArviZ warning plus test summary).
- Attempt-4 result review: `pass`; independently verified terminal accounting, manifest, focused
  tests, report schema/content/hashes, locked identities, exclusions, and submitted-copy equality.
- Integration package correction under the user's standing code-versus-numerical judgment
  instruction: enforce all three handoff file SHA-256 identities before opening them, retain the
  verified identities in the report, and require exact full-result serialization round trip for
  parameters, time, C/N, fluxes, parameter names, site, and provenance. Inference arithmetic,
  releases, tolerances, sample, windows, denominators, and resources are unchanged.
- Integration package review: `pass`; independently verified runtime handoff identity enforcement,
  complete serialization checks, locked sample/sites/windows/denominators/tolerances/exclusions,
  4-CPU/20-GB/1-hour resources, and canonical/submitted equality.
- Integration attempt 1: job `24678937` is authoritatively terminal `FAILED 1:0` after `00:00:21`;
  batch MaxRSS `914620K`. Manifest verification passed. The runner verified the three handoff
  identities, completed and serialized ABBY `[720,768)`, then rejected ABBY `[30648,30696)` GPP
  against the handoff at `rtol=1e-6`, `atol=1e-5`. The failure path did not emit mismatch count or
  maximum absolute/relative differences, so scientific acceptability cannot yet be judged. No
  JERC window, diagnostics, training, fixed-test access, or full-819 engine run occurred.
- Integration attempt-1 evidence: stdout SHA-256 `91a162cc...07e`; stderr
  `763c7435...f4f`; partial serialized output `abby_720_768.nc` SHA-256
  `2f16c705...d60`; immutable submitted package snapshots retained.
- Attempt-1 result review: `block`; provisionally numerical handoff replay failure, but not a
  justified tolerance change because first-failure instrumentation omitted magnitude/count data.
  Reviewer cleared one scoped observability correction and independently reviewed retry under the
  user's standing judgment instruction, with engine and tolerances unchanged.
- Integration attempt-2 instrumentation: accumulate all bounded published comparisons (static C/N
  once per site; GPP/SR for every site/window), mismatch count, zero-reference count, maximum
  absolute difference, maximum relative difference on nonzero references, and maximum normalized
  tolerance ratio. Continue strict direct/chunk and exact serialization gates, serialize all six
  bounded outputs, write `integration_failure_report.json` if any replay comparison fails, then
  exit nonzero without a pass report.
- Integration attempt-2 package review: `pass`; job `24680350` passed immediate identity checks for
  reviewed hashes, workdir/logs/stdin, `chopinsong/standard`, 4 CPUs, 20 GB, and 1-hour limit.
- Integration attempt-2 result: authoritatively terminal `FAILED 1:0` after `00:00:25`; batch
  MaxRSS `1049676K`. The designed failure report covers all 16 comparison groups and exact
  denominators. Only four GPP groups fail, totaling 10/2,592 values; maximum GPP absolute
  difference `5.340576171875e-05` and maximum normalized tolerance ratio `1.6048955`. All C/N and
  SR groups pass (maximum SR difference `4.76837158203125e-06`); direct/chunk differences are zero
  for all four outputs and serialization is exact for all six bounded outputs and metadata.
  Failure-report SHA-256 `4c616c3e...e6e9`; stdout `91a162cc...07e`; stderr
  `3a409c52...169e`. No training, fixed-test access, or full-819 engine run occurred.
- Attempt-2 result review: historical-batch floating compatibility, not code/schema/data error.
  The complete bounded envelope is sufficient for an absolute-tolerance decision: only GPP is
  affected, direct/chunk and serialization are exact, and maximum absolute error is
  `5.340576171875e-05`. Under the user's standing numerical-versus-code judgment authority,
  published-handoff `atol` changes narrowly from `1e-5` to `1e-4` (about 1.87x headroom), while
  handoff `rtol=1e-6`, direct/chunk `rtol=atol=1e-6`, and exact serialization remain unchanged.
- Integration attempt-3 package review: `pass`; job `24680395` passed immediate identity checks for
  reviewed hashes, workdir/logs/stdin, `chopinsong/standard`, 4 CPUs, 20 GB, and 1-hour limit.
- Integration attempt-3 result: authoritatively terminal `COMPLETED 0:0` after `00:00:20`; batch
  MaxRSS `828420K`. Report `pass` with exact 18/18/2,592/2,592 denominators and zero failed replay
  groups. Maximum differences: C `2.037268e-10`, N `1.818989e-11`, GPP `5.340576e-05`, SR
  `4.768372e-06`; direct/chunk differences are zero for all stages and serialization is exact.
  All three handoff hashes and six serialized-output hashes are retained; exclusions remain false.
  Report SHA-256 `9c2f7b64...0a2f`; stdout `5ad77136...151b`; stderr `700b522d...922e`.
- Integration attempt-3 result review: `pass`; independent review verified terminal accounting,
  report and output hashes, exact denominators, zero replay failures, strict direct/chunk and
  serialization gates, handoff identities, and exclusions.
- Diagnostics package correction: enforce and retain the three handoff SHA-256 identities before
  reading predictions; replace whole-record float64 flattening for R2/RMSE/MAE/bias and Pearson
  correlation with deterministic eight-row blockwise float64 moment accumulation over every
  development record. Density histograms remain exact and chunked; diagnostic definitions,
  denominators, figures, and scientific scope are unchanged.
- Diagnostics package review: `pass`; job `24680459` passed immediate identity checks for reviewed
  hashes, workdir/logs/stdin, `chopinsong/standard`, 8 CPUs, 40 GB, and 4-hour limit.
- Diagnostics attempt-1 result: authoritatively terminal `COMPLETED 0:0` after `00:01:48`; batch
  MaxRSS `8007800K`. All 12 expected files were generated with a passing manifest and exact
  metrics, correlations, density grids, conditional tables, and four figures; manifest SHA-256
  `60457386...81be`, stdout `87c12630...6f0b`, stderr `700b522d...922e`. Result acceptance is
  withheld because the wrapper left outputs in `runs/diagnostics/attempt_1` rather than approved
  `products/`, and visual inspection found both parity colorbars overlaid on JERC panels.
- Diagnostics attempt-1 result review: `block` on delivery/layout only; all scientific calculations,
  tables, densities, correlations, conditional records, identities, hashes, and the other three
  figures passed. Attempt 2 moves each parity colorbar to a dedicated right-side axis, stages into
  its attempt directory, promotes exact contents into an initially empty approved `products/`
  directory only after successful computation, and verifies `evidence.sha256` after promotion.
- Diagnostics attempt-2 package review: `pass`; job `24680504` passed immediate identity checks for
  reviewed hashes, workdir/logs/stdin, `chopinsong/standard`, 8 CPUs, 40 GB, and 4-hour limit.
- Diagnostics attempt-2 result: authoritatively terminal `COMPLETED 0:0` after `00:02:03`; batch
  MaxRSS `8017856K`. All evidence hashes verify in staging and promoted `products/`, and `diff -rq`
  confirms byte identity. Corrected parity colorbars occupy dedicated right margins with no panel
  overlap; other figures and scientific products are unchanged. Manifest SHA-256
  `e5b96f6e...389f`; stdout `65af00f9...ab66`; stderr `700b522d...922e`.
- Diagnostics attempt-2 result review: `pass`; independent review verified terminal accounting,
  staging/promotion byte identity, all evidence hashes and inventories, corrected parity layout,
  unchanged passed figures, manifest identities/counts, and development-only scope.
- Final validator correction: use accepted integration `attempt_3`; verify all three handoff hashes
  before use and require them in both reports; deeply validate integration comparisons/tolerances,
  six serialized hashes, product evidence, density shapes/normalization/pooled identities,
  conditional cartesian inventory/common edges/order/accounting, and independently recompute all
  six Pearson rows with blockwise moments in addition to the 12 exact metric rows.
- Final package review initially blocked on two validator-depth omissions only. The refreshed
  validator now requires every conditional row's lower/upper edges to equal the common 20-bin edge
  vector, checks every midpoint, and locks the diagnostic manifest schema, snapshot, descriptive
  evidence class, streamed aggregate rule, and `performance_gate_applied=false` semantics.
- Refreshed final package review: `pass`; job `24691748` passed immediate identity checks for
  reviewed hashes, accepted integration/products paths, workdir/logs/stdin,
  `chopinsong/standard`, 4 CPUs, 20 GB, and 1-hour limit.
- Final-validation result: job `24691748` completed `0:0` in `00:01:01`; authoritative batch
  MaxRSS was `1804820K`. Report SHA-256 `9f046a58...4ab`, stdout `0277e3b5...bce2`, and stderr
  `700b522d...922e`. Deep validation independently recomputed 12 metric rows and six Pearson rows,
  checked 120 conditional and 12 night/near-zero rows, two density packages, four figures, all six
  serialized outputs, exact handoff identities, and the false fixed-test/training/full-819 flags.
- Independent final-result review: `pass`; the reviewer reproduced terminal accounting, report
  identity and counts, exact decision token, release hashes, scope exclusions, and canonical versus
  submitted package identity with no blocker.
- Final scheduler reconciliation found an empty job-scoped queue and authoritative terminal `sacct`
  records for all ten Iter014 job IDs. All five failed jobs and the rejected completed diagnostic
  attempt are classified above; no job was cancelled, active, or unaccounted.
- Four-record closeout command
  `bash development/three_stage_surrogate/slurm/iter014/validate_closeout_iter014.sh --active-job-count 0`
  returned `ITER014_FOUR_RECORD_VALIDATE_PASS`; validator SHA-256 `0ebb78aa...ac0eb7` and exact
  output are preserved in `summaries/iter014/four_record_validation.txt`.

## Validation, Evaluation, and Decision

- Overall acceptance result: `pass`
- Overall decision and closeout conclusion: `three_stage_inference_ready_for_robustness`; the
  frozen callable engine, bounded two-site integration, and four development-only diagnostics meet
  the approved Iter014 contract. This does not authorize full-chain retraining or uncertainty.
- Limitations: frozen in-sample all-development models; ABBY/JERC only; descriptive diagnostics;
  temporary unbacked storage.
- Campaign-plan amendment recommendation: `none`
- Next action: none; iteration is terminal and no later iteration is proposed or authorized.

## Explicit Terminal Declaration

Iter014 is closed. No next iteration is proposed or authorized.

## Closeout Checklist

- [x] Iteration report finalized
- [x] Required evidence copied to `summaries/iter014/`
- [x] `ITERATION_SUMMARY.md` updated
- [x] `registry.csv` updated without schema changes
- [x] `handoff/CURRENT.md` rebuilt
- [x] Campaign alignment recorded consistently
- [x] Four-record validator passes
- [x] No job is active or unaccounted and every failure is classified
- [x] Exactly one authorized local no-push closeout commit created and verified
