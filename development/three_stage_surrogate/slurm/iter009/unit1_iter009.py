#!/usr/bin/env python
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
REPO_ROOT=Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
from development.three_stage_surrogate.slurm.iter009.iter009_common import load_candidates,smoke,validate_contract
from model_ELM.three_stage_data import ThreeStageSnapshot,require,sha256_file
from model_ELM.three_stage_sr import write_json
from model_ELM.three_stage_sr_release import _load_split_manifest,prepare_raw,validate_raw,validate_split_design

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--config",type=Path,required=True); p.add_argument("--output-directory",type=Path,required=True); a=p.parse_args(); require(not a.output_directory.exists(),"Unit1 output exists"); a.output_directory.mkdir(parents=True); config=json.loads(a.config.read_text())
    snapshot=ThreeStageSnapshot(config["snapshot_root"],verify_component_hashes=False); require(snapshot.snapshot_sha256==config["snapshot_sha256"],"snapshot mismatch"); require(sha256_file(snapshot.split_path)==config["global_split_sha256"],"global split mismatch"); validate_split_design(snapshot,_load_split_manifest(config)); load_candidates(config)
    for path,key in ((config["spinup_release_manifest"],"spinup_release_manifest_sha256"),(config["predicted_cn_handoff"],"predicted_cn_sha256"),(config["gpp_release_manifest"],"gpp_release_manifest_sha256"),(config["predicted_gpp_handoff"],"predicted_gpp_sha256")):
        require(sha256_file(Path(path))==config[key],f"dependency mismatch: {key}")
    write_json(a.output_directory/"preflight_report.json",{"schema":"three-stage-sr-iter009-preflight-v1","result":"pass","no_training":True,"fixed_test_access":False})
    raw=a.output_directory/"raw"; prepare_raw(config,raw); validation=validate_raw(config,raw,full_hashes=True); write_json(a.output_directory/"raw_validation.json",validation)
    manifest=json.loads((raw/"raw_manifest.json").read_text()); resolved=dict(config); resolved.update(raw_directory=str(raw.resolve()),raw_layout_sha256=manifest["layout_sha256"],raw_x_sha256=manifest["x_sha256"],raw_y_sha256=manifest["y_sha256"],raw_time_sha256=manifest["time_sha256"]); write_json(a.output_directory/"resolved_config.json",resolved)
    contract=validate_contract(resolved,full_raw_hashes=True); write_json(a.output_directory/"contract_validation.json",contract); smoke_report=smoke(resolved,a.output_directory/"smoke")
    report={"schema":"three-stage-sr-iter009-unit1-v1","result":"pass","preflight":"pass","raw_validation":"pass","contract_validation":"pass","smoke":"pass","features":44,"candidate_count":24,"fixed_test_access":False,"release_created":False,"resolved_config_sha256":sha256_file(a.output_directory/"resolved_config.json")}; write_json(a.output_directory/"unit1_report.json",report); (a.output_directory/"ELIGIBLE").touch(); print("ITER009_UNIT1_OK features=44 candidates=24 fixed_test=false"); return 0
if __name__=="__main__": raise SystemExit(main())
