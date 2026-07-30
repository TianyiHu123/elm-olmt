# iter007 summaries

Corrected aggregation job `23346902` produced all eight compact summary JSONs and all eight
feature-stability reports. `s08_tanh_adam_a10_lr1e3` is the only configuration passing every
locked gate; it exactly reproduces the iter006 `all_control` baseline. All other variants are
rejected by the recorded r2, rmse-ratio, or warning gates.
