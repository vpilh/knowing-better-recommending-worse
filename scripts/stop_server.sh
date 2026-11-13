#!/bin/bash
# Stop the vLLM server. The [v] pattern keeps pkill from matching its own command line.
pkill -f "[v]llm serve" && echo "stopped" || echo "no server running"
for i in $(seq 1 30); do pgrep -f "[v]llm serve" > /dev/null || break; sleep 1; done
nvidia-smi --query-gpu=memory.used --format=csv,noheader
