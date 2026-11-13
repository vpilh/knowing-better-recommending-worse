#!/bin/bash
# Build report figures for a split. Usage: make_figures.sh SPLIT
source ~/epistemics/.venv/bin/activate
export PATH="$HOME/.local/bin:$PATH"
python -c "import matplotlib" 2>/dev/null || uv pip install -q matplotlib
cd /mnt/c/Users/Valentin/AI_x_Epistemics/src && python figures.py "${1:-dev}"
