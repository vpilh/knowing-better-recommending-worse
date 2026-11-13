#!/bin/bash
source ~/epistemics/.venv/bin/activate
cd /mnt/c/Users/Valentin/AI_x_Epistemics
TAGS="qwen3-4b qwen3-8b qwen3-14b qwen3.8-27b gemma4-e4b gemma4-12b gemma4-31b olmo3-7b mistral-small-24b"
python - <<'PY'
import sys; sys.path.insert(0, "src")
from analyze import load
for t in "qwen3-4b qwen3-8b qwen3-14b qwen3.8-27b gemma4-e4b gemma4-12b gemma4-31b olmo3-7b mistral-small-24b".split():
    _, t2 = load(t + "-reason"); h = t2[t2["split"] == "heldout"]
    print(f"{t:18s} rows {len(h):5d}  missing {h['pA'].isna().mean():.3f}  by cond: " +
          " ".join(f"{c}={v:.2f}" for c, v in h.groupby('condition')['pA'].apply(lambda s: s.isna().mean()).items()))
PY
python src/confirm.py heldout $TAGS
python src/capitulation.py heldout $TAGS
