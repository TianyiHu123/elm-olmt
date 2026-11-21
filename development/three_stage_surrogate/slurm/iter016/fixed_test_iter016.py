"""One frozen target-free inference pass and separate Iter016 fixed-test evaluation."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset

from development.three_stage_surrogate.slurm.iter015.full_chain_iter015 import _metrics
from development.three_stage_surrogate.slurm.iter016.refit_iter016 import load_config, validate_config
from model_ELM.three_stage_coupled_release import CoupledThreeStageInference, load_artifacts
from model_ELM.three_stage_data import SITES, TARGETS, require, sha256_file
from model_ELM.three_stage_gpp import FORCING_NAMES, HOURS


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    require(bool(rows), f"empty CSV: {path.name}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def member_number(member: str) -> int:
    require(len(member) == 6 and member.startswith("g") and member[1:].isdigit(), "invalid member")
    return int(member[1:])


def load_fixed_targets(snapshot: Any, site: str, members: Sequence[str]) -> dict[str, np.ndarray]:
    """Evaluation-only target reader; never called by inference."""
    indices = np.asarray([member_number(member) - 1 for member in members], dtype=np.int64)
    path = snapshot.root / "sites" / site / "input_data_v1.nc"
    values: dict[str, np.ndarray] = {}
    with Dataset(str(path), "r") as dataset:
        for name in (*TARGETS, "GPP", "SR"):
            variable = dataset.variables[name]
            if name in {"GPP", "SR"}:
                require(str(variable.units) == "gC/m^2/day", f"{site} {name} units mismatch")
                array = np.empty((len(members), HOURS), dtype=np.float32)
                for row, index in enumerate(indices):
                    array[row] = np.asarray(variable[index, :HOURS], dtype=np.float32)
            else:
                array = np.asarray([float(variable[index]) for index in indices], dtype=np.float64)
            require(np.all(np.isfinite(array)), f"{site} {name} target nonfinite")
            if name in TARGETS:
                require(np.all(array > 0.0), f"{site} {name} target nonpositive")
            values[name] = array
    return values


def infer(config: Mapping[str, Any], output: Path) -> tuple[Any, tuple[str, ...]]:
    base_path = Path(config["base_config"])
    require(sha256_file(base_path) == config["base_config_sha256"], "fixed-test base config mismatch")
    base = load_config(base_path)
    snapshot = validate_config(base, verify_snapshot_components=True)
    recovery_path = Path(config["recovery_report"])
    require(sha256_file(recovery_path) == config["recovery_report_sha256"], "recovery report mismatch")
    recovery = read_json(recovery_path)
    require(recovery.get("result") == "pass" and recovery.get("additional_fitting") is False, "refit not accepted")
    require(recovery.get("artifact_manifest_sha256") == config["artifact_manifest_sha256"], "recovery artifact mismatch")
    require(recovery.get("snapshot_sha256") == snapshot.snapshot_sha256, "recovery snapshot mismatch")
    require(recovery.get("global_split_sha256") == base["global_split_sha256"], "recovery split mismatch")
    require(recovery.get("training_partition") == "development" and int(recovery.get("training_member_count", -1)) == 819, "recovery fit scope mismatch")
    require(recovery.get("fixed_test_fit_access") is False and recovery.get("fixed_test_target_access") is False, "recovery fixed-test boundary mismatch")
    require(recovery.get("gpp_output_policy") == "hard_zero_v1", "recovery gate policy mismatch")
    for key in (
        "artifact_reload_complete", "full_prediction_finite", "gpp_gate_equal_full_binary",
        "stored_prediction_replay", "direct_chunk_consistency", "conditional_cn_rejection",
    ):
        require(recovery.get(key) is True, f"recovery acceptance gate missing: {key}")
    require(recovery.get("attempt_1_mutated") is False and recovery.get("historical_release_modified") is False, "recovery immutability gate mismatch")
    require(recovery.get("fixed_test_evaluation_performed") is False and recovery.get("release_published") is False, "recovery downstream boundary mismatch")
    artifact_root = Path(config["artifact_root"])
    manifest_path = artifact_root / "artifact_manifest.json"
    require(sha256_file(manifest_path) == config["artifact_manifest_sha256"], "artifact manifest mismatch")
    spinup, gpp, sr, manifest = load_artifacts(artifact_root, snapshot)
    engine = CoupledThreeStageInference(snapshot, spinup, gpp, sr, manifest)
    members = tuple(snapshot.fixed_test_ranked)
    require(len(members) == int(config["member_count"]) == 205, "fixed-test member count mismatch")
    require(not set(members).intersection(manifest["training_member_ids"]), "fixed-test training leakage")
    parameters = snapshot._parameter_values(members)
    engine.validate_parameters(parameters)

    prediction_path = output / "fixed_test_predictions.nc"
    with Dataset(str(prediction_path), "w", clobber=False, format="NETCDF4") as target:
        target.schema = "three-stage-iter016-fixed-test-predictions-v1"
        target.contains_elm_targets = 0
        target.training_or_fitting = 0
        target.partition = "fixed_test"
        target.gpp_output_policy = "hard_zero_v1"
        target.snapshot_sha256 = snapshot.snapshot_sha256
        target.global_split_sha256 = base["global_split_sha256"]
        target.artifact_manifest_sha256 = config["artifact_manifest_sha256"]
        target.inference_entry_point = "model_ELM.three_stage_coupled_release.CoupledThreeStageInference"
        target.site_requirement = "ABBY,JERC"
        target.forcing_requirement = ",".join(FORCING_NAMES)
        target.calendar = "noleap"
        target.createDimension("site", len(SITES))
        target.createDimension("member", len(members))
        target.createDimension("parameter", len(snapshot.parameter_names))
        target.createDimension("time", HOURS)
        site_variable = target.createVariable("site", str, ("site",)); site_variable[:] = np.asarray(SITES, dtype=object)
        member_variable = target.createVariable("member_id", str, ("member",)); member_variable[:] = np.asarray(members, dtype=object)
        parameter_name_variable = target.createVariable("parameter_name", str, ("parameter",)); parameter_name_variable[:] = np.asarray(snapshot.parameter_names, dtype=object)
        parameter_variable = target.createVariable("parameter", "f8", ("member", "parameter")); parameter_variable[:] = parameters
        time_variable = target.createVariable("time", "i8", ("time",)); time_variable[:] = np.arange(HOURS, dtype=np.int64)
        time_variable.units = "hours since 2018-01-01 00:00:00"; time_variable.calendar = "noleap"
        cn_c = target.createVariable("TOTSOMC_predicted", "f8", ("site", "member"))
        cn_n = target.createVariable("TOTSOMN_predicted", "f8", ("site", "member"))
        cn_c.units = config["units"]["TOTSOMC"]; cn_n.units = config["units"]["TOTSOMN"]
        options = {"zlib": True, "complevel": 2, "chunksizes": (1, 1, 8760)}
        raw = target.createVariable("GPP_raw", "f4", ("site", "member", "time"), **options)
        gated = target.createVariable("GPP_gated", "f4", ("site", "member", "time"), **options)
        respiration = target.createVariable("SR_predicted", "f4", ("site", "member", "time"), **options)
        raw.units = config["units"]["GPP"]; gated.units = config["units"]["GPP"]
        respiration.units = config["units"]["SR"]
        gated.gpp_output_policy = "hard_zero_v1"
        for site_index, site in enumerate(SITES):
            site_path = snapshot.root / "sites" / site / "input_data_v1.nc"
            with Dataset(str(site_path), "r") as source:
                forcing = {name: np.asarray(source.variables[name][:HOURS], dtype=np.float64) for name in FORCING_NAMES}
                time = np.asarray(source.variables["time"][:HOURS], dtype=np.int64)
            temporary_paths = {
                name: output / f".{site.lower()}_{name}_temporary_float32.dat"
                for name in ("gpp_raw", "gpp_gated", "sr")
            }
            temporary = {
                name: np.memmap(path, mode="w+", dtype=np.float32, shape=(len(members), HOURS))
                for name, path in temporary_paths.items()
            }
            cn = engine.predict_to_arrays(
                parameters, site=site, forcing=forcing, time=time, start=0, end=HOURS,
                gpp_raw_output=temporary["gpp_raw"], gpp_output=temporary["gpp_gated"],
                sr_output=temporary["sr"], member_chunk=int(config["member_chunk"]),
            )
            cn_c[site_index] = cn[:, 0]
            cn_n[site_index] = cn[:, 1]
            raw[site_index] = temporary["gpp_raw"]
            gated[site_index] = temporary["gpp_gated"]
            respiration[site_index] = temporary["sr"]
            target.sync()
            for values in temporary.values():
                values.flush()
            del temporary
            for path in temporary_paths.values():
                path.unlink()
        target.sync()

    # Bounded deterministic reload/direct-vs-chunk replay, still without targets.
    with Dataset(str(prediction_path), "r") as stored:
        expected_dimensions = {"site": 2, "member": 205, "parameter": 18, "time": HOURS}
        require({name: len(value) for name, value in stored.dimensions.items()} == expected_dimensions, "prediction dimension inventory mismatch")
        expected_variables = {"site", "member_id", "parameter_name", "parameter", "time", "TOTSOMC_predicted", "TOTSOMN_predicted", "GPP_raw", "GPP_gated", "SR_predicted"}
        require(set(stored.variables) == expected_variables, "prediction variable inventory mismatch")
        expected_attributes = {"schema", "contains_elm_targets", "training_or_fitting", "partition", "gpp_output_policy", "snapshot_sha256", "global_split_sha256", "artifact_manifest_sha256", "inference_entry_point", "site_requirement", "forcing_requirement", "calendar"}
        require(set(stored.ncattrs()) == expected_attributes, "prediction global-attribute inventory mismatch")
        expected_variable_dimensions = {
            "site": ("site",), "member_id": ("member",), "parameter_name": ("parameter",),
            "parameter": ("member", "parameter"), "time": ("time",),
            "TOTSOMC_predicted": ("site", "member"), "TOTSOMN_predicted": ("site", "member"),
            "GPP_raw": ("site", "member", "time"), "GPP_gated": ("site", "member", "time"),
            "SR_predicted": ("site", "member", "time"),
        }
        require({name: value.dimensions for name, value in stored.variables.items()} == expected_variable_dimensions, "prediction variable dimensions mismatch")
        require(stored.schema == "three-stage-iter016-fixed-test-predictions-v1" and stored.partition == "fixed_test", "prediction schema/partition mismatch")
        require(int(stored.contains_elm_targets) == 0 and int(stored.training_or_fitting) == 0, "prediction serialization scope mismatch")
        require(stored.gpp_output_policy == "hard_zero_v1" and stored.snapshot_sha256 == snapshot.snapshot_sha256, "prediction identity mismatch")
        require(stored.global_split_sha256 == base["global_split_sha256"] and stored.artifact_manifest_sha256 == config["artifact_manifest_sha256"], "prediction provenance mismatch")
        require(stored.inference_entry_point == "model_ELM.three_stage_coupled_release.CoupledThreeStageInference", "prediction entry point mismatch")
        require(stored.site_requirement == "ABBY,JERC" and stored.forcing_requirement == ",".join(FORCING_NAMES), "prediction requirements mismatch")
        require(stored.calendar == "noleap", "prediction calendar mismatch")
        require(tuple(str(value) for value in stored.variables["site"][:]) == tuple(SITES), "prediction site coordinate mismatch")
        require(tuple(str(value) for value in stored.variables["member_id"][:]) == tuple(members), "prediction member coordinate mismatch")
        require(tuple(str(value) for value in stored.variables["parameter_name"][:]) == tuple(snapshot.parameter_names), "prediction parameter-name coordinate mismatch")
        require(np.array_equal(np.asarray(stored.variables["parameter"][:], dtype=np.float64), parameters), "prediction parameter values mismatch")
        require(np.array_equal(np.asarray(stored.variables["time"][:], dtype=np.int64), np.arange(HOURS)), "prediction time coordinate mismatch")
        require(stored.variables["time"].units == "hours since 2018-01-01 00:00:00" and stored.variables["time"].calendar == "noleap", "prediction time metadata mismatch")
        for variable_name, unit_key in (("TOTSOMC_predicted", "TOTSOMC"), ("TOTSOMN_predicted", "TOTSOMN"), ("GPP_raw", "GPP"), ("GPP_gated", "GPP"), ("SR_predicted", "SR")):
            require(stored.variables[variable_name].units == config["units"][unit_key], f"prediction units mismatch: {variable_name}")
        for site_index, site in enumerate(SITES):
            site_path = snapshot.root / "sites" / site / "input_data_v1.nc"
            with Dataset(str(site_path), "r") as source:
                forcing = {name: np.asarray(source.variables[name][:768], dtype=np.float64) for name in FORCING_NAMES}
                time = np.asarray(source.variables["time"][:768], dtype=np.int64)
            direct = engine.predict(parameters[:2], site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=1)
            chunked = engine.predict(parameters[:2], site=site, forcing=forcing, time=time, start=720, end=768, member_chunk=2)
            for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr"):
                require(np.allclose(getattr(direct, name), getattr(chunked, name), rtol=1e-6, atol=1e-6), f"{site} chunk mismatch: {name}")
            require(np.array_equal(direct.gpp, np.maximum(direct.gpp_raw, 0.0)), f"{site} replay gate mismatch")
            require(np.allclose(direct.totsomc, stored.variables["TOTSOMC_predicted"][site_index, :2], rtol=1e-6, atol=1e-6), f"{site} stored C replay mismatch")
            require(np.allclose(direct.totsomn, stored.variables["TOTSOMN_predicted"][site_index, :2], rtol=1e-6, atol=1e-6), f"{site} stored N replay mismatch")
            require(np.allclose(direct.gpp_raw, stored.variables["GPP_raw"][site_index, :2, 720:768], rtol=1e-6, atol=1e-6), f"{site} stored raw replay mismatch")
            require(np.allclose(direct.gpp, stored.variables["GPP_gated"][site_index, :2, 720:768], rtol=1e-6, atol=1e-6), f"{site} stored gate replay mismatch")
            require(np.allclose(direct.sr, stored.variables["SR_predicted"][site_index, :2, 720:768], rtol=1e-6, atol=1e-6), f"{site} stored SR replay mismatch")
    return snapshot, members


def aggregate(values: np.ndarray, resolution: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if resolution == "daily":
        require(array.shape[-1] % 24 == 0, "daily axis mismatch")
        return array.reshape(*array.shape[:-1], array.shape[-1] // 24, 24).mean(axis=-1)
    return array


def correlation(x: np.ndarray, y: np.ndarray) -> float:
    a = np.asarray(x, dtype=np.float64).reshape(-1)
    b = np.asarray(y, dtype=np.float64).reshape(-1)
    require(a.size == b.size and a.size > 1, "correlation size mismatch")
    return float(np.corrcoef(a, b)[0, 1])


def evaluate(config: Mapping[str, Any], snapshot: Any, members: Sequence[str], output: Path) -> None:
    prediction_path = output / "fixed_test_predictions.nc"
    truth = {site: load_fixed_targets(snapshot, site, members) for site in SITES}
    cn_rows: list[dict[str, Any]] = []
    flux_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    correlation_rows: list[dict[str, Any]] = []
    with Dataset(str(prediction_path), "r") as predicted:
        cn_names = {"TOTSOMC": "TOTSOMC_predicted", "TOTSOMN": "TOTSOMN_predicted"}
        for target_name, variable_name in cn_names.items():
            site_pairs = {
                site: (truth[site][target_name], np.asarray(predicted.variables[variable_name][index], dtype=np.float64))
                for index, site in enumerate(SITES)
            }
            for scope in (*SITES, "pooled"):
                observed, estimate = site_pairs[scope] if scope in SITES else (
                    np.concatenate([site_pairs[site][0] for site in SITES]),
                    np.concatenate([site_pairs[site][1] for site in SITES]),
                )
                for scale in ("physical", "natural_log"):
                    use_observed = np.log(observed) if scale == "natural_log" else observed
                    use_estimate = np.log(estimate) if scale == "natural_log" else estimate
                    cn_rows.append({
                        "scope": scope, "target": target_name, "scale": scale,
                        "units": config["units"][target_name] if scale == "physical" else "natural_log_of_physical_value",
                        "bias_convention": config["bias_convention"], "aggregation": "member_values",
                        **_metrics(use_observed, use_estimate),
                    })

        for target_name, variable_name in (("GPP", "GPP_gated"), ("SR", "SR_predicted")):
            site_pairs = {
                site: (truth[site][target_name], np.asarray(predicted.variables[variable_name][index], dtype=np.float32))
                for index, site in enumerate(SITES)
            }
            for scope in (*SITES, "pooled"):
                observed, estimate = site_pairs[scope] if scope in SITES else (
                    np.concatenate([site_pairs[site][0] for site in SITES]),
                    np.concatenate([site_pairs[site][1] for site in SITES]),
                )
                for resolution in ("hourly", "daily"):
                    flux_rows.append({
                        "scope": scope, "target": target_name, "resolution": resolution,
                        "units": config["units"][target_name], "bias_convention": config["bias_convention"],
                        "aggregation": "identity_hourly" if resolution == "hourly" else config["daily_aggregation"],
                        **_metrics(aggregate(observed, resolution), aggregate(estimate, resolution)),
                    })

        for scope in (*SITES, "pooled"):
            indices = range(len(SITES)) if scope == "pooled" else (SITES.index(scope),)
            observed = np.concatenate([truth[SITES[index]]["GPP"].reshape(-1) for index in indices])
            raw = np.concatenate([np.asarray(predicted.variables["GPP_raw"][index], dtype=np.float32).reshape(-1) for index in indices])
            gated = np.concatenate([np.asarray(predicted.variables["GPP_gated"][index], dtype=np.float32).reshape(-1) for index in indices])
            require(np.array_equal(gated, np.maximum(raw, np.float32(0.0))), f"{scope} full GPP gate mismatch")
            for resolution in ("hourly", "daily"):
                obs_use = aggregate(observed, resolution)
                raw_use = aggregate(raw, resolution)
                gated_use = aggregate(gated, resolution)
                raw_metrics = _metrics(obs_use, raw_use)
                gated_metrics = _metrics(obs_use, gated_use)
                gate_rows.append({
                    "scope": scope, "resolution": resolution,
                    "units": config["units"]["GPP"], "bias_convention": config["bias_convention"],
                    "aggregation": "identity_hourly" if resolution == "hourly" else config["daily_aggregation"],
                    "raw_r2": raw_metrics["r2"], "gated_r2": gated_metrics["r2"],
                    "raw_rmse": raw_metrics["rmse"], "gated_rmse": gated_metrics["rmse"],
                    "raw_mae": raw_metrics["mae"], "gated_mae": gated_metrics["mae"],
                    "raw_bias": raw_metrics["bias"], "gated_bias": gated_metrics["bias"],
                    "negative_raw_count": int(np.count_nonzero(raw_use < 0.0)),
                    "count": int(obs_use.size),
                })

        # Exact common-edge joint-density package and correlations.
        all_gpp = [truth[site]["GPP"] for site in SITES] + [np.asarray(predicted.variables["GPP_gated"][i], dtype=np.float32) for i in range(len(SITES))]
        all_sr = [truth[site]["SR"] for site in SITES] + [np.asarray(predicted.variables["SR_predicted"][i], dtype=np.float32) for i in range(len(SITES))]
        gpp_edges = np.linspace(min(float(np.min(v)) for v in all_gpp), max(float(np.max(v)) for v in all_gpp), int(config["density_bins"]) + 1)
        sr_edges = np.linspace(min(float(np.min(v)) for v in all_sr), max(float(np.max(v)) for v in all_sr), int(config["density_bins"]) + 1)
        density: dict[str, np.ndarray] = {"gpp_edges": gpp_edges, "sr_edges": sr_edges}
        for scope in (*SITES, "pooled"):
            indices = range(len(SITES)) if scope == "pooled" else (SITES.index(scope),)
            for series in ("ELM", "surrogate"):
                gpp_values = np.concatenate([(truth[SITES[i]]["GPP"] if series == "ELM" else all_gpp[len(SITES) + i]).reshape(-1) for i in indices])
                sr_values = np.concatenate([(truth[SITES[i]]["SR"] if series == "ELM" else all_sr[len(SITES) + i]).reshape(-1) for i in indices])
                counts = np.histogram2d(gpp_values, sr_values, bins=(gpp_edges, sr_edges))[0].astype(np.int64)
                require(int(np.sum(counts)) == gpp_values.size, "joint-density count mismatch")
                density[f"{scope}_{series}_counts"] = counts
                density[f"{scope}_{series}_probability"] = counts.astype(np.float64) / float(np.sum(counts))
                correlation_rows.append({
                    "scope": scope, "series": series, "resolution": "hourly",
                    "gpp_units": config["units"]["GPP"], "sr_units": config["units"]["SR"],
                    "count": int(gpp_values.size), "pearson_r": correlation(gpp_values, sr_values),
                })
        np.savez_compressed(output / "gpp_sr_joint_density.npz", **density)

        # Exactly three compact figures.
        figure, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        for axis, (target_name, variable_name) in zip(axes, cn_names.items()):
            observed = np.concatenate([truth[site][target_name] for site in SITES])
            estimate = np.concatenate([np.asarray(predicted.variables[variable_name][i], dtype=np.float64) for i in range(len(SITES))])
            axis.scatter(observed, estimate, s=7, alpha=0.45)
            limits = (min(float(observed.min()), float(estimate.min())), max(float(observed.max()), float(estimate.max())))
            axis.plot(limits, limits, color="black", lw=1); axis.set(xlabel="ELM", ylabel="surrogate", title=target_name)
        figure.tight_layout(); figure.savefig(output / "cn_parity.png", dpi=180); plt.close(figure)

        figure, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        for axis, (target_name, variable_name) in zip(axes, (("GPP", "GPP_gated"), ("SR", "SR_predicted"))):
            observed = np.concatenate([truth[site][target_name].reshape(-1) for site in SITES])
            estimate = np.concatenate([np.asarray(predicted.variables[variable_name][i], dtype=np.float32).reshape(-1) for i in range(len(SITES))])
            indices = np.linspace(0, observed.size - 1, 60000, dtype=np.int64)
            axis.hexbin(observed[indices], estimate[indices], gridsize=70, mincnt=1, bins="log")
            limits = (min(float(observed[indices].min()), float(estimate[indices].min())), max(float(observed[indices].max()), float(estimate[indices].max())))
            axis.plot(limits, limits, color="black", lw=1); axis.set(xlabel="ELM", ylabel="surrogate", title=f"{target_name} hourly")
        figure.tight_layout(); figure.savefig(output / "flux_parity.png", dpi=180); plt.close(figure)

        figure, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharex=True, sharey=True)
        xcenters = (gpp_edges[:-1] + gpp_edges[1:]) / 2
        ycenters = (sr_edges[:-1] + sr_edges[1:]) / 2
        for axis, scope in zip(axes, ("pooled", *SITES)):
            for series, color in (("ELM", "black"), ("surrogate", "tab:orange")):
                probability = density[f"{scope}_{series}_probability"]
                positive = probability[probability > 0]
                levels = np.quantile(positive, [0.75, 0.9, 0.97])
                axis.contour(xcenters, ycenters, probability.T, levels=np.unique(levels), colors=color)
            axis.set(title=scope, xlabel="GPP")
        axes[0].set_ylabel("SR"); figure.tight_layout(); figure.savefig(output / "gpp_sr_joint_density.png", dpi=180); plt.close(figure)

    write_csv(output / "cn_metrics.csv", cn_rows)
    write_csv(output / "flux_metrics.csv", flux_rows)
    write_csv(output / "gpp_gate_diagnostics.csv", gate_rows)
    write_csv(output / "gpp_sr_correlations.csv", correlation_rows)


def run(config_path: Path, output: Path) -> dict[str, Any]:
    config = read_json(config_path)
    require(config.get("schema") == "three-stage-iter016-fixed-test-config-v1", "fixed-test schema mismatch")
    require(not output.exists(), f"fixed-test output exists: {output}")
    for key in ("training_or_fitting_allowed", "configuration_selection_allowed", "fixed_test_target_access_inside_inference", "release_publication_allowed"):
        require(config.get(key) is False, f"fixed-test scope mismatch: {key}")
    require(config.get("fixed_test_inference_allowed") is True and config.get("fixed_test_target_access_in_separate_evaluation") is True, "fixed-test authority mismatch")
    output.mkdir(parents=True)
    snapshot, members = infer(config, output)
    evaluate(config, snapshot, members, output)
    files = []
    for path in sorted(output.iterdir()):
        if path.name != "fixed_test_report.json" and path.is_file():
            files.append({"path": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    report = {
        "schema": "three-stage-iter016-fixed-test-report-v1",
        "result": "pass",
        "partition": "fixed_test",
        "sites": list(SITES),
        "member_count": len(members),
        "hours_per_site_member": HOURS,
        "snapshot_sha256": snapshot.snapshot_sha256,
        "global_split_sha256": sha256_file(snapshot.split_path),
        "artifact_manifest_sha256": config["artifact_manifest_sha256"],
        "recovery_report_sha256": config["recovery_report_sha256"],
        "training_or_fitting": False,
        "configuration_selection": False,
        "target_free_inference": True,
        "separate_target_evaluation": True,
        "contains_exact_fixed_test_member_order": True,
        "gpp_output_policy": "hard_zero_v1",
        "units": config["units"],
        "bias_convention": config["bias_convention"],
        "daily_aggregation": config["daily_aggregation"],
        "inference_entry_point": "model_ELM.three_stage_coupled_release.CoupledThreeStageInference",
        "prediction_serialization_schema": "three-stage-iter016-fixed-test-predictions-v1",
        "prediction_variable_inventory_verified_target_free": True,
        "gpp_gate_equal_full_binary": True,
        "deterministic_reload_and_chunk_consistency": True,
        "metric_rows": {"cn": 12, "flux": 12, "gate": 6, "joint_correlation": 6},
        "figures": ["cn_parity.png", "flux_parity.png", "gpp_sr_joint_density.png"],
        "performance_threshold_applied": False,
        "uncertainty_refit": False,
        "release_published": False,
        "files": files,
    }
    write_json(output / "fixed_test_report.json", report)
    print("ITER016_FIXED_TEST_OK members=205 sites=2 hours=61320 tuning=false", flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return 0 if run(args.config, args.output)["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
