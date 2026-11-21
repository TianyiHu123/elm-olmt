#!/usr/bin/env python
"""Independently recompute the Iter003 evidence contract and selection."""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from statistics import median, pstdev

def need(value, message):
    if not value: raise ValueError(message)
def close(a,b): return math.isclose(float(a),float(b),rel_tol=1e-12,abs_tol=1e-12)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def lookup(rows, split_id, site, target, field):
    values=[float(row[field]) for row in rows if int(row["split_id"])==split_id and row["partition"]=="validation" and row["site"]==site and row["target"]==target and row["scale"]=="log"]
    need(len(values)==1 and math.isfinite(values[0]),f"metric lookup {split_id} {site} {target} {field}"); return values[0]
def summary(result):
    rows=result["metrics"]
    scores=[sum(lookup(rows,s,"pooled",t,"r2") for t in ("TOTSOMC","TOTSOMN"))/2 for s in range(20)]
    rmses=[sum(lookup(rows,s,"pooled",t,"rmse") for t in ("TOTSOMC","TOTSOMN"))/2 for s in range(20)]
    sites={f"{site}:{target}":median(lookup(rows,s,site,target,"r2") for s in range(20)) for site in ("ABBY","JERC") for target in ("TOTSOMC","TOTSOMN")}
    ordered=sorted(scores)
    return {"scores":scores,"median":median(scores),"mean":sum(scores)/20,"std":pstdev(scores),"iqr":median(ordered[10:])-median(ordered[:10]),"worst":min(scores),"rmse":median(rmses),"sites":sites}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--screen-root",type=Path,required=True); p.add_argument("--aggregate-directory",type=Path,required=True); p.add_argument("--output-directory",type=Path,required=True); p.add_argument("--candidate-manifest",type=Path,required=True); p.add_argument("--split-manifest",type=Path,required=True); p.add_argument("--global-split",type=Path,required=True); p.add_argument("--candidate-sha256",required=True); p.add_argument("--split-sha256",required=True); a=p.parse_args()
    need(sha(a.candidate_manifest)==a.candidate_sha256,"candidate hash"); need(sha(a.split_manifest)==a.split_sha256,"split hash")
    candidates=json.loads(a.candidate_manifest.read_text()); splits=json.loads(a.split_manifest.read_text()); global_split=json.loads(a.global_split.read_text()); aggregate=json.loads((a.aggregate_directory/"aggregate.json").read_text())
    fixed=set(global_split["fixed_test_member_ids_ranked"]); need(len(splits["splits"])==20,"split count")
    for split in splits["splits"]:
        train=set(split["train_member_ids"]); validation=set(split["validation_member_ids"])
        need(len(train)==655 and len(validation)==164 and not train&validation and not (train|validation)&fixed,"split/fixed-test contract")
    need(not list(a.screen_root.rglob("*.pkl")) and not list(a.screen_root.rglob("*.nc")),"prohibited outputs")
    raw={}; identities=set(); baseline=[]
    for cid in range(96):
        files=sorted(a.screen_root.glob(f"attempt_*/candidate_{cid:03d}/result.json")); need(files,f"missing {cid}")
        result=json.loads(files[-1].read_text()); need(result["status"]=="complete" and result["candidate_id"]==cid,"identity"); need(result["split_count"]==20 and len(result["metrics"])==480 and len(result["convergence"])==40,"coverage")
        source=result["source_identity"]; need(source["candidate_manifest_sha256"]==a.candidate_sha256 and source["split_manifest_sha256"]==a.split_sha256,"provenance")
        need(result["config"]==candidates["candidates"][cid]["config"] and result["config_sha256"]==candidates["candidates"][cid]["config_sha256"],"candidate config")
        strata={(r["split_id"],r["partition"],r["site"],r["target"],r["scale"]) for r in result["metrics"]}; need(len(strata)==480,"strata")
        identities.add(result["config_sha256"]); raw[cid]=summary(result)
        if result["is_iter002_baseline"]: baseline.append(cid)
    need(len(identities)==96 and baseline==[15],"uniqueness/baseline")
    base=raw[15]; observed={int(row["candidate_id"]):row for row in aggregate["ranking"]}; need(len(observed)==96,"ranking")
    eligible=[]
    for cid,item in raw.items():
        row=observed[cid]; deltas={key:item["sites"][key]-base["sites"][key] for key in base["sites"]}; is_eligible=min(deltas.values())>=-0.02
        for key,value in (("median_mean_pooled_log_r2",item["median"]),("mean_mean_pooled_log_r2",item["mean"]),("std_mean_pooled_log_r2",item["std"]),("iqr_mean_pooled_log_r2",item["iqr"]),("worst_mean_pooled_log_r2",item["worst"]),("median_mean_pooled_log_rmse",item["rmse"])): need(close(row[key],value),f"summary {cid} {key}")
        need(bool(row["eligible"])==is_eligible,"eligibility"); need(all(close(row["site_target_r2_delta_from_baseline"][k],v) for k,v in deltas.items()),"baseline deltas")
        if is_eligible: eligible.append(cid)
    best=max(raw[cid]["median"] for cid in eligible); near=[cid for cid in eligible if best-raw[cid]["median"]<=0.005]; near.sort(key=lambda cid:(raw[cid]["rmse"],raw[cid]["std"],cid)); need(aggregate["selected_candidate_id"]==near[0],"selection")
    out=a.output_directory.resolve(); out.mkdir(parents=True,exist_ok=False); report={"schema":"three-stage-spinup-iter003-validation-v1","result":"pass","candidate_count":96,"selected_candidate_id":near[0],"fixed_test_access":False,"model_artifacts_created":False}; (out/"validation_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); print(f"ITER003_VALIDATE_OK selected={near[0]}"); return 0
if __name__=="__main__": raise SystemExit(main())
