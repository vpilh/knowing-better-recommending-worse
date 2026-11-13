#!/bin/bash
# Build and check the blind hand-coding workbook. Usage: build_handcoding.sh [SPLIT]
source ~/epistemics/.venv/bin/activate
export PATH="$HOME/.local/bin:$PATH"
python -c "import openpyxl" 2>/dev/null || uv pip install -q openpyxl
cd /mnt/c/Users/Valentin/AI_x_Epistemics
python scripts/make_handcoding_xlsx.py "${1:-dev}"
python - "${1:-dev}" <<'EOF'
import sys, openpyxl
wb = openpyxl.load_workbook(f"results/tables/capitulation_handcoding_{sys.argv[1]}.xlsx")
ws = wb["Coding"]
print(wb.sheetnames, "rows:", ws.max_row - 1, "cols:", ws.max_column)
print("row 1:", [c.value for c in ws[2]][:4], "| reply starts:", str(ws["E2"].value)[:80])
print("hidden:", [k for k, d in ws.column_dimensions.items() if d.hidden])
EOF
