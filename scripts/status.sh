#!/bin/bash
# Sweep progress: sweep log, line counts per model run, current server.
date '+now: %F %T'
echo "--- sweep log"; cat ~/epistemics/logs/sweep.log 2>/dev/null
echo "--- results (items in turn 1 / readouts in turn 2)"
for d in /mnt/c/Users/Valentin/AI_x_Epistemics/results/raw/*-reason; do
  printf "%-26s %6s %6s\n" "$(basename "$d")" "$(cat "$d/turn1.jsonl" 2>/dev/null | wc -l)" "$(cat "$d/turn2.jsonl" 2>/dev/null | wc -l)"
done
echo "--- server"; pgrep -af "[v]llm serve" | sed 's/.*vllm serve //' | cut -c1-80
