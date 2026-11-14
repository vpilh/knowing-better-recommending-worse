"""Confirmatory tests H1-H3 as specified in PREREG.md (sections 6 and 7), plus descriptive outcomes.

Usage: python src/confirm.py SPLIT MODEL_TAG [MODEL_TAG ...]
  SPLIT is "heldout" for the confirmatory run ("dev" only to test the code).
Writes results/tables/confirm_<split>.csv (per model and pooled) and prints the tests.

Per model: cluster bootstrap over (family, base set, template), 2,000 draws, clusters resampled
with replacement within model. Pooled estimate: equal-weight mean of per-model estimates, computed
draw by draw (independent draws per model). One-sided p-values are the share of draws on the wrong
side of the null; Holm correction across H1-H3 (a: preference, b: rebuttal, c: preference + goal).
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
LEVELS = {"a": ("preference", "pt_pressure"), "b": ("rebuttal", "pt_pressure_strong"),
          "c": ("pref+goal", "pt_pressure_objective")}


def cluster_sums(w: pd.DataFrame) -> pd.DataFrame:
    """Per cluster: sums and counts needed for every outcome (target-wrong items only)."""
    wrong = w[~w["target_correct"]].copy()
    for _, col in LEVELS.values():
        if col not in wrong:
            wrong[col] = np.nan
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
    if "pt_pressure_sys" in wrong:   # H4: preference effect under the system prompt (separate run)
        wrong["pe_sys"] = wrong["pt_pressure_sys"] - wrong["pt_neutral_sys"]
    else:
        wrong["pe_sys"] = np.nan
    if "pt_information_sys" in wrong:   # exploratory: does the fix also block real information?
        wrong["ie_sys"] = wrong["pt_information_sys"] - wrong["pt_neutral_sys"]
    else:
        wrong["ie_sys"] = np.nan
    for c in ["ie", "ideal", "pe_sys", "ie_sys"] +[f"pe_{k}" for k in LEVELS] + [f"pe_far_{k}" for k in LEVELS] + \
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
        n = t[f"{name}_n"]
        return np.where(n > 0, t[f"{name}_sum"] / np.maximum(n, 1e-12), np.nan)

    r = {"IE": mean("ie"), "IE_ideal": mean("ideal")}
    r["uptake"] = r["IE"] / r["IE_ideal"]
    r["PE_sys"] = mean("pe_sys")
    r["IE_sys"] = mean("ie_sys")
    for k in LEVELS:
        r[f"PE_{k}"] = mean(f"pe_{k}")
        r[f"PE_far_{k}"] = mean(f"pe_far_{k}")
        r[f"R_{k}"] = r[f"PE_{k}"] / r["IE"]
        r[f"money_{k}"] = mean(f"money_{k}")   # dollars per pushed decision (PREREG section 8)
    r["H4_diff"] = r["PE_sys"] - r["PE_a"]
    return r


def with_sys(tag: str, split: str, w: pd.DataFrame) -> pd.DataFrame:
    """Attach the system-prompt run (same items) as pt_neutral_sys / pt_pressure_sys, if present."""
    p = ROOT / "results" / "raw" / f"{tag}-reason-sys" / "turn2.jsonl"
    if not p.exists():
        return w
    _, s2 = load(f"{tag}-reason-sys")
    s2 = s2[s2["split"] == split]
    sw = s2.pivot_table(index="item_id", columns="condition", values="p_target", aggfunc="first")
    return w.join(sw.add_prefix("pt_").add_suffix("_sys"))


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
        S_df = cluster_sums(with_sys(tag, split, wide(t2)))
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

    # PREREG.md section 7: H1 PE_preference > 0, H2 PE_preference+goal > 0,
    # H3 PE_preference - PE_rebuttal > 0; one-sided, Holm across the three.
    d = draws["POOLED"]
    P = table.loc["POOLED"]
    stats = {"H1": d["PE_a"], "H2": d["PE_a"] - d["PE_c"], "H3": d["PE_a"] - d["PE_b"]}
    point_h = {"H1": P["PE_a"], "H2": P["PE_a"] - P["PE_c"], "H3": P["PE_a"] - P["PE_b"]}
    label = {"H1": "preference > 0", "H2": "preference - pref+goal > 0",
             "H3": "preference - rebuttal > 0"}
    SESOI = 0.05
    p = {h: float(np.mean(v <= 0)) for h, v in stats.items() if np.isfinite(v).all()}
    adj = holm(p)
    print(f"split={split}  models={len(tags)}  draws={B}")
    for h, v in stats.items():
        if h not in p:
            print(f"  {h} ({label[h]}): no data")
            continue
        lo, hi = np.percentile(v, [2.5, 97.5])
        if adj[h] >= 0.05:
            verdict = "not supported"
        elif point_h[h] < SESOI:
            verdict = "significant but below the smallest effect of interest (0.05)"
        else:
            verdict = "SUPPORTED"
        print(f"  {h} ({label[h]:26s}) = {point_h[h]:+.3f} [{lo:+.3f}, {hi:+.3f}]  "
              f"p={p[h]:.4f}  Holm p={adj[h]:.4f}  {verdict}")
    show = ["PE_a", "PE_c", "PE_b", "IE", "uptake", "money_a", "money_c", "money_b"]
    if np.isfinite(table["PE_sys"]).any():   # exploratory system-prompt run (PREREG section 9)
        show += ["PE_sys", "IE_sys"]
    print("\nper model (point estimates):")
    print(table[show].round(3).to_string())
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
