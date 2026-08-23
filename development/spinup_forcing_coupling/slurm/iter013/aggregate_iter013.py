#!/usr/bin/env python3
"""Aggregate Iter013 site classifications into comparison tables and report."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load(path: Path) -> dict:
    require(path.is_file(), f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--abby-dir", required=True, type=Path)
    parser.add_argument("--jerc-dir", required=True, type=Path)
    parser.add_argument("--accounting", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    for name in (
        "aggregate_result.json",
        "site_comparison_table.csv",
        "ITER013_REPORT.md",
    ):
        if (out / name).exists():
            raise FileExistsError(out / name)

    sites = {}
    for site, directory in (("ABBY", args.abby_dir), ("JERC", args.jerc_dir)):
        classification = load(directory / "classification.json")
        geometry = load(directory / "geometry.json")
        common = load(directory / "common_target_logp.json")
        topk = load(directory / "topk_counterfactual.json")
        require(classification["status"] == "pass", f"{site} classification failed")
        require(geometry["status"] == "pass", f"{site} geometry failed")
        require(common["status"] == "pass", f"{site} common-target failed")
        require(topk["status"] == "pass", f"{site} topk failed")
        require((directory / "parameter_overlay.png").is_file(), f"{site} overlay missing")
        sites[site] = {
            "classification": classification,
            "geometry": geometry,
            "common_target_logp": common,
            "topk_counterfactual": topk,
        }

    rows = []
    for site, payload in sites.items():
        cmp_walk = payload["geometry"]["comparisons"]["tim_walkers_vs_iter012_walkers"]
        cmp_pool = payload["geometry"]["comparisons"]["tim_walkers_vs_iter012_pool"]
        rows.append(
            {
                "site": site,
                "geometry_class": payload["classification"]["geometry_class"],
                "selection_class": payload["classification"]["selection_class"],
                "max_wasserstein_walkers": cmp_walk["max_per_parameter_wasserstein"],
                "overlap_tim_to_iter012_walkers": cmp_walk[
                    "overlap_fraction_left_to_right"
                ],
                "overlap_tim_to_iter012_pool": cmp_pool["overlap_fraction_left_to_right"],
                "mean_pairwise_tim_walkers": cmp_walk["mean_pairwise_distance_left"],
                "mean_pairwise_iter012_walkers": cmp_walk[
                    "mean_pairwise_distance_right"
                ],
                "pool_top640_intersection_fraction": payload["topk_counterfactual"][
                    "pool_vs_ledger_top640"
                ]["intersection_fraction_of_a"],
                "median_logp_diff_tim_minus_iter012_walkers": payload[
                    "common_target_logp"
                ]["median_difference_tim_walkers_minus_iter012_walkers"],
            }
        )

    with (out / "site_comparison_table.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    aggregate = {
        "schema": "spinup-forcing-coupling-iter013-aggregate-v1",
        "sites": {
            site: {
                "geometry_class": payload["classification"]["geometry_class"],
                "selection_class": payload["classification"]["selection_class"],
                "classification": payload["classification"],
                "geometry_summary": {
                    "max_wasserstein_walkers": payload["geometry"]["comparisons"][
                        "tim_walkers_vs_iter012_walkers"
                    ]["max_per_parameter_wasserstein"],
                    "overlap_tim_to_iter012_walkers": payload["geometry"]["comparisons"][
                        "tim_walkers_vs_iter012_walkers"
                    ]["overlap_fraction_left_to_right"],
                    "overlap_tim_to_iter012_pool": payload["geometry"]["comparisons"][
                        "tim_walkers_vs_iter012_pool"
                    ]["overlap_fraction_left_to_right"],
                },
                "topk_summary": payload["topk_counterfactual"]["pool_vs_ledger_top640"],
                "common_target_median_diff": payload["common_target_logp"][
                    "median_difference_tim_walkers_minus_iter012_walkers"
                ],
            }
            for site, payload in sites.items()
        },
        "accounting_path": str(args.accounting),
        "status": "pass",
        "decision": (
            f"ABBY {sites['ABBY']['classification']['geometry_class']}/"
            f"{sites['ABBY']['classification']['selection_class']}; "
            f"JERC {sites['JERC']['classification']['geometry_class']}/"
            f"{sites['JERC']['classification']['selection_class']}"
        ),
    }
    (out / "aggregate_result.json").write_text(
        json.dumps(aggregate, indent=2) + "\n", encoding="utf-8"
    )

    report = [
        "# Iter013 — Stage A initialization-cloud comparison",
        "",
        f"Decision: `{aggregate['decision']}`",
        "",
        "## Site comparison",
        "",
        "| Site | Geometry | Selection | Max W walkers | TIM→I012 walker overlap | TIM→I012 pool overlap | Pool∩top640 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        report.append(
            f"| {row['site']} | {row['geometry_class']} | {row['selection_class']} | "
            f"{row['max_wasserstein_walkers']:.4f} | "
            f"{row['overlap_tim_to_iter012_walkers']:.4f} | "
            f"{row['overlap_tim_to_iter012_pool']:.4f} | "
            f"{row['pool_top640_intersection_fraction']:.4f} |"
        )
    report.extend(
        [
            "",
            "## Interpretation policy",
            "",
            "Geometry and selection classes are descriptive. They do not promote a posterior,",
            "change the initializer, or authorize MCMC. Stage A ends here.",
            "",
            "## Artifact paths",
            "",
            f"- ABBY analysis: `{args.abby_dir}`",
            f"- JERC analysis: `{args.jerc_dir}`",
            f"- Accounting: `{args.accounting}`",
            "",
        ]
    )
    (out / "ITER013_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(f"AGGREGATE_PASS decision={aggregate['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
