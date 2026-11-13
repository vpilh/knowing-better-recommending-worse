# AI x Epistemics Research Sprint: project plan (research phase)

Status 9 Nov 2026: research only. No code before the sprint starts (Fri 13 Nov). Reading notes and
sources: [READING_NOTES.md](READING_NOTES.md).

## Sprint facts

| Item | Value |
|---|---|
| Sprint | [AI x Epistemics Research Sprint](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15), online, Fri 13 to Sun 15 Nov 2026 |
| Start | **Fri 13 Nov, 13:00 CET** (from the sprint page countdown, 9 Nov) |
| Cutoff | Sun 23:59 AoE = **Mon 16 Nov, 12:59 CET**. Internal target Mon 10:00 CET |
| Report | Official template, at most 8 pages before references and appendices, abstract 150-250 words, required appendix "Limitations and Dual-Use / Ethical Considerations" |
| Judging | 1-5 each on impact and innovation, execution quality, presentation and clarity |
| Rules | Teams of 1-5; declare prior work; fabricated results or references disqualify |

To check on Friday: the sprint page showed a "submission window closed" banner on 9 Nov (probably stale);
the detailed schedule and the report template link were not yet posted.

## Constraints

- **Solo.** The main figure must exist by Saturday night; Sunday is for writing.
- **Compute.** RTX 5090 (32 GB), 64 GB RAM: open-weight models up to about 14B in bf16 or 27-32B in 4-bit.
- **API below $100.** No LLM judge; frontier models only as a replication.
- **Sponsor credits (Adaption).** 1,250 credits plus three months of the Builder plan for every
  registered participant (sprint page, checked 12 Nov). Adaption's products are fine-tuning and data
  tools (AutoScientist, Adaptive Data, Forge), not an inference API, so they do not replace the 5090 or
  the API budget. To check on Friday: what one credit buys. Possible use only after the main figure
  exists: an intervention that fine-tunes a small model to resist pressure while still taking up
  information. Not in the pre-registered core.
- **One setup.** Every model runs the same items, prompts, decoding and readout.

## Gap

State of the Field 2026 names decision quality as the least measured property, and Track 1 asks which
behaviours matter for real decisions. The 2026 sycophancy work does not separate updating on evidence
from giving in to pressure. SycoBench-600 checks whether a model accepts a *correct* user on
multiple-choice facts. SPINE uses only a mistaken user. "Price of Agreement" (finance) uses pushback
without valid information. "Beyond the Sycophancy Score" finds 77% concessions on personal choices vs
1.3% on anchored facts, but its personal choices have no right answer. Nobody has measured pressure
against information on the same decision with a computable optimum.

## Finance motivation (sources checked 12 Nov; read the full texts before citing numbers)

Why personal finance is the right test bed: LLMs are good enough at finance to be used for it, households
already ask them for advice, and the advice already moves with who is asking. Nobody has tested whether it
also moves with how hard the user pushes.

| Source | Status | What it gives us |
|---|---|---|
| Lopez-Lira and Tang, "Can ChatGPT forecast stock price movements? Return predictability and large language models", *Journal of Financial Economics* 184 (2026), 104335, doi:10.1016/j.jfineco.2026.104335 | Published (top-3 finance journal) | LLMs without financial training extract value-relevant information from news. Finance capability is established, so a failure under pressure is not a failure of ability |
| Choukhmane, de Silva, Lin and Akuzawa, "AI Financial Advice: Supply, Demand, and Life Cycle Implications", Stanford GSB WP 4325 (Mar 2026); NBER WP 35574 | Working paper | Real respondents' prompts to GPT-5.2 and Gemini 3 Flash; advice mostly moves people closer to life-cycle theory, but varies with gender and financial literacy, about 4-5% retirement wealth difference. Closest finance paper: advice depends on the asker. We add: it depends on pushback, measured in money |
| Baldinger, "Generative AI and Retail Investment", job market paper (PhD student of Arpit Gupta, presumably NYU Stern; check the affiliation and an SSRN or website link before citing), described on Gupta's blog 9 Nov 2026 | Job market paper | About 70,000 ChatGPT/Gemini prompt-answer pairs on a wealth-management platform, linked to trades. 36% of answers with a buy recommendation are acted on within ten trading days; after adoption, the passive share of new purchases rises 7.6 pp. A system-prompt change in Dec 2025 moved both the recommendations and the purchases. So LLM advice moves real money, and what the model says depends on how it is steered. Sycophancy is mentioned as motivation, not tested: our gap |
| Sheng, Sun, Yang and Zhang, "Generative AI and Asset Management", *Review of Financial Studies*, advance access, doi:10.1093/rfs/hhag050 (SSRN 4786575) | Published (top-3 finance journal); check authors and year on the journal page | Capital-market side: hedge funds that adopt generative AI earn 2-4% higher annualised abnormal returns; non-hedge funds do not benefit; identified partly via ChatGPT outages. Professionals also act on LLM output |
| Bäckman, "One Advisor for the Whole World? Cross-Country Evidence on Financial Advice from Large Language Models", SAFE WP 490 (Jul 2026), SSRN 7167398 | Working paper | Advice is nearly uniform across 21 countries and ignores a stated household balance sheet. Links to our information-uptake metric (does stated information change the decision?) |
| Fieberg, Hornuf, Meiler and Streich, "Using Large Language Models for Financial Advice", CESifo WP 11666 (Jan 2025), SSRN 5133294 | Working paper | Whether LLMs give suitable advice |
| Financial Health Network, 2025 Financial Health Pulse U.S. Trends Report (article 7 Oct 2025) | Survey | 7% of US respondents used a generative AI chatbot for financial advice in 2025, up from 3% in 2024. Use this conservative figure; industry surveys (TD Bank, NerdWallet, J.D. Power) report 26-55% with looser questions |

