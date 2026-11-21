#!/usr/bin/env python
"""Deterministic ordinal ranking for Iter009 screen and final evidence."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any, Mapping, Sequence
import numpy as np
REPO_ROOT = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))
from development.three_stage_surrogate.slurm.iter009.iter009_common import FINALIST_SPLITS, SCREEN_SPLITS, candidate_by_id, leaf_directory, load_candidates, read_csv, read_json, write_csv
from model_ELM.three_stage_data import require, sha256_file
from model_ELM.three_stage_sr import FEATURE_COUNT, write_json

def _resolve_leaf(roots: Sequence[Path], cid: int, sid: int) -> Path:
    matches=[]
    for root in roots:
        leaf=leaf_directory(root,cid,sid); report=leaf/"leaf_report.json"
        if report.is_file() and read_json(report).get("result")=="pass": matches.append(leaf)
    require(len(matches)==1,f"eligible leaf count mismatch candidate={cid} split={sid}"); return matches[0]

def _rows(roots: Sequence[Path], cid: int, split_ids: Sequence[int]) -> list[dict[str,Any]]:
    result=[]
    for sid in split_ids:
        leaf=_resolve_leaf(roots,cid,sid); report=read_json(leaf/"leaf_report.json")
        require(report["fixed_test_access"] is False and report["release_created"] is False,"leaf boundary mismatch")
        require(report.get("successful_scaled_scratch_removed") is True,"scratch cleanup missing")
        require(sha256_file(leaf/"pooled_metrics.csv")==report["metrics_sha256"],"metric hash mismatch")
        for row in read_csv(leaf/"pooled_metrics.csv"):
            if row["partition"]=="validation":
                result.append({"candidate_id":cid,"split_id":sid,"resolution":row["resolution"],"r2":float(row["r2"]),"rmse":float(row["rmse"]),"bias":float(row["bias"]),"warning_count":int(row["convergence_warning_count"]),"coverage_fraction":float(row["coverage_fraction"])})
    require(len(result)==len(split_ids)*2,"validation metric coverage mismatch"); return result

def _parameter_count(candidate: Mapping[str,Any]) -> int:
    sizes=[FEATURE_COUNT,*[int(x) for x in candidate["hidden_layer_sizes"]],1]
    return sum((a+1)*b for a,b in zip(sizes[:-1],sizes[1:]))

def _raw_stats(candidate: Mapping[str,Any], rows: Sequence[Mapping[str,Any]]) -> dict[str,Any]:
    split_ids=sorted({int(r["split_id"]) for r in rows}); components={}; split_raw={sid:[] for sid in split_ids}
    for resolution in ("hourly","daily"):
        selected=[r for r in rows if r["resolution"]==resolution]; require(len(selected)==len(split_ids),"resolution coverage mismatch")
        components[f"{resolution}_r2_q10"]=float(np.quantile([r["r2"] for r in selected],.10,method="linear"))
        components[f"{resolution}_rmse_q90"]=float(np.quantile([r["rmse"] for r in selected],.90,method="linear"))
        components[f"{resolution}_median_absolute_bias"]=float(np.median(np.abs([r["bias"] for r in selected])))
        for r in selected: split_raw[int(r["split_id"])].extend((float(r["r2"]),-float(r["rmse"]),-abs(float(r["bias"]))))
    eligible=all(r["warning_count"]==0 and r["coverage_fraction"]==1.0 for r in rows)
    return {"candidate_id":int(candidate["candidate_id"]),"eligible":bool(eligible),"components":components,"split_raw":split_raw,"parameter_count":_parameter_count(candidate)}

def _ordinal_scores(stats: list[dict[str,Any]]) -> list[dict[str,Any]]:
    eligible=[r for r in stats if r["eligible"]]; require(eligible,"no eligible candidates")
    keys=("hourly_r2_q10","hourly_rmse_q90","hourly_median_absolute_bias","daily_r2_q10","daily_rmse_q90","daily_median_absolute_bias"); maximize={"hourly_r2_q10","daily_r2_q10"}; n=len(eligible)
    scores={r["candidate_id"]:[] for r in eligible}
    for key in keys:
        ordered=np.asarray([r["components"][key] if key in maximize else -r["components"][key] for r in eligible])
        for row,value in zip(eligible,ordered):
            lower=int(np.sum(ordered<value)); equal=int(np.sum(ordered==value)); avg=lower+(equal-1)/2
            scores[row["candidate_id"]].append(1.0 if n==1 else float(avg/(n-1)))
    for row in stats:
        if not row["eligible"]: row.update(worst_normalized_score=-1.0,mean_normalized_score=-1.0,composite_variability=float("inf")); continue
        vals=scores[row["candidate_id"]]; split_composites=[float(np.mean(v)) for v in row["split_raw"].values()]
        row.update(worst_normalized_score=float(min(vals)),mean_normalized_score=float(np.mean(vals)),composite_variability=float(np.std(split_composites)))
    return sorted(stats,key=lambda r:(-int(r["eligible"]),-r["worst_normalized_score"],-r["mean_normalized_score"],r["composite_variability"],r["parameter_count"],r["candidate_id"]))

def screen_selection(config: Mapping[str,Any], roots: Sequence[Path]) -> dict[str,Any]:
    candidates=load_candidates(config); stats=[_raw_stats(candidate_by_id(candidates,cid),_rows(roots,cid,SCREEN_SPLITS)) for cid in range(24)]; ranked=_ordinal_scores(stats)
    require(next(r for r in ranked if r["candidate_id"]==0)["eligible"],"mandatory candidate 0 ineligible")
    noncontrol=[r["candidate_id"] for r in ranked if r["eligible"] and r["candidate_id"]!=0]; require(len(noncontrol)>=5,"fewer than five eligible non-control candidates")
    finalists=[0,*noncontrol[:5]]; fingerprint=[]
    for cid in range(24):
        for sid in SCREEN_SPLITS:
            leaf=_resolve_leaf(roots,cid,sid); fingerprint.append(f"{cid}:{sid}:{sha256_file(leaf/'leaf_report.json')}")
    return {"schema":"three-stage-sr-iter009-screen-selection-v1","result":"pass","screen_fingerprint_sha256":hashlib.sha256("\n".join(fingerprint).encode()).hexdigest(),"finalist_candidate_ids":finalists,"finalist_split_ids":list(FINALIST_SPLITS),"ranking":ranked}

def final_selection(config: Mapping[str,Any], screen_roots: Sequence[Path], finalist_roots: Sequence[Path], output: Path) -> dict[str,Any]:
    require(not output.exists(),f"final output exists: {output}"); output.mkdir(parents=True); screen=screen_selection(config,screen_roots); candidates=load_candidates(config); all_roots=[*screen_roots,*finalist_roots]; stats=[]; metric_rows=[]
    for cid in screen["finalist_candidate_ids"]:
        rows=_rows(all_roots,cid,tuple(range(20))); stats.append(_raw_stats(candidate_by_id(candidates,cid),rows)); metric_rows.extend(rows)
    ranked=_ordinal_scores(stats); eligible=[r for r in ranked if r["eligible"]]; require(eligible,"no eligible finalist")
    write_csv(output/"final_metric_distribution.csv",metric_rows); flat=[]
    for rank,row in enumerate(ranked,1): flat.append({"rank":rank,"candidate_id":row["candidate_id"],"eligible":row["eligible"],"worst_normalized_score":row["worst_normalized_score"],"mean_normalized_score":row["mean_normalized_score"],"composite_variability":row["composite_variability"],"parameter_count":row["parameter_count"],**row["components"]})
    write_csv(output/"final_ranking.csv",flat)
    report={"schema":"three-stage-sr-iter009-final-selection-v1","result":"pass","decision":"sr_configuration_selected","best_candidate_id":eligible[0]["candidate_id"],"finalist_candidate_ids":screen["finalist_candidate_ids"],"screen_fingerprint_sha256":screen["screen_fingerprint_sha256"],"metric_sha256":sha256_file(output/"final_metric_distribution.csv"),"ranking_sha256":sha256_file(output/"final_ranking.csv"),"performance_gate_applied":False,"fixed_test_access":False,"release_created":False}
    write_json(output/"final_selection_report.json",report); return report

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--mode",choices=("map","final"),required=True); p.add_argument("--config",type=Path,required=True); p.add_argument("--screen-root",type=Path,action="append",required=True); p.add_argument("--finalist-root",type=Path,action="append",default=[]); p.add_argument("--task-id",type=int); p.add_argument("--output-directory",type=Path); a=p.parse_args(); config=json.loads(a.config.read_text())
    if a.mode=="map":
        require(a.task_id is not None and 0<=a.task_id<72,"task ID invalid"); selected=screen_selection(config,a.screen_root); cid=selected["finalist_candidate_ids"][a.task_id//12]; sid=FINALIST_SPLITS[a.task_id%12]; print(json.dumps({"candidate_id":cid,"split_id":sid,"screen_fingerprint_sha256":selected["screen_fingerprint_sha256"],"finalist_candidate_ids":selected["finalist_candidate_ids"]},sort_keys=True))
    else:
        require(a.output_directory is not None and a.finalist_root,"final arguments missing"); report=final_selection(config,a.screen_root,a.finalist_root,a.output_directory); print(f"ITER009_FINAL_SELECTION_OK best={report['best_candidate_id']}",flush=True)
    return 0
if __name__=="__main__": raise SystemExit(main())
