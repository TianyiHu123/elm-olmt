#!/usr/bin/env python
"""Strict coupled spinup→forcing inference CLI (MCMC-reusable primitive)."""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any, List, Optional

import numpy as np

from model_ELM.coupled_surrogate import predict_coupled_sr
from model_ELM.spinup_surrogate_artifact import parse_physical_parameter_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workdir", default=".")
    parser.add_argument("--case", required=True)
    parser.add_argument("--spinup-case", default=None)
    parser.add_argument("--spinup-artifact", required=True)
    parser.add_argument("--forcing-artifact", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--members", help="Comma-separated one-based existing case member IDs")
    mode.add_argument(
        "--parameters",
        help="Comma-separated positional values in spinup artifact physical-parameter order",
    )
    mode.add_argument(
        "--parameters-json",
        help="Path to JSON physical-name object, positional list, or list-of-lists",
    )
    parser.add_argument(
        "--surface-member",
        type=int,
        default=None,
        help="Surface member for new parameters; default uses case-member mean",
    )
    parser.add_argument("--output-json", default=None)
    parser.add_argument(
        "--save-timeseries",
        default=None,
        help="Optional NetCDF path for SR timeseries (and spinup scalars)",
    )
    return parser


def _load_case(workdir: Path, name: str) -> Any:
    import model_ELM  # noqa: F401 - register ELMcase for trusted case pickle

    path = workdir / "pklfiles" / f"{name}.pkl"
    if not path.is_file():
        raise FileNotFoundError(f"Case pickle not found: {path}")
    with path.open("rb") as fp:
        return pickle.load(fp)


def _load_parameter_json_file(raw: str) -> Any:
    value = str(raw).strip()
    if not value:
        raise ValueError("--parameters-json requires a JSON file path")
    if value.startswith(("{", "[")):
        raise ValueError("--parameters-json accepts a JSON file path, not inline JSON")
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Parameter JSON file not found: {path}")
    return parse_physical_parameter_json(path.read_text(encoding="utf-8"))


def _write_timeseries_netcdf(
    path: Path,
    records: List[dict],
    time_axis: Any,
) -> None:
    import netCDF4

    path.parent.mkdir(parents=True, exist_ok=True)
    n_members = len(records)
    ntime = int(records[0]["ntime"])
    with netCDF4.Dataset(path, "w") as ds:
        ds.createDimension("member", n_members)
        ds.createDimension("time", ntime)
        members = ds.createVariable("member", "i4", ("member",))
        sr = ds.createVariable("SR_coupled", "f8", ("member", "time"), zlib=True)
        totsomc = ds.createVariable("TOTSOMC_pred", "f8", ("member",))
        totsomn = ds.createVariable("TOTSOMN_pred", "f8", ("member",))
        for i, rec in enumerate(records):
            members[i] = int(rec["member"]) if rec["member"] is not None else i + 1
            sr[i, :] = np.asarray(rec["SR"], dtype=np.float64)
            totsomc[i] = float(rec["TOTSOMC"])
            totsomn[i] = float(rec["TOTSOMN"])
        ds.setncattr("ntime", ntime)
        ds.setncattr("forcing_time_source", str(records[0].get("forcing_time_source", "")))
        # time axis may be object/cftime; store as string when needed
        try:
            tax = np.asarray(time_axis).reshape(-1)
            if tax.size == ntime and np.issubdtype(tax.dtype, np.number):
                tvar = ds.createVariable("time", "f8", ("time",))
                tvar[:] = tax.astype(np.float64)
        except Exception:
            pass


def main() -> int:
    args = _parser().parse_args()
    workdir = Path(args.workdir).resolve()
    case = _load_case(workdir, args.case)
    spinup_case = _load_case(workdir, args.spinup_case or args.case)

    records = []
    if args.members is not None:
        members = [int(v.strip()) for v in args.members.split(",") if v.strip()]
        if not members or len(set(members)) != len(members):
            raise ValueError("--members must contain unique one-based member IDs")
        for member in members:
            pred = predict_coupled_sr(
                case,
                spinup_artifact=args.spinup_artifact,
                forcing_artifact=args.forcing_artifact,
                member=member,
                spinup_case=spinup_case,
                surface_member=args.surface_member,
            )
            records.append(pred)
        mode = "existing_members"
    else:
        if args.parameters is not None:
            supplied: Any = [
                float(v.strip()) for v in args.parameters.split(",") if v.strip()
            ]
        else:
            supplied = _load_parameter_json_file(args.parameters_json)
        # Support single vector or batch rows
        arr = np.asarray(supplied, dtype=object)
        if isinstance(supplied, dict):
            rows = [supplied]
        elif isinstance(supplied, (list, tuple)) and supplied and isinstance(supplied[0], (list, tuple)):
            rows = list(supplied)
        else:
            rows = [supplied]
        for row in rows:
            pred = predict_coupled_sr(
                case,
                spinup_artifact=args.spinup_artifact,
                forcing_artifact=args.forcing_artifact,
                parameters=row,
                spinup_case=spinup_case,
                surface_member=args.surface_member,
            )
            records.append(pred)
        mode = "new_parameters"

    serializable = []
    for rec in records:
        serializable.append(
            {
                "member": rec["member"],
                "parameters_physical_order": np.asarray(rec["parameters"]).tolist(),
                "TOTSOMC": rec["TOTSOMC"],
                "TOTSOMN": rec["TOTSOMN"],
                "ntime": rec["ntime"],
                "SR_mean": float(np.mean(rec["SR"])),
                "SR_std": float(np.std(rec["SR"])),
                "spinup_warnings": rec["spinup_warnings"],
                "spinup_variant": rec.get("spinup_variant"),
            }
        )

    if args.save_timeseries:
        _write_timeseries_netcdf(
            Path(args.save_timeseries).resolve(),
            records,
            records[0]["time"],
        )

    payload = {
        "case": args.case,
        "spinup_case": args.spinup_case or args.case,
        "mode": mode,
        "spinup_artifact": args.spinup_artifact,
        "forcing_artifact": args.forcing_artifact,
        "predictions": serializable,
    }
    text = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    if args.output_json:
        out = Path(args.output_json).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
