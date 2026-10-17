#!/usr/bin/env python3
import argparse,csv,hashlib,json,math
from collections import Counter
from pathlib import Path

ROWS={"parameter_metadata.csv":4,"metric_definitions.csv":47,"member_metrics.csv":400,"response_curves.csv":32560,"ratio_support.csv":4800,"observation_summary.csv":1,"carbon_balance_metric_definitions.csv":6,"carbon_balance_members.csv":400,"carbon_balance_response_curves.csv":1320,"carbon_balance_parameter_summary.csv":4}
FIGS={"ABBY_cumulative_litter_input_response.png","ABBY_cumulative_total_hr_response.png","ABBY_decomposer_pool_delta_c_response.png","ABBY_carbon_balance_closure.png"}
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for c in iter(lambda:f.read(8*1024*1024),b""): h.update(c)
 return h.hexdigest()
def count(p):
 with p.open(newline="") as f:return sum(1 for _ in csv.reader(f))-1
def rows(p):
 with p.open(newline="") as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--results",type=Path,required=True);a=ap.parse_args();r=a.results
 out=json.loads((r/"output_manifest.json").read_text())
 if out.get("schema")!="elm_oat_carbon_balance_output_v1" or out.get("status")!="pass" or out.get("csv_data_rows")!=39542 or out.get("figure_count")!=21:raise ValueError("manifest contract")
 if sum(count(r/n) for n in ROWS)!=39542:raise ValueError("total rows")
 inp=json.loads((r/"input_manifest.json").read_text())
 if inp.get("direct_hr_only") is not True or inp.get("boundary_status")!="partial" or inp.get("core_input_manifest_sha256")!="bb2836591c0857fb45a560cc1d7fdfb2d85053571394a85633f10855f982bf62":raise ValueError("input/boundary contract")
 for n,v in ROWS.items():
  if count(r/n)!=v:raise ValueError(f"{n} rows")
 if len(list(r.glob("*.png")))!=21 or not FIGS.issubset({p.name for p in r.glob("*.png")}):raise ValueError("figures")
 expected=set(ROWS)|{p.name for p in r.glob("*.png")}|{"input_manifest.json","validation_receipt.json","output_manifest.json"}
 if {p.name for p in r.iterdir() if p.is_file()}!=expected:raise ValueError("exact artifact membership")
 if set(out["artifacts"])!=expected-{"output_manifest.json"}:raise ValueError("manifest artifact coverage")
 defs=rows(r/"carbon_balance_metric_definitions.csv")
 if list(defs[0])!=["metric","kind","units"] or {x["metric"] for x in defs}!={"input_C","HR_C","delta_C","rhs_C","residual_C","absolute_relative_closure_error"}:raise ValueError("metric definitions")
 m=rows(r/"carbon_balance_members.csv")
 if list(m[0]) != ["parameter","member","parameter_value","input_C","HR_C","delta_C","rhs_C","residual_C","closure_supported","closure_rejection_reason","absolute_relative_closure_error"]:raise ValueError("member header")
 if Counter(x["parameter"] for x in m)!={"cn_s1":100,"cn_s2":100,"cn_s3":100,"cn_s4":100}:raise ValueError("member multiplicity")
 for x in m:
  i,h,d,q,z=map(float,(x["input_C"],x["HR_C"],x["delta_C"],x["rhs_C"],x["residual_C"]))
  if not math.isclose(q,h+d,rel_tol=1e-12,abs_tol=1e-9) or not math.isclose(z,i-q,rel_tol=1e-12,abs_tol=1e-9):raise ValueError("independent balance reproduction")
  if x["closure_supported"]=="True" and not math.isclose(float(x["absolute_relative_closure_error"]),abs(z)/abs(i),rel_tol=1e-12,abs_tol=1e-12):raise ValueError("relative error")
  if x["closure_supported"]=="False" and (x["absolute_relative_closure_error"]!="" or not x["closure_rejection_reason"]):raise ValueError("unsupported semantics")
 c=rows(r/"carbon_balance_response_curves.csv")
 groups=Counter((x["parameter"],x["metric"],x["point_type"]) for x in c)
 if set(groups)!={(p,m,t) for p in ("cn_s1","cn_s2","cn_s3","cn_s4") for m in ("input_C","HR_C","delta_C") for t in ("member","bin_median")} or set(groups.values())!={100,10}:raise ValueError("curve inventory/multiplicity")
 s=rows(r/"carbon_balance_parameter_summary.csv")
 if any(int(x["members"])!=100 or int(x["supported"])+int(x["unsupported"])!=100 or not math.isclose(float(x["within_1pct_percent_of_supported"]),100*int(x["within_1pct_count"])/int(x["supported"]),rel_tol=1e-12) or not math.isclose(float(x["within_5pct_percent_of_supported"]),100*int(x["within_5pct_count"])/int(x["supported"]),rel_tol=1e-12) for x in s):raise ValueError("summary denominators/percentages")
 for n,m in out["artifacts"].items():
  p=r/n
  if not p.is_file() or p.stat().st_size!=m["bytes"] or digest(p)!=m["sha256"]:raise ValueError(f"artifact {n}")
 print("ITER010_ARTIFACT_VALIDATE_PASS csv_rows=39542 figures=21")
if __name__=="__main__":main()
