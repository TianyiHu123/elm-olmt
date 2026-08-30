#!/usr/bin/env python3
"""Iter002 integrated SR plots and hourly skill tables from a passing receipt."""
from __future__ import annotations
import argparse, csv, json, pickle, sys, hashlib
from datetime import datetime
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path("/xdisk/chopinsong/tianyihu/elm-olmt"); TARGET="SR"
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import model_ELM  # noqa
from model_ELM.load_obs_nc import load_observations_with_time_from_nc, collocate_obs_to_forcing_time
from model_ELM.surrogate_NN_Forcing import _load_forcing_matrix

def load(p):
    with p.open("rb") as h: return pickle.load(h)
def digest(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def matrix(case):
    a=np.asarray(case.output[TARGET],float); n=len(case.output["taxis"])
    return a.reshape(n,1) if a.ndim==1 else (a if a.shape[0]==n else a.T)
def dates(a): return np.array([datetime(x.year,x.month,x.day,x.hour) for x in a])
def metric(p,o):
    r=p-o; rmse=float(np.sqrt(np.mean(r*r))); bias=float(np.mean(r)); mae=float(np.mean(abs(r)))
    den=np.sum((o-o.mean())**2); r2=float(1-np.sum(r*r)/den) if den else float("nan"); corr=float(np.corrcoef(p,o)[0,1]) if np.std(p) and np.std(o) else float("nan")
    kge=float(1-np.sqrt((corr-1)**2+(np.std(p)/np.std(o)-1)**2+(np.mean(p)/np.mean(o)-1)**2)) if np.isfinite(corr) and np.mean(o) else float("nan")
    return dict(n=int(len(o)),rmse=rmse,bias=bias,mae=mae,r2=r2,pearson_r=corr,kge=kge)
def grouped(t,*arrays, key):
    groups={}
    for i,x in enumerate(t): groups.setdefault(key(x),[]).append(i)
    keys=sorted(groups); return keys,[len(groups[k]) for k in keys],[np.array([a[ix].mean(axis=0) for ix in (groups[k] for k in keys)]) for a in arrays]
def line(path,x,op,cm,cs,obs,title):
    fig,ax=plt.subplots(figsize=(14,4)); colors=plt.cm.tab10(np.linspace(0,1,len(op)))
    for (seed,v),c in zip(op.items(),colors): ax.plot(x,v,lw=.45,color=c,label=f"opt {seed}")
    ax.plot(x,cm,color="black",lw=.8,label="ppe6 mean"); ax.fill_between(x,cm-cs,cm+cs,color="black",alpha=.18,label="ppe6 ±1 SD")
    ax.plot(x,obs,color="tab:blue",lw=.55,label="obs"); ax.set(title=title,ylabel="SR (gC m-2 day-1)"); ax.legend(ncol=4,fontsize=6); fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(path,dpi=150); plt.close(fig)
def main():
 p=argparse.ArgumentParser(); p.add_argument("--receipt",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
 rec=json.loads(a.receipt.read_text());
 if rec.get("status")!="pass": raise ValueError("receipt is not a passing preflight")
 a.output.mkdir(parents=True,exist_ok=True); rows=[]; manifest={"receipt":str(a.receipt),"sites":{}}
 for site,info in rec["sites"].items():
  ctrlp=ROOT/"pklfiles"/info["control"]["filename"];
  if digest(ctrlp)!=info["control"]["sha256"]: raise ValueError(f"{site}: control hash drift")
  if digest(info["observation"]["path"])!=info["observation"]["sha256"]: raise ValueError(f"{site}: observation hash drift")
  ctrlcase=load(ctrlp); ctrl=matrix(ctrlcase)
  _,_,ft=_load_forcing_matrix(Path(ctrlcase.metdir),("FSDS",),ctrl.shape[0]); op={}
  for e in info["optimized"]:
   q=ROOT/"pklfiles"/e["filename"]
   if digest(q)!=e["sha256"]: raise ValueError(f"{site}/{e['seed']}: optimized hash drift")
   op[int(e["seed"])]=matrix(load(q))[:,0]
  payload=load_observations_with_time_from_nc(info["observation"]["path"],[TARGET]); oo,oe,ov=collocate_obs_to_forcing_time(ft,payload["time"],payload["obs"],payload["obs_err"],[TARGET]); ix=np.asarray(ov["forcing_overlap_indices"],int)
  obs=np.asarray(oo[TARGET],float); err=np.asarray(oe[TARGET],float); cm=np.nanmean(ctrl[ix],1); cs=np.nanstd(ctrl[ix],1); valid=(obs>-9000)&np.isfinite(obs)&(err>0)&np.isfinite(err)&np.isfinite(cm)&np.isfinite(cs)
  for v in op.values(): valid &= np.isfinite(v[ix])&(v[ix]>-9000)
  t=np.asarray(ft)[ix][valid]; x=dates(t); control=ctrl[ix][valid]; cm=control.mean(1); cs=control.std(1); obs=obs[valid]; op={s:v[ix][valid] for s,v in op.items()}; out=a.output/site; out.mkdir(parents=True,exist_ok=True)
  line(out/"hourly.png",x,op,cm,cs,obs,f"{site} hourly SR")
  dkeys,dcount,(dc,dobs,*dops)=grouped(t,control,obs,*op.values(),key=lambda z:(z.year,z.month,z.day)); keep=[i for i,n in enumerate(dcount) if n==24 and {z.hour for z in t if (z.year,z.month,z.day)==dkeys[i]}==set(range(24))]; dx=[datetime(*dkeys[i]) for i in keep]; dop={s:v[keep] for s,v in zip(op,dops)}; line(out/"daily.png",dx,dop,dc[keep].mean(1),dc[keep].std(1),dobs[keep],f"{site} complete-day SR")
  for name,key,xlab in (("monthly",lambda z:z.month,"month"),("diurnal",lambda z:z.hour,"UTC hour")):
   ks,_,(cc,o,*vv)=grouped(t,control,obs,*op.values(),key=key); m=cc.mean(1); sd=cc.std(1); fig,ax=plt.subplots(figsize=(9,4));
   for (seed,_),v,c in zip(op.items(),vv,plt.cm.tab10(np.linspace(0,1,len(op)))): ax.plot(ks,v,color=c,lw=.7,label=f"opt {seed}")
   ax.plot(ks,m,color="black",label="ppe6 mean"); ax.fill_between(ks,m-sd,m+sd,color="black",alpha=.18); ax.plot(ks,o,color="tab:blue",label="obs"); ax.set(xlabel=xlab,ylabel="SR",title=f"{site} {name}"); ax.legend(ncol=4,fontsize=6); fig.tight_layout(); fig.savefig(out/f"{name}.png",dpi=150); plt.close(fig)
  fig,ax=plt.subplots(figsize=(max(8,len(op)),4)); labels=[f"opt {s}" for s in op]+["ppe6 mean","obs"]; ax.boxplot([*op.values(),cm,obs],tick_labels=labels); ax.tick_params(axis="x",rotation=45); ax.set(title=f"{site} hourly SR distribution",ylabel="SR"); fig.tight_layout(); fig.savefig(out/"boxplot.png",dpi=150); plt.close(fig)
  for s,v in op.items(): rows.append(dict(site=site,series="optimized",seed=s,**metric(v,obs)))
  rows.append(dict(site=site,series="ppe6_control_mean",seed="",**metric(cm,obs)))
  manifest["sites"][site]={"n":int(len(obs)),"figures":[str(out/f) for f in ("hourly.png","daily.png","monthly.png","diurnal.png","boxplot.png")]}
 with (a.output/"metrics.csv").open("w",newline="") as h: w=csv.DictWriter(h,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
 if len(manifest["sites"])!=9 or len(rows)!=69: raise ValueError(f"unexpected completeness sites={len(manifest['sites'])} rows={len(rows)}")
 (a.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
 print(f"ITER002_DIAGNOSTIC_PASS sites={len(manifest['sites'])} rows={len(rows)}")
if __name__=="__main__": main()
