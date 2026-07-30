#!/usr/bin/env python
"""Validate exact iter010 result identity before aggregation."""
import csv
import json
import math
from pathlib import Path

ROOT = Path('/xdisk/chopinsong/tianyihu/elm-olmt')
OUT = Path('/xdisk/chopinsong/tianyihu/E3SM_out/SOIL_project/UQ_output')
MANIFEST = ROOT / 'development/spinup_surrogate/slurm/iter010/iter010_variants.tsv'
SEEDS = tuple(range(10001, 10101))
CASES = [f'{site}_ppe6_I20TRCNPRDCTCBC' for site in ('ABBY','JERC','OSBS','SOAP','RMNP','TALL','TEAK','WREF','YELL')]
FULL45 = 'parm_0,parm_1,parm_2,parm_3,parm_4,parm_5,parm_6,parm_7,parm_8,parm_9,parm_10,parm_11,parm_12,parm_13,PCT_SAND,PCT_CLAY,ORGANIC,PRECTmms_clim_mean,PRECTmms_clim_std,PRECTmms_clim_max,PRECTmms_clim_seasonal_amp,FSDS_clim_mean,FSDS_clim_max,FSDS_clim_seasonal_amp,FLDS_clim_mean,FLDS_clim_std,FLDS_clim_min,FLDS_clim_max,FLDS_clim_seasonal_amp,TBOT_clim_mean,TBOT_clim_std,TBOT_clim_min,TBOT_clim_max,RH_clim_mean,RH_clim_std,RH_clim_min,RH_clim_seasonal_amp,WIND_clim_mean,WIND_clim_std,WIND_clim_min,WIND_clim_max,WIND_clim_seasonal_amp,PSRF_clim_mean,PSRF_clim_std,PSRF_clim_seasonal_amp'.split(',')
DROP32 = [x for x in FULL45 if not x.startswith(('FLDS_', 'WIND_', 'PSRF_'))]

def main():
    rows = list(csv.DictReader(MANIFEST.open(newline=''), delimiter='\t')); assert len(rows) == 15
    for row in rows:
        variant = row['variant']; stats = OUT / f'spinup_surrogate_iter010_{variant}' / 'surrogate_spinup'
        expected = [stats / f'surrogate_spinup_stats_seed{seed}.json' for seed in SEEDS]
        assert sorted(stats.glob('surrogate_spinup_stats_seed*.json')) == expected, variant
        schemas = set()
        for seed, path in zip(SEEDS, expected):
            data = json.loads(path.read_text()); fixed = data['fixed_mlp_params']; diag = data['feature_diagnostics']
            assert data['stats_run_id'] == f'seed{seed}' and data['split_random_state'] == seed
            assert data['output_label'] == f'spinup_surrogate_iter010_{variant}'
            assert data['model_type'] == 'nn' and data['split_mode'] == 'by_member' and data['train_fraction'] == .8 and data['case_names'] == CASES and data['spinup_vars'] == ['TOTSOMC','TOTSOMN']
            assert fixed == {'hidden_layer_sizes':[32], 'activation':'tanh', 'solver':'lbfgs', 'alpha':float(row['alpha']), 'learning_rate_init':.001}
            assert diag['filter_scope'] == 'global_pre_split' and diag['apply_variance_filter'] is False and diag['feature_subset_policy'] == row['feature_subset_policy'] and diag['apply_corr_filter'] is (row['apply_corr_filter'] == 'true')
            selected = diag['selected_feature_names']
            if row['apply_corr_filter'] == 'true': assert diag['corr_threshold'] == .8 and set(selected).issubset(FULL45)
            elif row['feature_policy'] == 'drop_flds_wind_psrf': assert selected == DROP32 and data['input_feature_names'] == DROP32
            else: assert selected == FULL45
            assert data['input_feature_names'] == selected
            for target in ('TOTSOMC','TOTSOMN'):
                variable = data['by_variable'][target]
                assert variable['permutation_repeats'] == 8
                ranked = variable['permutation_importance_rmse']
                names = [item['feature'] for item in ranked]
                assert len(names) == len(selected) and len(set(names)) == len(names)
                assert set(names) == set(selected)
                for item in ranked:
                    assert set(item) >= {'feature', 'mean_rmse_increase', 'mean_r2_drop'}
                    assert math.isfinite(float(item['mean_rmse_increase']))
                    assert math.isfinite(float(item['mean_r2_drop']))
            schemas.add(tuple(selected))
        assert len(schemas) == 1, variant
    print('iter010 exact seed, metadata, model, feature-policy, and importance results passed')
if __name__ == '__main__': main()
