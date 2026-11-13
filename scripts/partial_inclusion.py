"""Inclusion check (neutral P(correct) on dev) from whatever readouts exist so far. Usage: TAG"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from analyze import load  # noqa: E402

_, t2 = load(f"{sys.argv[1]}-reason")
n = t2[(t2["condition"] == "neutral") & (t2["split"] == "dev")]
print(f"neutral readouts so far: {len(n)} of 900; missing: {n['pA'].isna().sum()}")
print(f"mean P(correct) so far: {n['p_correct'].mean():.3f} (threshold 0.60)")
print(n.groupby("family")["p_correct"].agg(["count", "mean"]).round(3).to_string())
