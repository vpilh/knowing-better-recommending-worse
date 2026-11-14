#!/bin/bash
# Build the report tables and print the pooled intervals the text cites.
source ~/epistemics/.venv/bin/activate
cd /mnt/c/Users/Valentin/AI_x_Epistemics
python src/report_tables.py heldout
python - <<'PY'
import pandas as pd
t = pd.read_csv("results/tables/confirm_heldout.csv", index_col=0)
k = ["PE_b", "PE_b_lo", "PE_b_hi", "PE_c", "PE_c_lo", "PE_c_hi", "IE", "IE_lo", "IE_hi",
     "uptake", "uptake_lo", "uptake_hi", "R_a", "R_a_lo", "R_a_hi", "IE_sys_lo", "IE_sys_hi"]
print(t.loc["POOLED", k].round(3).to_string())
PY
