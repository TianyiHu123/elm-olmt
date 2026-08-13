#!/usr/bin/env python3
"""Conditional branch guard for Iter010.

The topology contract permits new coupled evaluations only after a site is classified
two_basin_supported. This script materializes a validated skip when no site qualifies;
it refuses to silently substitute a constructed or median parameter vector.
"""
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--decision",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    d=json.loads(a.decision.read_text()); a.output.mkdir(parents=True,exist_ok=True)
    if d["prediction_required"]:
        raise SystemExit("PREDICTION_REQUIRED: approved conditional coupled-evaluation implementation must be reviewed before execution")
    result={"schema":"spinup-forcing-coupling-iter010-prediction-v1","status":"skipped","reason":"neither site classified two_basin_supported","evaluations":0}
    (a.output/"conditional_prediction.json").write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps({"status":"PREDICTION_SKIPPED","evaluations":0},sort_keys=True))
if __name__ == "__main__": main()
