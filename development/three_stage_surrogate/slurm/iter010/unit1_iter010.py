#!/usr/bin/env python
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
REPO_ROOT=Path("/xdisk/chopinsong/tianyihu/elm-olmt")
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
from development.three_stage_surrogate.slurm.iter010.iter010_common import load_candidates,smoke,validate_contract
from model_ELM.three_stage_data import ThreeStageSnapshot,require,sha256_file
from model_ELM.three_stage_sr import write_json
from model_ELM.three_stage_spinup_release import balanced_split_manifest
from model_ELM.three_stage_sr_release import _load_split_manifest,validate_raw,validate_split_design

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--config",type=Path,required=True); p.add_argument("--output-directory",type=Path,required=True); a=p.parse_args(); require(not a.output_directory.exists(),"Unit1 output exists"); a.output_directory.mkdir(parents=True); config=json.loads(a.config.read_text())
    snapshot=ThreeStageSnapshot(config["snapshot_root"],verify_component_hashes=False); require(snapshot.snapshot_sha256==config["snapshot_sha256"],"snapshot mismatch"); require(sha256_file(snapshot.split_path)==config["global_split_sha256"],"global split mismatch"); load_candidates(config)
    for path,key in ((config["spinup_release_manifest"],"spinup_release_manifest_sha256"),(config["predicted_cn_handoff"],"predicted_cn_sha256"),(config["gpp_release_manifest"],"gpp_release_manifest_sha256"),(config["predicted_gpp_handoff"],"predicted_gpp_sha256")):
        require(sha256_file(Path(path))==config[key],f"dependency mismatch: {key}")
    fresh=balanced_split_manifest(snapshot.development_ranked,seed=int(config["repeated_split_seed"])); fresh_sets=[frozenset(item["validation_member_ids"]) for item in fresh["splits"]]; require(len(fresh_sets)==len(set(fresh_sets))==20,"fresh split duplicate")
    reference=json.loads(Path(config["reference_split_manifest"]).read_text()); require(sha256_file(Path(config["reference_split_manifest"]))==config["reference_split_manifest_sha256"],"reference split mismatch"); old_sets={frozenset(item["validation_member_ids"]) for item in reference["splits"]}; require(all(item not in old_sets for item in fresh_sets),"fresh split matches Iter009 selection split")
    split_path=a.output_directory/"repeated_split_manifest.json"; write_json(split_path,fresh); resolved=dict(config); resolved.update(repeated_split_manifest=str(split_path.resolve()),repeated_split_manifest_sha256=sha256_file(split_path),split_design_sha256=fresh["split_design_sha256"]); write_json(a.output_directory/"resolved_config.json",resolved); validate_split_design(snapshot,_load_split_manifest(resolved))
    write_json(a.output_directory/"preflight_report.json",{"schema":"three-stage-sr-iter010-preflight-v1","result":"pass","no_training":True,"split_seed":int(config["repeated_split_seed"]),"split_manifest_sha256":sha256_file(split_path),"split_design_sha256":fresh["split_design_sha256"],"reference_matching_validation_sets":0,"fixed_test_access":False})
    raw=Path(config["raw_directory"]); validation=validate_raw(resolved,raw,full_hashes=True); write_json(a.output_directory/"raw_validation.json",validation)
    contract=validate_contract(resolved,full_raw_hashes=True); write_json(a.output_directory/"contract_validation.json",contract); smoke_report=smoke(resolved,a.output_directory/"smoke")
    report={"schema":"three-stage-sr-iter010-unit1-v1","result":"pass","preflight":"pass","raw_validation":"pass","contract_validation":"pass","smoke":"pass","features":44,"candidate_count":33,"fresh_splits":20,"fixed_test_access":False,"release_created":False,"resolved_config_sha256":sha256_file(a.output_directory/"resolved_config.json")}; write_json(a.output_directory/"unit1_report.json",report); (a.output_directory/"ELIGIBLE").touch(); print("ITER010_UNIT1_OK features=44 candidates=33 fixed_test=false"); return 0
if __name__=="__main__": raise SystemExit(main())
