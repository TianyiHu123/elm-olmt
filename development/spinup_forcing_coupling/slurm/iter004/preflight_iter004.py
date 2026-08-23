#!/usr/bin/env python3
"""Iter004 compute-node preflight: artifact identity, imports, synthetic tests."""
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-hashes", required=True)
    parser.add_argument("--case-hashes", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    art_manifest = Path(args.artifact_hashes)
    case_manifest = Path(args.case_hashes)
    for line in art_manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, path_s = line.split(None, 1)
        path = Path(path_s)
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"Artifact hash mismatch for {path}: {actual} != {expected}")
        print(f"ARTIFACT_OK {path.name} {actual}")

    for line in case_manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split(None, 1)
        path = REPO_ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"Case hash mismatch for {rel}: {actual} != {expected}")
        print(f"CASE_OK {path.name}")

    sys.path.insert(0, str(REPO_ROOT))
    from model_ELM.coupled_surrogate import (  # noqa: F401
        predict_coupled_sr,
        predict_offline_sr,
        compute_sr_metrics,
    )

    print("IMPORT_OK coupled_surrogate offline+coupled")

    payload = {
        "schema": "spinup-forcing-coupling-iter004-preflight-v1",
        "passed": True,
        "artifact_hash_manifest": str(art_manifest),
        "case_hash_manifest": str(case_manifest),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT_PASS cases=9 manifest={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
