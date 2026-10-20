#!/usr/bin/env python3
"""Check a fresh run against the numbers reported in the manuscript (results/expected_results.json).

Usage: python scripts/06_verify.py [--run results/main] [--models results/model_comparison] [--weights results/pooled_weights.csv]
Prints PASS/FAIL for every check, writes results/verification_report.txt, exits 1 on any failure."""
import argparse, csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--run", default=os.path.join(ROOT, "results/main"))
ap.add_argument("--models", default=os.path.join(ROOT, "results/model_comparison"))
ap.add_argument("--weights", default=os.path.join(ROOT, "results/pooled_weights.csv"))
ap.add_argument("--expected", default=os.path.join(ROOT, "results/expected_results.json"))
ap.add_argument("--report", default=os.path.join(ROOT, "results/verification_report.txt"))
a = ap.parse_args()
E = json.load(open(a.expected)); lines, fails = [], 0


def check(name, got, want, tol=0.0):
    global fails
    ok = (got == want) if isinstance(want, (int, str)) and not isinstance(want, bool) and tol == 0 else abs(float(got) - float(want)) <= tol + 1e-12
    fails += not ok
    lines.append(f"{'PASS' if ok else 'FAIL'}  {name}: got {got}, expected {want}" + (f" (tol {tol})" if tol else ""))


m = json.load(open(os.path.join(a.run, "manifest.json"))); e = E["main"]
check("valid cells", m["cells"], e["cells"])
check("area km2", m["area_km2"], e["area_km2"], 0.001)
check("score min", m["score"]["min"], e["score_min"], 0.001)
check("score max", m["score"]["max"], e["score_max"], 0.001)
check("score mean", m["score"]["mean"], e["score_mean"], 0.0001)
check("High + Very High %", m["high_plus_very_high_pct"], e["high_plus_very_high_pct"], 0.005)
check("scenario count", m["scenario_count"], e["scenario_count"])
for c, p in zip([r[0] for r in m["class_areas"]], [r[3] for r in m["class_areas"]]):
    check(f"class % {c}", p, e["class_pct"][c], 0.005)
if m.get("points"):
    check("apiaries inside study area", m["points"]["n_inside"], e["apiaries_inside"])
    check("apiaries in High/Very High", m["points"]["in_high_or_very_high"], e["apiaries_in_high_or_very_high"])

sc = {r["scenario"]: r for r in csv.DictReader(open(os.path.join(a.run, "scenarios.csv")))}
for name, want in E.get("scenarios_changed_pct", {}).items():
    check(f"scenario changed % [{name}]", sc[name]["changed_pct"], want, 0.005)
pf = os.path.join(a.run, "points_500m.csv")
if os.path.exists(pf) and "points_500m" in E:
    p5 = {r["id"]: r for r in csv.DictReader(open(pf))}
    for pid, want in E["points_500m"].items():
        check(f"500 m mean percentile [{pid}]", p5[pid]["mean_500m_percentile"], want, 0.05)

v = json.load(open(os.path.join(a.models, "model_comparison_verification.json")))
check("independent WLC recompute: max |diff|", v["max_abs_difference"], E["wlc_recompute_max_abs_difference"], 1e-9)
check("independent WLC recompute: class changes", v["cells_with_class_change"], E["wlc_recompute_class_changes"])
check("cells where all three models agree %", v["all_three_models_same_class_pct"], E["all_three_models_same_class_pct"], 0.005)
rows = {r["model"].split(" ")[0]: r for r in csv.DictReader(open(os.path.join(a.models, "model_comparison.csv")))}
for mod, exp in E["models"].items():
    for k, want in exp.items():
        check(f"{mod} {k}", rows[mod][k], want, 0.005 if k.endswith("pct") else 0.0005)

if os.path.exists(a.weights):
    for r in csv.DictReader(open(a.weights)):
        check(f"pooled weight {r['criterion']}", r["weight_used"], E["pooled_weights"][r["criterion"]], 1e-9)

lines.append(f"\n{len(lines) - fails} passed, {fails} failed")
open(a.report, "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
sys.exit(1 if fails else 0)
