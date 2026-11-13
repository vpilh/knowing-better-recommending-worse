#!/bin/bash
# Run every model in sequence: start vLLM, wait until ready, run the items, stop.
# Usage: sweep.sh SPLIT [TAG_SUFFIX]      SPLIT = dev | heldout
# Progress: ~/epistemics/logs/sweep.log ; per-model run output: ~/epistemics/logs/run_<tag>_<split>.log
SPLIT="$1"
ROOT=/mnt/c/Users/Valentin/AI_x_Epistemics
LOG=~/epistemics/logs/sweep.log
source ~/epistemics/.venv/bin/activate
cd "$ROOT"
OLMO_T="--chat-template $ROOT/templates/allenai--Olmo-3-7B-Instruct.jinja"

# tag | checkpoint | extra vllm args
MODELS=(
  "qwen3-4b|Qwen/Qwen3-4B-AWQ|"
  "qwen3-8b|Qwen/Qwen3-8B-AWQ|"
  "qwen3-14b|Qwen/Qwen3-14B-AWQ|"
  "gemma4-e4b|google/gemma-4-E4B-it-qat-w4a16-ct|"
  "gemma4-12b|google/gemma-4-12B-it-qat-w4a16-ct|"
  "olmo3-7b|allenai/Olmo-3-7B-Instruct|$OLMO_T"
  "mistral-small-24b|Intel/Mistral-Small-3.2-24B-Instruct-2506-int4-AutoRound|"
  "qwen3.8-27b|RedHatAI/Qwen3.8-27B-INT4|--max-num-seqs 128"
  "gemma4-31b|google/gemma-4-31B-it-qat-w4a16-ct|"
  "olmo3.1-32b|cyankiwi/Olmo-3.1-32B-Instruct-AWQ-4bit|--chat-template $ROOT/templates/cyankiwi--Olmo-3.1-32B-Instruct-AWQ-4bit.jinja"
)
[ -n "$ONLY" ] && mapfile -t MODELS < <(printf '%s\n' "${MODELS[@]}" | grep -E "^($ONLY)\|")

for entry in "${MODELS[@]}"; do
  IFS='|' read -r tag ckpt extra <<< "$entry"
  name=$(echo "$ckpt" | tr '/' '_')
  echo "$(date '+%F %T') [$SPLIT] start $tag ($ckpt)" >> "$LOG"
  bash scripts/stop_server.sh > /dev/null
  # shellcheck disable=SC2086
  setsid bash scripts/serve.sh "$ckpt" $extra &
  ready=0
  for i in $(seq 1 380); do   # up to ~32 min, matching VLLM_ENGINE_READY_TIMEOUT_S
    sleep 5
    if grep -q "Application startup complete" ~/epistemics/logs/vllm_${name}.log 2>/dev/null; then ready=1; break; fi
    if grep -qE "RuntimeError|Error:" ~/epistemics/logs/vllm_${name}.log 2>/dev/null; then break; fi
  done
  if [ $ready -ne 1 ]; then
    echo "$(date '+%F %T') [$SPLIT] FAIL server $tag (see vllm_${name}.log)" >> "$LOG"
    continue
  fi
  if python src/run_model.py --model "$ckpt" --tag "${tag}-reason" --split "$SPLIT" --format reason \
       > ~/epistemics/logs/run_${tag}_${SPLIT}.log 2>&1; then
    echo "$(date '+%F %T') [$SPLIT] done  $tag" >> "$LOG"
    if [ "$SPLIT" = "heldout" ] && [ "${SYSFIX:-0}" = "1" ]; then   # optional: system-prompt fix
      if python src/run_model.py --model "$ckpt" --tag "${tag}-reason-sys" --split "$SPLIT" --format reason \
           --system --wrong-only --conditions neutral,pressure \
           > ~/epistemics/logs/run_${tag}_${SPLIT}_sys.log 2>&1; then
        echo "$(date '+%F %T') [$SPLIT] done  $tag (system prompt)" >> "$LOG"
      else
        echo "$(date '+%F %T') [$SPLIT] FAIL run $tag system prompt" >> "$LOG"
      fi
    fi
  else
    echo "$(date '+%F %T') [$SPLIT] FAIL run $tag (see run_${tag}_${SPLIT}.log)" >> "$LOG"
  fi
done
bash scripts/stop_server.sh > /dev/null
echo "$(date '+%F %T') [$SPLIT] sweep finished" >> "$LOG"
