# Iter005 Closeout Summary

- Iteration/work type: `iter005` / `implementation`.
- Objective/result: implement, fit, and independently validate the fixed-upstream ABBY/JERC GPP
  baseline using all valid hourly rows from 655 training and 164 validation development members;
  `pass` under the user-approved batch-aware reload contract.
- Decision: `freeze_baseline`. Perform fixed-configuration robustness in planning-only Iter006;
  reconsider configuration optimization only if robustness evidence is poor.
- Model: one hourly-trained sklearn MLP with hidden layers `(128,)`, ReLU/Adam, physical-target
  standardization, early stopping, seed `42`, 29 iterations, and zero convergence warnings.
- Scope: 43 ordered features; 80,329,200 training and 20,112,960 validation site/member/hour rows;
  zero fixed-test access and zero spinup execution. Published all-819 predicted C/N is fixed and
  in-sample upstream input, so validation is `fixed_upstream_gpp_stage`, not end-to-end held out.
- Artifact identity: `09820737baf9fa9c4760c35b7ce1cbc3c9e6b09eb4ed2f4143a7836416d5c31b`;
  predictions `74b2b1334645238311370013f5f98bc87c6b5674cc723e3eb933027ccdee4024`;
  metrics `5b7a40bfe1eecae9d4ef246c7899c7ad8c2a55483170f0211dab5a6d380f172d`.

## Metrics

All daily metrics aggregate the same hourly artifact predictions and ELM targets over complete
24-hour blocks as `sum(hourly)/24`; no daily-specific artifact was trained. Bias is prediction
minus ELM in `gC/m^2/day`. RMSE and MAE use the same target units.

| Partition | Site | Resolution | Count | R2 | RMSE | MAE | Bias | Residual SD | Gaps | Coverage |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | ABBY | hourly | 40,164,600 | 0.959621 | 2.604634 | 1.557442 | -0.165282 | 2.599385 | 0 | 1.0 |
| train | ABBY | daily | 1,673,525 | 0.967994 | 1.202612 | 0.821531 | -0.165282 | 1.191200 | 0 | 1.0 |
| train | JERC | hourly | 40,164,600 | 0.923555 | 4.099626 | 2.314698 | -0.022741 | 4.099563 | 0 | 1.0 |
| train | JERC | daily | 1,673,525 | 0.876753 | 2.147648 | 1.425142 | -0.022741 | 2.147527 | 0 | 1.0 |
| train | pooled | hourly | 80,329,200 | 0.939464 | 3.434462 | 1.936070 | -0.094012 | 3.433175 | 0 | 1.0 |
| train | pooled | daily | 3,347,050 | 0.928255 | 1.740498 | 1.123337 | -0.094012 | 1.737957 | 0 | 1.0 |
| validation | ABBY | hourly | 10,056,480 | 0.918870 | 3.542763 | 1.866823 | -0.021565 | 3.542697 | 0 | 1.0 |
| validation | ABBY | daily | 419,020 | 0.886994 | 2.191377 | 1.183667 | -0.021565 | 2.191270 | 0 | 1.0 |
| validation | JERC | hourly | 10,056,480 | 0.904396 | 4.456558 | 2.435926 | 0.196706 | 4.452215 | 0 | 1.0 |
| validation | JERC | daily | 419,020 | 0.819122 | 2.528898 | 1.603145 | 0.196706 | 2.521236 | 0 | 1.0 |
| validation | pooled | hourly | 20,112,960 | 0.911104 | 4.025672 | 2.151374 | 0.087570 | 4.024720 | 0 | 1.0 |
| validation | pooled | daily | 838,040 | 0.860052 | 2.366163 | 1.393406 | 0.087570 | 2.364542 | 0 | 1.0 |

- Validation: preparation hashes/layout and 20 independently reconstructed source rows passed;
  revised validation job `24488737` independently reproduced all 12 metric rows. Three original
  250,000-row prediction chunks covering 692,160 rows passed unchanged `1e-6` replay tolerance;
  batches 1/7/1,000 were finite and exactly repeatable within batch. Cross-batch difference
  `3.33786e-06` is characterization only.
- Accounting: preparation `24485863`, smoke `24485909`, baseline `24485952`, and revised validation
  `24488737` completed `0:0`. Four failed validation attempts are preserved and classified; they
  exposed float32 batch-shape sensitivity and motivated the explicitly user-approved gate revision.
- Limitations: two sites; one 655/164 split; fixed upstream C/N is in-sample for all 819 development
  members; no fixed-test, repeated-split robustness, all-819 GPP refit/release, SR, full-chain,
  observational, likelihood, or posterior evidence; external outputs are temporary and unbacked.
- Campaign-plan amendment recommendation: `none`.
- Next direction: planning-only Iter006 20-repeat fixed-upstream GPP robustness using the frozen
  configuration; fresh consolidated kickoff approval required.
