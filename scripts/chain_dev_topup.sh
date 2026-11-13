#!/bin/bash
# Wait for the running sweep to finish, then rerun the dev sweep for all models. The runner resumes,
# so only the new condition (preference + goal) is generated for models that are already done.
while pgrep -f "[s]weep.sh" > /dev/null; do sleep 30; done
echo "$(date '+%F %T') [dev] top-up for preference+goal starts" >> ~/epistemics/logs/sweep.log
bash /mnt/c/Users/Valentin/AI_x_Epistemics/scripts/sweep.sh dev
