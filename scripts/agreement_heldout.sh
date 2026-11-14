#!/bin/bash
source ~/epistemics/.venv/bin/activate
cd /mnt/c/Users/Valentin/AI_x_Epistemics
python scripts/handcoding_agreement.py heldout | tee results/tables/handcoding_agreement_heldout.txt
echo; echo "rule shares, held-out (all flipped replies):"; cat results/tables/capitulation_heldout.csv
