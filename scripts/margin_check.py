import json, collections
rows=[json.loads(l) for l in open("/mnt/c/Users/Valentin/AI_x_Epistemics/data/items.jsonl")]
by=collections.defaultdict(list)
for r in rows: by[r["item_id"].split("-")[0]].append(abs(r["margin"]))
for f,v in sorted(by.items()): v=sorted(v); print(f, "median", round(v[len(v)//2],2), "max", round(v[-1],2))
big=max(rows,key=lambda r:abs(r["margin"])); print(big["item_id"], big["margin"]); print(big["prompt"][:900])
