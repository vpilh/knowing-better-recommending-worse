#!/bin/bash
# Stop any running server, install bitsandbytes, report download progress.
pkill -f "vllm serve" || true
source ~/epistemics/.venv/bin/activate
export PATH="$HOME/.local/bin:$PATH"
uv pip install -q bitsandbytes 2>&1 | tail -2
python -c "import bitsandbytes as b; print('bitsandbytes', b.__version__)"
tail -3 ~/epistemics/logs/download.log
