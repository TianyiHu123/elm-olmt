#!/usr/bin/env python
"""Fresh-process independent validation of Iter010 selection and replacement gate."""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
from typing import Any,Sequence
import numpy as np
REPO_ROOT=Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
from development.three_stage_surrogate.slurm.iter010.iter010_common import FINALIST_SPLITS,SCREEN_SPLITS,candidate_by_id,leaf_directory,load_candidates,read_json
from model_ELM.three_stage_data import require,sha256_file
from model_ELM.three_stage_sr import FEATURE_COUNT,HOURS
from model_ELM.three_stage_sr_release import DAY_COUNT,_load_split_manifest,_positions,load_raw

def resolve(roots:Sequence[Path],cid:int,sid:int)->Path:
    found=[leaf_directory(root,cid,sid) for root in roots if (leaf_directory(root,cid,sid)/"leaf_report.json").is_file()]
    eligible=[p for p in found if read_json(p/"leaf_report.json").get("result")=="pass"]
    require(len(eligible)==1,f"leaf attempt mismatch {cid}/{sid}"); return eligible[0]

def metric(obs:np.ndarray,pred:np.ndarray)->tuple[float,float,float]:
    o=np.asarray(obs,dtype=np.float64).ravel(); p=np.asarray(pred,dtype=np.float64).ravel(); require(o.size==p.size and np.all(np.isfinite(p)),"metric input invalid"); e=p-o; denom=np.sum((o-np.mean(o))**2); return float(1-np.sum(e**2)/denom),float(np.sqrt(np.mean(e**2))),float(np.mean(e))

def leaf_rows(config:dict[str,Any],roots:Sequence[Path],cid:int,sid:int,raw:tuple[Any,...])->list[dict[str,Any]]:
    leaf=resolve(roots,cid,sid); report=read_json(leaf/"leaf_report.json"); require(report["fixed_test_access"] is False and report["convergence_warning_count"]==0,"leaf ineligible"); require(sha256_file(leaf/"predictions_physical_float32.dat")==report["predictions_sha256"],"prediction hash mismatch")
    layout,_,y,_=raw; split=_load_split_manifest(config)["splits"][sid]; positions=_positions(layout,split["validation_member_ids"]); n=len(positions); predictions=np.memmap(leaf/"predictions_physical_float32.dat",mode="r",dtype=np.float32,shape=(2*n*HOURS,)); cursor=0; obs_parts=[]; pred_parts=[]
    for site in range(2):
        end=cursor+n*HOURS; obs_parts.append(np.asarray(y[site,positions],dtype=np.float64).reshape(-1)); pred_parts.append(np.asarray(predictions[cursor:end],dtype=np.float64)); cursor=end
    require(cursor==predictions.size,"prediction coverage mismatch"); oh=np.concatenate(obs_parts); ph=np.concatenate(pred_parts); od=np.concatenate([x.reshape(n,DAY_COUNT,24).mean(2).reshape(-1) for x in obs_parts]); pd=np.concatenate([x.reshape(n,DAY_COUNT,24).mean(2).reshape(-1) for x in pred_parts]); result=[]
    for resolution,o,p in (("hourly",oh,ph),("daily",od,pd)):
        r2,rmse,bias=metric(o,p); result.append({"candidate_id":cid,"split_id":sid,"resolution":resolution,"r2":r2,"rmse":rmse,"bias":bias})
    return result

def pcount(candidate:dict[str,Any])->int:
    sizes=[FEATURE_COUNT,*candidate["hidden_layer_sizes"],1]; return sum((a+1)*b for a,b in zip(sizes[:-1],sizes[1:]))

