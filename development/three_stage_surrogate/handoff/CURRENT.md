# Three-Stage Surrogate - Current Handoff

## Campaign Plan

- Plan path: `development/three_stage_surrogate/PLAN.md`
- Current SHA-256: `6fe376067f122a4b6f049b4d5420c69d2f1fcce40e3e6954202814346473214d`
- Last-iteration locked SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360` (Iter014 historical identity)
- Campaign progression: item 6 is complete; item 7 full-chain robustness remains next, with no
  iteration initialized or authorized
- Alignment: `aligned`; approved deviation: `none`
- Campaign-plan amendment: user-authorized prospective nonnegative GPP policy for future
  full-chain training; Iter014 and existing `release_0001` artifacts remain unchanged

## Live State

- Last closed iteration: `iter014`
- Status: `completed`
- Phase: `closed`
- Work type: `integration`
- Acceptance result: `pass`
- Decision: `three_stage_inference_ready_for_robustness`
- Active job scope: none; all ten Iter014 job IDs are authoritatively terminal
- Active monitoring: none; no job is active or unaccounted
- Site profile: `development/hpc/puma.md`
- Closed: `2026-11-17T15:21:18-07:00`

## Completed Scope and Authority

- Implemented the frozen ABBY/JERC spinup -> GPP -> SR callable engine with canonical 18-parameter,
  conditional C:N, site, forcing, timestamp, and 720-hour-history validation.
- Used only published `release_0001` artifacts and predicted upstream C/N and same-hour GPP; no
  model fitting, fixed-test access, ELM truth in inference, release edit, or full-819 engine chain.
- Validated the locked nine-member, two-site, three-window sample against published handoffs at
  handoff `rtol=1e-6`, `atol=1e-4`; direct/chunk remained `rtol=atol=1e-6` and serialization exact.
- Produced the four approved in-sample development-only descriptive figures and exact metric,
  correlation, density, conditional, and night/near-zero evidence from published predictions/truth.
- Exactly one local no-push closeout commit is the approved branch; no push is authorized.

## Evidence and Accounting

- Snapshot `39b05495...187a`; split `99467dea...0fce`; C/N, GPP, and SR handoffs
  `9e2d5be4...fdb5`, `c905fc60...98bb`, and `3704cab6...d3a1`.
- Preflight jobs `24678619`, `24678718`, and `24678814` failed with classified numerical/interface,
  historical-batch compatibility, and import-path causes; corrected `24678875` completed `0:0`.
- Integration jobs `24678937` and `24680350` failed with classified handoff-replay observability and
  historical-batch numerical causes; bounded accepted job `24680395` completed `0:0`.
- Diagnostics jobs `24680459` and `24680504` completed `0:0`; the first was rejected only for
  delivery/layout and the corrected second product set passed. Final job `24691748` completed `0:0`.
- Final validation report SHA-256 `9f046a58ff0599f868ce722191e08751f5afdede8062ab56baaee898e796a4ab`;
  all scopes are terminal, no cancellation occurred, and compact evidence is in
  `development/three_stage_surrogate/summaries/iter014/`.
- Limitations: frozen in-sample all-development models, ABBY/JERC only, descriptive diagnostics,
  no end-to-end held-out or full-chain uncertainty claim, and temporary unbacked `/xdisk` storage.

## Next Action

None. Iter014 is terminal.

## Next Iteration Plan (Planning Only)

No next iteration is proposed or authorized.

## Artifact References

- Report: `development/three_stage_surrogate/iterations/iter014.md`
- Registry: `development/three_stage_surrogate/registry.csv`
- Cumulative summary: `development/three_stage_surrogate/ITERATION_SUMMARY.md`
- Canonical scripts: `development/three_stage_surrogate/slurm/iter014/`
- External root: `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/three_stage_surrogate/iter014_abby_jerc_coupled_inference`
