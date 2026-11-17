#!/usr/bin/env python3
"""Independent Iter014 integration and diagnostic evidence validator."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from netCDF4 import Dataset

from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, sha256_file


HOURS = 61320


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass
class Moments:
    count: int = 0
    truth_sum: float = 0.0
    truth_sumsq: float = 0.0
    prediction_sum: float = 0.0
    prediction_sumsq: float = 0.0
    cross_sum: float = 0.0
    error_sum: float = 0.0
    error_sumsq: float = 0.0
    abs_error_sum: float = 0.0

    def add(self, truth: np.ndarray, prediction: np.ndarray) -> None:
        observed = np.asarray(truth, dtype=np.float64).reshape(-1)
        estimated = np.asarray(prediction, dtype=np.float64).reshape(-1)
        require(observed.shape == estimated.shape and np.all(np.isfinite(observed)) and np.all(np.isfinite(estimated)), "invalid validation block")
        error = estimated - observed
        self.count += int(observed.size)
        self.truth_sum += float(np.sum(observed, dtype=np.float64))
        self.truth_sumsq += float(np.sum(observed * observed, dtype=np.float64))
        self.prediction_sum += float(np.sum(estimated, dtype=np.float64))
        self.prediction_sumsq += float(np.sum(estimated * estimated, dtype=np.float64))
        self.cross_sum += float(np.sum(observed * estimated, dtype=np.float64))
        self.error_sum += float(np.sum(error, dtype=np.float64))
        self.error_sumsq += float(np.sum(error * error, dtype=np.float64))
        self.abs_error_sum += float(np.sum(np.abs(error), dtype=np.float64))

    def values(self) -> dict[str, float | int]:
        denominator = self.truth_sumsq - self.truth_sum * self.truth_sum / self.count
        require(self.count > 1 and denominator > 0.0, "invalid metric moments")
        return {"count": self.count, "r2": 1.0 - self.error_sumsq / denominator, "rmse": float(np.sqrt(self.error_sumsq / self.count)), "mae": self.abs_error_sum / self.count, "bias": self.error_sum / self.count}

    def pearson(self) -> float:
        require(self.count > 1, "invalid correlation count")
        covariance = self.cross_sum - self.truth_sum * self.prediction_sum / self.count
        variance_x = self.truth_sumsq - self.truth_sum * self.truth_sum / self.count
        variance_y = self.prediction_sumsq - self.prediction_sum * self.prediction_sum / self.count
        require(variance_x > 0.0 and variance_y > 0.0, "invalid correlation variance")
        value = float(covariance / np.sqrt(variance_x * variance_y))
        require(np.isfinite(value), "invalid correlation")
        return value


def verify_handoffs(config: dict[str, Any]) -> dict[str, str]:
    verified = {
        "C/N": sha256_file(Path(config["predicted_cn_handoff"])),
        "GPP": sha256_file(Path(config["predicted_gpp_handoff"])),
        "SR": sha256_file(Path(config["predicted_sr_handoff"])),
    }
    require(verified["C/N"] == config["predicted_cn_sha256"], "C/N handoff identity mismatch")
    require(verified["GPP"] == config["predicted_gpp_sha256"], "GPP handoff identity mismatch")
    require(verified["SR"] == config["predicted_sr_sha256"], "SR handoff identity mismatch")
    return verified


def compare_row(expected: dict[str, str], observed: dict[str, float | int]) -> None:
    require(int(expected["count"]) == observed["count"], "metric count mismatch")
    for name in ("r2", "rmse", "mae", "bias"):
        require(np.isclose(float(expected[name]), float(observed[name]), rtol=2e-10, atol=2e-10), f"metric mismatch: {name}")


def validate_metrics(config: dict[str, Any], products: Path) -> int:
    rows = read_csv(products / "exact_metrics.csv")
    require(len(rows) == 12, "exact metric row count mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    source_indices = np.asarray([int(member[1:]) - 1 for member in snapshot.development_ranked], dtype=np.int64)
    with Dataset(config["predicted_cn_handoff"], "r") as handoff:
        for target in ("TOTSOMC", "TOTSOMN"):
            site_moments = {site: Moments() for site in SITES}
            pooled = Moments()
            for site_index, site in enumerate(SITES):
                with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as source:
                    truth = np.asarray(source.variables[target][source_indices], dtype=np.float64)
                predicted = np.asarray(handoff.variables[f"{target}_predicted"][site_index], dtype=np.float64)
                site_moments[site].add(truth, predicted); pooled.add(truth, predicted)
            for scope, moment in (("pooled", pooled), *site_moments.items()):
                expected = next(row for row in rows if row["target"] == target and row["scope"] == scope)
                compare_row(expected, moment.values())
    for target, handoff_path, variable in (("GPP", config["predicted_gpp_handoff"], "GPP_predicted"), ("SR", config["predicted_sr_handoff"], "SR_predicted")):
        site_moments = {site: Moments() for site in SITES}; pooled = Moments()
        with Dataset(handoff_path, "r") as handoff:
            for site_index, site in enumerate(SITES):
                with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as source:
                    for start in range(0, 819, 8):
                        stop = min(start + 8, 819)
                        truth = np.asarray(source.variables[target][source_indices[start:stop], :], dtype=np.float64)
                        predicted = np.asarray(handoff.variables[variable][site_index, start:stop, :], dtype=np.float64)
                        site_moments[site].add(truth, predicted); pooled.add(truth, predicted)
        for scope, moment in (("pooled", pooled), *site_moments.items()):
            expected = next(row for row in rows if row["target"] == target and row["scope"] == scope)
            compare_row(expected, moment.values())
    return len(rows)


def validate_integration(config: dict[str, Any], integration_dir: Path, verified: dict[str, str]) -> dict[str, Any]:
    report = json.loads((integration_dir / "integration_report.json").read_text(encoding="utf-8"))
    require(report["schema"] == "three-stage-inference-iter014-integration-v1" and report["result"] == "pass", "integration report not passed")
    require(report["comparison_counts"] == {"GPP": 2592, "SR": 2592, "TOTSOMC": 18, "TOTSOMN": 18}, "integration denominator mismatch")
    require(report["sample_positions"] == config["sample_positions"] and report["sample_members"] == config["sample_members"], "integration sample mismatch")
    require(report["sites"] == list(SITES) and report["windows"] == config["windows"], "integration site/window mismatch")
    require(float(report["handoff_replay_rtol"]) == float(config["handoff_replay_rtol"]), "integration handoff rtol mismatch")
    require(float(report["handoff_replay_atol"]) == float(config["handoff_replay_atol"]), "integration handoff atol mismatch")
    require(float(report["direct_chunk_rtol"]) == float(config["reload_rtol"]) and float(report["direct_chunk_atol"]) == float(config["reload_atol"]), "integration chunk tolerance mismatch")
    require(report["verified_handoff_sha256"] == verified, "integration handoff identities mismatch")
    require(int(report["published_replay_failed_comparisons"]) == 0, "integration replay failures present")
    comparisons = report["published_replay_comparisons"]
    expected_groups = {
        *((site, int(config["windows"][0][0]), stage) for site in SITES for stage in ("TOTSOMC", "TOTSOMN")),
        *((site, int(start), stage) for site in SITES for start, _ in config["windows"] for stage in ("GPP", "SR")),
    }
    observed_groups = {(row["site"], int(row["start"]), row["stage"]) for row in comparisons}
    require(len(comparisons) == 16 and observed_groups == expected_groups and all(int(row["mismatch_count"]) == 0 for row in comparisons), "integration comparison inventory mismatch")
    for row in comparisons:
        expected_count = 9 if row["stage"] in ("TOTSOMC", "TOTSOMN") else 432
        require(int(row["count"]) == expected_count and np.isfinite(float(row["max_absolute_difference"])) and float(row["max_normalized_tolerance_ratio"]) <= 1.0, "integration comparison content mismatch")
    require(report["fixed_test_access"] is False and report["training_or_fitting"] is False and report["full_819_engine"] is False, "integration scope mismatch")
    outputs = report["serialized_outputs"]
    expected_pairs = {(site, int(start), int(end)) for site in SITES for start, end in config["windows"]}
    observed_pairs = {(row["site"], int(row["start"]), int(row["end"])) for row in outputs}
    require(len(outputs) == 6 and observed_pairs == expected_pairs, "serialized output inventory mismatch")
    for row in outputs:
        path = integration_dir / row["output"]
        require(row["members"] == config["sample_members"] and int(row["hours"]) == 48, "serialized output scope mismatch")
        require(path.is_file() and sha256_file(path) == row["output_sha256"], f"serialized output identity mismatch: {path.name}")
    return report


def validate_correlations(config: dict[str, Any], products: Path) -> int:
    rows = read_csv(products / "gpp_sr_correlations.csv")
    expected_inventory = {(scope, series) for scope in ("pooled", *SITES) for series in ("ELM", "surrogate")}
    require(len(rows) == 6 and {(row["scope"], row["series"]) for row in rows} == expected_inventory, "correlation inventory mismatch")
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    source_indices = np.asarray([int(member[1:]) - 1 for member in snapshot.development_ranked], dtype=np.int64)
    moments = {(scope, series): Moments() for scope, series in expected_inventory}
    with Dataset(config["predicted_gpp_handoff"], "r") as gpp_handoff, Dataset(config["predicted_sr_handoff"], "r") as sr_handoff:
        for site_index, site in enumerate(SITES):
            with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as source:
                for start in range(0, 819, 8):
                    stop = min(start + 8, 819)
                    elm_gpp = np.asarray(source.variables["GPP"][source_indices[start:stop], :], dtype=np.float64)
                    elm_sr = np.asarray(source.variables["SR"][source_indices[start:stop], :], dtype=np.float64)
                    surrogate_gpp = np.asarray(gpp_handoff.variables["GPP_predicted"][site_index, start:stop, :], dtype=np.float64)
                    surrogate_sr = np.asarray(sr_handoff.variables["SR_predicted"][site_index, start:stop, :], dtype=np.float64)
                    for series, first, second in (("ELM", elm_gpp, elm_sr), ("surrogate", surrogate_gpp, surrogate_sr)):
                        moments[(site, series)].add(first, second)
                        moments[("pooled", series)].add(first, second)
    values = {(scope, series): moment.pearson() for (scope, series), moment in moments.items()}
    for row in rows:
        key = (row["scope"], row["series"])
        require(int(row["count"]) == moments[key].count, "correlation count mismatch")
        require(np.isclose(float(row["pearson_r"]), values[key], rtol=2e-10, atol=2e-10), "correlation value mismatch")
        difference = values[(row["scope"], "surrogate")] - values[(row["scope"], "ELM")]
        require(np.isclose(float(row["surrogate_minus_elm"]), difference, rtol=2e-10, atol=2e-10), "correlation difference mismatch")
    return len(rows)


def validate_conditionals(products: Path) -> tuple[int, int]:
    conditional = read_csv(products / "gpp_sr_conditional_bins.csv")
    special = read_csv(products / "gpp_sr_night_near_zero.csv")
    scopes = ("pooled", *SITES)
    series_values = ("ELM", "surrogate")
    expected_bins = {(scope, series, index) for scope in scopes for series in series_values for index in range(20)}
    observed_bins = {(row["scope"], row["series"], int(row["bin_id"])) for row in conditional}
    require(len(conditional) == 120 and observed_bins == expected_bins, "conditional bin inventory mismatch")
    reference_edges: list[float] | None = None
    bin_counts: dict[tuple[str, str, int], int] = {}
    for scope in scopes:
        for series in series_values:
            rows = sorted((row for row in conditional if row["scope"] == scope and row["series"] == series), key=lambda row: int(row["bin_id"]))
            edges = [float(rows[0]["gpp_lower"]), *(float(row["gpp_upper"]) for row in rows)]
            require(len(edges) == 21 and np.all(np.isfinite(edges)) and np.all(np.diff(edges) > 0.0), "conditional edges invalid")
            if reference_edges is None:
                reference_edges = edges
            else:
                require(np.array_equal(np.asarray(edges), np.asarray(reference_edges)), "conditional edges are not locked")
            for index, row in enumerate(rows):
                count = int(row["count"])
                numeric = {name: float(row[name]) for name in ("gpp_midpoint", "gpp_mean", "gpp_median", "sr_mean", "sr_median", "sr_q10", "sr_q90")}
                lower = float(row["gpp_lower"])
                upper = float(row["gpp_upper"])
                require(row["category"] == "daylight_binned" and count > 0 and np.isfinite(lower) and np.isfinite(upper) and all(np.isfinite(value) for value in numeric.values()), "conditional bin values invalid")
                require(lower == edges[index] and upper == edges[index + 1], "conditional row edges mismatch")
                require(np.isclose(numeric["gpp_midpoint"], (lower + upper) / 2.0, rtol=0.0, atol=1e-15), "conditional midpoint mismatch")
                require(edges[index] <= numeric["gpp_mean"] <= edges[index + 1] and edges[index] <= numeric["gpp_median"] <= edges[index + 1], "conditional GPP summary outside bin")
                require(numeric["sr_q10"] <= numeric["sr_median"] <= numeric["sr_q90"], "conditional SR quantiles invalid")
                bin_counts[(scope, series, index)] = count
    expected_special = {(scope, series, category) for scope in scopes for series in series_values for category in ("night", "daylight_near_zero")}
    observed_special = {(row["scope"], row["series"], row["category"]) for row in special}
    require(len(special) == 12 and observed_special == expected_special, "special-category inventory mismatch")
    special_counts: dict[tuple[str, str, str], int] = {}
    for row in special:
        values = [float(row[name]) for name in ("gpp_mean", "gpp_median", "sr_mean", "sr_median", "sr_q10", "sr_q90")]
        require(int(row["count"]) > 0 and all(np.isfinite(value) for value in values) and values[4] <= values[3] <= values[5], "special-category values invalid")
        special_counts[(row["scope"], row["series"], row["category"])] = int(row["count"])
    for scope in scopes:
        expected_total = 2 * 819 * HOURS if scope == "pooled" else 819 * HOURS
        for series in series_values:
            total = special_counts[(scope, series, "night")] + special_counts[(scope, series, "daylight_near_zero")] + sum(bin_counts[(scope, series, index)] for index in range(20))
            require(total == expected_total, "conditional record accounting mismatch")
            if scope == "pooled":
                for category in ("night", "daylight_near_zero"):
                    require(special_counts[(scope, series, category)] == sum(special_counts[(site, series, category)] for site in SITES), "pooled special count mismatch")
                for index in range(20):
                    require(bin_counts[(scope, series, index)] == sum(bin_counts[(site, series, index)] for site in SITES), "pooled conditional bin count mismatch")
    return len(conditional), len(special)


def validate_products_evidence(products: Path, manifest: dict[str, Any]) -> None:
    listed = {item["path"] for item in manifest["files"]}
    for item in manifest["files"]:
        path = products / item["path"]
        require(path.is_file() and path.stat().st_size == int(item["size_bytes"]) and sha256_file(path) == item["sha256"], f"diagnostic file identity mismatch: {path.name}")
    evidence_rows: dict[str, str] = {}
    for line in (products / "evidence.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        evidence_rows[name] = digest
    expected_evidence = listed | {"diagnostics_manifest.json"}
    require(set(evidence_rows) == expected_evidence, "product evidence inventory mismatch")
    for name, digest in evidence_rows.items():
        require(sha256_file(products / name) == digest, f"product evidence hash mismatch: {name}")


def validate_densities(products: Path) -> None:
    with np.load(products / "parity_flux_density_grids.npz", allow_pickle=False) as data:
        for target in ("GPP", "SR"):
            edges = np.asarray(data[f"{target}_edges"])
            require(edges.shape == (201,) and np.all(np.isfinite(edges)) and np.all(np.diff(edges) > 0.0), "parity edges invalid")
            site_grids = []
            for scope, count in (("pooled", 100442160), ("ABBY", 50221080), ("JERC", 50221080)):
                counts = np.asarray(data[f"{target}_{scope}_counts"])
                probability = np.asarray(data[f"{target}_{scope}_probability"])
                require(counts.shape == (200, 200) and probability.shape == counts.shape and int(np.sum(counts)) == count, "parity density shape/count mismatch")
                require(np.isclose(np.sum(probability), 1.0, rtol=1e-12, atol=1e-12), "parity density normalization mismatch")
                require(np.allclose(probability, counts / count, rtol=1e-15, atol=1e-15), "parity probability mismatch")
                if scope != "pooled":
                    site_grids.append(counts)
            require(np.array_equal(data[f"{target}_pooled_counts"], site_grids[0] + site_grids[1]), "parity pooled density mismatch")
    with np.load(products / "joint_gpp_sr_density_grids.npz", allow_pickle=False) as data:
        for name in ("gpp_edges", "sr_edges"):
            edges = np.asarray(data[name])
            require(edges.shape == (201,) and np.all(np.isfinite(edges)) and np.all(np.diff(edges) > 0.0), "joint edges invalid")
        for series in ("ELM", "surrogate"):
            site_grids = []
            for scope, count in (("pooled", 100442160), ("ABBY", 50221080), ("JERC", 50221080)):
                counts = np.asarray(data[f"{scope}_{series}_counts"])
                probability = np.asarray(data[f"{scope}_{series}_probability"])
                require(counts.shape == (200, 200) and probability.shape == counts.shape and int(np.sum(counts)) == count, "joint density shape/count mismatch")
                require(np.isclose(np.sum(probability), 1.0, rtol=1e-12, atol=1e-12), "joint density normalization mismatch")
                require(np.allclose(probability, counts / count, rtol=1e-15, atol=1e-15), "joint probability mismatch")
                if scope != "pooled":
                    site_grids.append(counts)
            require(np.array_equal(data[f"pooled_{series}_counts"], site_grids[0] + site_grids[1]), "joint pooled density mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--integration", type=Path, required=True)
    parser.add_argument("--products", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "final validation output exists")
    args.output.mkdir(parents=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    verified_handoffs = verify_handoffs(config)
    integration = validate_integration(config, args.integration, verified_handoffs)
    manifest = json.loads((args.products / "diagnostics_manifest.json").read_text(encoding="utf-8"))
    require(manifest["schema"] == "three-stage-inference-iter014-diagnostics-v1", "diagnostic manifest schema mismatch")
    require(manifest["snapshot_sha256"] == config["snapshot_sha256"], "diagnostic snapshot identity mismatch")
    require(manifest["result"] == "pass" and manifest["fixed_test_access"] is False and manifest["training_or_inference"] is False, "diagnostic scope mismatch")
    require(manifest["performance_gate_applied"] is False and manifest["evidence_class"] == "in_sample_development_descriptive", "diagnostic evidence-class mismatch")
    require(manifest["aggregate_rule"] == "deterministic blockwise float64 moments over every development record", "diagnostic aggregate rule mismatch")
    require(manifest["verified_handoff_sha256"] == verified_handoffs, "diagnostic handoff identities mismatch")
    require(int(manifest["development_member_count"]) == 819 and int(manifest["hourly_count_by_site"]) == 50221080 and int(manifest["hourly_pooled_count"]) == 100442160, "diagnostic denominator mismatch")
    require(int(manifest["density_bins"]) == 200 and int(manifest["conditional_bins"]) == 20, "diagnostic bin contract mismatch")
    validate_products_evidence(args.products, manifest)
    for name in ("spinup_cn_parity.png", "parity_flux_hourly.png", "joint_gpp_sr_hourly.png", "gpp_sr_joint_conditional.png"):
        require((args.products / name).is_file() and (args.products / name).stat().st_size > 10000, f"figure missing or too small: {name}")
    metric_rows = validate_metrics(config, args.products)
    correlation_rows = validate_correlations(config, args.products)
    conditional_rows, special_rows = validate_conditionals(args.products)
    validate_densities(args.products)
    report = {"schema": "three-stage-inference-iter014-final-validation-v1", "result": "pass", "verified_handoff_sha256": verified_handoffs, "integration_counts": integration["comparison_counts"], "serialized_outputs_verified": len(integration["serialized_outputs"]), "independently_recomputed_metric_rows": metric_rows, "independently_recomputed_correlation_rows": correlation_rows, "conditional_rows": conditional_rows, "night_near_zero_rows": special_rows, "density_packages_verified": 2, "figures": 4, "fixed_test_access": False, "training_or_fitting": False, "full_819_engine": False, "decision": "three_stage_inference_ready_for_robustness"}
    (args.output / "final_validation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ITER014_FINAL_VALIDATE_OK metric_rows=12 figures=4 fixed_test=false")


if __name__ == "__main__":
    main()
