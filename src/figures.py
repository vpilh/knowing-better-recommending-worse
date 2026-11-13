"""Report figures. Usage: python src/figures.py SPLIT [MODEL_TAG ...]

fig1_curves_<split>: P(target) against the target's signed distance from the threshold, one panel
    per model, four conditions. x < 0: the target is the worse option; x > 0: the better one.
fig2_effects_<split>: (a) pressure effect per model with 95% cluster-bootstrap intervals,
    (b) expected money lost per 1,000 pushed decisions. Needs results/tables/confirm_<split>.csv.
Writes PDF and PNG to results/figures/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analyze import load  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "figures"

# Reference palette (dataviz skill), slots 1-3 validated all-pairs in light mode; neutral in ink.
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
COND = {  # condition: (label, color, linestyle, marker)
    "neutral": ("Neutral", INK2, (0, (4, 2)), "o"),
    "pressure": ("Preference", "#eb6834", "-", "s"),
    "pressure_strong": ("Rebuttal", "#2a78d6", "-", "^"),
    "information": ("Information", "#1baf7a", "-", "D"),
}
NAMES = {"qwen3-4b": "Qwen3 4B", "qwen3-8b": "Qwen3 8B", "qwen3-14b": "Qwen3 14B",
         "qwen3.8-27b": "Qwen3.8 27B", "gemma4-e4b": "Gemma 4 E4B", "gemma4-12b": "Gemma 4 12B",
         "gemma4-31b": "Gemma 4 31B", "olmo3-7b": "OLMo 3 7B", "olmo3.1-32b": "OLMo 3.1 32B",
         "mistral-small-24b": "Mistral Small 24B"}
ORDER = list(NAMES)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6, "figure.facecolor": "white",
    "axes.facecolor": "white", "savefig.dpi": 300, "legend.frameon": False,
})


def tags_from_args(split: str) -> list[str]:
    tags = sys.argv[2:] or [t for t in ORDER if (ROOT / "results" / "raw" / f"{t}-reason" / "turn2.jsonl").exists()]
    return [t for t in ORDER if t in tags]


def curve_data(tag: str, split: str) -> pd.DataFrame:
    _, t2 = load(f"{tag}-reason")
    t2 = t2[t2["split"] == split].copy()
    # target's side: x > 0 when the target is the better option
    t1 = t2["target_letter"] == t2["correct_letter"]
    t2["x"] = np.where(t1, t2["abs_delta"], -t2["abs_delta"]) * 100
    return t2.groupby(["condition", "x"])["p_target"].mean().reset_index()


def fig1(split: str, tags: list[str]) -> None:
    n = len(tags)
    cols = min(5, n)
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(7.0, 1.75 * rows + 0.5), sharex=True, sharey=True,
                             squeeze=False)
    for ax, tag in zip(axes.flat, tags):
        d = curve_data(tag, split)
        ax.axvline(0, color=GRID, lw=0.8, zorder=0)
        ax.axhline(0.5, color=GRID, lw=0.8, zorder=0)
        for cond, (label, color, ls, marker) in COND.items():
            s = d[d["condition"] == cond].sort_values("x")
            if s.empty:
                continue
            ax.plot(s["x"], s["p_target"], color=color, ls=ls, lw=1.6, marker=marker, ms=3.2,
                    mec="white", mew=0.6, label=label, zorder=3)
        ax.set_title(NAMES.get(tag, tag), fontsize=8, color=INK, pad=3)
        ax.set_ylim(-0.03, 1.03)
        ax.set_yticks([0, 0.5, 1])
        ax.set_xticks([-50, 0, 50])
        ax.tick_params(length=2, width=0.5)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    for ax in axes.flat[n:]:
        ax.set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel("P(target)")
    for ax in axes.flat[:n]:
        ax.tick_params(labelbottom=True)
    fig.supxlabel("Target's distance from the threshold θ* (%): left of 0 the target is the worse "
                  "option, right of 0 the better one", fontsize=8, color=INK)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.0), fontsize=8,
               handlelength=2.4)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    save(fig, f"figA1_curves_{split}")


def fig_levels(split: str, tags: list[str]) -> None:
    """Headline: share of pushed decisions that go to the user's worse option, per condition."""
    rows = []
    for tag in tags:
        _, t2 = load(f"{tag}-reason")
        t2 = t2[(t2["split"] == split) & (~t2["target_correct"])]
        m = t2.groupby("condition")["p_target"].mean()
        rows.append({"model": tag, **{c: m.get(c, np.nan) for c in ("neutral", "pressure_strong", "pressure")}})
    d = pd.DataFrame(rows).set_index("model")
    d = d.loc[(d["pressure"] - d["neutral"]).sort_values().index]
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(5.2, 0.3 * len(d) + 1.0))
    for i, (_, r) in enumerate(d.iterrows()):
        lo, hi = r.min(), r.max()
        ax.plot([lo, hi], [i, i], color=GRID, lw=2.2, zorder=1, solid_capstyle="round")
    for cond, off in (("neutral", 0.0), ("pressure_strong", -0.16), ("pressure", 0.16)):
        label, color, _, marker = COND[cond]
        ax.scatter(d[cond], y + off, s=34, marker=marker, color=color, edgecolor="white", linewidth=0.8,
                   label=label, zorder=3)
    ax.set_yticks(y, [NAMES.get(i, i) for i in d.index])
    ax.set_xlim(-0.02, 1.0)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("Recommends the worse option the user pushed for (mean P)")
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(length=2, width=0.5)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=3, fontsize=8, handletextpad=0.3,
              scatterpoints=1)
    fig.tight_layout()
    save(fig, f"fig1_levels_{split}")


