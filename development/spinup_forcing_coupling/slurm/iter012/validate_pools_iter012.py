#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--abby", type=Path, required=True); parser.add_argument("--jerc", type=Path, required=True); parser.add_argument("--repository-commit", required=True); parser.add_argument("--source-manifest", type=Path, required=True); parser.add_argument("--dependency-manifest", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(); rows = []
    for site, root in (("ABBY", args.abby), ("JERC", args.jerc)):
        contract = json.loads((root / "search_contract.json").read_text())
        artifact_manifest = json.loads((root / "artifact_manifest.json").read_text())
        pool = np.load(root / "candidate_pool.npz", allow_pickle=False)
        states = np.asarray(pool["physical_states"], float); strata = np.asarray(pool["strata"], int)
        required_arrays = {
            "physical_states",
            "physical_log_posterior",
            "prior_component",
            "log_likelihood",
            "strata",
        }
        if required_arrays - set(pool.files):
            raise ValueError(f"{site}: pool component arrays missing")
        if states.shape[0] < 640 or states.shape[1] != 15 or strata.shape != (states.shape[0], 15):
            raise ValueError(f"{site}: pool shape gate failed")
        if not np.all(np.isfinite(states)) or np.unique(states, axis=0).shape[0] != states.shape[0]:
            raise ValueError(f"{site}: pool finite/unique gate failed")
        if contract.get("status") != "pass" or contract.get("pool_sha256") != sha256(root / "candidate_pool.npz") or contract.get("repository_commit") != args.repository_commit or contract.get("source_manifest_sha256") != sha256(args.source_manifest) or contract.get("dependency_manifest_sha256") != sha256(args.dependency_manifest):
            raise ValueError(f"{site}: contract/hash gate failed")
        for name, digest in artifact_manifest.get("artifacts", {}).items():
            if sha256(root / name) != digest:
                raise ValueError(f"{site}: initialization artifact hash mismatch: {name}")
        if set(artifact_manifest.get("artifacts", {})) != {
            "candidate_pool.npz",
            "candidate_ledger.npz",
            "candidate_metadata.json",
            "diversity_diagnostics.json",
            "initialization_report.json",
            "search_contract.json",
        }:
            raise ValueError(f"{site}: incomplete initialization artifact manifest")
        rows.append({"site": site, "pool": str(root / "candidate_pool.npz"), "pool_sha256": sha256(root / "candidate_pool.npz"), "pool_size": int(states.shape[0]), "target_sha256": contract["target_identity"]["sha256"], "condition": contract["pool_gate"]["normalized_condition_number"]})
    args.output.write_text(json.dumps({"schema": "spinup-forcing-coupling-iter012-pool-validation-v1", "pools": rows, "status": "pass"}, indent=2) + "\n", encoding="utf-8")
    print("POOL_VALIDATION_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
