# Iter009 scheduler material

`iter009_matrix.tsv` is the six-leaf parent-array template.  During authorized preparation,
the materializer writes one immutable, arm-specific copy for each `B`, `T`, `I`, `M`, and `TIM`
array; it must preserve the fixed leaf/site/seed mapping and change only the arm columns.

The canonical preflight and initialization jobs must validate this source template and the
materialized five-arm 30-row manifest before any campaign array can be submitted.
