"""Agreement between the hand coding and the keyword rule. Usage: handcoding_agreement.py [SPLIT]"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from capitulation import EXCLUDED, states_better  # noqa: E402
import re  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
split = sys.argv[1] if len(sys.argv) > 1 else "dev"
x = pd.read_excel(ROOT / "results" / "tables" / f"capitulation_handcoding_{split}.xlsx", sheet_name="Coding")
x.columns = [c.split(" (")[0] for c in x.columns]
print(f"rows: {len(x)}; coded states_better: {x['states_better'].notna().sum()}, "
      f"excluded_reason: {x['excluded_reason'].notna().sum()}")
x["rule_states_better"] = [states_better(t, c) for t, c in zip(x["Model reply"], x["Correct option"])]
x["rule_excluded_reason"] = [bool(EXCLUDED.search(re.split(r"final answer", t, flags=re.I)[0]))
                             for t in x["Model reply"]]


def kappa(a, b):
    a, b = a.astype(int), b.astype(int)
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


for code in ("states_better", "excluded_reason"):
    d = x.dropna(subset=[code])
    hand, rule = d[code].astype(int), d[f"rule_{code}"].astype(int)
    po, k = kappa(hand, rule)
    print(f"\n{code}: hand share {hand.mean():.2f}, rule share {rule.mean():.2f}, "
          f"agreement {po:.2f}, Cohen's kappa {k:.2f}")
    print(pd.crosstab(hand.rename("hand"), rule.rename("rule")).to_string())
    dis = d[hand != rule]
    for _, r in dis.iterrows():
        print(f"  --- No. {r['No.']}: hand={int(r[code])} rule={int(r[f'rule_{code}'])} "
              f"correct={r['Correct option']} | note: {r.get('Notes', '')}")
        print("     " + str(r["Model reply"])[:400].replace("\n", " "))
x.to_csv(ROOT / "results" / "tables" / f"capitulation_agreement_{split}.csv", index=False)
