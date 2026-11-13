#!/bin/bash
# Rerun the held-out sweep for the two models whose servers were stopped by the old error check (13 Nov).
ONLY="mistral-small-24b|qwen3.8-27b" bash /mnt/c/Users/Valentin/AI_x_Epistemics/scripts/sweep.sh heldout
