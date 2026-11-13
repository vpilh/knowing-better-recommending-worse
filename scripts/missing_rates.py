"""Inclusion check for all models on dev: neutral P(correct) and share of missing neutral readouts."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
rows = []
for d in sorted((ROOT / "results" / "raw").glob("*-reason")):
    _, t2 = load(d.name)
    n = t2[(t2["condition"] == "neutral") & (t2["split"] == "dev")]
    miss = 1 - n["pA"].notna().sum() / 900
    acc = n["p_correct"].mean()
    rows.append({"model": d.name.removesuffix("-reason"), "neutral readouts": n["pA"].notna().sum(),
                 "missing share": miss, "P(correct)": acc,
                 "included": (miss <= 0.20) and (acc >= 0.60)})
print(pd.DataFrame(rows).set_index("model").round(3).to_string())
