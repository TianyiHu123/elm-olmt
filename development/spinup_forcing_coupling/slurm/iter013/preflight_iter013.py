#!/usr/bin/env python3
"""Iter013 preflight: lock hashes, TIM membership, target fingerprints, midpoint fixtures."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model_ELM.coupling_pipeline import build_coupling_target

PARAMS = [
    "k_l1",
    "k_l2",
    "k_l3",
    "k_s1",
    "k_s2",
    "k_s3",
    "k_s4",
    "k_frag",
    "rf_l1s1",
    "rf_l2s2",
    "rf_l3s3",
    "rf_s1s2",
    "rf_s2s3",
    "rf_s3s4",
    "sigma_SR",
]
SEEDS = (9009, 9010, 9011)
EXPECTED = {
    "ABBY": {
        "resolution": "daily",
        "case": "ABBY_ppe6_I20TRCNPRDCTCBC",
        "target_sha256": "bf9ade8b68bf7179cdb5c5712682dd1c343d510749efd7041cf0414ec4773bbd",
        "pool_sha256": "982350b16e17202acb4f2b82ab40c26e24c31dff159bb68dafbd6d8cc69a2d19",
        "ledger_sha256": "ec8b34ede77f3d9dd519c3b759bfa0d9daee018fe2a2ff2c7fc9e1c5c0bf036b",
        "tim_pool_sha256": "b19cbe90bdc746a4c2bf577fc2dc4877a32d89ee6bf77d76b6058c3f9085ad4a",
        "tim_bundle_sha256": {
            9009: "37f51011638e93ef1420d092d7f97bbd8e6bfa24342d205fcc09b9d5a9d8716a",
            9010: "49a32268e72a183414e2ba684717b1b7675c84f4ebf12b2ffd23df850c9f69cb",
            9011: "8c30198df99da7225f9c3235866c3020fef8d1e7a9349494149ddcfa11d14e0c",
        },
    },
    "JERC": {
        "resolution": "hourly",
        "case": "JERC_ppe6_I20TRCNPRDCTCBC",
        "target_sha256": "26e5caa07f25bea9bfc76d21348440918869603937f2cae5335d3ca0dcfeb196",
        "pool_sha256": "32d2ba5fa7e21f60a9df38fa8bcc6d6fe06a08bcbfa3ba6ce4fdcb62e5afaf96",
        "ledger_sha256": "25382a57acd91b2b03db5a94312ba932a2c2c9501a392ed84e2a3e8633dedc3d",
        "tim_pool_sha256": "fcd909188789ab97b222773fc21f2a60e401a730f16e95edeee1e7aac49140e8",
        "tim_bundle_sha256": {
            9009: "394902f2c2378a6793196f226c7cf136872a2631012f559ba857c989c47bd8fe",
            9010: "86fa8a3a732be080454bb451ab025cf604c1c8c0a98ffbdce26ed2b46d3870d6",
            9011: "fa19ed47a533f540e88992c1eac6346f46478192ed85b1132222ac08599f063e",
        },
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--forcing-artifact", required=True, type=Path)
    parser.add_argument("--spinup-artifact", required=True, type=Path)
    parser.add_argument("--dependency-manifest", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    for site in ("abby", "jerc"):
        parser.add_argument(f"--{site}-pool", required=True, type=Path)
        parser.add_argument(f"--{site}-ledger", required=True, type=Path)
        parser.add_argument(f"--{site}-tim-pool", required=True, type=Path)
        for seed in SEEDS:
            parser.add_argument(f"--{site}-selection-{seed}", required=True, type=Path)
            parser.add_argument(f"--{site}-tim-bundle-{seed}", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    require(args.source_manifest.is_file(), "missing source manifest")
    require(args.dependency_manifest.is_file(), "missing dependency manifest")

    site_results = []
    for site, cfg in EXPECTED.items():
        site_l = site.lower()
        pool = Path(getattr(args, f"{site_l}_pool"))
        ledger = Path(getattr(args, f"{site_l}_ledger"))
        tim_pool = Path(getattr(args, f"{site_l}_tim_pool"))
        require(sha256(pool) == cfg["pool_sha256"], f"{site} pool hash")
        require(sha256(ledger) == cfg["ledger_sha256"], f"{site} ledger hash")
        require(sha256(tim_pool) == cfg["tim_pool_sha256"], f"{site} TIM pool hash")
        tim_states = np.asarray(
            np.load(tim_pool, allow_pickle=False)["physical_chain"], dtype=float
        )
        tim_keys = {np.asarray(row, dtype=np.float64).tobytes() for row in tim_states}
        for seed in SEEDS:
            bundle = Path(getattr(args, f"{site_l}_tim_bundle_{seed}"))
            require(
                sha256(bundle) == cfg["tim_bundle_sha256"][seed],
                f"{site} TIM bundle {seed} hash",
            )
            walkers = np.asarray(
                np.load(bundle, allow_pickle=False)["initial_state"], dtype=float
            )
            require(walkers.shape == (64, 15), f"{site} TIM bundle shape")
            missing = [
                i
                for i, key in enumerate(
                    np.asarray(row, dtype=np.float64).tobytes() for row in walkers
                )
                if key not in tim_keys
            ]
            require(not missing, f"{site} TIM seed {seed} not in pool")
            selection = Path(getattr(args, f"{site_l}_selection_{seed}"))
            payload = json.loads(selection.read_text(encoding="utf-8"))
            selected = np.asarray(payload["selected_physical_states"], dtype=float)
            require(selected.shape == (64, 15), f"{site} selection shape")
            require(payload.get("site") == site, f"{site} selection site field")
            require(int(payload.get("production_seed")) == seed, f"{site} selection seed")

        target = build_coupling_target(
            cases=[cfg["case"]],
            resolution=cfg["resolution"],
            forcing_artifact=args.forcing_artifact,
            spinup_artifact=args.spinup_artifact,
            expected_physical_parameter_count=14,
        )
        require(target["parameter_names"] == PARAMS, f"{site} parameter names")
        require(
            target["identity"]["sha256"] == cfg["target_sha256"],
            f"{site} target fingerprint",
        )
        midpoint = 0.5 * (target["pmin"] + target["pmax"])
        logp = float(target["log_posterior"](midpoint))
        require(np.isfinite(logp), f"{site} midpoint logp")
        site_results.append(
            {
                "site": site,
                "resolution": cfg["resolution"],
                "target_sha256": target["identity"]["sha256"],
                "midpoint_log_posterior": logp,
                "pool_sha256": cfg["pool_sha256"],
                "ledger_sha256": cfg["ledger_sha256"],
                "tim_pool_sha256": cfg["tim_pool_sha256"],
            }
        )

    payload = {
        "schema": "spinup-forcing-coupling-iter013-preflight-v1",
        "sites": site_results,
        "source_manifest_sha256": sha256(args.source_manifest),
        "dependency_manifest_sha256": sha256(args.dependency_manifest),
        "status": "pass",
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("PREFLIGHT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
