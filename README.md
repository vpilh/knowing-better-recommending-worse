# Knowing better, recommending worse

Code, items, pre-registration and results for a study of how user pushback moves LLM recommendations
on personal-finance decisions with a computable optimum (AI x Epistemics Research Sprint, Apart
Research, Track 1, November 2026).

**Finding.** When a user who has stated that their only goal is the most money says they would rather
take the worse option, several open-weight LLMs switch their final recommendation to it, while
stating that the other option leaves more money. Restating the goal in the same message removes the
shift; a claim that the worse option is better barely moves it; correct information is taken up
almost fully. Pre-registered test on 900 held-out items and nine models (Qwen3, Qwen3.8, Gemma 4,
OLMo 3, Mistral Small 3.2).

Author: Valentin Pilhofer, Chair of Statistics and Risk Management, University of Regensburg.

## Pre-registration

- [PREREG.md](PREREG.md): hypotheses H1-H3, outcomes, inference and inclusion rules. Frozen in commit
  `3302dae` before any held-out item was run.
- [DEVIATIONS.md](DEVIATIONS.md): every change after the freeze, with date and reason.
- [DESIGN.md](DESIGN.md): design and pilot decisions on the development families.

## Layout

| Path | Content |
|---|---|
| `src/families.py`, `src/items.py` | six decision families with closed-form optima; item generator |
| `data/items.jsonl` | 1,800 items (F1-F3 development, F4-F6 held-out) |
| `src/run_model.py` | two-turn conversations against a vLLM server, log-probability readout |
| `src/confirm.py` | confirmatory tests H1-H3 (cluster bootstrap, Holm) and descriptive outcomes |
| `src/capitulation.py` | keyword rule for "knowing capitulation" and the hand-coding sample |
| `src/money_family.py`, `src/report_tables.py`, `src/figures.py` | report tables and figures |
| `results/tables/`, `results/figures/` | results on the development and held-out families |
| `scripts/` | serving, sweeps and analysis helpers (WSL2 / bash) |
| `tests/` | unit tests for the item generator |

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
```

Code was written with the help of Claude (Anthropic) through Claude Code.
