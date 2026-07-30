#!/usr/bin/env python
"""Collect no-fitting evidence for the Iter012 target-metadata stop condition."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping

import numpy as np
from netCDF4 import Dataset

REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
OUTPUT_ROOT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output/"
    "spinup_surrogate_iter012_metadata_diagnostic"
)
OUTPUT_JSON = OUTPUT_ROOT / "target_metadata_diagnostic.json"
NEON_PPE_ROOT = Path(
    "/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/NEON_ppe"
)
CASE_SITES = ["ABBY", "JERC", "OSBS", "SOAP", "RMNP", "TALL", "TEAK", "WREF", "YELL"]
TARGET_COMPONENTS = {
    "TOTSOMC": ["totsomc"],
    "TOTSOMN": [
        "litr1n",
        "litr2n",
        "litr3n",
        "cwdn",
        "soil1n",
        "soil2n",
        "soil3n",
        "soil4n",
    ],
}
HISTORY_TARGETS = ["TOTSOMC", "TOTSOMN"]
MAX_HISTORY_FILES_PER_CASE = 3

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"type": "bytes", "repr": repr(value)}
    if isinstance(value, np.ndarray):
        return [_jsonable(item) for item in value.tolist()]
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, float):
        return value if math.isfinite(value) else {"type": "float", "repr": repr(value)}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return {"type": type(value).__name__, "repr": repr(value)}


def _attributes(obj: Any) -> Dict[str, Any]:
    return {name: _jsonable(obj.getncattr(name)) for name in obj.ncattrs()}


def _variable_record(var: Any) -> Dict[str, Any]:
    raw = np.ma.asarray(var[:])
    values = np.asarray(raw.filled(np.nan), dtype=np.float64)
    finite = values[np.isfinite(values)]
    return {
        "datatype": str(var.dtype),
        "dimensions": list(var.dimensions),
        "shape": list(var.shape),
        "attributes": _attributes(var),
        "masked_count": int(np.ma.count_masked(raw)),
        "finite_count": int(finite.size),
        "nan_count": int(np.isnan(values).sum()),
        "finite_min": float(np.min(finite)) if finite.size else None,
        "finite_max": float(np.max(finite)) if finite.size else None,
        "numpy_nansum": float(np.nansum(values)),
    }


def _candidate_history_files(dependcase: str, restart: Path) -> Dict[str, Any]:
    roots = [restart.parent]
    roots.extend([NEON_PPE_ROOT / dependcase, NEON_PPE_ROOT / "UQ" / dependcase])
    candidates: Dict[str, Path] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for pattern in ("*.elm.h*.nc", "*.clm2.h*.nc"):
            for path in root.glob(pattern):
                candidates[str(path)] = path
    ordered = [candidates[key] for key in sorted(candidates)]
    selected = ordered[:MAX_HISTORY_FILES_PER_CASE]
    return {
        "candidate_count": len(ordered),
        "selected": selected,
        "omitted_count": max(0, len(ordered) - len(selected)),
        "selection_rule": (
            f"first {MAX_HISTORY_FILES_PER_CASE} lexicographically sorted direct history files"
        ),
    }


def _history_evidence(selection: Mapping[str, Any]) -> Dict[str, Any]:
    searched = []
    matches = []
    for path in selection["selected"]:
        searched.append(str(path))
        with Dataset(str(path), "r") as nc:
            found = [name for name in HISTORY_TARGETS if name in nc.variables]
            if found:
                matches.append(
                    {
                        "path": str(path),
                        "sha256": _sha256(path),
                        "global_attributes": _attributes(nc),
                        "targets": {
                            name: _variable_record(nc.variables[name]) for name in found
                        },
                    }
                )
    return {
        "candidate_count": int(selection["candidate_count"]),
        "searched": searched,
        "omitted_count": int(selection["omitted_count"]),
        "selection_rule": str(selection["selection_rule"]),
        "matches": matches,
    }


def main() -> None:
    case_records = []
    for site in CASE_SITES:
        case_name = f"{site}_ppe6_I20TRCNPRDCTCBC"
        dependcase = f"{site}_ppe6_I1850CNPRDCTCBC"
        restart = (
            NEON_PPE_ROOT
            / "UQ"
            / dependcase
            / "g00001"
            / f"{dependcase}.elm.r.0201-01-01-00000.nc"
        )
        with Dataset(str(restart), "r") as nc:
            targets = {}
            for target, components in TARGET_COMPONENTS.items():
                targets[target] = {
                    component: _variable_record(nc.variables[component])
                    for component in components
                }
            restart_record = {
                "path": str(restart),
                "sha256": _sha256(restart),
                "file_format": str(nc.file_format),
                "global_attributes": _attributes(nc),
                "targets": targets,
            }
        case_records.append(
            {
                "case": case_name,
                "dependcase": dependcase,
                "path_derivation": (
                    "locked NEON_PPE_ROOT/UQ/<SITE>_ppe6_I1850CNPRDCTCBC/g00001/"
                    "<SITE>_ppe6_I1850CNPRDCTCBC.elm.r.0201-01-01-00000.nc"
                ),
                "restart": restart_record,
                "history_evidence": _history_evidence(
                    _candidate_history_files(dependcase, restart)
                ),
            }
        )

    missing_or_empty = []
    unit_values: Dict[str, Dict[str, List[str]]] = {}
    for case_record in case_records:
        case_name = case_record["case"]
        for target, component_records in case_record["restart"]["targets"].items():
            for component, record in component_records.items():
                attrs = record["attributes"]
                units = str(attrs.get("units", "")).strip()
                long_name = str(attrs.get("long_name", "")).strip()
                unit_values.setdefault(target, {}).setdefault(component, []).append(units)
                if not units or not long_name:
                    missing_or_empty.append(
                        {
                            "case": case_name,
                            "target": target,
                            "component": component,
                            "units": units,
                            "long_name": long_name,
                        }
                    )

    payload = {
        "diagnostic": "iter012-target-metadata-no-fitting",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "training_or_fitting_performed": False,
        "repository_root": str(REPO_ROOT),
        "mapping_source": {
            "path": str(REPO_ROOT / "model_ELM/surrogate_NN_Forcing.py"),
            "sha256": _sha256(REPO_ROOT / "model_ELM/surrogate_NN_Forcing.py"),
            "target_components": TARGET_COMPONENTS,
            "scalar_implementation": (
                "numpy.nansum(component[:]) for TOTSOMC; sum of numpy.nansum(component[:]) "
                "across the eight listed TOTSOMN components"
            ),
        },
        "case_records": case_records,
        "restart_unit_values": unit_values,
        "restart_missing_or_empty_units_or_long_name": missing_or_empty,
        "restart_metadata_gate_resolved": len(missing_or_empty) == 0,
        "resolution_note": (
            "This diagnostic records evidence only. A false resolution flag requires "
            "authoritative supplemental definitions before any release-audit correction."
        ),
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT_JSON.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(OUTPUT_JSON)
    print(
        "ITER012_TARGET_METADATA_DIAGNOSTIC_OK "
        f"cases={len(case_records)} components={sum(len(v) for v in TARGET_COMPONENTS.values())} "
        f"missing_or_empty={len(missing_or_empty)} output={OUTPUT_JSON}"
    )


if __name__ == "__main__":
    main()
