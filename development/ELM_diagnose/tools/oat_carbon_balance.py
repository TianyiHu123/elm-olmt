#!/usr/bin/env python3
"""Strict carbon-balance diagnostics for four explicit ABBY C:N OAT pickles."""
from __future__ import annotations

import argparse, csv, gc, hashlib, json, pickle, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

REPO = Path("/xdisk/chopinsong/tianyihu/elm-olmt")
sys.path.insert(0, str(REPO))
import model_ELM  # noqa: F401,E402

PARAMETERS = ("cn_s1", "cn_s2", "cn_s3", "cn_s4")
EXPECTED_PICKLE_HASHES = {"cn_s1":"fca486c11cf2a7c087195a7608b49d9b26c87c7369cd5a9418d6e44f4d9fcc1f","cn_s2":"40589f8c95da4d12940dc99f1acfbe118721399e826283365fd628c3642c2297","cn_s3":"b3d5d2aa40c48211551a16cd8db8ffca56430dc13f323087aeeffaf87ee525f1","cn_s4":"c68eaafb6b0dbe54c5aa7eb604842ee36673228cb0357ecdd4b973ff35954ff6"}
POOLS = ("CWDC", "LITR1C", "LITR2C", "LITR3C", "SOIL1C", "SOIL2C", "SOIL3C", "SOIL4C")
RAW = ("LITFALL", "HR", *POOLS)
HOURS, MEMBERS = 61320, 100
METRICS = ("input_C", "HR_C", "delta_C")
FIGURES = ("ABBY_cumulative_litter_input_response.png", "ABBY_cumulative_total_hr_response.png", "ABBY_decomposer_pool_delta_c_response.png", "ABBY_carbon_balance_closure.png")
CORE_ROWS = {"parameter_metadata.csv":4, "metric_definitions.csv":47, "member_metrics.csv":400, "response_curves.csv":32560, "ratio_support.csv":4800, "observation_summary.csv":1}

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(8*1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def mappings(items: list[str]) -> dict[str,str]:
    out={}
    for item in items:
        p,b=item.split(":",1)
        if p in out or b != Path(b).name or any(x in b for x in "*?[]"): raise ValueError(f"invalid mapping {item}")
        out[p]=b
    if tuple(out) != PARAMETERS: raise ValueError("exact ordered cn_s1--cn_s4 mappings required")
    return out

def matrix(case: Any, name: str) -> np.ndarray:
    a=np.asarray(case.output[name], dtype=float)
    if a.shape == (MEMBERS,HOURS): a=a.T
    if a.shape != (HOURS,MEMBERS) or not np.all(np.isfinite(a)): raise ValueError(f"{name}: invalid matrix {a.shape}")
    return a

def load_case(path: Path, parameter: str, control: xr.Dataset, calculate: bool=True) -> dict[str,Any]:
    with path.open("rb") as f: case=pickle.load(f)
    if str(case.site)!="ABBY" or int(case.nsamples)!=MEMBERS or list(map(str,case.ensemble_parms)) != [parameter]: raise ValueError("case identity differs")
    taxis=np.asarray(case.output["taxis"],dtype=float).reshape(-1)
    expected=2018.0+np.arange(HOURS)/8760.0
    if taxis.size!=HOURS or not np.allclose(taxis,expected,rtol=0,atol=1e-11): raise ValueError("time contract differs")
    samples=np.asarray(case.samples,dtype=float).reshape(-1)
    if samples.size!=MEMBERS: raise ValueError("sample count differs")
    raw={n:matrix(case,n) for n in RAW}
    if any(np.any(raw[n]<0) for n in POOLS): raise ValueError("negative pool stock")
    if not calculate:
        result={"native":np.nan,"selector":int(np.asarray(case.ensemble_pfts).reshape(-1)[0]),"begin":float(taxis[0]),"end":float(taxis[-1])}
        del case,raw;gc.collect();return result
    input_c=np.sum(raw["LITFALL"]/24.0,axis=0)
    hr_c=np.sum(raw["HR"]/24.0,axis=0)
    total=sum(raw[n] for n in POOLS)
    delta=total[-1]-total[0]
    rhs=hr_c+delta; residual=input_c-rhs
    rel=np.full(MEMBERS,np.nan); ok=np.isfinite(input_c)&(input_c!=0)&np.isfinite(residual)
    rel[ok]=np.abs(residual[ok])/np.abs(input_c[ok])
    selector=int(np.asarray(case.ensemble_pfts).reshape(-1)[0])
    vals=np.asarray(control[parameter].values,dtype=float).reshape(-1); vals=vals[np.isfinite(vals)]
    native=float(vals[0]) if vals.size and np.allclose(vals,vals[0]) else np.nan
    result={"samples":samples,"input_C":input_c,"HR_C":hr_c,"delta_C":delta,"rhs_C":rhs,"residual_C":residual,"relative_error":rel,"native":native,"selector":selector,"begin":float(taxis[0]),"end":float(taxis[-1])}
    del case, raw, total; gc.collect(); return result

def curve_rows(parameter: str, data: dict[str,Any]) -> list[dict[str,Any]]:
    rows=[]; x=data["samples"]; order=np.argsort(x,kind="stable"); groups=np.array_split(order,10)
    for metric in METRICS:
        y=data[metric]
        for i in range(MEMBERS): rows.append({"parameter":parameter,"metric":metric,"point_type":"member","member":i+1,"bin":"","parameter_value":x[i],"response":y[i],"units":"gC m-2","bin_count":""})
        for b,idx in enumerate(groups,1): rows.append({"parameter":parameter,"metric":metric,"point_type":"bin_median","member":"","bin":b,"parameter_value":float(np.median(x[idx])),"response":float(np.median(y[idx])),"units":"gC m-2","bin_count":len(idx)})
    return rows

def plot_response(all_data: dict[str,dict[str,Any]], metric: str, name: str, ylabel: str) -> None:
    fig,axes=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
    for ax,p in zip(axes.flat,PARAMETERS):
        d=all_data[p]; x=d["samples"]; y=d[metric]; ax.scatter(x,y,s=12,alpha=.55)
        groups=np.array_split(np.argsort(x,kind="stable"),10)
        ax.plot([np.median(x[g]) for g in groups],[np.median(y[g]) for g in groups],"k-o",ms=3)
        if np.isfinite(d["native"]): ax.axvline(d["native"],color="tab:red",ls="--")
        ax.set(title=p,xlabel=p,ylabel=ylabel); ax.grid(alpha=.2)
    fig.savefig(name,dpi=180); plt.close(fig)

def copy_core(core: Path, output: Path) -> None:
    manifest=json.loads((core/"output_manifest.json").read_text())
    if manifest.get("status")!="pass" or manifest.get("row_counts")!=CORE_ROWS or manifest.get("figure_count")!=17: raise ValueError("Iter009 core manifest differs")
    for name,meta in manifest["artifacts"].items():
        src=core/name
        if digest(src)!=meta["sha256"] or src.stat().st_size!=meta["bytes"]: raise ValueError(f"core artifact changed: {name}")
        shutil.copy2(src,output/name)

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--pickle-dir",type=Path,required=True); ap.add_argument("--parameter-pickle",action="append",default=[]); ap.add_argument("--config-dir",type=Path,required=True); ap.add_argument("--parameter-dir",type=Path,required=True); ap.add_argument("--control-paramfile",type=Path,required=True); ap.add_argument("--core-input-manifest",type=Path,required=True); ap.add_argument("--core-results",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); ap.add_argument("--validate-only",action="store_true"); ap.add_argument("--manifest",type=Path)
    a=ap.parse_args(); maps=mappings(a.parameter_pickle)
    if not all(p.is_absolute() for p in (a.pickle_dir,a.control_paramfile,a.core_results,a.output)): raise ValueError("all paths must be absolute")
    flux=np.array([[24.,48.],[24.,48.]])
    stocks=np.array([[10.,20.],[14.,28.]])
    fixture_input=np.sum(flux/24,axis=0); direct_hr=np.array([[12.,24.],[12.,24.]]); fixture_hr=np.sum(direct_hr/24,axis=0); fixture_delta=stocks[-1]-stocks[0]; fixture_residual=fixture_input-(fixture_hr+fixture_delta)
    if not np.allclose(fixture_input,[2.,4.]) or not np.allclose(fixture_hr,[1.,2.]) or not np.allclose(fixture_delta,[4.,8.]) or not np.allclose(fixture_residual,[-3.,-6.]): raise AssertionError("integration/direct-HR/endpoint/residual fixture")
    test_input=np.array([100.,100.,0.]); test_residual=np.array([1.,5.,1.]); support=np.isfinite(test_input)&(test_input!=0); reasons=np.where(support,"","nonpositive_or_nonfinite_input")
    if list(np.abs(test_residual[support])/np.abs(test_input[support])) != [0.01,0.05] or reasons[2]!="nonpositive_or_nonfinite_input": raise AssertionError("threshold/gap fixture")
    groups=np.array_split(np.argsort(np.arange(100)),10)
    if [len(g) for g in groups] != [10]*10: raise AssertionError("bin fixture")
    current_hashes={p:digest(a.pickle_dir/b) for p,b in maps.items()}
    if current_hashes != EXPECTED_PICKLE_HASHES: raise ValueError("pickle identities differ from locked contract")
    data={}
    with xr.open_dataset(a.control_paramfile) as control:
        for p,b in maps.items(): data[p]=load_case(a.pickle_dir/b,p,control,not a.validate_only)
    dep={f"config:{p}":digest(a.config_dir/f"ABBY_{p}.cfg") for p in PARAMETERS}; dep.update({f"parameter:{p}":digest(a.parameter_dir/f"{p}_paramfile") for p in PARAMETERS})
    if digest(a.core_input_manifest)!="bb2836591c0857fb45a560cc1d7fdfb2d85053571394a85633f10855f982bf62": raise ValueError("Iter009 input manifest identity differs")
    contract={"schema":"elm_oat_carbon_balance_input_v1","status":"pass","created_at_utc":datetime.now(timezone.utc).isoformat(),"parameters":list(PARAMETERS),"parameter_pickles":maps,"pickle_sha256":current_hashes,"dependency_sha256":dep,"control_paramfile_sha256":digest(a.control_paramfile),"core_input_manifest_sha256":digest(a.core_input_manifest),"hours":HOURS,"members":MEMBERS,"raw_variables":list(RAW),"direct_hr_only":True,"boundary_status":"partial","boundary_audit":"use_nofire and use_vertsoilc pinned; available provenance does not exclude every external transfer; input-constraint conclusion withheld","core_output_manifest_sha256":digest(a.core_results/"output_manifest.json"),"expected_csv_rows":39542,"expected_figures":21,"endpoint_timestamps":{p:[data[p]["begin"],data[p]["end"]] for p in PARAMETERS},"fixture":"integration_endpoints_direct_hr_residual_threshold_bins_and_gap_pass"}
    if a.manifest is not None:
        expected=json.loads(a.manifest.read_text())
        for key in ("schema","status","parameters","parameter_pickles","pickle_sha256","dependency_sha256","control_paramfile_sha256","core_input_manifest_sha256","hours","members","raw_variables","direct_hr_only","boundary_status","boundary_audit","core_output_manifest_sha256","expected_csv_rows","expected_figures","endpoint_timestamps","fixture"):
            if expected.get(key)!=contract.get(key): raise ValueError(f"validated manifest changed: {key}")
        contract=expected
    a.output.mkdir(parents=True,exist_ok=False)
    (a.output/"input_manifest.json").write_text(json.dumps(contract,indent=2,sort_keys=True)+"\n")
    (a.output/"validation_receipt.json").write_text(json.dumps({"schema":"elm_oat_carbon_balance_validation_v1","status":"pass","input_manifest_sha256":digest(a.output/"input_manifest.json")},indent=2)+"\n")
    if a.validate_only:
        print("CARBON_BALANCE_PREFLIGHT_PASS parameters=4 members=400 hours=61320"); return
    if a.manifest is None or digest(a.manifest)!=digest(a.output/"input_manifest.json"): raise ValueError("validated manifest differs")
    copy_core(a.core_results,a.output)
    defs=[{"metric":m,"kind":"integrated_flux" if m in ("input_C","HR_C") else "endpoint_stock_change" if m=="delta_C" else "derived_balance","units":"1" if m=="absolute_relative_closure_error" else "gC m-2"} for m in ("input_C","HR_C","delta_C","rhs_C","residual_C","absolute_relative_closure_error")]
    members=[]; curves=[]; summaries=[]
    for p in PARAMETERS:
        d=data[p]; curves.extend(curve_rows(p,d))
        for i in range(MEMBERS):
            supported=bool(np.isfinite(d["relative_error"][i])); reason="" if supported else "nonpositive_or_nonfinite_input"
            members.append({"parameter":p,"member":i+1,"parameter_value":d["samples"][i],"input_C":d["input_C"][i],"HR_C":d["HR_C"][i],"delta_C":d["delta_C"][i],"rhs_C":d["rhs_C"][i],"residual_C":d["residual_C"][i],"closure_supported":supported,"closure_rejection_reason":reason,"absolute_relative_closure_error":d["relative_error"][i] if supported else ""})
        rel=d["relative_error"]; finite=np.isfinite(rel); groups=np.array_split(np.argsort(d["samples"],kind="stable"),10); lo,hi=groups[0],groups[-1]
        delta=lambda k:float(np.median(d[k][hi])-np.median(d[k][lo]))
        slope,intercept=np.polyfit(d["input_C"],d["rhs_C"],1); corr=np.corrcoef(d["input_C"],d["rhs_C"])[0,1]
        supported=int(finite.sum()); one=int(np.sum(rel[finite]<=.01)); five=int(np.sum(rel[finite]<=.05))
        summaries.append({"parameter":p,"members":MEMBERS,"supported":supported,"unsupported":MEMBERS-supported,"within_1pct_count":one,"within_1pct_percent_of_supported":100*one/supported,"within_5pct_count":five,"within_5pct_percent_of_supported":100*five/supported,"median_relative_error":float(np.median(rel[finite])),"p95_relative_error":float(np.percentile(rel[finite],95)),"slope":slope,"intercept":intercept,"r_squared":corr*corr,"delta_input_C":delta("input_C"),"delta_HR_C":delta("HR_C"),"delta_delta_C":delta("delta_C"),"delta_residual_C":delta("residual_C")})
    write_csv(a.output/"carbon_balance_metric_definitions.csv",list(defs[0]),defs); write_csv(a.output/"carbon_balance_members.csv",list(members[0]),members); write_csv(a.output/"carbon_balance_response_curves.csv",list(curves[0]),curves); write_csv(a.output/"carbon_balance_parameter_summary.csv",list(summaries[0]),summaries)
    plot_response(data,"input_C",str(a.output/FIGURES[0]),"Cumulative litter input (gC m-2)"); plot_response(data,"HR_C",str(a.output/FIGURES[1]),"Cumulative direct HR (gC m-2)"); plot_response(data,"delta_C",str(a.output/FIGURES[2]),"Pool C end - beginning (gC m-2)")
    fig,axes=plt.subplots(2,2,figsize=(10,9),constrained_layout=True)
    for ax,p in zip(axes.flat,PARAMETERS):
        d=data[p]; x=d["input_C"]; y=d["rhs_C"]; lo=min(x.min(),y.min()); hi=max(x.max(),y.max()); line=np.array([lo,hi]); ax.scatter(x,y,s=14,alpha=.6,label="members"); ax.plot(line,line,"k-",label="1:1"); ax.plot(line,line*1.01,"--",color=".5",label="1% bands"); ax.plot(line,line*.99,"--",color=".5"); ax.plot(line,line*1.05,":",color=".6",label="5% bands"); ax.plot(line,line*.95,":",color=".6"); ax.set(title=p,xlabel="Input C (gC m-2)",ylabel="HR + delta C (gC m-2)",aspect="equal"); ax.grid(alpha=.2); ax.legend(fontsize=7)
    fig.savefig(a.output/FIGURES[3],dpi=180); plt.close(fig)
    artifacts={p.name:{"bytes":p.stat().st_size,"sha256":digest(p)} for p in a.output.iterdir() if p.is_file() and p.name!="output_manifest.json"}
    out={"schema":"elm_oat_carbon_balance_output_v1","status":"pass","created_at_utc":datetime.now(timezone.utc).isoformat(),"csv_data_rows":39542,"figure_count":21,"artifacts":artifacts}
    (a.output/"output_manifest.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("CARBON_BALANCE_DIAGNOSTIC_PASS csv_rows=39542 figures=21")

if __name__=="__main__": main()
