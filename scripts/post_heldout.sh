#!/bin/bash
# Held-out post-processing: tests (seeded, reproducible), money by family, hand-coding workbook, figures.
source ~/epistemics/.venv/bin/activate
cd /mnt/c/Users/Valentin/AI_x_Epistemics
TAGS="qwen3-4b qwen3-8b qwen3-14b qwen3.8-27b gemma4-e4b gemma4-12b gemma4-31b olmo3-7b mistral-small-24b"
python src/confirm.py heldout $TAGS | head -5
python - $TAGS <<'PY'
import sys; sys.path.insert(0, "src")
import pandas as pd
from analyze import load, wide
rows = []
for t in sys.argv[1:]:
    _, t2 = load(t + "-reason"); w = wide(t2[t2["split"] == "heldout"])
    w = w[~w["target_correct"]]
    w["money"] = w["margin"] * (w["pt_pressure"] - w["pt_neutral"])
    rows.append(w.groupby("family")["money"].mean().rename(t))
print("\nmoney per pushed decision ($), preference condition, by family:")
print(pd.DataFrame(rows).round(0).to_string())
PY
python -c "import pandas as pd; s=pd.read_csv('results/tables/capitulation_sample_heldout.csv'); print('\nsample:', len(s), 'rows, conditions', s.condition.unique(), '\n', s.model.value_counts().to_string())"
bash scripts/build_handcoding.sh heldout
bash scripts/make_figures.sh heldout
