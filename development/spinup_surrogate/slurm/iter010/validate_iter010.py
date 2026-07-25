#!/usr/bin/env python
"""No-training compute-node checks for the locked iter010 matrix."""
import csv
import re
import sys
from pathlib import Path

ROOT = Path('/xdisk/chopinsong/tianyihu/elm-olmt')
sys.path.insert(0, str(ROOT))
from model_ELM.surrogate_NN_Spinup import _select_feature_columns

MANIFEST = ROOT / 'development/spinup_surrogate/slurm/iter010/iter010_variants.tsv'
CANONICAL = ROOT / 'development/spinup_surrogate/slurm/iter010/case.train_surrogate_spinup_iter010.slurm'
OUT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output')
ALPHAS = {'40', '42.5', '45', '47.5', '50'}
POLICIES = {'full45', 'corr080_prioritydrop', 'drop_flds_wind_psrf'}

def config(path):
    lines = path.read_text().splitlines(); assert len(lines) == 7
    return dict(line.split('=', 1) for line in lines)

def main():
    rows = list(csv.DictReader(MANIFEST.open(newline=''), delimiter='\t'))
    assert len(rows) == 15 and len({r['variant'] for r in rows}) == 15
    assert {(r['alpha'], r['feature_policy']) for r in rows} == {(a, p) for a in ALPHAS for p in POLICIES}
    text = CANONICAL.read_text(); assert '#SBATCH --array=1-100' in text and '--permutation-repeats 8' in text
    assert re.search(r'^readonly FULL45=.*$', text, re.M) and re.search(r'^readonly DROP32=.*$', text, re.M)
    for r in rows:
        v = r['variant']; assert v == f"s32_tanh_lbfgs_a{r['alpha'].replace('.', 'p')}_lr1e3_{r['feature_policy']}"
        if r['feature_policy'] == 'corr080_prioritydrop': assert (r['forcing_vars'], r['feature_subset_policy'], r['apply_corr_filter'], r['corr_threshold']) == ('PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF', 'eligible_pool', 'true', '0.80')
        elif r['feature_policy'] == 'drop_flds_wind_psrf': assert (r['forcing_vars'], r['feature_subset_policy'], r['apply_corr_filter'], r['corr_threshold']) == ('PRECTmms,FSDS,TBOT,RH', 'strict', 'false', 'NA')
        else: assert (r['forcing_vars'], r['feature_subset_policy'], r['apply_corr_filter'], r['corr_threshold']) == ('PRECTmms,FSDS,FLDS,TBOT,RH,WIND,PSRF', 'strict', 'false', 'NA')
        d = OUT / f'spinup_surrogate_iter010_{v}'; assert (d / f'submit_{v}.slurm').read_bytes() == CANONICAL.read_bytes(); assert config(d / 'submission_config.env') == {'VARIANT':v,'MLP_ALPHA':r['alpha'],'FEATURE_POLICY':r['feature_policy'],'FORCING_VARS':r['forcing_vars'],'FEATURE_SUBSET_POLICY':r['feature_subset_policy'],'APPLY_CORR_FILTER':r['apply_corr_filter'],'CORR_THRESHOLD':r['corr_threshold']}
    import numpy as np
    selected, diag = _select_feature_columns(
        np.arange(25.).reshape(5,5),
        ['parm_0','FLDS_clim_mean','WIND_clim_mean','PSRF_clim_mean','FSDS_clim_mean'],
        n_params=5, n_surface=0, n_climatology=0, feature_set='all',
        explicit_feature_subset=['parm_0','FSDS_clim_mean'],
        feature_subset_policy='strict', apply_corr_filter=False,
    )
    assert selected.tolist() == [0,4] and diag['filter_scope'] == 'global_pre_split'
    print('iter010 manifest, submitted artifacts, and no-training invariants passed')
if __name__ == '__main__': main()
