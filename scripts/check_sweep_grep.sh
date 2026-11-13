grep -n "port" /mnt/c/Users/Valentin/AI_x_Epistemics/scripts/serve.sh; which ss
f=~/epistemics/logs/vllm_Intel_Mistral-Small-3.2-24B-Instruct-2506-int4-AutoRound.log
echo "fatal matches mistral: $(grep -vE '^\S*\s*W[0-9]{4} |WARNING' $f | grep -cE 'RuntimeError|Error:')"
f=~/epistemics/logs/vllm_RedHatAI_Qwen3.8-27B-INT4.log
echo "fatal matches qwen27: $(grep -vE '^\S*\s*W[0-9]{4} |WARNING' $f | grep -cE 'RuntimeError|Error:')"
