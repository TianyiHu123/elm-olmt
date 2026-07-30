#!/usr/bin/env python
"""Validate exact Iter011 result identity before aggregation or selection."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
OUTPUT_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output")
MANIFEST = REPO_ROOT / "development/spinup_surrogate/slurm/iter011/iter011_variants.tsv"
SEEDS = tuple(range(10001, 10101))
CASES = [
    f"{site}_ppe6_I20TRCNPRDCTCBC"
    for site in ("ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL")
]
CONTROL = "s32_tanh_lbfgs_a40_lr1e3_drop_flds_wind_psrf"
CANDIDATE = "s32_tanh_lbfgs_a40_lr1e3_drop32_corr080_prioritydrop"
DROP32 = (
    "parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,"
    "parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,"
    "PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,"
    "PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,"
    "FSDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,"
    "TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp"
).split(",")
FORBIDDEN_PREFIXES = ("FLDS_", "WIND_", "PSRF_")
TARGETS = ("TOTSOMC", "TOTSOMN")


def assert_finite(value: object, label: str) -> None:
    assert math.isfinite(float(value)), label


def main() -> None:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["variant"] for row in rows] == [CONTROL, CANDIDATE]

    candidate_schema: tuple[str, ...] | None = None
    reference_input_universe: tuple[str, ...] | None = None
    for row in rows:
        variant = row["variant"]
        stats_dir = OUTPUT_ROOT / f"spinup_surrogate_iter011_{variant}" / "surrogate_spinup"
        expected = [stats_dir / f"surrogate_spinup_stats_seed{seed}.json" for seed in SEEDS]
        assert sorted(stats_dir.glob("surrogate_spinup_stats_seed*.json")) == expected, variant
        schemas: set[tuple[str, ...]] = set()
        input_universes: set[tuple[str, ...]] = set()

        for seed, path in zip(SEEDS, expected):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data["stats_run_id"] == f"seed{seed}"
            assert data["split_random_state"] == seed
            assert data["output_label"] == f"spinup_surrogate_iter011_{variant}"
            assert data["model_type"] == "nn"
            assert data["split_mode"] == "by_member"
            assert data["train_fraction"] == 0.8
            assert data["case_names"] == CASES
            assert data["spinup_vars"] == list(TARGETS)
            assert data["fixed_mlp_params"] == {
                "hidden_layer_sizes": [32],
                "activation": "tanh",
                "solver": "lbfgs",
                "alpha": 40.0,
                "learning_rate_init": 0.001,
            }

            diagnostics = data["feature_diagnostics"]
            assert diagnostics["filter_scope"] == "global_pre_split"
            assert diagnostics["apply_variance_filter"] is False
            assert diagnostics["feature_subset_policy"] == row["feature_subset_policy"]
            assert diagnostics["apply_corr_filter"] is (row["apply_corr_filter"] == "true")
            assert diagnostics["explicit_feature_subset_requested"] == DROP32
            selected = diagnostics["selected_feature_names"]
            assert data["input_feature_names"] == selected
            assert set(selected).issubset(DROP32)
            assert not any(name.startswith(FORBIDDEN_PREFIXES) for name in selected)
            assert all(
                pair["feature_i"] in DROP32 and pair["feature_j"] in DROP32
                for pair in diagnostics["full_corr_pairs_pre_prune"]
            )
            if variant == CONTROL:
                assert diagnostics["corr_threshold"] == 0.98
                assert selected == DROP32
                assert diagnostics["dropped_by_correlation"] == []
            else:
                assert diagnostics["corr_threshold"] == 0.80
                assert len(selected) < len(DROP32)
                assert diagnostics["dropped_by_correlation"]
            schemas.add(tuple(selected))
            input_universes.add(tuple(data["input_feature_names_all"]))

            for target in TARGETS:
                variable = data["by_variable"][target]
                for metric in (
                    "r2_train",
                    "r2_val",
                    "rmse_train",
                    "rmse_val",
                    "r2_gap",
                    "rmse_ratio",
                ):
                    assert_finite(variable[metric], f"{variant} seed {seed} {target} {metric}")
                assert isinstance(variable["overfit_warning"], bool)
                assert variable["permutation_repeats"] == 8
                ranking = variable["permutation_importance_rmse"]
                names = [item["feature"] for item in ranking]
                assert len(names) == len(selected)
                assert len(set(names)) == len(names)
                assert set(names) == set(selected)
                for item in ranking:
                    for key in (
                        "mean_rmse_increase",
                        "std_rmse_increase",
                        "mean_r2_drop",
                        "std_r2_drop",
                    ):
                        assert_finite(
                            item[key],
                            f"{variant} seed {seed} {target} {item['feature']} {key}",
                        )

        assert len(schemas) == 1, (variant, schemas)
        assert len(input_universes) == 1, (variant, input_universes)
        input_universe = next(iter(input_universes))
        if reference_input_universe is None:
            reference_input_universe = input_universe
        else:
            assert input_universe == reference_input_universe
        if variant == CANDIDATE:
            candidate_schema = next(iter(schemas))

    assert candidate_schema is not None
    assert len(candidate_schema) < len(DROP32)
    print(
        "Iter011 exact seed, metadata, input-universe, schema, metric, and importance results passed"
    )


if __name__ == "__main__":
    main()
