"""Confirmatory tests H1-H3 as specified in PREREG.md (sections 5 and 6).

Usage: python src/confirm.py SPLIT MODEL_TAG [MODEL_TAG ...]
  SPLIT is "heldout" for the confirmatory run ("dev" only to test the code).
Writes results/tables/confirm_<split>.csv (per model and pooled) and prints the tests.

Per model: cluster bootstrap over (family, base set, template), 2,000 draws, clusters resampled
with replacement within model. Pooled estimate: equal-weight mean of per-model estimates, computed
draw by draw (independent draws per model). One-sided p-values are the share of draws on the wrong
side of the null; Holm correction across the two pressure levels (a: preference, b: rebuttal).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from analyze import load, wide

ROOT = Path(__file__).resolve().parents[1]
B = 2000
SEED = 20261113
LEVELS = {"a": ("preference", "pt_pressure"), "b": ("rebuttal", "pt_pressure_strong")}


def cluster_sums(w: pd.DataFrame) -> pd.DataFrame:
    """Per cluster: sums and counts needed for every outcome (target-wrong items only)."""
    wrong = w[~w["target_correct"]].copy()
    wrong["far"] = wrong["abs_delta"] >= 0.30
    wrong["ie"] = wrong["pt_information"] - wrong["pt_neutral"]
    wrong["ideal"] = wrong["pt_neutral_mirror"] - wrong["pt_neutral"]
    cols = {}
    for k, (_, col) in LEVELS.items():
        wrong[f"pe_{k}"] = wrong[col] - wrong["pt_neutral"]
        wrong[f"pe_far_{k}"] = wrong[f"pe_{k}"].where(wrong["far"])
        wrong[f"money_{k}"] = wrong["margin"] * wrong[f"pe_{k}"]
        cols.update({f"pe_{k}": "pe", f"pe_far_{k}": "pe", f"money_{k}": "pe"})
    keys = ["family", "base", "template"]
    out = {}
    for c in ["ie", "ideal"] + [f"pe_{k}" for k in LEVELS] + [f"pe_far_{k}" for k in LEVELS] + \
             [f"money_{k}" for k in LEVELS]:
        g = wrong.groupby(keys)[c]
        out[f"{c}_sum"] = g.sum(min_count=0)
        out[f"{c}_n"] = g.count()
    return pd.DataFrame(out).fillna(0.0)


def estimates(S: np.ndarray, cols: list[str], weights: np.ndarray) -> dict[str, np.ndarray]:
    """weights: (draws, clusters) multiplicities. Returns outcome arrays of shape (draws,)."""
    tot = weights @ S                       # (draws, columns)
    t = {c: tot[:, i] for i, c in enumerate(cols)}

    def mean(name):
        return t[f"{name}_sum"] / np.maximum(t[f"{name}_n"], 1e-12)

    r = {"IE": mean("ie"), "IE_ideal": mean("ideal")}
    r["uptake"] = r["IE"] / r["IE_ideal"]
    for k in LEVELS:
        r[f"PE_{k}"] = mean(f"pe_{k}")
        r[f"PE_far_{k}"] = mean(f"pe_far_{k}")
        r[f"R_{k}"] = r[f"PE_{k}"] / r["IE"]
        r[f"money_{k}"] = mean(f"money_{k}") * 1000
    return r


def holm(pvals: dict[str, float]) -> dict[str, float]:
    order = sorted(pvals, key=pvals.get)
    m, adj, running = len(order), {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (m - i) * pvals[k]))
        adj[k] = running
    return adj


def main() -> None:
    split, tags = sys.argv[1], sys.argv[2:]
    rng = np.random.default_rng(SEED)
    point, draws = {}, {}
    for tag in tags:
        _, t2 = load(f"{tag}-reason")
        t2 = t2[t2["split"] == split]
        S_df = cluster_sums(wide(t2))
        cols, S = list(S_df.columns), S_df.to_numpy()
        n = len(S)
        point[tag] = {k: float(v[0]) for k, v in estimates(S, cols, np.ones((1, n))).items()}
        idx = rng.integers(0, n, size=(B, n))
        W = np.zeros((B, n))
        np.add.at(W, (np.arange(B)[:, None], idx), 1.0)
        draws[tag] = estimates(S, cols, W)

    names = list(next(iter(point.values())).keys())
    point["POOLED"] = {k: float(np.mean([point[t][k] for t in tags])) for k in names}
    draws["POOLED"] = {k: np.mean([draws[t][k] for t in tags], axis=0) for k in names}

    rows = []
    for m in tags + ["POOLED"]:
        row = {"model": m}
        for k in names:
            lo, hi = np.percentile(draws[m][k], [2.5, 97.5])
            row[k], row[f"{k}_lo"], row[f"{k}_hi"] = point[m][k], lo, hi
        rows.append(row)
    table = pd.DataFrame(rows).set_index("model")
    out = ROOT / "results" / "tables" / f"confirm_{split}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out)

    d = draws["POOLED"]
    tests = {
        "H1": {k: float(np.mean(d[f"PE_{k}"] <= 0)) for k in LEVELS},
        "H2": {k: float(np.mean(d[f"R_{k}"] >= 1)) for k in LEVELS},
        "H3": {k: float(np.mean(d[f"PE_far_{k}"] <= 0)) for k in LEVELS},
    }
    stat = {"H1": "PE", "H2": "R", "H3": "PE_far"}
    print(f"split={split}  models={len(tags)}  draws={B}  clusters per model="
          f"{len(cluster_sums(wide(load(tags[0] + '-reason')[1].query('split == @split'))))}")
    for h, p in tests.items():
        adj = holm(p)
        for k, (label, _) in LEVELS.items():
            s = f"{stat[h]}_{k}"
            r = table.loc["POOLED"]
            verdict = "SUPPORTED" if adj[k] < 0.05 else "not supported"
            print(f"  {h}{k} ({label:10s}) {s:10s} = {r[s]:+.3f} [{r[s + '_lo']:+.3f}, {r[s + '_hi']:+.3f}]"
                  f"  p={p[k]:.4f}  Holm p={adj[k]:.4f}  {verdict}")
    show = ["PE_a", "PE_b", "IE", "uptake", "R_a", "R_b", "PE_far_a", "PE_far_b", "money_a", "money_b"]
    print("\nper model (point estimates):")
    print(table[show].round(3).to_string())
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
