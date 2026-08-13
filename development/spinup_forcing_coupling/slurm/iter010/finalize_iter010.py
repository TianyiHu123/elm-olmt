#!/usr/bin/env python3
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--topology",type=Path,required=True); ap.add_argument("--prediction",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args(); a.output.mkdir(parents=True,exist_ok=True)
    d=json.loads(a.topology.read_text()); p=json.loads(a.prediction.read_text())
    routes={"two_basin_supported":"Iter009 Experiment 3 likelihood-continuity/boundary-path audit","connected_ridge_supported":"Experiment 3 first; then Experiment 4 parameter reduction if numerical discontinuity is declined","two_basin_declined":"Replace the forced screen, reassess TIM/JERC, and propose Experiment 5 for ABBY acceptance/saturation","inconclusive":"Narrow Experiment 3 path/connectivity audit targeting the conflicting directions"}
    lines=["# Iter010 TIM topology diagnosis", "", "This report is generated from the locked six-chain source manifest and deterministic analysis.", "", "## Site conclusions", ""]
    for site, item in d["sites"].items():
        lines += [f"### {site}", "", f"Topology result: `{item['topology']}`.", "", f"Maximum cross-seed same-group location distance (prior normalized): `{item['max_cross_seed_group_location_distance']:.6g}`.", "", "The five chain figures answer the scalar partition, physical parameter geometry, temporal persistence, and cross-seed reproducibility questions. They cannot establish posterior basin weights or mathematical convergence on their own.", ""]
    overall="two_basin_supported" if all(x["topology"] == "two_basin_supported" for x in d["sites"].values()) else "site-specific-or-declined"
    lines += ["## Conditional prediction", "", f"Status: `{p['status']}`; evaluations: `{p.get('evaluations', 0)}`.", "", "## Secondary interpretation and route", "", f"Overall TIM topology route: `{overall}`.", "", "No posterior sampling or convergence-length claim is made. The next planning-only route is selected from the immutable site result: " + "; ".join(sorted(set(routes[x["topology"]] for x in d["sites"].values()))) + ".", "", "## Figure construction", "", "Each chain has five deterministic figures: all 64 physical-log-posterior traces colored by the 7001--8000 reference assignment; sorted terminal medians with forced threshold, density/rug; a 15-parameter physical corner; prior-width-normalized PCA with identical 2048 draws; and rolling assignments with transitions and occupancy. Site figures compare the three seeds. Supporting metrics include GMM BIC, KDE bandwidth sensitivity, classifier accuracy, standardized group differences, assignment agreement, and transitions."]
    (a.output/"ITER010_REPORT.md").write_text("\n".join(lines)+"\n")
    (a.output/"conditional_prediction.json").write_text(json.dumps(p,indent=2,sort_keys=True))
    print(json.dumps({"status":"FINALIZE_PASS","overall":overall},sort_keys=True))
if __name__ == "__main__": main()
