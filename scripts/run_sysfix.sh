#!/bin/bash
# Exploratory system-prompt mitigation (PREREG section 9) on held-out, all nine models.
# The main held-out runs are complete, so run_model.py resumes them without new requests.
SYSFIX=1 bash /mnt/c/Users/Valentin/AI_x_Epistemics/scripts/sweep.sh heldout
