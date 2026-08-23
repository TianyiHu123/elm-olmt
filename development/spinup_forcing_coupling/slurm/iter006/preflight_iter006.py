#!/usr/bin/env python3
"""Iter006 compute-node preflight: hashes, imports, unit tests, fail-closed negatives."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_manifest(manifest: Path, *, relative_to: Path | None = None) -> int:
    n = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, path_s = line.split(None, 1)
        path = Path(path_s) if relative_to is None else relative_to / path_s
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"Hash mismatch for {path}: {actual} != {expected}")
        print(f"HASH_OK {path.name} {actual}")
        n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-hashes", required=True)
    parser.add_argument("--case-hashes", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    n_art = _check_manifest(Path(args.artifact_hashes))
    n_case = _check_manifest(Path(args.case_hashes), relative_to=REPO_ROOT)

    sys.path.insert(0, str(REPO_ROOT))
    from model_ELM.coupled_surrogate import predict_coupled_sr, predict_offline_sr  # noqa: F401
    from model_ELM.mcmc_spinup_modes import (  # noqa: F401
        DEFAULT_COUPLED_VARIANT,
        resolve_coupled_spinup_artifact,
        resolve_spinup_mode,
    )

    print("IMPORT_OK mcmc_spinup_modes + coupled primitives")
    assert DEFAULT_COUPLED_VARIANT == "drop21_corr080"
    assert resolve_spinup_mode(spinup_mode=None, spinup_member=None) == "mean_spinup"
    drop21 = resolve_coupled_spinup_artifact(variant="drop21_corr080")
    drop32 = resolve_coupled_spinup_artifact(variant="drop32")
    print(f"COUPLED_PATH_OK drop21={drop21}")
    print(f"COUPLED_PATH_OK drop32={drop32}")

    # Negative gate: missing artifact must fail closed.
    try:
        resolve_coupled_spinup_artifact(
            spinup_artifact="/xdisk/chopinsong/tianyihu/elm-olmt/does_not_exist_iter006.pkl"
        )
        raise AssertionError("missing spinup artifact did not fail closed")
    except FileNotFoundError as exc:
        print(f"NEGATIVE_GATE_OK missing_spinup_artifact: {exc}")

    payload = {
        "schema": "spinup-forcing-coupling-iter006-preflight-v1",
        "passed": True,
        "artifact_hash_count": n_art,
        "case_hash_count": n_case,
        "default_coupled_variant": DEFAULT_COUPLED_VARIANT,
        "drop21_corr080_path": str(drop21),
        "drop32_path": str(drop32),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT_PASS cases={n_case} artifacts={n_art} manifest={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
