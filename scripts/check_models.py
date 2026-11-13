"""Check candidate checkpoints on Hugging Face: gating, access for the logged-in user, size."""
from huggingface_hub import HfApi
from huggingface_hub.utils import GatedRepoError, HfHubHTTPError

CANDIDATES = [
    "Qwen/Qwen3-4B-AWQ", "Qwen/Qwen3-8B-AWQ", "Qwen/Qwen3-14B-AWQ",
    "Qwen/Qwen3-4B", "Qwen/Qwen3-8B", "Qwen/Qwen3-14B", "Qwen/Qwen3.8-27B",
    "google/gemma-4-E4B-it", "google/gemma-4-12B-it", "google/gemma-4-31B-it",
    "allenai/Olmo-3-7B-Instruct", "allenai/Olmo-3.1-32B-Instruct",
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
]
api = HfApi()
for repo in CANDIDATES:
    try:
        info = api.model_info(repo, files_metadata=True)
        size = sum((s.size or 0) for s in info.siblings if s.rfilename.endswith(".safetensors"))
        gated = info.gated or "no"
        try:  # can we actually download? (fails if licence not accepted)
            api.auth_check(repo)
            access = "ok"
        except GatedRepoError:
            access = "NEEDS LICENCE"
        print(f"{repo:50s} gated={str(gated):6s} access={access:14s} weights={size/1e9:6.1f} GB  "
              f"licence={(info.card_data or {}).get('license', '?')}")
    except HfHubHTTPError as e:
        print(f"{repo:50s} ERROR {e.__class__.__name__}: {str(e)[:80]}")
