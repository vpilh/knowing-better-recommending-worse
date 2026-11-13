#!/bin/bash
# Stop chained sweeps, the sweep, the runner and the vLLM server. Usage: stop_all.sh "reason for the log"
pkill -f "[c]hain_dev_topup" ; pkill -f "[s]weep.sh" ; pkill -f "[r]un_model.py"
bash /mnt/c/Users/Valentin/AI_x_Epistemics/scripts/stop_server.sh
echo "still running: $(pgrep -af '[s]weep|[r]un_model|[v]llm serve' | wc -l)"
[ -n "$1" ] && echo "$(date '+%F %T') stopped by hand: $1" >> ~/epistemics/logs/sweep.log
