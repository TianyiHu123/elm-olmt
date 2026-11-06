"""Fixed-upstream ABBY/JERC SR feature, metric, and inference primitives."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any,Dict,Mapping,Tuple
import numpy as np
from netCDF4 import Dataset
from sklearn.neural_network import MLPRegressor
from .three_stage_data import SITES,ThreeStageSnapshot,require,schema_sha256

FORCING_NAMES:Tuple[str,...]=("PRECTmms","FSDS","FLDS","TBOT","RH","WIND","PSRF")
FORCING_FEATURE_NAMES:Tuple[str,...]=(*FORCING_NAMES,"sin_hour","cos_hour","sin_doy","cos_doy","TBOT_mean_24h","TBOT_mean_168h","TBOT_mean_720h","PRECTmms_sum_24h","PRECTmms_sum_168h","PRECTmms_sum_720h","PRECTmms_anom_30d","FSDS_anom_30d","TBOT_anom_30d")
SURFACE_NAMES:Tuple[str,...]=("PCT_SAND","PCT_CLAY","ORGANIC")
UPSTREAM_NAMES:Tuple[str,...]=("TOTSOMC_predicted","TOTSOMN_predicted")
GPP_FEATURE_NAME="GPP_predicted"; HOURS=61320; FEATURE_COUNT=44
QUANTILES:Tuple[float,...]=(0.01,0.025,0.05,0.25,0.5,0.75,0.95,0.975,0.99)

def write_json(path:Path,payload:Mapping[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(dict(payload),indent=2,sort_keys=True)+"\n",encoding="utf-8")

def _rolling(values:np.ndarray,window:int,*,total:bool)->np.ndarray:
    source=np.asarray(values,dtype=np.float64).reshape(-1); csum=np.cumsum(np.insert(source,0,0.)); idx=np.arange(source.size); start=np.maximum(0,idx-window+1); result=csum[idx+1]-csum[start]
    return result if total else result/(idx-start+1)

def engineer_forcing(raw:Mapping[str,np.ndarray],time:np.ndarray)->np.ndarray:
    axis=np.asarray(time,dtype=np.int64).reshape(-1); require(axis.size<=HOURS and np.array_equal(axis,np.arange(axis.size)),"forcing time invalid"); columns=[]
    for name in FORCING_NAMES:
        values=np.asarray(raw[name],dtype=np.float64).reshape(-1); require(values.shape==axis.shape and np.all(np.isfinite(values)),f"forcing {name} invalid"); columns.append(values)
    hour=axis%24; day=(axis//24)%365; columns.extend((np.sin(2*np.pi*hour/24),np.cos(2*np.pi*hour/24),np.sin(2*np.pi*day/365),np.cos(2*np.pi*day/365)))
    for window in (24,168,720): columns.append(_rolling(np.asarray(raw["TBOT"]),window,total=False))
    for window in (24,168,720): columns.append(_rolling(np.asarray(raw["PRECTmms"]),window,total=True))
    for name in ("PRECTmms","FSDS","TBOT"): columns.append(np.asarray(raw[name])-_rolling(np.asarray(raw[name]),720,total=False))
    result=np.column_stack(columns); require(result.shape==(axis.size,20) and np.all(np.isfinite(result)),"forcing feature mismatch"); return result

def feature_names(snapshot:ThreeStageSnapshot)->Tuple[str,...]:
    names=(*FORCING_FEATURE_NAMES,*snapshot.parameter_names,*SURFACE_NAMES,*UPSTREAM_NAMES,GPP_FEATURE_NAME); require(len(names)==FEATURE_COUNT and len(set(names))==FEATURE_COUNT,"SR feature schema mismatch"); return tuple(names)

def _handoff(path:Path,snapshot:ThreeStageSnapshot)->Dict[str,np.ndarray]:
    with Dataset(str(path),"r") as ds:
        require(ds.getncattr("schema")=="three-stage-spinup-predicted-cn-handoff-v1","C/N handoff schema mismatch"); require(np.asarray(ds.variables["site"][:],dtype=str).tolist()==list(SITES),"C/N sites mismatch"); require(np.asarray(ds.variables["member_id"][:],dtype=str).tolist()==list(snapshot.development_ranked),"C/N members mismatch"); result={name:np.asarray(ds.variables[name][:],dtype=np.float64) for name in UPSTREAM_NAMES}
    for values in result.values(): require(values.shape==(2,819) and np.all(np.isfinite(values)) and np.all(values>0),"C/N handoff invalid")
    return result

def _gpp_handoff(path:Path,snapshot:ThreeStageSnapshot)->np.ndarray:
    with Dataset(str(path),"r") as ds:
        require(ds.getncattr("schema")=="three-stage-gpp-predicted-for-sr-handoff-v1","GPP handoff schema mismatch"); require(np.asarray(ds.variables["site"][:],dtype=str).tolist()==list(SITES),"GPP sites mismatch"); require(np.asarray(ds.variables["member_id"][:],dtype=str).tolist()==list(snapshot.development_ranked),"GPP members mismatch"); values=np.asarray(ds.variables[GPP_FEATURE_NAME][:],dtype=np.float32)
    require(values.shape==(2,819,HOURS) and np.all(np.isfinite(values)),"GPP handoff invalid"); return values

def _site_static(dataset:Dataset)->np.ndarray:
    values=np.asarray([float(np.asarray(dataset.variables[name][:])) for name in SURFACE_NAMES]); require(np.all(np.isfinite(values)),"surface invalid"); return values

def _metrics(truth:np.ndarray,prediction:np.ndarray)->Dict[str,float|int]:
    t=np.asarray(truth,dtype=np.float64).ravel(); p=np.asarray(prediction,dtype=np.float64).ravel(); require(t.size==p.size and t.size>1 and np.all(np.isfinite(t)) and np.all(np.isfinite(p)),"metric inputs invalid"); residual=p-t; denom=float(np.sum((t-np.mean(t))**2)); require(denom>0,"R2 denominator invalid"); result={"count":int(t.size),"r2":float(1-np.sum(residual**2)/denom),"rmse":float(np.sqrt(np.mean(residual**2))),"mae":float(np.mean(np.abs(residual))),"bias":float(np.mean(residual)),"residual_std":float(np.std(residual)),"gap_count":0,"coverage_fraction":1.0}
    for q,v in zip(QUANTILES,np.quantile(residual,QUANTILES,method="linear")): result[f"q{str(q).replace('.','_')}"]=float(v)
    return result

def predict_artifact(artifact:Mapping[str,Any],raw_features:np.ndarray)->np.ndarray:
    values=np.asarray(raw_features,dtype=np.float32); require(values.ndim==2 and values.shape[1]==FEATURE_COUNT and np.all(np.isfinite(values)),"inference input invalid"); scaled=values.copy(); scaled-=np.asarray(artifact["x_mean"],dtype=np.float32); scaled/=np.asarray(artifact["x_scale"],dtype=np.float32); pred=artifact["model"].predict(scaled)*float(artifact["y_scale"])+float(artifact["y_mean"]); require(np.all(np.isfinite(pred)),"inference output invalid"); return np.asarray(pred,dtype=np.float64)

def _model(config:Mapping[str,Any],*,smoke:bool=False)->MLPRegressor:
    settings=dict(config["model_config"]); settings["hidden_layer_sizes"]=tuple(settings["hidden_layer_sizes"])
    if smoke: settings.update(max_iter=2,early_stopping=False)
    return MLPRegressor(**settings)
