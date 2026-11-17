#!/usr/bin/env python3
"""Create Iter014 full-development descriptive diagnostics without model inference."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
from netCDF4 import Dataset

from model_ELM.three_stage_data import SITES, ThreeStageSnapshot, sha256_file


DISCLAIMER = "In-sample 819-member development diagnostic; descriptive only; not causal, held-out end-to-end, or full-chain uncertainty."
HOURS = 61320


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"no rows for {path.name}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def paired_blocks(first: np.ndarray, second: np.ndarray, rows: int = 8) -> Iterable[tuple[np.ndarray, np.ndarray]]:
    x = np.asarray(first)
    y = np.asarray(second)
    require(x.shape == y.shape and x.size > 1, "paired block shape mismatch")
    if x.ndim == 1:
        yield x, y
        return
    x_rows = x.reshape(-1, x.shape[-1])
    y_rows = y.reshape(-1, y.shape[-1])
    for start in range(0, x_rows.shape[0], rows):
        yield x_rows[start : start + rows], y_rows[start : start + rows]


def pair_moments(first: np.ndarray, second: np.ndarray) -> dict[str, float | int]:
    count = 0
    sum_x = sum_y = sum_xx = sum_yy = sum_xy = 0.0
    sum_error = sum_abs_error = sum_squared_error = 0.0
    for raw_x, raw_y in paired_blocks(first, second):
        x = np.asarray(raw_x, dtype=np.float64)
        y = np.asarray(raw_y, dtype=np.float64)
        require(np.all(np.isfinite(x)) and np.all(np.isfinite(y)), "paired moment values invalid")
        error = y - x
        count += int(x.size)
        sum_x += float(np.sum(x, dtype=np.float64))
        sum_y += float(np.sum(y, dtype=np.float64))
        sum_xx += float(np.sum(x * x, dtype=np.float64))
        sum_yy += float(np.sum(y * y, dtype=np.float64))
        sum_xy += float(np.sum(x * y, dtype=np.float64))
        sum_error += float(np.sum(error, dtype=np.float64))
        sum_abs_error += float(np.sum(np.abs(error), dtype=np.float64))
        sum_squared_error += float(np.sum(error * error, dtype=np.float64))
    require(count > 1, "paired moment count invalid")
    return {
        "count": count,
        "sum_x": sum_x,
        "sum_y": sum_y,
        "sum_xx": sum_xx,
        "sum_yy": sum_yy,
        "sum_xy": sum_xy,
        "sum_error": sum_error,
        "sum_abs_error": sum_abs_error,
        "sum_squared_error": sum_squared_error,
    }


def metrics(truth: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    moments = pair_moments(truth, prediction)
    count = int(moments["count"])
    denominator = float(moments["sum_xx"] - moments["sum_x"] * moments["sum_x"] / count)
    require(denominator > 0.0, "R2 denominator invalid")
    return {
        "count": count,
        "r2": float(1.0 - moments["sum_squared_error"] / denominator),
        "rmse": float(np.sqrt(moments["sum_squared_error"] / count)),
        "mae": float(moments["sum_abs_error"] / count),
        "bias": float(moments["sum_error"] / count),
    }


def correlation(first: np.ndarray, second: np.ndarray) -> float:
    moments = pair_moments(first, second)
    count = int(moments["count"])
    covariance = moments["sum_xy"] - moments["sum_x"] * moments["sum_y"] / count
    variance_x = moments["sum_xx"] - moments["sum_x"] * moments["sum_x"] / count
    variance_y = moments["sum_yy"] - moments["sum_y"] * moments["sum_y"] / count
    require(variance_x > 0.0 and variance_y > 0.0, "correlation variance invalid")
    value = float(covariance / np.sqrt(variance_x * variance_y))
    require(np.isfinite(value) and -1.0000000001 <= value <= 1.0000000001, "correlation invalid")
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


def hist2d_chunked(x: np.ndarray, y: np.ndarray, x_edges: np.ndarray, y_edges: np.ndarray) -> np.ndarray:
    require(x.shape == y.shape and x.ndim == 2, "histogram input shape mismatch")
    grid = np.zeros((x_edges.size - 1, y_edges.size - 1), dtype=np.int64)
    for start in range(0, x.shape[0], 8):
        observed, _, _ = np.histogram2d(
            np.asarray(x[start : start + 8]).reshape(-1),
            np.asarray(y[start : start + 8]).reshape(-1),
            bins=(x_edges, y_edges),
        )
        grid += observed.astype(np.int64)
    require(int(np.sum(grid)) == int(x.size), "density histogram coverage mismatch")
    return grid


def probability(grid: np.ndarray) -> np.ndarray:
    values = np.asarray(grid, dtype=np.float64)
    require(np.sum(values) > 0.0, "empty density grid")
    return values / np.sum(values)


def contour_thresholds(grid: np.ndarray, masses: Iterable[float]) -> list[float]:
    values = probability(grid).reshape(-1)
    ordered = np.sort(values)[::-1]
    cumulative = np.cumsum(ordered)
    thresholds = [float(ordered[min(int(np.searchsorted(cumulative, mass, side="left")), ordered.size - 1)]) for mass in masses]
    require(all(value > 0.0 for value in thresholds), "density contour threshold invalid")
    return thresholds


def load_flux(config: dict[str, Any], snapshot: ThreeStageSnapshot) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], np.ndarray]:
    shape = (len(SITES), 819, HOURS)
    truth = {name: np.empty(shape, dtype=np.float32) for name in ("GPP", "SR")}
    predicted = {name: np.empty(shape, dtype=np.float32) for name in ("GPP", "SR")}
    fsds = np.empty((len(SITES), HOURS), dtype=np.float32)
    source_indices = np.asarray([int(member[1:]) - 1 for member in snapshot.development_ranked], dtype=np.int64)
    for site_index, site in enumerate(SITES):
        with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
            fsds[site_index] = np.asarray(dataset.variables["FSDS"][:], dtype=np.float32)
            for name in truth:
                for start in range(0, 819, 16):
                    stop = min(start + 16, 819)
                    truth[name][site_index, start:stop] = np.asarray(
                        dataset.variables[name][source_indices[start:stop], :], dtype=np.float32
                    )
    with Dataset(config["predicted_gpp_handoff"], "r") as dataset:
        predicted["GPP"][:] = np.asarray(dataset.variables["GPP_predicted"][:], dtype=np.float32)
    with Dataset(config["predicted_sr_handoff"], "r") as dataset:
        predicted["SR"][:] = np.asarray(dataset.variables["SR_predicted"][:], dtype=np.float32)
    for name in truth:
        require(np.all(np.isfinite(truth[name])) and np.all(np.isfinite(predicted[name])), f"nonfinite {name}")
    return truth, predicted, fsds


def load_spinup(config: dict[str, Any], snapshot: ThreeStageSnapshot) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    source_indices = np.asarray([int(member[1:]) - 1 for member in snapshot.development_ranked], dtype=np.int64)
    truth = {name: np.empty((2, 819), dtype=np.float64) for name in ("TOTSOMC", "TOTSOMN")}
    for site_index, site in enumerate(SITES):
        with Dataset(str(snapshot.root / "sites" / site / "input_data_v1.nc"), "r") as dataset:
            for name in truth:
                truth[name][site_index] = np.asarray(dataset.variables[name][source_indices], dtype=np.float64)
    predicted: dict[str, np.ndarray] = {}
    with Dataset(config["predicted_cn_handoff"], "r") as dataset:
        for name in truth:
            predicted[name] = np.asarray(dataset.variables[f"{name}_predicted"][:], dtype=np.float64)
    return truth, predicted


def metric_products(spinup_truth: dict[str, np.ndarray], spinup_predicted: dict[str, np.ndarray], flux_truth: dict[str, np.ndarray], flux_predicted: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    units = {"TOTSOMC": "gC/m^2", "TOTSOMN": "gN/m^2", "GPP": "gC/m^2/day", "SR": "gC/m^2/day"}
    rows: list[dict[str, Any]] = []
    for target in ("TOTSOMC", "TOTSOMN", "GPP", "SR"):
        source_truth = spinup_truth[target] if target in spinup_truth else flux_truth[target]
        source_pred = spinup_predicted[target] if target in spinup_predicted else flux_predicted[target]
        for scope in ("pooled", *SITES):
            if scope == "pooled":
                observed, estimate = source_truth, source_pred
            else:
                site_index = SITES.index(scope)
                observed, estimate = source_truth[site_index], source_pred[site_index]
            rows.append({"target": target, "scope": scope, "units": units[target], **metrics(observed, estimate), "residual_convention": "prediction minus ELM", "evidence_class": "in_sample_development_descriptive"})
    return rows


def spinup_figure(output: Path, truth: dict[str, np.ndarray], predicted: dict[str, np.ndarray], metric_rows: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.5))
    for row_index, target in enumerate(("TOTSOMC", "TOTSOMN")):
        values = np.concatenate((truth[target].reshape(-1), predicted[target].reshape(-1)))
        limits = (float(np.min(values)), float(np.max(values)))
        for column, scope in enumerate(("pooled", *SITES)):
            ax = axes[row_index, column]
            if scope == "pooled":
                observed, estimate = truth[target].reshape(-1), predicted[target].reshape(-1)
            else:
                index = SITES.index(scope)
                observed, estimate = truth[target][index], predicted[target][index]
            row = next(item for item in metric_rows if item["target"] == target and item["scope"] == scope)
            ax.scatter(observed, estimate, s=5, alpha=0.3, rasterized=True)
            ax.plot(limits, limits, color="black", linewidth=1)
            ax.set_xlim(limits); ax.set_ylim(limits)
            ax.set_title(f"{scope}  R²={row['r2']:.4f}  RMSE={row['rmse']:.3g}")
            ax.set_xlabel(f"ELM {target}")
            ax.set_ylabel(f"Surrogate {target}")
    fig.suptitle("Published spinup C/N parity")
    fig.text(0.5, 0.01, DISCLAIMER, ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.035, 1, 0.96))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def flux_parity_figure(output: Path, truth: dict[str, np.ndarray], predicted: dict[str, np.ndarray], metric_rows: list[dict[str, Any]], bins: int, grid_output: Path) -> None:
    payload: dict[str, np.ndarray] = {}
    figure, axes = plt.subplots(2, 3, figsize=(14, 8.8))
    colorbar_axes = (
        figure.add_axes((0.92, 0.56, 0.012, 0.31)),
        figure.add_axes((0.92, 0.14, 0.012, 0.31)),
    )
    for row_index, target in enumerate(("GPP", "SR")):
        lower = float(min(np.min(truth[target]), np.min(predicted[target])))
        upper = float(max(np.max(truth[target]), np.max(predicted[target])))
        edges = np.linspace(lower, upper, bins + 1)
        grids: dict[str, np.ndarray] = {}
        for scope in (*SITES,):
            index = SITES.index(scope)
            grids[scope] = hist2d_chunked(truth[target][index], predicted[target][index], edges, edges)
        grids["pooled"] = grids["ABBY"] + grids["JERC"]
        probabilities = {scope: probability(grid) for scope, grid in grids.items()}
        positive = np.concatenate([grid[grid > 0.0] for grid in probabilities.values()])
        normalization = LogNorm(vmin=float(np.min(positive)), vmax=float(max(np.max(grid) for grid in probabilities.values())))
        for column, scope in enumerate(("pooled", *SITES)):
            ax = axes[row_index, column]
            mesh = ax.pcolormesh(edges, edges, probabilities[scope].T, shading="auto", cmap="viridis", norm=normalization)
            ax.plot((lower, upper), (lower, upper), color="white", linewidth=1)
            ax.set_xlim(lower, upper); ax.set_ylim(lower, upper)
            row = next(item for item in metric_rows if item["target"] == target and item["scope"] == scope)
            ax.set_title(f"{scope}  R²={row['r2']:.4f}  RMSE={row['rmse']:.3g}")
            ax.set_xlabel(f"ELM {target} (gC m⁻² day⁻¹)")
            ax.set_ylabel(f"Surrogate {target} (gC m⁻² day⁻¹)")
            payload[f"{target}_{scope}_counts"] = grids[scope]
            payload[f"{target}_{scope}_probability"] = probabilities[scope]
        payload[f"{target}_edges"] = edges
        figure.colorbar(mesh, cax=colorbar_axes[row_index], label="probability mass per bin")
    figure.suptitle("Hourly flux parity densities")
    figure.text(0.5, 0.01, DISCLAIMER, ha="center", fontsize=8)
    figure.subplots_adjust(left=0.07, right=0.89, bottom=0.08, top=0.92, wspace=0.28, hspace=0.3)
    figure.savefig(output, dpi=180)
    plt.close(figure)
    np.savez_compressed(grid_output, **payload)


def joint_figure(output: Path, truth: dict[str, np.ndarray], predicted: dict[str, np.ndarray], bins: int, grid_output: Path) -> list[dict[str, Any]]:
    gpp_lower = float(min(np.min(truth["GPP"]), np.min(predicted["GPP"])))
    gpp_upper = float(max(np.max(truth["GPP"]), np.max(predicted["GPP"])))
    sr_lower = float(min(np.min(truth["SR"]), np.min(predicted["SR"])))
    sr_upper = float(max(np.max(truth["SR"]), np.max(predicted["SR"])))
    gpp_edges = np.linspace(gpp_lower, gpp_upper, bins + 1)
    sr_edges = np.linspace(sr_lower, sr_upper, bins + 1)
    site_grids: dict[tuple[str, str], np.ndarray] = {}
    correlation_rows: list[dict[str, Any]] = []
    for site_index, site in enumerate(SITES):
        for series, source in (("ELM", truth), ("surrogate", predicted)):
            site_grids[(site, series)] = hist2d_chunked(source["GPP"][site_index], source["SR"][site_index], gpp_edges, sr_edges)
            correlation_rows.append({"scope": site, "series": series, "count": int(source["GPP"][site_index].size), "pearson_r": correlation(source["GPP"][site_index], source["SR"][site_index])})
    for series in ("ELM", "surrogate"):
        correlation_rows.append({"scope": "pooled", "series": series, "count": int(truth["GPP"].size), "pearson_r": correlation((truth if series == "ELM" else predicted)["GPP"], (truth if series == "ELM" else predicted)["SR"])})
    rows_with_difference = []
    for scope in ("pooled", *SITES):
        elm = next(row["pearson_r"] for row in correlation_rows if row["scope"] == scope and row["series"] == "ELM")
        surrogate = next(row["pearson_r"] for row in correlation_rows if row["scope"] == scope and row["series"] == "surrogate")
        for row in correlation_rows:
            if row["scope"] == scope:
                rows_with_difference.append({**row, "surrogate_minus_elm": surrogate - elm})
    figure, axes = plt.subplots(1, 3, figsize=(15, 4.9), sharex=True, sharey=True)
    payload: dict[str, np.ndarray] = {"gpp_edges": gpp_edges, "sr_edges": sr_edges}
    x_centers = (gpp_edges[:-1] + gpp_edges[1:]) / 2.0
    y_centers = (sr_edges[:-1] + sr_edges[1:]) / 2.0
    for ax, scope in zip(axes, ("pooled", *SITES)):
        grids = {}
        for series in ("ELM", "surrogate"):
            grid = site_grids[("ABBY", series)] + site_grids[("JERC", series)] if scope == "pooled" else site_grids[(scope, series)]
            grids[series] = grid
            payload[f"{scope}_{series}_counts"] = grid
            payload[f"{scope}_{series}_probability"] = probability(grid)
        for series, color in (("ELM", "black"), ("surrogate", "tab:orange")):
            levels = sorted(set(contour_thresholds(grids[series], (0.50, 0.75, 0.90, 0.99))))
            ax.contour(x_centers, y_centers, probability(grids[series]).T, levels=levels, colors=color, linewidths=1.0)
        elm_r = next(row["pearson_r"] for row in rows_with_difference if row["scope"] == scope and row["series"] == "ELM")
        surrogate_r = next(row["pearson_r"] for row in rows_with_difference if row["scope"] == scope and row["series"] == "surrogate")
        ax.set_title(f"{scope}\nPearson r: ELM={elm_r:.4f}, surrogate={surrogate_r:.4f}")
        ax.set_xlabel("Hourly GPP (gC m⁻² day⁻¹)")
        ax.set_xlim(gpp_lower, gpp_upper); ax.set_ylim(sr_lower, sr_upper)
    axes[0].set_ylabel("Hourly SR (gC m⁻² day⁻¹)")
    axes[0].plot([], [], color="black", label="ELM density")
    axes[0].plot([], [], color="tab:orange", label="surrogate density")
    axes[0].legend(loc="upper left")
    figure.suptitle("Hourly GPP–SR joint density (common axes and probability normalization)")
    figure.text(0.5, 0.01, DISCLAIMER, ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.04, 1, 0.94))
    figure.savefig(output, dpi=180)
    plt.close(figure)
    np.savez_compressed(grid_output, **payload)
    return rows_with_difference


def summarize_category(scope: str, series: str, category: str, gpp: np.ndarray, sr: np.ndarray) -> dict[str, Any]:
    x = np.asarray(gpp, dtype=np.float64).reshape(-1)
    y = np.asarray(sr, dtype=np.float64).reshape(-1)
    require(x.shape == y.shape and x.size > 0, f"empty category: {scope}/{series}/{category}")
    return {"scope": scope, "series": series, "category": category, "count": int(x.size), "gpp_mean": float(np.mean(x)), "gpp_median": float(np.median(x)), "sr_mean": float(np.mean(y)), "sr_median": float(np.median(y)), "sr_q10": float(np.quantile(y, 0.10, method="linear")), "sr_q90": float(np.quantile(y, 0.90, method="linear"))}


def conditional_products(output: Path, truth: dict[str, np.ndarray], predicted: dict[str, np.ndarray], fsds: np.ndarray, config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    eligible: list[np.ndarray] = []
    for site_index in range(len(SITES)):
        daylight = fsds[site_index] > float(config["night_fsds_max"])
        for source in (truth, predicted):
            values = source["GPP"][site_index, :, daylight].reshape(-1)
            eligible.append(values[values > float(config["near_zero_gpp_max"])])
    combined = np.concatenate(eligible).astype(np.float64, copy=False)
    quantiles = np.linspace(0.0, 1.0, int(config["conditional_bins"]) + 1)
    edges = np.quantile(combined, quantiles, method="linear")
    require(np.all(np.diff(edges) > 0.0), "duplicate or non-increasing conditional edges")
    bin_rows: list[dict[str, Any]] = []
    special_rows: list[dict[str, Any]] = []
    plotted: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for scope in ("pooled", *SITES):
        site_indices = range(len(SITES)) if scope == "pooled" else (SITES.index(scope),)
        for series, source in (("ELM", truth), ("surrogate", predicted)):
            daylight_gpp: list[np.ndarray] = []
            daylight_sr: list[np.ndarray] = []
            night_gpp: list[np.ndarray] = []
            night_sr: list[np.ndarray] = []
            near_gpp: list[np.ndarray] = []
            near_sr: list[np.ndarray] = []
            for site_index in site_indices:
                night = fsds[site_index] <= float(config["night_fsds_max"])
                day = ~night
                gpp = source["GPP"][site_index]
                sr = source["SR"][site_index]
                night_gpp.append(gpp[:, night].reshape(-1))
                night_sr.append(sr[:, night].reshape(-1))
                near = day[None, :] & (gpp <= float(config["near_zero_gpp_max"]))
                near_gpp.append(gpp[near])
                near_sr.append(sr[near])
                eligible_mask = day[None, :] & (gpp > float(config["near_zero_gpp_max"]))
                daylight_gpp.append(gpp[eligible_mask])
                daylight_sr.append(sr[eligible_mask])
            special_rows.append(summarize_category(scope, series, "night", np.concatenate(night_gpp), np.concatenate(night_sr)))
            special_rows.append(summarize_category(scope, series, "daylight_near_zero", np.concatenate(near_gpp), np.concatenate(near_sr)))
            x = np.concatenate(daylight_gpp).astype(np.float64, copy=False)
            y = np.concatenate(daylight_sr).astype(np.float64, copy=False)
            bin_index = np.searchsorted(edges, x, side="right") - 1
            bin_index[x == edges[-1]] = edges.size - 2
            require(np.all((bin_index >= 0) & (bin_index < edges.size - 1)), "conditional bin assignment mismatch")
            plotted[(scope, series)] = []
            for index in range(edges.size - 1):
                selected = bin_index == index
                require(np.any(selected), f"empty required conditional bin: {scope}/{series}/{index}")
                x_bin, y_bin = x[selected], y[selected]
                row = {"scope": scope, "series": series, "category": "daylight_binned", "bin_id": index, "gpp_lower": float(edges[index]), "gpp_upper": float(edges[index + 1]), "gpp_midpoint": float((edges[index] + edges[index + 1]) / 2.0), "count": int(y_bin.size), "gpp_mean": float(np.mean(x_bin)), "gpp_median": float(np.median(x_bin)), "sr_mean": float(np.mean(y_bin)), "sr_median": float(np.median(y_bin)), "sr_q10": float(np.quantile(y_bin, 0.10, method="linear")), "sr_q90": float(np.quantile(y_bin, 0.90, method="linear"))}
                bin_rows.append(row); plotted[(scope, series)].append(row)
    figure, axes = plt.subplots(1, 3, figsize=(15, 5.2), sharex=True)
    for ax, scope in zip(axes, ("pooled", *SITES)):
        for series, color in (("ELM", "black"), ("surrogate", "tab:orange")):
            rows = plotted[(scope, series)]
            x = np.asarray([row["gpp_midpoint"] for row in rows])
            median = np.asarray([row["sr_median"] for row in rows])
            q10 = np.asarray([row["sr_q10"] for row in rows])
            q90 = np.asarray([row["sr_q90"] for row in rows])
            ax.plot(x, median, color=color, label=f"{series} median")
            ax.fill_between(x, q10, q90, color=color, alpha=0.18, label=f"{series} q10–q90")
        special = [row for row in special_rows if row["scope"] == scope]
        text = "\n".join(f"{row['series']} {row['category']}: n={row['count']}, SR med={row['sr_median']:.3g}" for row in special)
        ax.text(0.02, 0.98, text, transform=ax.transAxes, va="top", fontsize=7, bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "none"})
        ax.set_title(scope)
        ax.set_xlabel("Daylight GPP bin midpoint (gC m⁻² day⁻¹)")
    axes[0].set_ylabel("Conditional hourly SR (gC m⁻² day⁻¹)")
    axes[-1].legend(loc="best", fontsize=8)
    figure.suptitle("Hourly conditional SR versus GPP; night and daylight near-zero accounted separately")
    figure.text(0.5, 0.01, DISCLAIMER, ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.04, 1, 0.94))
    figure.savefig(output, dpi=180)
    plt.close(figure)
    return bin_rows, special_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "diagnostic output exists")
    args.output.mkdir(parents=True)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    snapshot = ThreeStageSnapshot(config["snapshot_root"], verify_component_hashes=False)
    require(snapshot.snapshot_sha256 == config["snapshot_sha256"], "snapshot mismatch")
    verified_handoffs = verify_handoffs(config)
    spinup_truth, spinup_predicted = load_spinup(config, snapshot)
    flux_truth, flux_predicted, fsds = load_flux(config, snapshot)
    metric_rows = metric_products(spinup_truth, spinup_predicted, flux_truth, flux_predicted)
    require([row["count"] for row in metric_rows if row["target"] in ("GPP", "SR") and row["scope"] == "pooled"] == [100442160, 100442160], "flux metric denominator mismatch")
    write_csv(args.output / "exact_metrics.csv", metric_rows)
    spinup_figure(args.output / "spinup_cn_parity.png", spinup_truth, spinup_predicted, metric_rows)
    flux_parity_figure(args.output / "parity_flux_hourly.png", flux_truth, flux_predicted, metric_rows, int(config["density_bins"]), args.output / "parity_flux_density_grids.npz")
    correlation_rows = joint_figure(args.output / "joint_gpp_sr_hourly.png", flux_truth, flux_predicted, int(config["density_bins"]), args.output / "joint_gpp_sr_density_grids.npz")
    write_csv(args.output / "gpp_sr_correlations.csv", correlation_rows)
    conditional_rows, special_rows = conditional_products(args.output / "gpp_sr_joint_conditional.png", flux_truth, flux_predicted, fsds, config)
    write_csv(args.output / "gpp_sr_conditional_bins.csv", conditional_rows)
    write_csv(args.output / "gpp_sr_night_near_zero.csv", special_rows)
    files = []
    for path in sorted(item for item in args.output.iterdir() if item.is_file()):
        files.append({"path": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    manifest = {"schema": "three-stage-inference-iter014-diagnostics-v1", "result": "pass", "snapshot_sha256": config["snapshot_sha256"], "verified_handoff_sha256": verified_handoffs, "development_member_count": 819, "fixed_test_access": False, "training_or_inference": False, "hourly_count_by_site": 50221080, "hourly_pooled_count": 100442160, "density_bins": config["density_bins"], "conditional_bins": config["conditional_bins"], "night_rule": "FSDS <= 1 W m-2", "near_zero_rule": "FSDS > 1 W m-2 and applicable GPP <= 0.1 gC m-2 day-1", "conditional_edge_rule": "exact linear quantiles of pooled combined eligible daylight ELM and surrogate GPP", "aggregate_rule": "deterministic blockwise float64 moments over every development record", "evidence_class": "in_sample_development_descriptive", "performance_gate_applied": False, "files": files}
    write_json(args.output / "diagnostics_manifest.json", manifest)
    evidence_lines = [f"{sha256_file(path)}  {path.name}" for path in sorted(item for item in args.output.iterdir() if item.is_file())]
    (args.output / "evidence.sha256").write_text("\n".join(evidence_lines) + "\n", encoding="utf-8")
    print("ITER014_DIAGNOSTICS_OK figures=4 exact_metric_rows=12 fixed_test=false")


if __name__ == "__main__":
    main()
