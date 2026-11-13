#!/bin/bash
# Start a vLLM server with the project's fixed settings. Usage: serve.sh MODEL [extra vllm args]
# QUANT=nvfp4 serve.sh MODEL  -> online NVFP4 quantization of all linear layers at load time.
# Log: ~/epistemics/logs/vllm_<name>.log
set -e
MODEL="$1"; shift
cd ~/epistemics && source .venv/bin/activate
export CUDA_HOME=/usr/local/cuda
export PATH="$CUDA_HOME/bin:$PATH"
export VLLM_ENGINE_READY_TIMEOUT_S=1800   # large 4-bit models need more than the default 600 s
mkdir -p ~/epistemics/logs
NAME=$(echo "$MODEL" | tr '/' '_')
QARGS=()
if [ "${QUANT:-}" = "nvfp4" ]; then
  QARGS=(--quantization online --quantization-config '{"linear": "nvfp4_per_token", "moe": "nvfp4_per_token"}')
fi
exec vllm serve "$MODEL" --max-model-len 4096 --gpu-memory-utilization 0.90 --seed 0 \
  --generation-config vllm "${QARGS[@]}" "$@" > ~/epistemics/logs/vllm_${NAME}.log 2>&1
