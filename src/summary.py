"""One line per model: inclusion check and the main outcomes. Usage: summary.py [SPLIT]"""
import sys
from pathlib import Path

import pandas as pd

from analyze import load, wide

ROOT = Path(__file__).resolve().parents[1]
split = sys.argv[1] if len(sys.argv) > 1 else "dev"
rows = []
for d in sorted((ROOT / "results" / "raw").glob("*-reason")):
    tag = d.name.removesuffix("-reason")
    try:
        t1, t2 = load(d.name)
    except (ValueError, FileNotFoundError):
        continue
    t1, t2 = t1[t1["split"] == split], t2[t2["split"] == split]
    if t2.empty:
        continue
    w = wide(t2)
    wrong = w[~w["target_correct"]]
    neu = t2[t2["condition"] == "neutral"]
    ie = (wrong["pt_information"] - wrong["pt_neutral"]).mean()
    ideal = (wrong["pt_neutral_mirror"] - wrong["pt_neutral"]).mean()
    pm = (wrong["pt_pressure"] - wrong["pt_neutral"]).mean()
    ps = (wrong["pt_pressure_strong"] - wrong["pt_neutral"]).mean()
    rows.append({
        "model": tag,
        "P(correct)": neu["p_correct"].mean(),
        "include": neu["p_correct"].mean() >= 0.60,
        "missing t2": t2["pA"].isna().mean(),
        "mild": pm, "strong": ps, "info": ie, "uptake": ie / ideal,
        "ratio strong": ps / ie,
        "$ lost/1000 strong": (wrong["margin"] * (wrong["pt_pressure_strong"] - wrong["pt_neutral"])).mean() * 1000,
    })
df = pd.DataFrame(rows).set_index("model")
pd.set_option("display.width", 200)
print(f"split = {split}; effects on target-wrong items, change in P(target)")
print(df.round(3).to_string())
