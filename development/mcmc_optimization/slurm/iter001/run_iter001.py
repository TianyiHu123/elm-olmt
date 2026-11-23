#!/usr/bin/env python3
"""Compute-node validation and benchmark driver for MCMC Iter001."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import statistics
import sys
import time
from pathlib import Path

import numpy as np
from netCDF4 import Dataset


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    root = Path(config["repository_root"])
    if root.resolve() != Path("/xdisk/chopinsong/tianyihu/elm-olmt-mcmc"):
        raise RuntimeError("execution checkout mismatch")
    if sha256(root / "development/mcmc_optimization/MCMC_OPTIMIZATION_PLAN.md") != config["plan_sha256"]:
        raise RuntimeError("campaign plan identity mismatch")
    return config


def environment() -> dict:
    return {
        "hostname": platform.node(),
        "python": sys.version,
        "executable": sys.executable,
        "numpy": np.__version__,
        "threads": {key: os.environ.get(key) for key in (
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"
        )},
    }


def load_release(config: dict):
    from model_ELM.mcmc_coupled_adapter import load_ppe1_coupled_release
    from model_ELM.mcmc_prior import PPE1, Prior18
    prior = Prior18.from_directory(PPE1, config["ppe1_root"])
    return prior, load_ppe1_coupled_release(
        prior=prior,
        release_root=config["release_root"],
        snapshot_root=config["snapshot_root"],
        source_file=Path(config["repository_root"]) / "model_ELM/three_stage_coupled_release.py",
        uncertainty_root=Path(config["uncertainty_handoff"]).parent,
    )


def forcing(config: dict, site: str, end: int):
    from model_ELM.three_stage_gpp import FORCING_NAMES
    path = Path(config["snapshot_root"]) / "sites" / site / "input_data_v1.nc"
    with Dataset(path, "r") as dataset:
        values = {name: np.asarray(dataset.variables[name][:end], dtype=np.float64) for name in FORCING_NAMES}
        axis = np.asarray(dataset.variables["time"][:end], dtype=np.int64)
    return values, axis


def run_prior(config: dict, output: Path) -> None:
    from model_ELM.mcmc_prior import EXPECTED_FILE_HASHES, PPE1, PPE2, Prior18
    records = {}
    for prior_id, key in ((PPE1, "ppe1_root"), (PPE2, "ppe2_root")):
        prior = Prior18.from_directory(prior_id, config[key])
        unit = np.loadtxt(prior.metadata_file.parent / "sobol18_1024_unit.txt")
        expected = np.loadtxt(prior.metadata_file.parent / "sobol18_1024.txt")
        mapped = prior.inverse_unit(unit)
        relative = np.abs(mapped - expected) / np.maximum(np.abs(expected), np.finfo(np.float64).tiny)
        records[prior_id] = {
            "file_sha256": {name: sha256(prior.metadata_file.parent / name) for name in EXPECTED_FILE_HASHES[prior_id]},
            "expected_file_sha256": EXPECTED_FILE_HASHES[prior_id],
            "max_abs_inverse_error": float(np.max(np.abs(mapped - expected))),
            "max_rel_inverse_error": float(np.max(relative)),
            "inverse_allclose_rtol_1e_10_atol_1e_12": bool(np.allclose(mapped, expected, rtol=1e-10, atol=1e-12)),
            "all_support_valid": bool(np.all(prior.support_mask(mapped))),
            "finite_log_density": bool(np.all(np.isfinite(prior.log_density(mapped)))),
        }
    report = {"schema": "mcmc-iter001-prior-report-v1", "status": "pass", "environment": environment(), "priors": records}
    write_json(output, report)
    print("MCMC_ITER001_PRIOR_PASS")


def run_interface(config: dict, output: Path) -> None:
    from model_ELM.mcmc_coupled_adapter import OUTPUT_UNITS
    prior, loaded = load_release(config)
    parameters = prior.inverse_unit(np.vstack((np.full(18, 0.25), np.full(18, 0.75))))
    sites = {}
    for site in config["sites"]:
        values, axis = forcing(config, site, 768)
        first = loaded.engine.predict(parameters, site=site, forcing=values, time=axis, start=720, end=768, member_chunk=1)
        repeat = loaded.engine.predict(parameters, site=site, forcing=values, time=axis, start=720, end=768, member_chunk=1)
        chunked = loaded.engine.predict(parameters, site=site, forcing=values, time=axis, start=720, end=768, member_chunk=2)
        if not all(np.array_equal(getattr(first, name), getattr(repeat, name)) for name in ("totsomc", "totsomn", "gpp_raw", "gpp", "sr")):
            raise RuntimeError("deterministic replay failed")
        if not np.array_equal(first.gpp, np.maximum(first.gpp_raw, 0.0)):
            raise RuntimeError("hard-zero GPP policy failed")
        if not all(np.allclose(getattr(first, name), getattr(chunked, name), rtol=1e-6, atol=1e-6) for name in ("gpp_raw", "gpp", "sr")):
            raise RuntimeError("member-chunk equivalence failed")
        sites[site] = {
            "shape": list(first.gpp.shape),
            "deterministic": True,
            "hard_zero_exact": True,
            "chunk_equivalent": True,
            "finite_sr": bool(np.all(np.isfinite(first.sr))),
            "contains_elm_truth": first.provenance["contains_elm_truth"],
            "training_or_fitting": first.provenance["training_or_fitting"],
            "sr_min": float(np.min(first.sr)),
        }
    report = {
        "schema": "mcmc-iter001-interface-report-v1", "status": "pass", "environment": environment(),
        "release_manifest_sha256": sha256(Path(config["release_root"]) / "release_manifest.json"),
        "catalog_sha256": sha256(Path(config["release_root"]).parent / "catalog.json"), "sites": sites,
        "output_units": loaded.output_units,
        "unit_provenance": loaded.unit_provenance,
    }
    write_json(output, report)
    print("MCMC_ITER001_INTERFACE_PASS")


def run_benchmark(config: dict, output: Path) -> None:
    from model_ELM.mcmc_prior import PPE1, Prior18
    prior_start = time.perf_counter()
    prior = Prior18.from_directory(PPE1, config["ppe1_root"])
    prior_seconds = time.perf_counter() - prior_start
    _, loaded = load_release(config)
    engine = loaded.engine
    rows = []
    max_batch = max(config["batch_sizes"])
    unit = np.linspace(0.05, 0.95, max_batch * 18, dtype=np.float64).reshape(max_batch, 18)
    parameters = prior.inverse_unit(unit)
    forcing_load_seconds = {}
    for site in config["sites"]:
        for hours in config["window_hours"]:
            start = config["history_hours"]
            end = start + hours
            values, axis = forcing(config, site, end)
            if hours == max(config["window_hours"]):
                forcing_start = time.perf_counter()
                forcing(config, site, end)
                forcing_load_seconds[site] = time.perf_counter() - forcing_start
            for batch in config["batch_sizes"]:
                args = dict(site=site, forcing=values, time=axis, start=start, end=end, member_chunk=2)
                baseline = engine.predict(parameters[:batch], **args)
                timings = []
                checksum = None
                for _ in range(config["warm_repetitions"]):
                    begin = time.perf_counter()
                    result = engine.predict(parameters[:batch], **args)
                    timings.append(time.perf_counter() - begin)
                    if not np.array_equal(result.gpp, baseline.gpp) or not np.array_equal(result.sr, baseline.sr):
                        raise RuntimeError("benchmark deterministic replay failed")
                    current = hashlib.sha256(result.gpp.tobytes() + result.sr.tobytes()).hexdigest()
                    checksum = current if checksum is None else checksum
                    if current != checksum:
                        raise RuntimeError("benchmark checksum changed")
                rows.append({
                    "site": site, "window_hours": hours, "batch_size": batch,
                    "warm_seconds": timings, "median_seconds": statistics.median(timings),
                    "seconds_per_parameter_hour": statistics.median(timings) / (batch * hours),
                    "checksum": checksum,
                })
    rates = [row["seconds_per_parameter_hour"] for row in rows if row["window_hours"] == max(config["window_hours"])]
    rate = statistics.median(rates)
    expected_cells = len(config["sites"]) * len(config["window_hours"]) * len(config["batch_sizes"])
    peak_rss_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    complete = len(rows) == expected_cells and all(len(row["warm_seconds"]) == config["warm_repetitions"] for row in rows)
    report = {
        "schema": "mcmc-iter001-benchmark-report-v1", "status": "pass", "environment": environment(),
        "loading_seconds": {"prior": prior_seconds, **loaded.loading_seconds, "forcing_by_site": forcing_load_seconds},
        "peak_rss_kib": peak_rss_kib,
        "validated_release_manifest_sha256": sha256(Path(config["release_root"]) / "release_manifest.json"),
        "matrix": rows,
        "projections": {
            "basis_median_seconds_per_parameter_hour": rate,
            "sobol_1024_full_61320_seconds": rate * 1024 * 61320,
            "mcmc_100000_full_61320_seconds": rate * 100000 * 61320,
            "interpretation": "linear cost projections from measured throughput; not approved production budgets"
        },
        "recommendation": "deferred_to_independent_result_evaluation",
        "measurement_completeness": {"expected_cells": expected_cells, "observed_cells": len(rows),
                                     "all_repeats_complete": complete},
    }
    write_json(output, report)
    print("MCMC_ITER001_BENCHMARK_PASS recommendation=deferred")


def run_final(config: dict, output: Path) -> None:
    root = Path(config["output_root"]) / "results"
    paths = [root / "prior/prior_report.json", root / "interface/interface_report.json", root / "benchmark/benchmark_report.json"]
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    decision_path = root / "benchmark/decision.json"
    decision_report = json.loads(decision_path.read_text(encoding="utf-8"))
    prior, interface, benchmark = reports
    if [report.get("schema") for report in reports] != [
        "mcmc-iter001-prior-report-v1", "mcmc-iter001-interface-report-v1", "mcmc-iter001-benchmark-report-v1"
    ] or any(report.get("status") != "pass" for report in reports):
        raise RuntimeError("one or more work-unit reports did not pass")
    if set(prior.get("priors", {})) != {"ppe1", "ppe2"}:
        raise RuntimeError("prior report coverage mismatch")
    for record in prior["priors"].values():
        if record["file_sha256"] != record["expected_file_sha256"] or not record["all_support_valid"] or not record["finite_log_density"]:
            raise RuntimeError("prior identity/support gate failed")
        if not record.get("inverse_allclose_rtol_1e_10_atol_1e_12", False):
            raise RuntimeError("prior inverse-map gate failed")
    if interface.get("release_manifest_sha256") != "4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a":
        raise RuntimeError("interface release identity mismatch")
    if interface.get("output_units") != {"TOTSOMC": "gC/m^2", "TOTSOMN": "gN/m^2", "GPP": "gC/m^2/day", "SR": "gC/m^2/day"}:
        raise RuntimeError("interface output units mismatch")
    if set(interface.get("unit_provenance", {})) != {"three_stage_spinup.py", "three_stage_gpp.py", "three_stage_sr.py", "three_stage_inference.py"}:
        raise RuntimeError("interface unit provenance mismatch")
    if set(interface.get("sites", {})) != set(config["sites"]):
        raise RuntimeError("interface site coverage mismatch")
    for record in interface["sites"].values():
        if not all((record["deterministic"], record["hard_zero_exact"], record["chunk_equivalent"], record["finite_sr"])):
            raise RuntimeError("interface numerical gate failed")
        if record["contains_elm_truth"] or record["training_or_fitting"]:
            raise RuntimeError("interface target-free gate failed")
    expected = {(site, hours, batch) for site in config["sites"] for hours in config["window_hours"] for batch in config["batch_sizes"]}
    observed = {(row["site"], row["window_hours"], row["batch_size"]) for row in benchmark.get("matrix", ())}
    if observed != expected or len(benchmark.get("matrix", ())) != len(expected):
        raise RuntimeError("benchmark matrix coverage mismatch")
    for row in benchmark["matrix"]:
        timings = row.get("warm_seconds", ())
        if len(timings) != config["warm_repetitions"] or not all(np.isfinite(t) and t > 0 for t in timings):
            raise RuntimeError("benchmark repetition gate failed")
        if not isinstance(row.get("checksum"), str) or len(row["checksum"]) != 64:
            raise RuntimeError("benchmark replay checksum missing")
    loading = benchmark.get("loading_seconds", {})
    if set(loading.get("forcing_by_site", {})) != set(config["sites"]) or not all(np.isfinite(value) and value >= 0 for key, value in loading.items() if key != "forcing_by_site"):
        raise RuntimeError("benchmark loading evidence incomplete")
    if not all(value >= 0 for value in loading["forcing_by_site"].values()) or benchmark.get("peak_rss_kib", 0) <= 0:
        raise RuntimeError("benchmark memory/context evidence incomplete")
    if benchmark.get("validated_release_manifest_sha256") != "4bdc91e2eed6ad8b8228bbc814767fe739a649599c197fade4bf9256ceab543a":
        raise RuntimeError("benchmark release identity mismatch")
    projections = benchmark.get("projections", {})
    for name in ("basis_median_seconds_per_parameter_hour", "sobol_1024_full_61320_seconds", "mcmc_100000_full_61320_seconds"):
        if not np.isfinite(projections.get(name, np.nan)) or projections[name] <= 0:
            raise RuntimeError("benchmark projection evidence invalid")
    if benchmark.get("recommendation") != "deferred_to_independent_result_evaluation":
        raise RuntimeError("benchmark prematurely selected a recommendation")
    if decision_report.get("schema") != "mcmc-iter001-benchmark-decision-v1" or decision_report.get("independent_review") != "pass":
        raise RuntimeError("benchmark decision review missing")
    if decision_report.get("benchmark_report_sha256") != sha256(paths[2]) or decision_report.get("recommendation") not in ("A", "B"):
        raise RuntimeError("benchmark decision identity or recommendation mismatch")
    if not decision_report.get("rationale"):
        raise RuntimeError("benchmark decision rationale missing")
    recommendation = decision_report["recommendation"]
    decision = "continue_existing_inference_path" if recommendation == "A" else "propose_infrastructure_optimization"
    result = {
        "schema": "mcmc-iter001-final-report-v1", "status": "pass", "decision": decision,
        "recommendation": recommendation, "report_sha256": {str(path): sha256(path) for path in paths},
        "benchmark_decision_sha256": sha256(decision_path),
        "environment": environment(),
    }
    write_json(output, result)
    print(f"MCMC_ITER001_FINAL_PASS decision={decision}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prior", "interface", "benchmark", "final"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    {"prior": run_prior, "interface": run_interface, "benchmark": run_benchmark, "final": run_final}[args.mode](config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
