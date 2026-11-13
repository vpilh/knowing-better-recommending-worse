"""Find 4-bit checkpoints (AWQ / GPTQ / W4A16 / NVFP4) for the planned models from known quantizers."""
from huggingface_hub import HfApi

api = HfApi()
BASES = ["Qwen3-4B", "Qwen3-8B", "Qwen3-14B", "Qwen3.8-27B", "gemma-4-E4B-it", "gemma-4-12B-it",
         "gemma-4-31B-it", "Olmo-3-7B-Instruct", "Olmo-3.1-32B-Instruct", "Mistral-Small-3.2-24B-Instruct-2506"]
TRUSTED = ("Qwen/", "google/", "RedHatAI/", "nvidia/", "allenai/", "mistralai/", "neuralmagic/",
           "cyankiwi/", "QuantTrio/", "casperhansen/", "ISTA-DASLab/")
KEYS = ("awq", "gptq", "w4a16", "nvfp4", "int4", "4bit", "fp4")
for base in BASES:
    print(f"=== {base}")
    hits = []
    for m in api.list_models(search=base, sort="downloads", limit=60):
        mid = m.id.lower()
        if any(k in mid for k in KEYS) and not any(x in mid for x in ("gguf", "mlx", "vl-", "abliterated", "uncensored")):
            hits.append((m.downloads or 0, m.id, m.id.startswith(TRUSTED)))
    for d, mid, trusted in sorted(hits, reverse=True)[:8]:
        print(f"  {'*' if trusted else ' '} {mid:70s} {d:>9}")
