"""Print sample items: python scripts/show_items.py F1-b0-d+0.10-t0-s0 F3-b1-d-0.05-t2-s1"""
import json
import sys
from pathlib import Path

items = {json.loads(l)["item_id"]: json.loads(l)
         for l in open(Path(__file__).resolve().parents[1] / "data" / "items.jsonl", encoding="utf-8")}
for iid in sys.argv[1:] or list(items)[:1]:
    it = items[iid]
    print(f"===== {iid}  correct={it['correct_letter']}  target={it['target_letter']}  "
          f"theta={it['theta']}  theta*={it['theta_star']:.4g}  margin=${it['margin']:,.0f}")
    print(it["prompt"])
    for c in ("neutral", "pressure", "information"):
        print(f"  [{c}] {it[f'msg_{c}']}")
