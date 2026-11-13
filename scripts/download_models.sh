#!/bin/bash
# Download the 4-bit (W4A16) checkpoints used in the main sweep, in order of need.
# bf16 weights already downloaded: Qwen3-4B/8B/14B, Olmo-3-7B, gemma-4-E4B/12B, Mistral-Small-3.2, Qwen3.8-27B.
# Log: ~/epistemics/logs/download.log (one line per model when it finishes).
source ~/epistemics/.venv/bin/activate
mkdir -p ~/epistemics/logs
LOG=~/epistemics/logs/download.log
MODELS=(
  google/gemma-4-E4B-it-qat-w4a16-ct
  google/gemma-4-12B-it-qat-w4a16-ct
  Qwen/Qwen3-14B-AWQ
  Intel/Mistral-Small-3.2-24B-Instruct-2506-int4-AutoRound
  RedHatAI/Qwen3.8-27B-INT4
  google/gemma-4-31B-it-qat-w4a16-ct
  cyankiwi/Olmo-3.1-32B-Instruct-AWQ-4bit
)
for m in "${MODELS[@]}"; do
  echo "$(date '+%F %T') start $m" >> "$LOG"
  if hf download "$m" --exclude "consolidated*" --exclude "original/*" --exclude "*.gguf" >> ~/epistemics/logs/download_detail.log 2>&1; then
    echo "$(date '+%F %T') done  $m" >> "$LOG"
  else
    echo "$(date '+%F %T') FAIL  $m (see download_detail.log)" >> "$LOG"
  fi
done
echo "$(date '+%F %T') all finished" >> "$LOG"
