#!/usr/bin/env python3
"""Technical Iter012 preflight: imports, target identity, fixtures, and one finite target eval."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from model_ELM.coupling_pipeline import build_coupling_target

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results = []
    targets = []
    for site, resolution in (("ABBY", "daily"), ("JERC", "hourly")):
        target = build_coupling_target(
            cases=[f"{site}_ppe6_I20TRCNPRDCTCBC"],
            resolution=resolution,
            forcing_artifact=args.forcing_artifact,
            spinup_artifact=args.spinup_artifact,
            expected_physical_parameter_count=14,
        )
        targets.append(target)
        midpoint = 0.5 * (target["pmin"] + target["pmax"])
        logp = float(target["log_posterior"](midpoint))
        if not np.isfinite(logp):
            raise RuntimeError(f"{site}: midpoint physical target is not finite")
        results.append({"site": site, "resolution": resolution, "target_sha256": target["identity"]["sha256"], "parameter_names": target["parameter_names"], "pmin": target["pmin"].tolist(), "pmax": target["pmax"].tolist(), "midpoint_log_posterior": logp, "daily_map_sha256": None if site not in target["daily_maps"] else target["daily_maps"][site]["sha256"]})
    if results[0]["target_sha256"] == results[1]["target_sha256"]:
        raise RuntimeError("independent target identities unexpectedly match")
    # Re-evaluate the first target after building the second. This detects
    # accidental dependence on mutable module-global likelihood state.
    if not np.isfinite(
        targets[0]["log_posterior"](0.5 * (targets[0]["pmin"] + targets[0]["pmax"]))
    ):
        raise RuntimeError("interleaved target evaluation failed")
    abby_hourly = build_coupling_target(
        cases=["ABBY_ppe6_I20TRCNPRDCTCBC"],
        resolution="hourly",
        forcing_artifact=args.forcing_artifact,
        spinup_artifact=args.spinup_artifact,
        expected_physical_parameter_count=14,
    )
    joint = build_coupling_target(
        cases=[
            "JERC_ppe6_I20TRCNPRDCTCBC",
            "ABBY_ppe6_I20TRCNPRDCTCBC",
        ],
        resolution="hourly",
        forcing_artifact=args.forcing_artifact,
        spinup_artifact=args.spinup_artifact,
        expected_physical_parameter_count=14,
    )
    if joint["identity"]["cases"] != [
        "ABBY_ppe6_I20TRCNPRDCTCBC",
        "JERC_ppe6_I20TRCNPRDCTCBC",
    ]:
        raise RuntimeError("multi-site case membership was not canonicalized")
    shared_state = 0.5 * (joint["pmin"] + joint["pmax"])
    shared_state[-1] = 0.5 * min(
        abby_hourly["pmax"][-1], targets[1]["pmax"][-1]
    )
    abby_value = abby_hourly["log_posterior"](shared_state)
    jerc_value = targets[1]["log_posterior"](shared_state)
    joint_value = joint["log_posterior"](shared_state)
    if not np.isclose(joint_value, abby_value + jerc_value - 1.0, rtol=0, atol=1e-8):
        raise RuntimeError("multi-site target does not apply prior once and sum likelihoods")
    try:
        build_coupling_target(
            cases=["ABBY_ppe6_I20TRCNPRDCTCBC"],
            resolution="hourly",
            forcing_artifact=args.forcing_artifact,
            spinup_artifact=args.spinup_artifact,
            observation_paths={"EXTRA": args.forcing_artifact},
        )
    except ValueError:
        pass
    else:
        raise RuntimeError("extra observation configuration was not rejected")
    try:
        build_coupling_target(
            cases=["ABBY_ppe6_I20TRCNPRDCTCBC"],
            resolution="mixed",
            forcing_artifact=args.forcing_artifact,
            spinup_artifact=args.spinup_artifact,
        )
    except ValueError:
        pass
    else:
        raise RuntimeError("mixed likelihood resolution was not rejected")
    payload = {
        "schema": "spinup-forcing-coupling-general-pipeline-preflight-v2",
        "forcing_sha256": sha256(args.forcing_artifact),
        "spinup_sha256": sha256(args.spinup_artifact),
        "targets": results,
        "interleaved_target_state": "pass",
        "multi_site_fixture": {
            "cases": joint["identity"]["cases"],
            "prior_once_likelihood_sum": "pass",
            "extra_configuration_rejection": "pass",
            "mixed_resolution_rejection": "pass",
        },
        "status": "pass",
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("PREFLIGHT_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
