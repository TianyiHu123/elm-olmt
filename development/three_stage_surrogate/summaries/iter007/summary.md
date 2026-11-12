# Iter007 Closeout Summary

- Iteration/work type: `iter007` / `experiment`.
- Objective/result: select the best pooled ABBY/JERC GPP MLP configuration from a locked
  24-candidate matrix using development-only evidence; `pass`.
- Decision: `configuration_selected_gate_pass`. Freeze candidate 21—hidden layers `(64,32)`,
  `tanh`, alpha `1e-4`, and the otherwise frozen Adam controls—for a separately approved fresh
  robustness iteration. This selection does not authorize an all-819 fit, release, or SR handoff.
- Scope: all 24 candidates on eight screening splits; six finalists on the remaining 12 splits;
  120 finalist leaves covering all 20 shared 655/164 development splits; pooled hourly/daily
  metrics only; zero fixed-test access, spinup execution, convergence warnings, release work, or
  site-specific selection metrics.
- Interpretation: evidence is `fixed_upstream_gpp_stage`; published predicted C/N is an in-sample
  fixed upstream input, so this is not end-to-end held-out evidence.

## Best-candidate pooled gate

Quantiles use NumPy's linear method across 20 validation repetitions. Bias is prediction minus ELM
in `gC/m^2/day`.

| Resolution | R2 q10 / floor | RMSE q90 / ceiling | Median abs bias / ceiling | Result |
| --- | ---: | ---: | ---: | --- |
| hourly | 0.904205 / 0.85 | 4.260999 / 5.0 | 0.135299 / 0.35 | pass |
| daily | 0.829424 / 0.75 | 2.675357 / 3.0 | 0.135299 / 0.35 | pass |

Candidate 21's worst normalized margin is `0.063771`, mean margin is `0.275425`, median paired
composite improvement over candidate 0 is `0.288683`, and population composite variability is
`0.087708`. Candidate 18 also passed every gate, but candidate 21 ranked first by the larger worst
normalized margin. The independently reproduced order is `21,18,19,2,8,13`.

- Technical validation: all 120 finalist leaves and 480 pooled metric rows were independently
  reconciled; all leaf artifact hashes matched. Final aggregation and fresh-process validation
  agreed on best candidate 21, gate pass, and `configuration_selected_gate_pass`.
- Accounting: preflight `24494841`, smoke `24494873`, all 192 screen leaves under `24494900`,
  screen aggregation `24506893`, all 72 finalist leaves under `24507062`, and final job `24512103`
  completed `0:0`. One redundant dependency submission was rejected before a job ID; unchanged
  retry created `24507062`. No workload failure or cancellation occurred.
- Products: `final_metric_distribution.csv` (`abf7e60e...b662`), `final_ranking.csv`
  (`0beaac63...8c63`), `selection_report.json` (`d90cf503...e745`), and independent
  `final_validation.json` (`6edaf171...d728`) are retained here; full outputs remain under the
  external Iter007 run root.
- Boundary: no fixed-test use, all-819 GPP fit, model artifact, uncertainty/SR handoff, stable
  release, catalog, observation, likelihood, MCMC, or push.
- Limitations: two sites; pooled metrics can mask site behavior; fixed in-sample upstream C/N;
  repeated development splits reused for selection; finite candidate matrix; temporary unbacked
  storage; no release-qualified fresh-split robustness evidence.
- Campaign-plan amendment recommendation: `none`.
- Next state: planning-only Iter008 fresh robustness proposal; fresh consolidated kickoff approval
  is required before any implementation, directories, scheduler action, retry, or commit.

## Planning-only Iter008 proposal

Freeze candidate 21 and test it on 20 newly generated balanced 655/164 development-member splits
that are distinct from the Iter006/Iter007 selection splits. Preserve the exact fixed-upstream
43-feature, physical-GPP, Adam, pooled hourly/daily metric, and immutable gate contracts. Retain
compact repeated-fit diagnostics and independently validate coverage, predictions, metrics, and
the gate. A pass may support a later separately planned all-819 release iteration; a failure must
stop with diagnostic evidence. Fixed-test use, release fitting/publication, SR handoff, and MCMC
remain out of scope. This proposal grants no runtime authority.
