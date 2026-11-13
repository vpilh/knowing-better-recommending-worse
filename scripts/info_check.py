"""Information condition vs the model's own accuracy on the mirrored item, by family.
Usage: info_check.py TAG [TAG ...]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import load, wide  # noqa: E402

for tag in sys.argv[1:]:
    _, t2 = load(f"{tag}-reason")
    w = wide(t2[t2["split"] == "dev"])
    wrong = w[~w["target_correct"]]
    g = wrong.groupby("family")
    print(f"\n{tag}: target-wrong items; after the correction the target IS the better option")
    print("  family  P(T|neutral)  P(T|info)  P(T|neutral, mirror item) = own accuracy there   info/ceiling")
    for fam, d in g:
        ceil = d["pt_neutral_mirror"].mean()
        print(f"  {fam:6s}  {d['pt_neutral'].mean():12.3f}  {d['pt_information'].mean():9.3f}  "
              f"{ceil:12.3f}{'':35s}{d['pt_information'].mean() / ceil:8.2f}")
