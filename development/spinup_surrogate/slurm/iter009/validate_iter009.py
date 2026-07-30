#!/usr/bin/env python
"""No-training compute-node checks for the locked iter009 manifest and feature policies."""
import csv
from pathlib import Path
import re
import sys

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.surrogate_NN_Spinup import _select_feature_columns

MANIFEST = REPO_ROOT / "development/spinup_surrogate/slurm/iter009/iter009_variants.tsv"
ALPHAS = {"25", "35", "50", "65", "75"}
POLICIES = {"full45", "corr080_prioritydrop", "drop_flds_wind_psrf"}
FULL_FORCING = "PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF"
DROP_FORCING = "PRECTmms,FSDS,TBOT,RH"
FULL45 = (
    "parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,"
    "PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,"
    "PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,"
    "FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,"
    "TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,"
    "RH_clim_min,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,"
    "WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_seasonal_amp"
).split(",")
DROP32 = [name for name in FULL45 if not name.startswith(("FLDS_", "WIND_", "PSRF_"))]
CANONICAL = REPO_ROOT / "development/spinup_surrogate/slurm/iter009/case.train_surrogate_spinup_iter009.slurm"
OUTPUT_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output")


def read_config(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 7
    parsed = dict(line.split("=", 1) for line in lines)
    assert len(parsed) == 7
    return parsed


def main() -> None:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 15
    assert len({row["variant"] for row in rows}) == 15
    assert {(row["alpha"], row["feature_policy"]) for row in rows} == {
        (alpha, policy) for alpha in ALPHAS for policy in POLICIES
    }
    canonical_text = CANONICAL.read_text(encoding="utf-8")
    full_match = re.search(r"^readonly FULL45=(.*)$", canonical_text, re.MULTILINE)
    drop_match = re.search(r"^readonly DROP32=(.*)$", canonical_text, re.MULTILINE)
    assert full_match and full_match.group(1).split(",") == FULL45
    assert drop_match and drop_match.group(1).split(",") == DROP32
    assert len(FULL45) == 45 and len(DROP32) == 32
    assert set(FULL45) - set(DROP32) == {
        name for name in FULL45 if name.startswith(("FLDS_", "WIND_", "PSRF_"))
    }
    for row in rows:
        policy = row["feature_policy"]
        assert row["variant"] == f"s32_tanh_lbfgs_a{row['alpha']}_lr1e3_{policy}"
        if policy == "corr080_prioritydrop":
            assert row["forcing_vars"] == FULL_FORCING
            assert row["feature_subset_policy"] == "eligible_pool"
            assert row["apply_corr_filter"] == "true" and row["corr_threshold"] == "0.80"
        elif policy == "drop_flds_wind_psrf":
            assert row["forcing_vars"] == DROP_FORCING
            assert row["feature_subset_policy"] == "strict"
            assert row["apply_corr_filter"] == "false" and row["corr_threshold"] == "NA"
        else:
            assert row["forcing_vars"] == FULL_FORCING
            assert row["feature_subset_policy"] == "strict"
            assert row["apply_corr_filter"] == "false" and row["corr_threshold"] == "NA"

        run_dir = OUTPUT_ROOT / f"spinup_surrogate_iter009_{row['variant']}"
        submitted = run_dir / f"submit_{row['variant']}.slurm"
        config = run_dir / "submission_config.env"
        assert submitted.read_bytes() == CANONICAL.read_bytes()
        assert read_config(config) == {
            "VARIANT": row["variant"],
            "MLP_ALPHA": row["alpha"],
            "FEATURE_POLICY": row["feature_policy"],
            "FORCING_VARS": row["forcing_vars"],
            "FEATURE_SUBSET_POLICY": row["feature_subset_policy"],
            "APPLY_CORR_FILTER": row["apply_corr_filter"],
            "CORR_THRESHOLD": row["corr_threshold"],
        }

    names = ["parm_0", "FLDS_clim_mean", "WIND_clim_mean", "PSRF_clim_mean", "FSDS_clim_mean"]
    import numpy as np

    matrix = np.arange(25, dtype=float).reshape(5, 5)
    selected, diagnostics = _select_feature_columns(
        matrix,
        names,
        n_params=5,
        n_surface=0,
        n_climatology=0,
        feature_set="all",
        explicit_feature_subset=["parm_0", "FSDS_clim_mean"],
        feature_subset_policy="strict",
        apply_corr_filter=False,
    )
    assert selected.tolist() == [0, 4]
    assert diagnostics["filter_scope"] == "global_pre_split"
    print("iter009 manifest and no-training feature-policy invariants passed")


if __name__ == "__main__":
    main()
