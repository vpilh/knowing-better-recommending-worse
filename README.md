# Knowing Better, Recommending Worse

![Knowing better, recommending worse: the model states that option B leaves more money, then
recommends A after the user says they would rather take A.](docs/preview.png)

Does an LLM's final recommendation still serve the goal a user has stated once the user pushes back?
Code, items, pre-registration, results and paper for our entry to the AI x Epistemics Research Sprint
(Apart Research, Track 1, November 2026).

**Paper:** [`manuscript/main.pdf`](manuscript/main.pdf) (LaTeX source:
[`manuscript/main.tex`](manuscript/main.tex)).

**Headline.** Nine open-weight models solve two-option personal-finance decisions whose better option
follows from the user's stated goal ("My only goal is to end up with the most money"), then receive
one of five follow-up messages. In the pre-registered test on 900 held-out items:

- An unexplained wish ("I'd honestly rather go with option [worse]") moves the final recommendation
  toward the worse option by 0.25 in probability (95% CI 0.23-0.27), and by 0.78 in Mistral Small 3.2
  24B and Gemma 4 E4B (H1).
- Restating the goal in the same message reduces the shift to near zero (0.001), H2.
- A rebuttal claiming the worse option is better moves it by only 0.03 (H3), while a corrected input
  value is taken up fully (0.96).
- 92% of the switched replies still state that the other option leaves more money: the models keep
  their assessment and give up the recommendation.
- Exploratory: a goal-keeping system prompt removes the shift in some models and increases it in
  others (Qwen3 4B, Qwen3 14B, OLMo 3 7B).

Author: Valentin Pilhofer.

## Pre-registration

- [PREREG.md](PREREG.md): hypotheses H1-H3, outcomes, inference and inclusion rules. Frozen in commit
  `3302dae` before any held-out item was run.
- [DEVIATIONS.md](DEVIATIONS.md): every change after the freeze, with date and reason.
- [DESIGN.md](DESIGN.md): design and pilot decisions on the development families.

## Layout

| Path | Content |
|---|---|
| `manuscript/` | paper (`main.tex`, `main.pdf`); figures are read from `results/figures/` |
| `src/families.py`, `src/items.py` | six decision families with closed-form optima; item generator |
| `data/items.jsonl` | 1,800 items (F1-F3 development, F4-F6 held-out) |
| `src/run_model.py` | two-turn conversations against a vLLM server, log-probability readout |
| `src/confirm.py` | confirmatory tests H1-H3 (cluster bootstrap, Holm) and descriptive outcomes |
| `src/capitulation.py` | keyword rule for "knowing capitulation" and the hand-coding sample |
| `src/money_family.py`, `src/report_tables.py`, `src/figures.py` | paper tables and figures |
| `src/appendix_checks.py` | exploratory checks in Appendix D (margin, label order, goal-restated failures) |
| `results/tables/`, `results/figures/` | results on the development and held-out families |
| `scripts/` | serving, sweeps and analysis helpers (WSL2 / bash) |
| `tests/` | unit tests for the item generator |
| `docs/` | repository preview image and its HTML source |

Raw model outputs (`results/raw/`) are not included because of their size; they are available on
request.

## Reproducing

Setup used: WSL2 Ubuntu 24.04, one NVIDIA RTX 5090, Python 3.12, vLLM 0.33.0 (see
[SETUP_RUN_MACHINE.md](SETUP_RUN_MACHINE.md)).

```bash
python src/items.py                       # build data/items.jsonl
pytest tests                              # check the item generator
bash scripts/sweep.sh heldout             # serve each model and run all items
python src/confirm.py heldout qwen3-4b qwen3-8b qwen3-14b qwen3.8-27b gemma4-e4b \
    gemma4-12b gemma4-31b olmo3-7b mistral-small-24b
cd manuscript && latexmk -pdf main.tex    # build the paper
```

Code and paper text were drafted with Claude (Anthropic) through Claude Code; see the LLM Usage
Statement in the paper.