Wording rule for the report: "LLMs are already used for personal financial advice", not "widely relied on".
Only Lopez-Lira and Tang is a published top-journal paper; cite the others as working papers.

## Project: the price of pushback, sycophancy in decision units (Track 1)

**Question.** When a user pushes back on advice whose best option can be computed, how far does pure
pressure move the model's decision, compared with information that really changes the answer?

**Setup.**
- Personal-finance decisions with a closed-form optimum that depends on one parameter θ, with threshold
  θ*. Examples: pay down a loan vs invest (APR), refinance (months staying), insurance deductible
  (claim probability). The user states the objective ("lowest total cost"), so the right answer is not
  a matter of taste.
- Vary θ on a grid around θ*. P(recommend A | θ) traces a curve; the model's threshold θ_m is where it
  crosses 0.5.
- Three second-turn messages on the same items: **neutral** (baseline); **pressure** ("I'd rather do
  B", no information); **information** (a fact that moves θ across θ*). Pushback direction is fixed
  and counterbalanced. Full spec: [DESIGN.md](DESIGN.md).
- Readout: the answer comes first, P(A) from the answer-token logprobs, one pass per item. No judge.
- Decision families split into development (pilot, then freeze) and held-out (pre-registered test).

**Metrics.** Pressure effect on the threshold, in decision units; information uptake (ideal 1);
pressure-to-information ratio; expected money lost to pressure.

**Predictions (to freeze after the pilot).** (1) Pressure shifts θ_m toward the user's option.
(2) Pressure buys a measurable share of what real information buys. (3) The shift is largest near θ*
and not zero far from it.

**Models.** Main result: 8-12 open-weight models on the 5090 (3-4 families, 2-3 sizes), thinking off.
Secondary arm: Qwen3 4B/8B/14B with thinking on (same weights), readout after `</think>` averaged over
sampled traces; its size is set in the pilot ([DESIGN.md](DESIGN.md)). Extension: 2-3
frontier models on a subset of the same items, reported separately as a replication check and never
pooled. Where an API has no logprobs, the readout falls back to samples, and the report says so.
Cap: $60.

**Headline figure.** Baseline and pressure curves for one model; pressure shift and dollars lost across
models.

**Risks.** Small models may fail the arithmetic (flat baseline curve); the pilot drops such families or
models. Templates may leak θ*; use paraphrases and cluster-bootstrap over templates.

**Minimum viable result.** 3 families, 4 local models, all three conditions.

## Alternatives (not pursued)

| Idea | Why not now |
|---|---|
| Forged vs host-attached trust signals in RAG (Track 2, continues the swarm paper) | Backup if the pilot shows flat baseline curves |
| Parliamentary statistical claims vs official releases (Track 4) | Mostly data plumbing and hand labelling; too risky solo |
| MisleadBench, FlipRate (page examples) | Many teams will do them; FlipRate is covered by SycoBench-600 and SPINE |
| Calibration probes, confidence audits | Crowded, or few resolved events after the model's cutoff |
| Dispute, crux or decision-brief products | Need human experts or participants |

## Before the weekend (research only, no code)

1. ~~Novelty check against the full texts of the six closest papers.~~ Done 9 Nov: none matches
   ([READING_NOTES.md](READING_NOTES.md)).
2. ~~Decision families, formulas, θ grids, hand-checked thresholds.~~ Done 9 Nov ([DESIGN.md](DESIGN.md)).
3. ~~Local models.~~ Draft list in [DESIGN.md](DESIGN.md); check checkpoints on Hugging Face.
4. ~~Serving stack.~~ vLLM with uv in WSL, no Docker; set up and tested 9 Nov. Transformers as fallback ([DESIGN.md](DESIGN.md)). Run machine: Windows 11
   with WSL, 5090, 64 GB, 0.95 TB free. Check `nvidia-smi` in Windows and in WSL before Friday.
5. Frontier replication: readout by sampling for all frontier models (logprob support differs). Open:
   pick 2-3 models, check prices, Claude Code CLI access.
6. Draft the pre-registration and the paper outline.
7. Register on the sprint page as a team of one.

## Weekend timeline (Europe/Berlin)

| When | Deliverable |
|---|---|
| Fri 13:00 | Sprint start, kickoff |
| Fri afternoon | Item generator, serving stack |
| Fri evening | Pilot on development families with 2 small models |
| Fri night, before any held-out run | Freeze the pre-registration in a commit |
| Sat | Full local sweep; frontier replication; first figures by Sat night |
| Sun | Analysis and writing (8 pages plus appendix) |
| Mon 10:00 | Internal submission target; 12:59 CET hard cutoff |