def rank(candidates:dict[str,Any],by_candidate:dict[int,list[dict[str,Any]]])->list[dict[str,Any]]:
    stats=[]
    for cid,rows in by_candidate.items():
        comp={}; splitraw={sid:[] for sid in sorted({r["split_id"] for r in rows})}
        for res in ("hourly","daily"):
            selected=[r for r in rows if r["resolution"]==res]; comp[f"{res}_r2_q10"]=float(np.quantile([r["r2"] for r in selected],.1,method="linear")); comp[f"{res}_rmse_q90"]=float(np.quantile([r["rmse"] for r in selected],.9,method="linear")); comp[f"{res}_median_absolute_bias"]=float(np.median(np.abs([r["bias"] for r in selected])))
            for r in selected: splitraw[r["split_id"]].extend((r["r2"],-r["rmse"],-abs(r["bias"])))
        stats.append({"candidate_id":cid,"components":comp,"splitraw":splitraw,"parameter_count":pcount(candidate_by_id(candidates,cid))})
    keys=("hourly_r2_q10","hourly_rmse_q90","hourly_median_absolute_bias","daily_r2_q10","daily_rmse_q90","daily_median_absolute_bias"); maximize={"hourly_r2_q10","daily_r2_q10"}; scores={r["candidate_id"]:[] for r in stats}; n=len(stats)
    for key in keys:
        values=np.asarray([r["components"][key] if key in maximize else -r["components"][key] for r in stats])
        for row,value in zip(stats,values):
            avg=int(np.sum(values<value))+(int(np.sum(values==value))-1)/2; scores[row["candidate_id"]].append(float(avg/(n-1)) if n>1 else 1.0)
    for row in stats:
        s=scores[row["candidate_id"]]; row["worst"]=min(s); row["mean"]=float(np.mean(s)); row["variability"]=float(np.std([np.mean(v) for v in row["splitraw"].values()]))
    return sorted(stats,key=lambda r:(-r["worst"],-r["mean"],r["variability"],r["parameter_count"],r["candidate_id"]))

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--config",type=Path,required=True); p.add_argument("--screen-root",type=Path,action="append",required=True); p.add_argument("--finalist-root",type=Path,action="append",required=True); p.add_argument("--output-directory",type=Path,required=True); a=p.parse_args(); config=json.loads(a.config.read_text()); report=read_json(a.output_directory/"final_selection_report.json"); candidates=load_candidates(config); raw=load_raw(Path(config["raw_directory"])); finalists=report["finalist_candidate_ids"]; require(len(finalists)==6 and finalists[0]==0,"finalist contract mismatch"); roots=[*a.screen_root,*a.finalist_root]; by={cid:[] for cid in finalists}
    for cid in finalists:
        for sid in range(20): by[cid].extend(leaf_rows(config,roots,cid,sid,raw))
    ranked=rank(candidates,by); best=ranked[0]; incumbent=next(row for row in ranked if row["candidate_id"]==0); keys=("hourly_r2_q10","hourly_rmse_q90","hourly_median_absolute_bias","daily_r2_q10","daily_rmse_q90","daily_median_absolute_bias"); maximize={"hourly_r2_q10","daily_r2_q10"}; improvements=sum(best["components"][key]>incumbent["components"][key] if key in maximize else best["components"][key]<incumbent["components"][key] for key in keys); both_worse=any(best["components"][f"{res}_r2_q10"]<incumbent["components"][f"{res}_r2_q10"] and best["components"][f"{res}_rmse_q90"]>incumbent["components"][f"{res}_rmse_q90"] for res in ("hourly","daily")); replacement=best["candidate_id"]!=0 and improvements>=4 and not both_worse; selected=best["candidate_id"] if replacement else 0; decision="sr_refined_configuration_selected" if replacement else "sr_refinement_insufficient_control_retained"; require(best["candidate_id"]==report["best_ranked_candidate_id"] and selected==report["selected_candidate_id"] and decision==report["decision"] and replacement==report["replacement_gate_pass"],"independent replacement decision mismatch"); require(report["performance_gate_applied"] is True and report["fixed_test_access"] is False and report["release_created"] is False,"final boundary mismatch")
    validation={"schema":"three-stage-sr-iter010-final-validation-v1","result":"pass","best_ranked_candidate_id":best["candidate_id"],"selected_candidate_id":selected,"decision":decision,"replacement_gate_pass":replacement,"challenger_improved_component_count":int(improvements),"finalist_candidate_ids":finalists,"recomputed_metric_rows":240,"fixed_test_access":False,"release_created":False}; out=a.output_directory/"final_validation.json"; out.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n"); print(f"ITER010_FINAL_VALIDATE_OK selected={selected} decision={decision}"); return 0
if __name__=="__main__": raise SystemExit(main())
