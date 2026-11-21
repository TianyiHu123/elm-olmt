# Iter014 compact evidence

- Result: `pass`; decision: `three_stage_inference_ready_for_robustness`.
- Campaign plan SHA-256: `014a112ba6013b28da10d87415c53f39aefcfcf3bd56461ec9a032867d9d5360`;
  alignment `aligned`; approved deviation and amendment recommendation `none`.
- Frozen handoff SHA-256: C/N `9e2d5be4...fdb5`, GPP `c905fc60...98bb`, SR
  `3704cab6...d3a1`. Engine feature counts are 25/43/44 and no ELM truth enters inference.
- Bounded integration covers nine locked development members, ABBY/JERC, three 48-hour windows,
  C/N counts `18/18`, flux counts `2592/2592`, strict direct/chunk equality, and exact reload.
- Handoff replay uses `rtol=1e-6`, `atol=1e-4` only for historical published predictions; maximum
  GPP absolute difference is `5.340576171875e-05`. Direct/chunk remains `rtol=atol=1e-6`.
- Diagnostics contain 12 exact pooled/site metric rows, six GPP-SR Pearson rows, 120 conditional
  rows, 12 night/near-zero rows, two density packages, and four independently reviewed figures.
- Evidence is in-sample 819-member development-only descriptive evidence, not causal confirmation,
  held-out end-to-end performance, or full-chain uncertainty.
- No training/fitting, fixed-test access, full-819 engine chain, release mutation, or performance
  gate occurred. All ten jobs are terminal; every failure is classified in `job_accounting.csv`.
- No next iteration is proposed or authorized.
