#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import numpy as np

PARAMS = ["k_l1","k_l2","k_l3","k_s1","k_s2","k_s3","k_s4","k_frag","rf_l1s1","rf_l2s2","rf_l3s3","rf_s1s2","rf_s2s3","rf_s3s4","sigma_SR"]

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main(manifest):
    m=json.loads(Path(manifest).read_text()); seen=[]
    if len(m["sources"]) != 6: raise RuntimeError("expected six sources")
    for item in m["sources"]:
        p=Path(item["raw_chain"]); meta=json.loads(p.with_name("raw_chain_metadata.json").read_text())
        for key in ("raw_chain", "backend", "metadata", "checkpoint", "selection"):
            if not Path(item[key]).is_file(): raise RuntimeError(f"missing locked input: {item[key]}")
        for key, hash_key in (("raw_chain","raw_sha256"),("backend","backend_sha256"),("metadata","metadata_sha256"),("checkpoint","checkpoint_sha256"),("selection","selection_sha256")):
            if sha256(Path(item[key])) != item[hash_key]: raise RuntimeError(f"hash mismatch {key}: {item[key]}")
        if meta["chain_shape"] != [8000,64,15] or meta["parameter_names"] != PARAMS: raise RuntimeError(f"metadata mismatch: {p}")
        if meta["seed"] != item["seed"] or meta["sites"] != [item["site"]] or meta["nwalkers"] != 64 or meta["nsteps"] != 8000: raise RuntimeError(f"site/seed/shape provenance mismatch: {p}")
        if meta["sampler_log_prob_convention"] != "physical_log_posterior + log_abs_det_dphysical_dsampler": raise RuntimeError(f"log-prob convention mismatch: {p}")
        if meta["transform"]["coordinate_system"] != "transformed" or meta["transform"]["parameter_names"] != PARAMS: raise RuntimeError(f"transform provenance mismatch: {p}")
        z=np.load(p,allow_pickle=False)
        if z["chain"].shape != (8000,64,15) or z["physical_log_prob"].shape != (8000,64): raise RuntimeError(f"shape mismatch: {p}")
        if not np.isfinite(z["chain"]).all() or not np.isfinite(z["physical_log_prob"]).all(): raise RuntimeError(f"nonfinite source: {p}")
        seen.append({"site":item["site"],"seed":item["seed"],"sha256":item["raw_sha256"]})
    print(json.dumps({"status":"PREFLIGHT_PASS","sources":seen,"environment":sys.prefix},sort_keys=True))

if __name__ == "__main__": main(sys.argv[1])
