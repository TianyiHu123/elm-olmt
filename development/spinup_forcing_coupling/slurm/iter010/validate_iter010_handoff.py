#!/usr/bin/env python3
import csv, json, re, sys
from pathlib import Path

ROOT = Path('/xdisk/chopinsong/tianyihu/elm-olmt')
WF = ROOT / 'development/spinup_forcing_coupling'

def field(path, pattern):
    text = path.read_text()
    m = re.search(pattern, text, re.M)
    if not m: raise SystemExit(f'VALIDATE_BLOCK: missing {pattern} in {path}')
    return m.group(1)

def main():
    report = WF/'iterations/iter010.md'; current = WF/'handoff/CURRENT.md'; summary = WF/'ITERATION_SUMMARY.md'; registry = WF/'registry.csv'; compact = WF/'summaries/iter010'
    if field(report, r'- Iteration ID: `([^`]+)`') != 'iter010': raise SystemExit('VALIDATE_BLOCK: report id')
    if field(report, r'- Status: `([^`]+)`') != 'completed': raise SystemExit('VALIDATE_BLOCK: report status')
    if field(current, r'- Active iteration: `([^`]+)`') != 'iter010': raise SystemExit('VALIDATE_BLOCK: current id')
    if field(current, r'- Status: `([^`]+)`') != 'completed': raise SystemExit('VALIDATE_BLOCK: current status')
    if field(current, r'- Phase: `([^`]+)`') != 'closed': raise SystemExit('VALIDATE_BLOCK: current phase')
    if '## iter010 - TIM terminal-partition topology diagnosis' not in summary.read_text(): raise SystemExit('VALIDATE_BLOCK: summary section')
    rows = list(csv.reader(registry.open()))
    row = next((r for r in rows if r and r[0] == 'iter010'), None)
    if row is None or row[2] != 'completed' or row[6] != 'pass': raise SystemExit('VALIDATE_BLOCK: registry identity')
    decision = json.loads((compact/'topology_decision.json').read_text())
    if set(decision['sites']) != {'ABBY','JERC'} or any(v['topology'] != 'two_basin_declined' for v in decision['sites'].values()): raise SystemExit('VALIDATE_BLOCK: topology decision')
    skip = json.loads((compact/'conditional_prediction.json').read_text())
    if skip.get('status') != 'skipped' or skip.get('evaluations') != 0: raise SystemExit('VALIDATE_BLOCK: skip evidence')
    if len(list((WF/'summaries/iter010').glob('*.png'))) != 2: raise SystemExit('VALIDATE_BLOCK: selected figures')
    for job in ('23554607','23554935','23555136','23555187'):
        if job not in report.read_text(): raise SystemExit(f'VALIDATE_BLOCK: missing job {job}')
    print('ITER010_HANDOFF_VALIDATE_PASS')

if __name__ == '__main__': main()
