#!/usr/bin/env python
"""Validate exact iter009 result identity before aggregation or selection."""
import csv
import json
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
OUTPUT_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output")
MANIFEST = REPO_ROOT / "development/spinup_surrogate/slurm/iter009/iter009_variants.tsv"
SEEDS = tuple(range(10001, 10006))
CASES = [
    f"{site}_ppe6_I20TRCNPRDCTCBC"
    for site in ("ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL")
]
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


def main() -> None:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 15
    for row in rows:
        variant = row["variant"]
        stats_dir = OUTPUT_ROOT / f"spinup_surrogate_iter009_{variant}" / "surrogate_spinup"
        expected_paths = [stats_dir / f"surrogate_spinup_stats_seed{seed}.json" for seed in SEEDS]
        actual_paths = sorted(stats_dir.glob("surrogate_spinup_stats_seed*.json"))
        assert actual_paths == expected_paths, (variant, actual_paths)
        selected_schemas = set()
        for seed, path in zip(SEEDS, expected_paths):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data["stats_run_id"] == f"seed{seed}"
            assert data["split_random_state"] == seed
            assert data["output_label"] == f"spinup_surrogate_iter009_{variant}"
            assert data["model_type"] == "nn" and data["split_mode"] == "by_member"
            assert data["train_fraction"] == 0.8 and data["case_names"] == CASES
            assert data["spinup_vars"] == ["TOTSOMC", "TOTSOMN"]
            fixed = data["fixed_mlp_params"]
            assert fixed == {
                "hidden_layer_sizes": [32], "activation": "tanh", "solver": "lbfgs",
                "alpha": float(row["alpha"]), "learning_rate_init": 0.001,
            }
            diag = data["feature_diagnostics"]
            assert diag["filter_scope"] == "global_pre_split"
            assert diag["apply_variance_filter"] is False
            assert diag["feature_subset_policy"] == row["feature_subset_policy"]
            assert diag["apply_corr_filter"] is (row["apply_corr_filter"] == "true")
            if row["apply_corr_filter"] == "true":
                assert diag["corr_threshold"] == 0.8
                assert set(diag["selected_feature_names"]).issubset(FULL45)
            elif row["feature_policy"] == "drop_flds_wind_psrf":
                assert diag["selected_feature_names"] == DROP32
                assert data["input_feature_names"] == DROP32
            else:
                assert diag["selected_feature_names"] == FULL45
            selected_schemas.add(tuple(diag["selected_feature_names"]))
        assert len(selected_schemas) == 1, variant
    print("iter009 exact seed, metadata, model, and feature-policy results passed")


if __name__ == "__main__":
    main()
