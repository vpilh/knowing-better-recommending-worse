"""Deference or doubt? For each model and pressure condition (dev split):
  toward-target effect when the target is wrong and when it is right (deference moves toward the
  user in both cases), and the share of second-turn answers that differ from the model's own
  neutral answer, split by whether that neutral answer agreed with the user (doubt moves away from
  the own answer regardless of the user).
Usage: defer_vs_doubt.py TAG [TAG ...]"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import load, wide  # noqa: E402

rows = []
for tag in sys.argv[1:]:
    _, t2 = load(f"{tag}-reason")
    w = wide(t2[t2["split"] == "dev"])
    for cond, col in (("preference", "pt_pressure"), ("rebuttal", "pt_pressure_strong")):
        d = w.dropna(subset=["pt_neutral", col])
        agree = d["pt_neutral"] > 0.5            # model's neutral answer = user's option
        flipped = (d[col] > 0.5) != agree
        rows.append({
            "model": tag, "condition": cond,
            "toward target | target wrong": (d.loc[~d.target_correct, col] - d.loc[~d.target_correct, "pt_neutral"]).mean(),
            "toward target | target right": (d.loc[d.target_correct, col] - d.loc[d.target_correct, "pt_neutral"]).mean(),
            "flip | neutral disagreed with user": flipped[~agree].mean(),
            "flip | neutral agreed with user": flipped[agree].mean(),
        })
pd.set_option("display.width", 200)
print(pd.DataFrame(rows).set_index(["model", "condition"]).round(3).to_string())
print("\nDeference: flips concentrated where the model disagreed with the user (toward the user).")
print("Doubt: flips also where the model already agreed with the user (away from the user).")
