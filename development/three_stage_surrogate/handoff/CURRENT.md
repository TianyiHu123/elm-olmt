# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan: `development/three_stage_surrogate/PLAN.md`
- Current/latest locked SHA-256: `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`
- Phase/alignment: progression item 4 spinup release complete; `aligned`; deviation `none`

## Live State

- Latest iteration: `iter004`
- Active iteration: none
- Work type: `implementation`
- Status: `completed`
- Phase: `closed`
- Package state: `closed`
- Next proposal state: `planning_only`
- Active job scope: none
- Active monitoring: none; all Iter004 jobs terminally accounted
- Site profile: `development/hpc/puma.md`
- Last updated: `2026-10-31T04:59:22-07:00`

## Best Evidence and Decision

- Result/decision: `pass` / publish and authorize spinup `release_0001`, its predicted-C/N GPP
  handoff, and its explicitly surrogate-only uncertainty package.
- Stable product:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe_vertc/surrogate_products/spinup_abby_jerc/release_0001`.
- Identities: release manifest `69f840f7...f2dc`; artifact `9abb342d...a809`; predicted-C/N
  handoff `9e2d5be4...fdb5`; catalog `93f080de...10be`.
- Robustness: 20 fresh synchronized 655/164 development splits; 6,560 paired rows; cross-
  repetition log R2 ABBY C/N `0.8931/0.8899`, JERC C/N `0.8053/0.8011`; 22/40 nonfatal
  convergence warnings.
- Uncertainty: member-balanced `1/k`, population-`ddof=0` paired log-error covariance; C/N
  correlation ABBY/JERC `0.9775/0.9883`; minimum eigenvalues `0.00298/0.00287`.
- Validation: `ITER004_VALIDATE_OK`; exact 819-development-member fit; fixed-test access false;
  flexible fresh-process reload, explicit schemas, covariance, hashes, and catalog-last publication
  passed.
- Accounting: `24479223`, `24480121`, `24480153`, `24480174`, and `24480199` completed `0:0`.
  Robustness attempt `24479279` failed before fitting; its exact source and bounded non-scientific
  correction are preserved and independently reviewed.
- Evidence: `development/three_stage_surrogate/summaries/iter004/` and the external Iter004 root.
- Limitations: two sites; overlapping development splits; robustness uses 655-member fits while the
  release uses 819; handoff predictions are in-sample; strong C/N error correlation; convergence
  warnings; temporary unbacked `/xdisk`; no fixed-test, flux-stage, or full-chain evidence.
- Campaign-plan amendment recommendation: `none`.

## Current Objective and Next Action

Iter004 is closed. Review and, if acceptable, grant fresh consolidated kickoff authority for the
planning-only Iter005 proposal below. No Iter005 initialization, directory, implementation,
execution, scheduler, retry, publication, record, or commit authority is active.

## Next Iteration Plan (Planning Only)

### Iter005 - ABBY/JERC GPP input and inference-interface materialization

- Proposed sequential ID/work type: `iter005` / `data_initialization`.
- Campaign alignment: `development/three_stage_surrogate/PLAN.md`, SHA-256
  `9bbb68654a5ef7c41298a135758946f3a4ab3397b82d9238539cbc3dbe319128`; progression item 5;
  `aligned`; proposed deviation `none`.
- Evidence-derived objective: before any hourly GPP fit, implement and independently validate the
  memory-aware ABBY/JERC GPP loader, timestamp-aware feature builder, and deterministic inference
  interface using the published spinup `release_0001` and its 819-member predicted-C/N handoff.
  Freeze a reusable prepared-data contract that a later GPP baseline can consume without ELM C/N.
- Inputs/dependencies: immutable snapshot `r0001` and its exact 819-development/205-fixed-test
  boundary; stable spinup catalog `93f080de...10be`, release manifest `69f840f7...f2dc`, artifact
  `9abb342d...a809`, and handoff `9e2d5be4...fdb5`; ABBY/JERC forcing and ELM GPP targets in the
  snapshot; canonical 18-parameter order; and site-specific no-leap timestamp axes. Trust only
  recorded hashes and reject any identity, time, unit, or coverage mismatch.
- Bounded scope/work units: locked implementation and read-only review; one no-training preflight;
  one compute-node streaming/sharded development-only materialization; one independent contract
  validation; concise records; and one user-selected closeout branch. Implement one shared
  training/inference feature path with explicit `upstream_mode=in_sample`; predicted C/N only;
  exact site/member/time coordinates; actual-timestamp `sin_hour`, `cos_hour`, `sin_doy`, and
  `cos_doy`; declared forcing/history features and masks; per-site coverage; and deterministic
  shard/manifests. Unsupported upstream modes fail explicitly.
- Exclusions: no GPP model fit, tuning, artifact, or performance claim; no fixed-test parameter,
  C/N, GPP, or forcing access; no true ELM C/N as an upstream feature; no SR, full-chain robustness,
  observations, MCMC, campaign-plan edit, or push. Do not silently force a common site window or
  materialize duplicated parameter/CN columns when indexed references suffice.
- Tentative gates/decision: exact snapshot/release/member/parameter/site/time identities; all and
  only 819 development members; zero fixed-test access; GPP units/valid masks and each site's full
  declared window preserved; no-leap calendar and timestamp-derived cyclic features independently
  reproduced; predicted-C/N values exactly match the release handoff; training and inference
  feature order/values agree on sampled rows; deterministic shard hashes and row accounting;
  bounded memory behavior; no active/unaccounted jobs; independent validation. Publish the prepared
  GPP-input contract only if all gates pass; otherwise publish nothing and retain spinup release as
  valid but GPP-uninitialized.
- Proposed site/output/resources: Puma `chopinsong/standard`; run root
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter005_abby_jerc_gpp_input`;
  temporary unbacked `/xdisk`, with raw/sharded data external and compact schemas/evidence in Git.
  Propose one CPU/derived 5 GB/30 minutes for preflight and validation, and four CPUs/derived 20 GB/
  four hours for streaming materialization, single-threaded per worker and no GPU. Confirm capacity
  and input sizes at kickoff; any different shape requires explicit package approval.
- Proposed review/monitoring/retry/cancellation: independent read-only review before preflight and
  substantive materialization; exact submitted copies and configurations; job-scoped monitoring
  through terminal `sacct`; initial attempt plus up to three same-scope retries or bounded
  non-scientific debugging corrections that preserve the approved contract; any scientific,
  feature, target, coverage, upstream-mode, fixed-test, or resource change requires fresh approval.
  Cancel only recorded Iter005 jobs for identity mismatch, duplicate submission, unsafe behavior,
  or explicit user direction.
- Expected evidence/stop: validated GPP target/forcing/time inventory; frozen feature schema and
  units; predicted-C/N join proof; development-only shard/index manifests and hashes; sampled
  training/inference equivalence; coverage/mask/resource evidence; concise records. Stop before any
  GPP fitting. Fresh consolidated approval is required before initialization, directory creation,
  implementation, execution, scheduler mutation, publication, records, or closeout.
