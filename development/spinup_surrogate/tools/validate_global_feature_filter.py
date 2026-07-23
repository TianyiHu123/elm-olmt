#!/usr/bin/env python
"""Compute-node invariant checks for durable global feature filtering."""
from pathlib import Path
import sys

# This script is submitted by absolute path.  Keep the fixed Puma checkout root explicit so
# repository imports do not depend on Python's script-directory import behavior.
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from model_ELM.surrogate_NN_Spinup import _select_feature_columns


def main() -> None:
    # Every pair is perfectly correlated.  Priority prefixes must be removed before the
    # canonical-order tie-breaker applies, and the result must not depend on a split seed.
    matrix = np.asarray([[1, 1, 2, 4], [2, 2, 4, 8], [3, 3, 6, 12], [4, 4, 8, 16]], dtype=float)
    names = ["keep", "WIND_feature", "PSRF_feature", "other"]
    selected, diagnostics = _select_feature_columns(
        matrix,
        names,
        n_params=4,
        n_surface=0,
        n_climatology=0,
        feature_set="all",
        explicit_feature_subset=names,
        feature_subset_policy="eligible_pool",
        apply_corr_filter=True,
        corr_threshold=0.99,
    )
    assert selected.tolist() == [0], selected.tolist()
    assert diagnostics["filter_scope"] == "global_pre_split"
    assert diagnostics["dropped_by_correlation"] == ["WIND_feature", "PSRF_feature", "other"]
    assert diagnostics["dropped_by_correlation_pairs"][0]["drop_reason"] == "priority_prefix"
    assert diagnostics["dropped_by_correlation_pairs"][1]["drop_reason"] == "priority_prefix"
    print("global feature-filter invariants passed")


if __name__ == "__main__":
    main()
