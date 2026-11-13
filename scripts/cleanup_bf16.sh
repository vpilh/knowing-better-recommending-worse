#!/bin/bash
# Remove bf16 weights no longer used (main sweep uses 4-bit W4A16 checkpoints).
# Kept: Qwen3-8B (bf16 quantization check), Olmo-3-7B-Instruct (runs in bf16), all 4-bit repos.
source ~/epistemics/.venv/bin/activate
hf cache rm -y \
  model/Qwen/Qwen3-4B \
  model/Qwen/Qwen3-14B \
  model/Qwen/Qwen3.8-27B \
  model/google/gemma-4-E4B-it \
  model/google/gemma-4-12B-it \
  model/google/gemma-4-31B-it \
  model/mistralai/Mistral-Small-3.2-24B-Instruct-2506 \
  model/allenai/Olmo-3.1-32B-Instruct 2>&1 | tail -5
hf cache ls 2>&1 | tail -14
df -h ~ | tail -1
