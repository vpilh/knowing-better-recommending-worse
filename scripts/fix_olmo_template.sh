#!/bin/bash
# OLMo 3 chat template tests `tools is none`; vLLM renders it with `tools` undefined, which crashes
# in `tojson`. Make the test robust; the rendered prompt without tools is unchanged.
set -e
OUT=/mnt/c/Users/Valentin/AI_x_Epistemics/templates
mkdir -p "$OUT"
for repo in allenai--Olmo-3-7B-Instruct; do
  d=$(ls -d ~/.cache/huggingface/hub/models--$repo/snapshots/* | head -1)
  sed -e 's/tools is not none/(tools is defined and tools is not none)/g' \
      -e 's/tools is none/(tools is not defined or tools is none)/g' \
      "$d/chat_template.jinja" > "$OUT/$repo.jinja"
  echo "wrote $OUT/$repo.jinja"; grep -o "tools is[^-]*" "$OUT/$repo.jinja" | sort | uniq -c
done
