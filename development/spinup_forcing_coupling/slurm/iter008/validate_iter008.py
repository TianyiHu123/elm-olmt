#!/usr/bin/env python3
"""Iter008 validation: fail-closed products, raw-chain identity, and paired diagnosis."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np

REQUIRED = [
    "raw_chain.npz", "raw_chain_metadata.json", "raw_chain_hashes.json",
    "selection_ledger.json", "diagnostic_report.md", "best_params.txt",
    "clm_params_best.nc", "plots/corner/corner_plot.png",
    "plots/pdfs", "plots/predictions", "diagnostics/diagnostics_index.json",
    "diagnostics/chain_health.json", "diagnostics/collocation_audit.csv",
    "diagnostics/posterior_summary.csv", "diagnostics/prior_edge_occupancy.csv",
    "diagnostics/skill_table.csv", "diagnostics/delta_logL.csv",
    "diagnostics/residual_summary.csv", "diagnostics/walker_acceptance.csv",
    "diagnostics/parameter_chain_health.csv",
]
FORCING_SHA = "8d139b32473eebe3f75f77042e542f49ec3c80e89bc65c76b2e98a5c70f4553e"
SPINUP_SHA = "1427dc565af858e9c089a5b9545a7f127e42789ef1fe5c9af3af7f8cb12a3023"
OBS_SHA = {
    "ABBY": "e5f7b6795616e3dbb2f24ef351d84f79da29847e82729db09d8756b3d9a1fdb2",
    "JERC": "a5507878801b83c14a1583a4b9f69a039bee748d8a2da2c50073e5fb94ab2c1f",
}
CASE_NAMES = {
    "ABBY": "ABBY_ppe6_I20TRCNPRDCTCBC",
    "JERC": "JERC_ppe6_I20TRCNPRDCTCBC",
}
CASE_SHA = {
    "ABBY": "8d8717b12c32676479b6a10dc43359a59d8b09811b40f8210a32ad5cf73b07c3",
    "JERC": "274129ded20e20d80e7d8769ec1f8e0d2719c7a533cf5aa1b593932ad8deb209",
}
CONFIG_SHA = {
    "ABBY": "7a1c54a14ab17ce000b199672f3b9171787863409acea3331e812344636ac9f1",
    "JERC": "4f06fe34d35b46418d0c48cbb82951be3c0f8aa27c882bc65a8119b00e13aec2",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_hash(path: Path, relative_to: Path | None = None) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, raw = line.split(None, 1)
        target = Path(raw) if relative_to is None else relative_to / raw
        require(target.is_file(), f"manifest target missing: {target}")
        require(sha256(target) == expected, f"manifest hash mismatch: {target}")
        values[str(target)] = expected
    return values


def validate_site(path: Path, expected_site: str) -> dict:
    for rel in REQUIRED:
        target = path / rel
        require(target.exists(), f"{expected_site}: missing {target}")
    require(any((path / "plots/pdfs").glob("*.png")), f"{expected_site}: no posterior plots")
    require(any((path / "plots/predictions").glob("**/*.png")), f"{expected_site}: no prediction plots")
    require(not (path / "UQ_output").exists(), f"{expected_site}: unexpected UQ_output nesting")
    metadata = json.loads((path / "raw_chain_metadata.json").read_text())
    hashes = json.loads((path / "raw_chain_hashes.json").read_text())
    require(metadata["raw_chain_sha256"] == sha256(path / "raw_chain.npz"), f"{expected_site}: raw hash mismatch")
    require(hashes["raw_chain_sha256"] == metadata["raw_chain_sha256"], f"{expected_site}: hash ledger mismatch")
    require(hashes["raw_chain"] == str(path / "raw_chain.npz"), f"{expected_site}: raw path ledger mismatch")
    require(hashes["metadata"] == str(path / "raw_chain_metadata.json"), f"{expected_site}: metadata path ledger mismatch")
    require(hashes["metadata_sha256"] == sha256(path / "raw_chain_metadata.json"), f"{expected_site}: metadata hash mismatch")
    require(metadata["schema"] == "spinup-forcing-coupling-iter008-raw-chain-v1", f"{expected_site}: metadata schema")
    provenance = metadata.get("provenance", {})
    require(provenance.get("SITE_NAME") == expected_site, f"{expected_site}: provenance site")
    require(provenance.get("ITERATION_ID") == "iter008", f"{expected_site}: provenance iteration")
    require(provenance.get("MICROMAMBA_ENV") == "OLMT_puma", f"{expected_site}: provenance environment")
    require(provenance.get("FORCING_ARTIFACT"), f"{expected_site}: missing forcing provenance")
    require(provenance.get("SPINUP_ARTIFACT"), f"{expected_site}: missing spinup provenance")
    require(provenance.get("SPINUP_MODE") == "coupled", f"{expected_site}: spinup mode")
    require(provenance.get("COUPLED_VARIANT") == "drop21_corr080", f"{expected_site}: coupled variant")
    require(provenance.get("N_WALKERS") == "64" and provenance.get("N_STEPS") == "4000", f"{expected_site}: sampler budget provenance")
    require(provenance.get("N_PROCESSES") == "16" and provenance.get("SEED") == "8008", f"{expected_site}: execution provenance")
    require(provenance.get("SOURCE_MANIFEST_sha256"), f"{expected_site}: missing source-manifest provenance")
    require(provenance.get("CASE_HASH_MANIFEST_sha256"), f"{expected_site}: missing case-manifest provenance")
    require(provenance.get("ARTIFACT_HASH_MANIFEST_sha256"), f"{expected_site}: missing artifact-manifest provenance")
    require(provenance.get("SUBMISSION_CONFIG_sha256"), f"{expected_site}: missing config provenance")
    for key, value in {
        "FORCING_ARTIFACT": str(FORCING_SHA),
        "SPINUP_ARTIFACT": str(SPINUP_SHA),
        "SPINUP_MODE": "coupled",
        "COUPLED_VARIANT": "drop21_corr080",
        "N_WALKERS": "64", "N_STEPS": "4000", "N_PROCESSES": "16", "SEED": "8008",
        "CASE_NAME": CASE_NAMES[expected_site],
    }.items():
        if key.endswith("_ARTIFACT"):
            require(sha256(Path(provenance[key])) == value, f"{expected_site}: {key} identity")
        else:
            require(provenance.get(key) == value, f"{expected_site}: {key} value")
    obs_path = Path(provenance["OBS_PATH"])
    require(sha256(obs_path) == OBS_SHA[expected_site], f"{expected_site}: observation identity")
    source_manifest = Path(provenance["SOURCE_MANIFEST"])
    case_manifest = Path(provenance["CASE_HASH_MANIFEST"])
    artifact_manifest = Path(provenance["ARTIFACT_HASH_MANIFEST"])
    require(sha256(source_manifest) == provenance["SOURCE_MANIFEST_sha256"], f"{expected_site}: source manifest hash")
    manifest_hash(source_manifest, Path("/xdisk/chopinsong/tianyihu/elm-olmt"))
    require(sha256(case_manifest) == provenance["CASE_HASH_MANIFEST_sha256"], f"{expected_site}: case manifest hash")
    require(sha256(artifact_manifest) == provenance["ARTIFACT_HASH_MANIFEST_sha256"], f"{expected_site}: artifact manifest hash")
    require(provenance.get("SUBMISSION_CONFIG_sha256") == CONFIG_SHA[expected_site], f"{expected_site}: recorded configuration hash")
    require(sha256(Path(provenance["SUBMISSION_CONFIG"])) == CONFIG_SHA[expected_site], f"{expected_site}: canonical configuration identity")
    case_values = manifest_hash(case_manifest, Path("/xdisk/chopinsong/tianyihu/elm-olmt"))
    expected_case_path = str(Path("/xdisk/chopinsong/tianyihu/elm-olmt/pklfiles") / f"{CASE_NAMES[expected_site]}.pkl")
    require(case_values.get(expected_case_path) == CASE_SHA[expected_site], f"{expected_site}: case identity")
    artifact_values = manifest_hash(artifact_manifest)
    require(artifact_values.get(provenance["FORCING_ARTIFACT"]) == FORCING_SHA, f"{expected_site}: forcing manifest identity")
    require(artifact_values.get(provenance["SPINUP_ARTIFACT"]) == SPINUP_SHA, f"{expected_site}: spinup manifest identity")
    names = metadata["parameter_names"]
    require(len(names) == len(metadata["pmin"]) == len(metadata["pmax"]), f"{expected_site}: bounds/name lengths")
    require(all(np.isfinite(metadata["pmin"])) and all(np.isfinite(metadata["pmax"])), f"{expected_site}: nonfinite bounds")
    require(all(lo <= hi for lo, hi in zip(metadata["pmin"], metadata["pmax"])), f"{expected_site}: invalid bounds")
    raw = np.load(path / "raw_chain.npz", allow_pickle=False)
    require(list(raw["chain"].shape) == metadata["chain_shape"], f"{expected_site}: chain shape metadata mismatch")
    require(list(raw["log_prob"].shape) == metadata["log_prob_shape"], f"{expected_site}: log-prob shape metadata mismatch")
    require(raw["chain"].shape == (4000, 64, len(metadata["parameter_names"])), f"{expected_site}: raw chain shape")
    require(raw["log_prob"].shape == (4000, 64), f"{expected_site}: raw log-prob shape")
    require(metadata["seed"] == 8008, f"{expected_site}: seed mismatch")
    selection = json.loads((path / "selection_ledger.json").read_text())
    require(selection["raw_chain_sha256"] == metadata["raw_chain_sha256"], f"{expected_site}: selection provenance mismatch")
    health = json.loads((path / "diagnostics/chain_health.json").read_text())
    require(health["nwalkers"] == 64 and health["nsteps"] == 4000, f"{expected_site}: chain health budget mismatch")
    return {"site": expected_site, "path": str(path), "metadata": metadata, "health": health, "selection": selection}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--abby-run-dir", required=True)
    parser.add_argument("--jerc-run-dir", required=True)
    parser.add_argument("--validate-run-dir", required=True)
    parser.add_argument("--summary-root", required=True)
    args = parser.parse_args()
    abby = validate_site(Path(args.abby_run_dir), "ABBY")
    jerc = validate_site(Path(args.jerc_run_dir), "JERC")
    require(abby["metadata"]["parameter_names"] == jerc["metadata"]["parameter_names"], "parameter schema differs")
    require(abby["metadata"]["seed"] == jerc["metadata"]["seed"] == 8008, "paired seed differs")

    # Evidence-backed routing is descriptive and deliberately not an acceptance gate.
    health_values = [abby["health"], jerc["health"]]
    residual_lags = []
    for site in (Path(args.abby_run_dir), Path(args.jerc_run_dir)):
        with (site / "diagnostics/residual_summary.csv").open(newline="") as fp:
            residual_lags.extend(float(row["resid_lag1_corr"]) for row in csv.DictReader(fp) if row["resid_lag1_corr"] not in ("", "nan"))
    if any(float(h.get("mean_acceptance_fraction", 1.0)) < 0.2 for h in health_values):
        route = "sampler-limited"
    elif residual_lags and any(abs(x) > 0.9 for x in residual_lags):
        route = "likelihood-limited"
    else:
        route = "inconclusive"
    validate_dir = Path(args.validate_run_dir)
    validate_dir.mkdir(parents=True, exist_ok=True)
    comparison = {
        "schema": "spinup-forcing-coupling-iter008-paired-comparison-v1",
        "sites": {"ABBY": abby, "JERC": jerc},
        "same_seed": True,
        "route": route,
        "scientific_quality_gate": False,
        "evidence": {"residual_lag1_values": residual_lags},
    }
    (validate_dir / "paired_comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")
    (validate_dir / "paired_comparison.md").write_text(
        "# Iter008 paired ABBY-JERC comparison\n\n"
        f"- Same seed: `8008`\n- Diagnostic route: **{route}**\n"
        "- Scientific quality is characterization only; no quality hard gate was applied.\n"
        "- See `paired_comparison.json` and the site reports for evidence.\n"
    )

    summary = Path(args.summary_root)
    summary.mkdir(parents=True, exist_ok=True)
    rows = []
    for site, payload in (("ABBY", abby), ("JERC", jerc)):
        h = payload["health"]
        rows.append({
            "work_unit": site.lower(), "site": site, "run_dir": payload["path"],
            "raw_chain_sha256": payload["metadata"]["raw_chain_sha256"],
            "mean_acceptance_fraction": h.get("mean_acceptance_fraction"),
            "approx_ess": h.get("approx_ess"), "gate_result": "pass",
        })
    rows.append({"work_unit": "validate", "site": "ABBY+JERC", "run_dir": str(validate_dir), "raw_chain_sha256": "", "mean_acceptance_fraction": "", "approx_ess": "", "gate_result": "pass"})
    with (summary / "iter008_accounting.csv").open("w", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    shutil.copy2(validate_dir / "paired_comparison.json", summary / "iter008_paired_comparison.json")
    shutil.copy2(validate_dir / "paired_comparison.md", summary / "iter008_paired_comparison.md")
    for site, root in (("abby", Path(args.abby_run_dir)), ("jerc", Path(args.jerc_run_dir))):
        for name in ("chain_health.json", "collocation_audit.csv", "posterior_summary.csv", "prior_edge_occupancy.csv", "skill_table.csv", "delta_logL.csv", "residual_summary.csv", "walker_acceptance.csv", "parameter_chain_health.csv"):
            shutil.copy2(root / "diagnostics" / name, summary / f"iter008_{site}_{name}")
        shutil.copy2(root / "diagnostic_report.md", summary / f"iter008_{site}_diagnostic_report.md")
    decision = {
        "schema": "spinup-forcing-coupling-iter008-decision-v1",
        "iteration_id": "iter008", "status": "completed", "work_type": "implementation",
        "objective": "Single-site ABBY and JERC coupled/drop21_corr080 SR MCMC diagnostic campaign",
        "bounded_scope": "ABBY and JERC separately; coupled drop21_corr080; SR; 64x4000; seed 8008; raw-chain diagnostics; integrity-only",
        "acceptance_result": "pass", "decision": route,
        "output_root": str(Path(args.abby_run_dir).parent),
        "summary_path": "development/spinup_forcing_coupling/summaries/iter008",
        "paired_comparison": str(validate_dir / "paired_comparison.json"),
        "passed": True,
    }
    (summary / "iter008_decision.json").write_text(json.dumps(decision, indent=2) + "\n")
    print(f"VALIDATE_PASS route={route} summary={summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
