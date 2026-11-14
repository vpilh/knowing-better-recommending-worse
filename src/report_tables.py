"""Main results table for the report, from results/tables/confirm_<split>.csv.

Usage: python src/report_tables.py SPLIT
Writes results/tables/main_table_<split>.md: per model and pooled, the shift toward the worse option
under each message (95% cluster-bootstrap intervals for preference and the system-prompt run), the
information effect and the information effect under the system prompt.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"qwen3-4b": "Qwen3 4B", "qwen3-8b": "Qwen3 8B", "qwen3-14b": "Qwen3 14B",
         "qwen3.8-27b": "Qwen3.8 27B", "gemma4-e4b": "Gemma 4 E4B", "gemma4-12b": "Gemma 4 12B",
         "gemma4-31b": "Gemma 4 31B", "olmo3-7b": "OLMo 3 7B", "mistral-small-24b": "Mistral Small 3.2 24B",
         "POOLED": "Pooled (equal weights)"}


def f(x: float) -> str:
    s = f"{x:.2f}"
    return "0.00" if s == "-0.00" else s


def ci(r, k):
    return f"{f(r[k])} [{f(r[k + '_lo'])}, {f(r[k + '_hi'])}]"


def main() -> None:
    split = sys.argv[1] if len(sys.argv) > 1 else "heldout"
    t = pd.read_csv(ROOT / "results" / "tables" / f"confirm_{split}.csv", index_col=0)
    order = [m for m in t.drop(index="POOLED").sort_values("PE_a", ascending=False).index] + ["POOLED"]
    lines = ["| Model | Preference | Pref. + goal | Rebuttal | Information | Preference, system prompt | Information, system prompt |",
             "|---|---|---|---|---|---|---|"]
    for m in order:
        r = t.loc[m]
        lines.append(f"| {NAMES.get(m, m)} | {ci(r, 'PE_a')} | {f(r['PE_c'])} | {f(r['PE_b'])} | "
                     f"{f(r['IE'])} | {ci(r, 'PE_sys')} | {f(r['IE_sys'])} |")
    out = ROOT / "results" / "tables" / f"main_table_{split}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
