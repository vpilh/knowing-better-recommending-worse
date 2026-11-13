"""Why are readouts missing? Finish reasons, lengths and samples. Usage: TAG"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tag = sys.argv[1]
t1 = [json.loads(l) for l in open(ROOT / f"results/raw/{tag}-reason/turn1.jsonl", encoding="utf-8")]
t2 = [json.loads(l) for l in open(ROOT / f"results/raw/{tag}-reason/turn2.jsonl", encoding="utf-8")]
print("turn 1 finish:", Counter(r["finish"] for r in t1), "| missing:", sum(r["t1_pA"] is None for r in t1))
miss = [r for r in t2 if r["pA"] is None]
print("turn 2 missing:", len(miss), "of", len(t2), "| finish of missing:", Counter(r.get("finish") for r in miss))
print("turn 2 n_tokens of missing (median):", sorted(r.get("n_tokens", 0) for r in miss)[len(miss) // 2] if miss else 0)
for r in miss[:3]:
    txt = r["text"] or ""
    print(f"\n--- {r['item_id']} [{r['condition']}] len={len(txt)} chars\n{txt[:300]}\n   ...\n{txt[-300:]}")
