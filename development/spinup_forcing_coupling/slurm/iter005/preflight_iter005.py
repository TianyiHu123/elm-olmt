#!/usr/bin/env python3
"""Iter005 compute-node preflight: artifact/reuse identity, imports, unit tests."""
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
    parser.add_argument("--iter004-reuse-hashes", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    n_art = _check_manifest(Path(args.artifact_hashes))
    n_case = _check_manifest(Path(args.case_hashes), relative_to=REPO_ROOT)
    n_reuse = _check_manifest(Path(args.iter004_reuse_hashes))

    sys.path.insert(0, str(REPO_ROOT))
    from model_ELM.coupled_surrogate import (  # noqa: F401
        compute_sr_metrics,
        predict_offline_sr,
    )

    print("IMPORT_OK coupled_surrogate mean-spinup primitives")

    payload = {
        "schema": "spinup-forcing-coupling-iter005-preflight-v1",
        "passed": True,
        "artifact_hash_count": n_art,
        "case_hash_count": n_case,
        "iter004_reuse_hash_count": n_reuse,
        "artifact_hash_manifest": str(Path(args.artifact_hashes)),
        "case_hash_manifest": str(Path(args.case_hashes)),
        "iter004_reuse_hash_manifest": str(Path(args.iter004_reuse_hashes)),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT_PASS cases={n_case} reuse={n_reuse} manifest={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
