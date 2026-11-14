"""Diagnose the system-prompt run: baselines with and without the prompt, and sample replies where it backfires."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import load  # noqa: E402

TAGS = "qwen3-4b qwen3-8b qwen3-14b qwen3.8-27b gemma4-e4b gemma4-12b gemma4-31b olmo3-7b mistral-small-24b".split()
print(f"{'model':18s} {'P(T)|neu':>9s} {'neu+sys':>8s} {'P(T)|pref':>9s} {'pref+sys':>8s}   (target-wrong items)")
texts = {}
for t in TAGS:
    _, a = load(t + "-reason")
    _, s = load(t + "-reason-sys")
    a = a[(a["split"] == "heldout") & (~a["target_correct"])]
    s = s[s["split"] == "heldout"]
    m = lambda d, c: d.loc[d["condition"] == c, "p_target"].mean()  # noqa: E731
    print(f"{t:18s} {m(a, 'neutral'):9.3f} {m(s, 'neutral'):8.3f} {m(a, 'pressure'):9.3f} {m(s, 'pressure'):8.3f}")
    texts[t] = s[(s["condition"] == "pressure") & (s["p_target"] > 0.5)]

for t in ("qwen3-4b", "olmo3-7b", "qwen3-14b"):
    d = texts[t]
    print(f"\n===== {t}: {len(d)} flipped under the system prompt; two examples (reply tail)")
    for _, r in d.sample(n=min(2, len(d)), random_state=1).iterrows():
        print(f"--- {r['item_id']}\n{str(r['text'])[-700:]}\n")
