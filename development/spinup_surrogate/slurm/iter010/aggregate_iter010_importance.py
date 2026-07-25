#!/usr/bin/env python
"""Write the specified 100-seed, per-target and cross-target iter010 importance rankings."""
import argparse
import json
from pathlib import Path
from statistics import median

def summarize(values):
    values = sorted(float(x) for x in values)
    return {'count':len(values), 'median':median(values), 'min':values[0], 'max':values[-1]}

def main():
    p = argparse.ArgumentParser(); p.add_argument('--stats-dir', required=True); p.add_argument('--variant', required=True); p.add_argument('--output-json', required=True); args = p.parse_args()
    files = sorted(Path(args.stats_dir).glob('surrogate_spinup_stats_seed*.json')); assert len(files) == 100
    payloads = [json.loads(f.read_text()) for f in files]; targets = ('TOTSOMC','TOTSOMN'); by_target = {}
    for target in targets:
        features = {}
        for data in payloads:
            ranking = data['by_variable'][target]['permutation_importance_rmse']
            for rank, item in enumerate(ranking, 1):
                row = features.setdefault(item['feature'], {'ranks':[], 'rmse':[], 'r2':[]})
                row['ranks'].append(rank); row['rmse'].append(item['mean_rmse_increase']); row['r2'].append(item['mean_r2_drop'])
        rows = [{'feature':f, 'median_seed_rank':median(v['ranks']), 'rank_spread':{'min':min(v['ranks']),'max':max(v['ranks']),'iqr':median(sorted(v['ranks'])[50:]) - median(sorted(v['ranks'])[:50])}, 'median_rmse_increase':median(v['rmse']), 'rmse_increase':summarize(v['rmse']), 'r2_drop':summarize(v['r2'])} for f,v in features.items()]
        rows.sort(key=lambda r:(r['median_seed_rank'], -r['median_rmse_increase'], r['feature'])); by_target[target] = rows
    all_features = sorted(set().union(*(set(r['feature'] for r in rows) for rows in by_target.values())))
    combined=[]
    for feature in all_features:
        per = {target:next(r for r in by_target[target] if r['feature']==feature) for target in targets}
        combined.append({'feature':feature, 'median_seed_rank':median([per[t]['median_seed_rank'] for t in targets]), 'median_rmse_increase':median([per[t]['median_rmse_increase'] for t in targets]), 'by_target':per})
    combined.sort(key=lambda r:(r['median_seed_rank'], -r['median_rmse_increase'], r['feature']))
    Path(args.output_json).write_text(json.dumps({'variant':args.variant,'seed_count':100,'permutation_repeats':8,'ranking_rule':'median_seed_rank ascending, then median_rmse_increase descending','by_target':by_target,'combined_cross_target':combined}, indent=2)+'\n')
if __name__ == '__main__': main()
