"""Quick look at a run: letter bias and sample replies. Usage: inspect_run.py TAG [N]"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
items = {json.loads(l)["item_id"]: json.loads(l) for l in open(ROOT / "data/items.jsonl", encoding="utf-8")}
t1 = [json.loads(l) for l in open(ROOT / f"results/raw/{tag}/turn1.jsonl", encoding="utf-8")]
t2 = [json.loads(l) for l in open(ROOT / f"results/raw/{tag}/turn2.jsonl", encoding="utf-8")]

def letter(p):
    return None if p is None else ("A" if p > 0.5 else "B")

print("turn 1 answer letter:", Counter(letter(r["t1_pA"]) for r in t1))
print("turn 1 answer letter by correct letter:",
      Counter((items[r["item_id"]]["correct_letter"], letter(r["t1_pA"])) for r in t1))
print("turn 1 first tokens:", Counter(r["t1_tok"] for r in t1).most_common(8))
for cond in ("neutral", "pressure", "information"):
    rows = [r for r in t2 if r["condition"] == cond]
    print(f"turn 3 [{cond}] letters:", Counter(letter(r["pA"]) for r in rows),
          "first tokens:", Counter(r["tok"] for r in rows).most_common(5))
for r in t1[:n]:
    it = items[r["item_id"]]
    print(f"\n----- {r['item_id']} correct={it['correct_letter']} pA={r['t1_pA']}")
    print(r["reply"][:700])
