# iterXXX - <short MCMC optimization objective>

## Status

- Iteration ID: `iterXXX`
- Work type: `<audit | implementation | validation | integration | benchmark | experiment | release>`
- Run slug: `mcmc_optimization_iterXXX_<work_unit>`
- Status: `planned`
- Phase: `initializing`
- HPC profile: `development/hpc/<site>.md`
- Started: `<timestamp and timezone>`
- Closed: `<timestamp and timezone or pending>`

## Campaign Plan Alignment

- Campaign plan: `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md`
- Locked plan SHA-256:
- Applicable campaign phase:
- Alignment: `aligned | approved_deviation | amendment_recommended`
- Approved deviation: `none`

## Finalized Planning Proposal

- Sequential ID and work type:
- Evidence-derived objective and optional hypothesis:
- Prior ID, 18-parameter schema, support, transforms, and source identities:
- Surrogate release, uncertainty, observation, forcing, and other dependencies:
- Site and temporal scope:
- Bounded work units and exclusions:
- Tentative scientific, numerical, interface, reproducibility, and performance gates:
- Decision rule and tie-breaks where applicable:
- Proposed HPC profile, output root, resources, preflight, review, monitoring, retries,
  cancellation, retention, and stop boundaries:
- Expected evidence, artifacts, and record updates:
- Fresh consolidated kickoff-approval boundary:

## Consolidated Kickoff Package and Runtime Contract

| Field | Value |
| --- | --- |
| User response and approval timestamp | `<exact response; timestamp and timezone>` |
| Kickoff goal, finite work-unit count, and stop conditions | `<goal; count; conditions>` |
| Campaign plan identity and alignment | `<path; SHA-256; phase; alignment; deviation or none>` |
| Confirmed HPC system and profile | `<system; development/hpc/<site>.md>` |
| Approved output and storage policy | `<exact root; layout; creation authority; retention and backup assumptions>` |
| Locked scientific dependencies and scope | `<prior/schema; surrogate; uncertainty; observations; forcing; sites; time; exclusions>` |
| Immutable gates and decision rule | `<scientific; numerical; interface; reproducibility; performance; rule>` |
| Lifecycle authority | `<preparation through records and closeout>` |
| Resources, monitoring/wait, and retry boundaries | `<exact resources and separate limits>` |
| Cancellation scope | `<conditions; exact current-iteration job scope>` |
| Outside-sandbox authority | `<locked sbatch; job-scoped monitoring/accounting; bounded scancel>` |
| Closeout branch | `<one commit authorized | validated_uncommitted>` |

## Declared Inputs and Compatibility Evidence

| Input/dependency | Role | Path | Version/schema | Size/hash | Trust, leakage, and compatibility evidence |
| --- | --- | --- | --- | --- | --- |
| Campaign plan | scientific contract | `development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md` | `<identity>` | `<SHA-256>` | `<alignment>` |
| Prior design | posterior prior | `<path>` | `<prior_id; 18-parameter order/support>` | `<hashes>` | `<normalization/map/schema evidence>` |
| Coupled surrogate | target-free forward model | `<path>` | `<release/site/schema>` | `<manifest/catalog hashes>` | `<prior/support compatibility>` |
| Uncertainty | fixed likelihood input | `<path>` | `<resolution/site/schema>` | `<hashes>` | `<development-only provenance>` |
| Observations/forcing | likelihood/context | `<paths>` | `<variables/calendar/units/QC>` | `<hashes>` | `<site/time alignment>` |

## Frozen Scientific Configuration

- Prior ID and physical parameter order:
- Conditional `k_s4` and C:N rules:
- Sampling coordinates and Jacobian convention:
- Surrogate release, feature/output schemas, and target-free inference path:
- Observation and forcing identities, units, QC, calendar, and alignment:
- Site(s), observation windows, and independent site-configuration mapping:
- GPP/SR likelihood resolutions and aggregation/coverage rules:
- Fixed observational uncertainty and precedence:
- Joint C/N depth operator, covariance components, and fixed bias convention:
- Fixed-test exclusion and other leakage boundaries:
- Seeds, software/environment, and deterministic replay requirements:

