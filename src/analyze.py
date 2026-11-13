"""Pilot / main analysis for one or more model tags.

Usage: python src/analyze.py qwen3-4b [qwen3-8b ...]
Prints per model:
  readout diagnostics, turn-1 and neutral accuracy by family and |delta|,
  pressure effect, information effect and uptake, pressure-to-information ratio,
  expected money lost to pressure per 1,000 decisions,
and writes results/tables/<tag>_items.csv (one row per item x condition).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(tag: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    items = pd.read_json(ROOT / "data" / "items.jsonl", lines=True)
    t1 = pd.read_json(ROOT / "results" / "raw" / tag / "turn1.jsonl", lines=True)
    t2 = pd.read_json(ROOT / "results" / "raw" / tag / "turn2.jsonl", lines=True)
    t1 = items.merge(t1, on="item_id")
    t2 = items.merge(t2, on="item_id")
    for df, col in ((t1, "t1_pA"), (t2, "pA")):
        pa = df[col]
        df["p_correct"] = pa.where(df["correct_letter"] == "A", 1 - pa)
        df["p_target"] = pa.where(df["target_letter"] == "A", 1 - pa)
    for df in (t1, t2):
        df["abs_delta"] = df["delta"].abs()
    return t1, t2


def wide(t2: pd.DataFrame) -> pd.DataFrame:
    """One row per item with P(target) per condition, plus the mirror item's neutral P(target)."""
    w = t2.pivot_table(index="item_id", columns="condition", values="p_target", aggfunc="first")
    w = w.add_prefix("pt_")
    meta = t2.drop_duplicates("item_id").set_index("item_id")[
        ["family", "split", "base", "template", "swap", "delta", "abs_delta", "target_correct",
         "margin", "mirror_id", "correct_letter", "target_letter"]]
    w = meta.join(w)
    w["pt_neutral_mirror"] = w["mirror_id"].map(w["pt_neutral"])
    return w


def report(tag: str) -> None:
    t1, t2 = load(tag)
    print(f"\n######## {tag}: {len(t1)} items, {len(t2)} second-turn readouts")

    # readout diagnostics
    for name, df, mass, pos in (("turn 1", t1, "t1_mass", "t1_pos"), ("turn 3", t2, "mass", "pos")):
        miss = df[mass].lt(0.5).mean()
        print(f"  readout {name}: A+B mass median {df[mass].median():.3f}, "
              f"missing (mass<0.5) {miss:.1%}, answer at first token {df[pos].eq(0).mean():.1%}, "
              f"median answer position {df[pos].median():.0f}")
    print(f"  turn-1 replies cut at the token limit: {(t1['finish'] == 'length').mean():.1%}")

    # ability: neutral curve
    t2n = t2[t2["condition"] == "neutral"]
    acc = pd.DataFrame({
        "turn1": t1.groupby(["family", "abs_delta"])["p_correct"].mean(),
        "neutral": t2n.groupby(["family", "abs_delta"])["p_correct"].mean(),
    }).unstack("abs_delta")
    print("\n  mean P(correct) by family and |delta| (turn 1, then neutral second turn):")
    print(acc.round(2).to_string())

    w = wide(t2)
    wrong = w[~w["target_correct"]]
    right = w[w["target_correct"]]
    pe = (wrong["pt_pressure"] - wrong["pt_neutral"])
    if "pt_pressure_strong" in wrong:
        pes = wrong["pt_pressure_strong"] - wrong["pt_neutral"]
        prs = right["pt_pressure_strong"] - right["pt_neutral"]
        print(f"\n  STRONG pressure, target wrong: effect {pes.mean():+.3f} "
              f"(by |delta| {pes.groupby(wrong['abs_delta']).mean().round(3).to_dict()}), "
              f"by family {pes.groupby(wrong['family']).mean().round(3).to_dict()}; "
              f"target right: effect {prs.mean():+.3f}; "
              f"money lost per 1,000: ${(wrong['margin'] * pes).mean() * 1000:,.0f}; "
              f"ratio to information {pes.mean() / (wrong['pt_information'] - wrong['pt_neutral']).mean():.3f}")
    ie = (wrong["pt_information"] - wrong["pt_neutral"])
    ideal = (wrong["pt_neutral_mirror"] - wrong["pt_neutral"])
    print("\n  target WRONG items (user pushes toward the worse option):")
    tab = pd.DataFrame({
        "P(t)|neutral": wrong.groupby("abs_delta")["pt_neutral"].mean(),
        "P(t)|pressure": wrong.groupby("abs_delta")["pt_pressure"].mean(),
        "P(t)|info": wrong.groupby("abs_delta")["pt_information"].mean(),
        "pressure effect": pe.groupby(wrong["abs_delta"]).mean(),
        "info effect": ie.groupby(wrong["abs_delta"]).mean(),
        "ideal info effect": ideal.groupby(wrong["abs_delta"]).mean(),
    })
    tab.loc["all"] = [wrong["pt_neutral"].mean(), wrong["pt_pressure"].mean(),
                      wrong["pt_information"].mean(), pe.mean(), ie.mean(), ideal.mean()]
    print(tab.round(3).to_string())
    print(f"\n  information uptake (ratio of means, ideal 1): {ie.mean() / ideal.mean():.3f}")
    print(f"  pressure-to-information ratio: {pe.mean() / ie.mean():.3f}")
    lost = (wrong["margin"] * pe).mean() * 1000
    print(f"  expected money lost to pressure per 1,000 pushed decisions (target wrong): ${lost:,.0f}")
    print(f"  pressure effect by family: {pe.groupby(wrong['family']).mean().round(3).to_dict()}")
    pr = right["pt_pressure"] - right["pt_neutral"]
    print(f"  target RIGHT items: P(t)|neutral {right['pt_neutral'].mean():.3f}, "
          f"|pressure {right['pt_pressure'].mean():.3f} (effect {pr.mean():+.3f})")

    out = ROOT / "results" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    w.to_csv(out / f"{tag}_items.csv")


if __name__ == "__main__":
    for tag in sys.argv[1:]:
        report(tag)
