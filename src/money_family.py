"""Descriptive: expected money lost per pushed decision, by decision family (PREREG section 8, broken down).

Usage: python src/money_family.py SPLIT MODEL_TAG [MODEL_TAG ...]
Per model, family and pressure condition on target-wrong items: mean_i [margin_i x (P_i(T|c) - P_i(T|neutral))]
in dollars, with the mean margin (what one wrong decision costs) for scale. POOLED is the equal-weight mean
across models. Writes results/tables/money_family_<split>.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from analyze import load, wide

ROOT = Path(__file__).resolve().parents[1]
CONDS = {"preference": "pt_pressure", "rebuttal": "pt_pressure_strong", "pref+goal": "pt_pressure_objective"}


def main() -> None:
    split, tags = sys.argv[1], sys.argv[2:]
    rows = []
    for tag in tags:
        _, t2 = load(f"{tag}-reason")
        w = wide(t2[t2["split"] == split])
        w = w[~w["target_correct"]]
        for fam, g in w.groupby("family"):
            row = {"model": tag, "family": fam, "n": len(g), "mean_margin": g["margin"].mean()}
            for name, col in CONDS.items():
                row[f"money_{name}"] = (g["margin"] * (g[col] - g["pt_neutral"])).mean()
            rows.append(row)
    t = pd.DataFrame(rows)
    pooled = t.groupby("family").mean(numeric_only=True).reset_index().assign(model="POOLED")
    t = pd.concat([t, pooled], ignore_index=True)
    for name in CONDS:   # loss as a share of what one wrong decision costs on average
        t[f"share_{name}"] = t[f"money_{name}"] / t["mean_margin"]
    out = ROOT / "results" / "tables" / f"money_family_{split}.csv"
    t.to_csv(out, index=False)
    print(t.pivot(index="model", columns="family", values="money_preference").round(0).to_string())
    print("\nPOOLED:\n" + pooled.round(1).to_string(index=False))
    # report table: pooled rows, dollars and share of the stake per condition
    names = {"F4": "F4 monthly pass vs pay per ride", "F5": "F5 extended warranty",
             "F6": "F6 lump sum vs instalments"}
    P = t[t["model"] == "POOLED"]
    lines = ["| Family | Mean stake | Preference | Preference + goal | Rebuttal |", "|---|---|---|---|---|"]
    for _, r in P.iterrows():
        cells = [f"${r[f'money_{c}']:,.0f} ({r[f'share_{c}']:.0%})" for c in ("preference", "pref+goal", "rebuttal")]
        lines.append(f"| {names.get(r['family'], r['family'])} | ${r['mean_margin']:,.0f} | " + " | ".join(cells) + " |")
    md = ROOT / "results" / "tables" / f"money_family_table_{split}.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines))
    print(f"\nwrote {out} and {md}")


if __name__ == "__main__":
    main()
