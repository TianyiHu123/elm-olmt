#!/usr/bin/env python
"""No-training compute-node checks for the locked Iter011 matrix and artifacts."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from model_ELM.surrogate_NN_Spinup import _select_feature_columns

MANIFEST = REPO_ROOT / "development/spinup_surrogate/slurm/iter011/iter011_variants.tsv"
CANONICAL = (
    REPO_ROOT
    / "development/spinup_surrogate/slurm/iter011/case.train_surrogate_spinup_iter011.slurm"
)
OUTPUT_ROOT = Path("/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output")
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


def read_config(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 7
    assert all("=" in line for line in lines)
    return dict(line.split("=", 1) for line in lines)


def main() -> None:
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["variant"] for row in rows] == [CONTROL, CANDIDATE]
    assert len(rows) == 2

    script_text = CANONICAL.read_text(encoding="utf-8")
    assert "#SBATCH --array=1-100" in script_text
    assert "#SBATCH --time=00:15:00" in script_text
    assert "#SBATCH --cpus-per-task=10" in script_text
    assert "#SBATCH --output=spinup_iter011_%A_%a.out" in script_text
    assert "#SBATCH --error=spinup_iter011_%A_%a.err" in script_text
    assert "--permutation-repeats 8" in script_text
    assert re.search(r"^readonly DROP32=.*$", script_text, re.MULTILINE)

    for row in rows:
        assert row["alpha"] == "40"
        assert row["forcing_vars"] == "PRECTmms,FSDS,TBOT,RH"
        if row["variant"] == CONTROL:
            assert (
                row["feature_policy"],
                row["feature_subset_policy"],
                row["apply_corr_filter"],
                row["corr_threshold"],
            ) == ("drop_flds_wind_psrf", "strict", "false", "NA")
        else:
            assert (
                row["feature_policy"],
                row["feature_subset_policy"],
                row["apply_corr_filter"],
                row["corr_threshold"],
            ) == ("drop32_corr080_prioritydrop", "eligible_pool", "true", "0.80")

        run_dir = OUTPUT_ROOT / f"spinup_surrogate_iter011_{row['variant']}"
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

    # The forbidden FLDS column is deliberately present in the input matrix but absent from
    # the explicit DROP32 universe. The two allowed columns are perfectly correlated, proving
    # that explicit-subset restriction occurs before global correlation pruning.
    matrix = np.asarray(
        [
            [1.0, 10.0, 1.0, 4.0],
            [2.0, 20.0, 2.0, 3.0],
            [3.0, 30.0, 3.0, 2.0],
            [4.0, 40.0, 4.0, 1.0],
        ]
    )
    names = ["parm_0", "FLDS_clim_mean", "FSDS_clim_mean", "RH_clim_mean"]
    selected, diagnostics = _select_feature_columns(
        matrix,
        names,
        n_params=4,
        n_surface=0,
        n_climatology=0,
        feature_set="all",
        explicit_feature_subset=["parm_0", "FSDS_clim_mean", "RH_clim_mean"],
        feature_subset_policy="eligible_pool",
        apply_corr_filter=True,
        corr_threshold=0.80,
    )
    selected_names = [names[index] for index in selected.tolist()]
    assert diagnostics["filter_scope"] == "global_pre_split"
    assert "FLDS_clim_mean" in diagnostics["excluded_by_explicit_subset"]
    assert all(
        "FLDS_clim_mean" not in (pair["feature_i"], pair["feature_j"])
        for pair in diagnostics["full_corr_pairs_pre_prune"]
    )
    assert len(selected_names) < 3
    assert "FLDS_clim_mean" not in selected_names
    assert diagnostics["apply_corr_filter"] is True
    print("Iter011 manifest, submitted artifacts, and sequential DROP32-filter invariants passed")


if __name__ == "__main__":
    main()
