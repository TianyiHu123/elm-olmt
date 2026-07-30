# Perlmutter-to-Puma Case-Pickle Migration

This directory preserves the workload-specific procedure used to migrate the nine
spinup-surrogate case pickles from Perlmutter paths to Puma paths. It is not a general Puma setup
procedure and is not required for ordinary training or inference.

Use the repository Puma profile for site mechanics:
[`development/hpc/puma.md`](../../hpc/puma.md).

The migration requires an explicit runtime contract and must run on a Puma compute node. Inspect,
apply, and recovery operations load repository case pickles and access workload data; do not run
them on a login node.

## Utility

```text
development/spinup_surrogate/migrations/perlmutter_to_puma_case_pickles.py
```

The utility treats all nine case pickles as one transaction:

- `--inspect` performs a read-only full preflight;
- `--apply` preflights, stages, reload-validates, and activates the complete set;
- `--recover` restores the original set after interrupted activation.

It loads one pickle at a time. Each original is preserved as
`<case>.pkl.perlmutter.bak`; backups are not removed automatically. Recovery preserves backups
and any already activated Puma pickle as a staged file.

## Historical mapping

For the nine migrated case pickles:

- `case.runroot` maps to
  `/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe`;
- `case.metdir` maps per site to
  `/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON/<SITE>/1x1pt_<SITE>/CLM1PT_data`;
- `finidat`, `dependcase`, and unrelated historical path metadata remain unchanged;
- restart lookup continues under `case.runroot/UQ/case.dependcase/gNNNNN/` using the basename of
  `case.finidat`.

Inspect and apply validate the complete nine-case set, including resolved restart files, ensemble
surface files, forcing sequences, required NetCDF variables, spinup-cycle coverage, and compact
pickle invariants.

## Ordered case set

```text
ABBY_ppe6_I20TRCNPRDCTCBC
JERC_ppe6_I20TRCNPRDCTCBC
OSBS_ppe6_I20TRCNPRDCTCBC
SOAP_ppe6_I20TRCNPRDCTCBC
RMNP_ppe6_I20TRCNPRDCTCBC
TALL_ppe6_I20TRCNPRDCTCBC
TEAK_ppe6_I20TRCNPRDCTCBC
WREF_ppe6_I20TRCNPRDCTCBC
YELL_ppe6_I20TRCNPRDCTCBC
```

## Command example

Run only after the governing workflow and runtime contract authorize the operation:

```bash
readonly REPO_ROOT=/xdisk/chopinsong/tianyihu/elm-olmt
readonly MIGRATION_TOOL="${REPO_ROOT}/development/spinup_surrogate/migrations/perlmutter_to_puma_case_pickles.py"
readonly MIGRATION_CASES="ABBY_ppe6_I20TRCNPRDCTCBC,JERC_ppe6_I20TRCNPRDCTCBC,"\
"OSBS_ppe6_I20TRCNPRDCTCBC,SOAP_ppe6_I20TRCNPRDCTCBC,"\
"RMNP_ppe6_I20TRCNPRDCTCBC,TALL_ppe6_I20TRCNPRDCTCBC,"\
"TEAK_ppe6_I20TRCNPRDCTCBC,WREF_ppe6_I20TRCNPRDCTCBC,"\
"YELL_ppe6_I20TRCNPRDCTCBC"
readonly PICKLE_DIR="${REPO_ROOT}/pklfiles"
readonly RUN_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe
readonly MET_ROOT=/xdisk/chopinsong/tianyihu/E3SM_out/PTCLM/NEON/CTSM_NEON

module load micromamba

micromamba run -n OLMT_puma python "${MIGRATION_TOOL}" \
  --inspect \
  --pickle-dir "${PICKLE_DIR}" \
  --cases "${MIGRATION_CASES}" \
  --run-root "${RUN_ROOT}" \
  --met-root "${MET_ROOT}"

micromamba run -n OLMT_puma python "${MIGRATION_TOOL}" \
  --apply \
  --pickle-dir "${PICKLE_DIR}" \
  --cases "${MIGRATION_CASES}" \
  --run-root "${RUN_ROOT}" \
  --met-root "${MET_ROOT}"
```

Use identical arguments with `--recover` only to restore the original set after interrupted
activation. Do not remove backups as part of the utility run.

## Historical validation evidence

The completed migration observed:

- 84 monthly forcing files for ABBY, JERC, OSBS, SOAP, RMNP, and TALL;
- 72 monthly forcing files for TEAK, WREF, and YELL.

These counts support the recorded migration provenance. They are not general Puma storage,
forcing, or future-data guarantees.
