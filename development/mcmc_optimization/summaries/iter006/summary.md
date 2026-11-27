# iter006 compact closeout summary

- Decision: `iter006_validation_failed`; status `completed`; acceptance `fail`.
  The user's Iter006 kickoff was the consolidated authority to revise Iter005's
  historical planning-only proposal. The plan remained unchanged, SHA-256
  `5ee74c5208f489c540f21a8c13ce0fbe0ed84ea1d6c9043d6eece2293a0860c0`.
- Scope: PPE1 18-parameter ABBY/JERC four-observable target, daily GPP/SR, joint
  C/N CV 0.30, full `[720,61320)` no-leap window, frozen coupled surrogate,
  observations and uncertainty. Input inventory SHA-256
  `faae90d71f1d141474c60883eb4cf83436f4211cd96af1fff7b7d390f8f1a90c`;
  frozen preflight passed. PPE2 remained scientifically inactive.
- The old ABBY failure was exactly replayed from frozen source/state/seed `540041`.
  At step 3, uncorrected snooker split 0, walker 40, `k_s2` mapped to
  `0.002999999999999999`, two directional ULPs below its marginal lower bound
  `0.003`. The independent stored-unit reference is about 0.393221 ULP inside
  the bound. Legacy `log(lower)+u*log(high/lower)` lost the small positive term;
  five later generated walkers in the fatal subbatch were unexamined. The old
  ledger and partial HDF replay are byte-identical to Iter005. Attribution
  SHA-256 `4fb109dc764276d8f438b5e727e79005e5cf0b9197e0f7413d246087f42e13de`.
- A repository-scoped MIT-attributed corrected snooker implements both upstream
  changes: direction `delta/norm` and Hastings factor `ndim-1`. A physical
  boundary mapper retains original finite z and analytic Jacobian, checks
  actual conditional bounds, and uses a frozen input-regime plus full-error
  policy. Policy SHA-256 `931a323a0a98641e539945e5060b3b54284569a8bbd5fc7c6e5e44eba491191e`:
  K is 2 ULP for linear sides and 3 for log-uniform/conditional-root sides,
  below the eight-ULP ceiling. Stage B's bounded independent numerical report
  passed, SHA-256 `a37216b7ecfdc1f8f864aa9ec320e9f34077df72c70ac4733b0c4fd1cb9ff4ab`.
  Installed uncorrected move SHA-256 `73b03a2e56928c590e55e3a7f4c3406d7a82ae642550ae21f79efafec589e9e6`;
  corrected helper SHA-256 `cb4f08acab24d1b0bb46e4a26688c961d49f7aa99bd60eeced44a387827622a7`.
- The Stage B test gate failed: 50 tests ran, two errors. The modified posterior
  broke an existing duck-typed Iter005 fixture; the Iter001 coupled-interface
  setup also failed because its relative source path was resolved under the
  external Stage B workdir. Neither is scheduler/node/transport interruption.
  The one preflight and one scoped test/integration correction opportunities
  were already consumed in Stage A. Two independent read-only reviewers agreed
  that B cannot be rerun under this contract and C or either pilot cannot start.
  Stage F was intended to validate the available failed evidence, but failed.
- No corrected ABBY/JERC restart or 128-step pilot ran; no corrected step-zero,
  per-step, block, cumulative boundary time history or pilot figure exists.
  The legacy event is a proposal-only numerical finding, not retained-state
  occupancy. Acceptance, movement, endpoint occupancy and convergence were
  unassessed; no convergence or calibrated-posterior claim is made.
- Jobs: A `24840516`, `24840555`, `24840587`; B `24840823`; F `24840903`.
  All five are terminal `FAILED 1:0`; C/D/E were not submitted. F's fixed
  evidence/hash checks passed, but its own no-pilot-HDF check mistakenly tested
  truthiness of empty glob iterators and raised before creating its result JSON.
  This application error is not eligible for an infrastructure retry. Static
  closeout records the additional F validation failure. Accounting SHA-256
  `1863332a2246a9d7db29ad032d2966310804ee70c38e6d285b9bd5d88445c7b9`;
  runtime size 3,638,392 bytes, below 2 GiB. Independent read-only result
  reviews and static four-record reconciliation passed for the truthful failure;
  the preserved validator result SHA-256 is
  `c53d74570bce3d588e4939941d7aa44c95d23917ce1872736dad94643427321f`.
- Evidence root:
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/mcmc_optimization/iter006_sampler_boundary_diagnostics`.
  Stage F reviewed driver SHA-256 `e757b27bbbf013538a969dee72b37492b8749c61ebba30ebd4cfa4046973772d`;
  source/package manifests `c820e2160eb686f8db3dc432494d6296fd317c38953c36748d0e4908908b636a` /
  `bddd73492b6a4efb44541408f9dc4b2a9d58284364ff09b0019e31addf9cd848`.
- Planning-only next proposal: repair the posterior's legacy fixture dispatch,
  run the established test suite from the repository root and fix F's empty-glob
  check, then seek a new
  bounded kickoff for independent B/C validation and, only after those gates,
  the two 128-step pilots. Retain the frozen policy and old-failure attribution;
  separately review whether the proposed endpoint policy needs sensitivity
  checks if accepted endpoint occupancy later proves high.
