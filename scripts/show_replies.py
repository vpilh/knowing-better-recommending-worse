"""Show second-turn replies for one model and condition on target-wrong items where the model moved.
Usage: show_replies.py TAG CONDITION [N]"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tag, cond = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 3
items = {json.loads(l)["item_id"]: json.loads(l) for l in open(ROOT / "data/items.jsonl", encoding="utf-8")}
t2 = [json.loads(l) for l in open(ROOT / f"results/raw/{tag}/turn2.jsonl", encoding="utf-8")]
neutral = {r["item_id"]: r["pA"] for r in t2 if r["condition"] == "neutral"}
moved = []
for r in t2:
    it = items[r["item_id"]]
    if r["condition"] != cond or it["target_correct"] or r["pA"] is None or neutral.get(r["item_id"]) is None:
        continue
    pt = r["pA"] if it["target_letter"] == "A" else 1 - r["pA"]
    pt0 = neutral[r["item_id"]] if it["target_letter"] == "A" else 1 - neutral[r["item_id"]]
    if pt > 0.5 and pt0 < 0.5:
        moved.append((r, it))
random.seed(1)
print(f"{tag} [{cond}]: {len(moved)} target-wrong items flipped from correct to target")
for r, it in random.sample(moved, min(n, len(moved))):
    print(f"\n----- {r['item_id']} correct={it['correct_letter']} target={it['target_letter']} margin=${it['margin']:,.0f}")
    print(r["text"][:900])
