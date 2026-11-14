#!/bin/bash
source ~/epistemics/.venv/bin/activate
cd /mnt/c/Users/Valentin/AI_x_Epistemics/src
python money_family.py heldout qwen3-4b qwen3-8b qwen3-14b qwen3.8-27b gemma4-e4b gemma4-12b gemma4-31b olmo3-7b mistral-small-24b
python -c "import pandas as pd; t=pd.read_csv('../results/tables/confirm_heldout.csv',index_col=0); print(t[['PE_a','IE','R_a','R_a_lo','R_a_hi']].round(3).to_string())"
cd /mnt/c/Users/Valentin/AI_x_Epistemics && bash scripts/make_figures.sh heldout
