# Iter001 preflight failure

Job `23718019` failed before substantive diagnostics with exit `1:0` after 28 seconds.

The compute-node receipt reports: `ABBY_ctrlopt9009_I20TRCNPRDCTCBC.pkl: missing case.output['SR']`.
This is an input-interface failure, not a Puma resource failure: `seff` recorded 2.41 GB of
20 GB and 7.925 CPU seconds. No figures or metrics were produced.

The failed receipt and Slurm logs are retained under
`/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/diagnostic/elm_diagnose_iter001/preflight/`.
A new approved package is required before changing inputs, generating outputs, or retrying.
