# Related work: verified references (checked 14 Nov 2026)

"Verified" = title, authors, ID and the stated content checked on arXiv/ACL pages; numbers marked
"secondary" come from summaries and must be checked in the full text before they are quoted.

## Closest papers

| Reference | What they do | Overlap with us | What we add |
|---|---|---|---|
| Zhao, Balagopalan, Agrawal, Yergasheva, Alshikh, Bikel, "The Price of Agreement: Measuring LLM Sycophancy in Agentic Financial Applications", arXiv:2604.24668 (v3, Jun 2026), ICLR 2026 FinAI Workshop | FinanceBench/FinanceAgent (extraction, numerical reasoning, reference answers). Rebuttal/contradiction after the answer give light-to-moderate drops (Sonnet 4.5: 0.87 to 0.72); biasing user-preference text injected *before* the answer gives large drops (Gemini 3 Pro: 0.83 to 0.24). Acknowledgment rate 0.23-0.49 (LLM judge). Mitigations: LLM input filtering, reliability scores, LoRA. Closed and large open models. | **Same direction as our H3**: preference >> rebuttal, in finance. | Preference about a *decision* stated *after* the recommendation (not a bias about a fact); goal restatement as mechanism test (H2); information benchmark on identical items; money; pre-registered, held-out; small open-weight models; the assessment stays correct while the recommendation changes (C4). |
| Basta, Haghighi, Kaafar, Beheshti, "Correction or Manipulation? Measuring Epistemic Vigilance in LLM Agents Under User Pressure", arXiv:2610.36453 (Oct 2026, preprint) | Same pressure applied when the user is right vs wrong; signal detection (d'). QA (MMLU-Pro, GPQA, MATH-500) and a policy task. Pressure = claims (expertise, citations, consensus), not wishes. Evidence-gated system prompt mainly lowered concession to everyone, correct users included; "prompting alone" unlikely to produce vigilance. | Correction vs pressure on the same items (our information vs pressure contrast). | Wishes vs claims; decisions with a stated goal; mechanism. **Their prompt result is why our system-prompt run includes the information condition.** |
| Yang, Hosseinmardi, Liu, Ghasemian, "Beyond the Sycophancy Score: How Task, Model, and Pressure Shape LLM Yielding", arXiv:2610.08840 (Sep 2026) | 8 models, 13 pressure conditions; personal choices endorsed in 77.0% of conversations vs 1.3% concessions on anchored facts; attributed to missing guardrails, as personal choices have no keyed answer. | Personal choices draw high yielding. | Our choices *have* a keyed answer under the user's own goal, and yielding persists. |
| Tang, Wei, Jiang, Huang, "Measuring LLM Sycophancy under Sustained Multi-Turn Pressure" (SPINE), arXiv:2609.09090 (Sep 2026) | Up to 25 turns of adaptive pressure from a mistaken user; false presuppositions and unethical queries. Secondary: in 50-89% of collapse turns reasoning traces still contain the correct position. | "Knows but accommodates" (our C4). | In our case the *visible reply* states the better option, and the setting is a decision with a cost. |
| Sinha, "SycoBench-600: Measuring Sycophancy and Correction Selectivity in LLM Assistants", Findings of ACL 2026, pp. 35278-35284 | 600 MCQ items; doubt, authority, explicit wrong suggestion; correction selectivity (accept correct, resist incorrect suggestions); cluster bootstrap. | Correction selectivity ~ our information vs pressure. | Decisions, wishes, money, mechanism. |

## Classic sycophancy

- Sharma, Tong, et al., "Towards Understanding Sycophancy in Language Models", ICLR 2024, arXiv:2310.13548. Sycophancy across five assistants; linked to human preference data.
- Laban, Murakhovs'ka, Xiong, Wu, "Are You Sure? Challenging LLMs Leads to Performance Drops in The FlipFlop Experiment", arXiv:2311.08596 (2023/2024). "Are you sure?" challenge: answers flip 46% on average, accuracy drop 17%.

## Still to verify

- Baldinger, "Generative AI and Retail Investment" (job market paper): not found by search on 14 Nov; needs a link from Valentin or drop it.
- Finance-motivation papers in PLAN.md: checked 12 Nov, full texts to read before numbers are quoted.
