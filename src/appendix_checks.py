"""Exploratory descriptive checks on the held-out target-wrong items (Appendix D, Limitations).

Usage: python src/appendix_checks.py
Writes results/tables/appendix_checks_heldout.txt with
  (1) PE_pref by the letter of the target option, per model;
  (2) PE_pref by |delta|, per model and pooled with equal model weights;
  (3) preference + goal replies that switch to the target (P(T) > 0.5) although the neutral reply did not.
"""
from __future__ import annotations

import pandas as pd

from analyze import ROOT, load, wide

TAGS = ["qwen3-4b", "qwen3-8b", "qwen3-14b", "qwen3.8-27b", "gemma4-e4b", "gemma4-12b",
        "gemma4-31b", "olmo3-7b", "mistral-small-24b"]


def main() -> None:
    rows = []
    for tag in TAGS:
        _, t2 = load(tag + "-reason")
        w = wide(t2)
        w = w[(w["split"] == "heldout") & (~w["target_correct"])].copy()
        w["pe_pref"] = w["pt_pressure"] - w["pt_neutral"]
        w["model"] = tag
        rows.append(w)
    d = pd.concat(rows)
    out = []
    out.append("(1) PE_pref by target letter\n" + d.pivot_table(
        index="model", columns="target_letter", values="pe_pref").round(3).to_string())
    by_delta = d.pivot_table(index="model", columns="abs_delta", values="pe_pref")
    by_delta.loc["POOLED"] = by_delta.mean()
    out.append("(2) PE_pref by |delta|\n" + by_delta.round(3).to_string())
    switched = d[(d["pt_neutral"] < 0.5) & (d["pt_pressure_objective"] > 0.5)]
    already = d[(d["pt_neutral"] >= 0.5) & (d["pt_pressure_objective"] > 0.5)]
    out.append(f"(3) pref+goal switches from a correct neutral reply: {len(switched)} of {len(d)}\n"
               + switched[["model", "family", "delta", "pt_neutral", "pt_pressure_objective"]].to_string()
               + f"\npref+goal P(T) > 0.5 with neutral already on the target: {len(already)}\n"
               + already.groupby(["model", "family"]).size().to_string())
    text = "\n\n".join(out)
    path = ROOT / "results" / "tables" / "appendix_checks_heldout.txt"
    path.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
