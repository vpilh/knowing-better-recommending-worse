#!/bin/bash
# Print the first part of a cached model's chat template. Usage: show_template.sh org--name
d=$(ls -d ~/.cache/huggingface/hub/models--$1/snapshots/* | head -1)
echo "snapshot: $d"; ls "$d"
if [ -f "$d/chat_template.jinja" ]; then
  head -c 1500 "$d/chat_template.jinja"
else
  python3 - "$d/tokenizer_config.json" <<'EOF'
import json, sys
print(json.load(open(sys.argv[1])).get("chat_template", "")[:1500])
EOF
fi