## Acceptance Gates and Decision Rule

- Required completeness and provenance:
- Prior/transformed-density numerical gates:
- Likelihood/covariance numerical gates:
- Surrogate interface, schema, compatibility, and no-target-leakage gates:
- Candidate/pool/walker validity gates where applicable:
- Chain/checkpoint/restart reproducibility gates where applicable:
- Convergence and posterior-predictive evidence where applicable:
- Throughput, walltime, and memory gates where applicable:
- Decision rule, aggregation, ranking, and tie-breaker:
- Changes requiring fresh authorization:

## Provenance and Work-Unit Ledger

| Work unit | Canonical script/hash | Submitted script/config/hash | Run directory/logs | Dependencies | Source identity | Job scope | State | Monitoring/retry notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<name>` | `<path/hash>` | `<paths/hashes>` | `<paths>` | `<identities>` | `<commit/diff>` | `<scope>` | `<state>` | `<mechanism; outcome; reason>` |

## Independent Read-Only Review

- Reviewer:
- Reviewed source/configuration identity:
- Outcome: `pass | pass_with_concerns | block`
- Scientific, numerical, leakage, interface, resource, and provenance findings:
- Primary-agent response and re-review where required:

## Execution, Performance, and Failure Accounting

- Static validation:
- Compute-node preflight:
- Exact submission commands and job identity checks:
- Queue and terminal accounting:
- Reproducible cold/warm walltime and peak-memory evidence:
- Candidate-search/MCMC resource projections:
- Scientific, infrastructure, numerical, scheduler/resource, interface/data, observation-context,
  rejection, retry, or cancellation classification:

## Validation, Reproducibility, and Results

| Work unit | Complete/eligible | Evidence | Gate result | Decision rationale |
| --- | --- | --- | --- | --- |
| `<name>` | `<yes/no>` | `<paths/findings>` | `<pass/fail/rejected>` | `<rationale>` |

- Prior and transformed-density validation:
- Likelihood and covariance validation:
- Surrogate compatibility and target-free inference validation:
- Candidate/pool/walker validation:
- Chain/checkpoint/restart reproducibility:
- Convergence diagnostics and limitations:
- Posterior and component log-likelihood evidence:
- Posterior-predictive and residual/QC evidence:
- Numerical-equivalence evidence for infrastructure changes:
- Overall acceptance result:
- Overall decision and closeout conclusion:
- Scientific and infrastructure limitations:
- Campaign-plan amendment recommendation: `<none or advisory recommendation>`
- Next action:

## Proposed Next-Iteration Plan (Planning Only)

Use this section for exactly one complete proposal or replace it with an explicit terminal
declaration. A plan amendment requires separate user authorization.

- Proposed sequential ID and work type:
- Campaign-plan identity, phase, alignment, and proposed deviation:
- Evidence-derived objective and optional hypothesis:
- Proposed prior, parameter schema, surrogate release, observations, uncertainty, sites, temporal
  scope, identities, and trust assumptions:
- Bounded work units and exclusions:
- Tentative scientific, numerical, reproducibility, and performance gates and decision rule:
- Proposed HPC profile, output root, resources, preflight, review, monitoring, retry,
  cancellation, retention, and stop boundaries:
- Expected evidence, artifacts, and record updates:
- Authorization boundary: fresh approval of one complete kickoff package is required; do not
  create the next report or iteration-specific scaffold automatically.

## Closeout Checklist

- [ ] Report finalized with exact prior, parameter, surrogate, uncertainty, observation, and site identities
- [ ] Required compact evidence copied to `summaries/iterXXX/`
- [ ] `ITERATION_SUMMARY.md` appended and `registry.csv` updated without schema changes
- [ ] `handoff/CURRENT.md` rebuilt with authority, active work, dependencies, blockers, and next action
- [ ] Campaign alignment and any advisory amendment recommendation are consistent
- [ ] Cross-record validator identity, command, output, and pass recorded
- [ ] No job is active/unaccounted and every failure or rejection is classified
- [ ] Authorized closeout branch satisfied: one verified commit or `validated_uncommitted`