def fig2(split: str, tags: list[str]) -> None:
    t = pd.read_csv(ROOT / "results" / "tables" / f"confirm_{split}.csv", index_col=0)
    tags = [x for x in tags if x in t.index]
    t = t.loc[tags].sort_values("PE_a")
    y = np.arange(len(t))
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 0.32 * len(t) + 1.0), sharey=True,
                               gridspec_kw={"width_ratios": [1.15, 1]})
    for k, cond, off in (("a", "pressure", 0.14), ("b", "pressure_strong", -0.14)):
        label, color, _, marker = COND[cond]
        pe, lo, hi = t[f"PE_{k}"], t[f"PE_{k}_lo"], t[f"PE_{k}_hi"]
        a.errorbar(pe, y + off, xerr=[pe - lo, hi - pe], fmt=marker, color=color, ms=4.5, mec="white",
                   mew=0.6, elinewidth=1.2, capsize=0, label=label, zorder=3)
        m = t[f"money_{k}"] / 1000  # thousands of dollars per 1,000 decisions = dollars per decision
        b.barh(y + off, m, height=0.26, color=color, label=label, zorder=3)
    a.axvline(0, color=INK2, lw=0.6)
    a.set_yticks(y, [NAMES.get(i, i) for i in t.index])
    a.set_xlabel("pressure effect on P(target), target wrong")
    a.set_xlim(-0.05, 1.0)
    b.set_xlabel("expected loss per pushed decision ($)")
    for ax in (a, b):
        ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
        ax.tick_params(length=2, width=0.5)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    a.set_title("(a) Shift toward the user's option", fontsize=8, loc="left", color=INK)
    b.set_title("(b) Money lost to pressure", fontsize=8, loc="left", color=INK)
    a.legend(loc="lower right", fontsize=7.5)
    fig.tight_layout()
    save(fig, f"fig2_effects_{split}")


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT / name}.pdf/.png")


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    tags = tags_from_args(split)
    fig_levels(split, tags)
    fig1(split, tags)
    if (ROOT / "results" / "tables" / f"confirm_{split}.csv").exists():
        fig2(split, tags)
