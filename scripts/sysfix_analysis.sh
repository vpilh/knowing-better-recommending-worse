#!/bin/bash
# Exploratory system-prompt run: completeness check, then confirm.py (adds PE_sys, IE_sys to confirm_heldout.csv).
source ~/epistemics/.venv/bin/activate
cd /mnt/c/Users/Valentin/AI_x_Epistemics
TAGS="qwen3-4b qwen3-8b qwen3-14b qwen3.8-27b gemma4-e4b gemma4-12b gemma4-31b olmo3-7b mistral-small-24b"
grep -E "system prompt|FAIL" ~/epistemics/logs/sweep.log | tail -9
python - $TAGS <<'PY'
import sys; sys.path.insert(0, "src")
from analyze import load
for t in sys.argv[1:]:
    _, s = load(t + "-reason-sys"); s = s[s["split"] == "heldout"]
    print(f"{t:18s} rows {len(s)}  missing {s['pA'].isna().mean():.3f}")
PY
python src/confirm.py heldout $TAGS | head -4
python - <<'PY'
import pandas as pd
t = pd.read_csv("results/tables/confirm_heldout.csv", index_col=0)
c = ["PE_a", "PE_sys", "PE_sys_lo", "PE_sys_hi", "IE", "IE_sys", "IE_sys_lo", "IE_sys_hi"]
print(t[c].round(3).to_string())
PY
