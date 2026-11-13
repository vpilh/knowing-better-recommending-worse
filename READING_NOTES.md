# Reading notes, AI x Epistemics sprint (9 Nov 2026)

Depth codes: **F** = page read in full, **A** = abstract or summary only, **K** = known from earlier
reading, not re-read this time. Use **A** sources for positioning only until the full text has been read.

## Sprint-wide reading list

| Source | Depth | Takeaway for us |
|---|---|---|
| [State of the Field: AI for Epistemics and Coordination](https://www.lesswrong.com/posts/uw8RQ8yjKexnhTw6E/state-of-the-field-ai-for-epistemics-and-coordination) (Ben N, Csaky 2026) | F | Nine niches. Forecasting, truthfulness and sycophancy evals are "comparatively well studied"; impact measurement is "very underdeveloped"; benchmarks are one-off, not maintained; little work links calibration or non-sycophancy to decision quality; "faster decisions are not necessarily better decisions"; provenance is not truth. Recommends maintained multi-turn decision-making evals, including whether users decide better with AI |
| [AI Impacts on Epistemics: the Good, the Bad and the Ugly](https://www.forethought.org/research/ai-impacts-on-epistemics-the-good-the-bad-and-the-ugly) (Cotton-Barratt, Hadshar 2026) | F | Mechanisms: cheaper thinking, collective tools vs slop, dependence, automated persuasion, trust lock-in. No metrics proposed; open question on how to assess epistemic tools when "good" is hard to define |
| [Design Sketches for a More Sensible World](https://www.forethought.org/research/design-sketches-for-a-more-sensible-world) (2026) | F | 19 tools in four clusters (collective epistemics, angels-on-the-shoulder, strategic awareness, coordination); no evaluation methods given |
| [Design Sketches: Collective Epistemics](https://www.forethought.org/research/design-sketches-collective-epistemics) (2025) | F | Epistemic virtue evals: "flip tests" swapping the organisation or user view in otherwise identical scenarios; calibration via proper scoring rules; "pedantic mode". Recommends building one eval first. Reliability tracking: gameability, ground truth in contested domains. Provenance: LLM errors compound over recursive steps |
| [AI for AI for Epistemics](https://www.forethought.org/research/ai-for-ai-for-epistemics) (2026) | F | As AI makes tools cheap to build, evaluation becomes the scarce input. Risks: epistemic misalignment (Goodhart) and trust lock-in. AI judges create a regress, so use ground-truth scoring where possible. Suggests strict-cutoff models for forecasting tests |
| [What's Important in "AI for Epistemics"?](https://www.forethought.org/research/whats-important-in-ai-for-epistemics) (Finnveden 2024) | F | Prefer durable projects that leverage compute; forecasting with automated question resolution; past-casting and leakage; persuasion experiments (does AI move people toward truth?) |
| [Project Ideas: Epistemics](https://lukasfinnveden.substack.com/p/project-ideas-epistemics) (Finnveden 2024/25) | F | Testable ideas: held-out forecasting benchmarks, detecting persuasive-but-wrong arguments, experiments on which epistemic habits help models avoid misleading, standards for truthfulness evals |
| [80,000 Hours: AI for epistemics](https://80000hours.org/2024/05/project-idea-ai-for-epistemics/) | K | Motivation piece |
| [A Full Epistemic Stack](https://www.lesswrong.com/posts/DMswzhPQqkqx2XAma/a-full-epistemic-stack-knowledge-commons-for-the-21st-1) (Sourbut, Goldhaber 2025) | K | "Epistack": provenance, reliability and argument layers readable by humans and agents |
| [Multi-Agent Risks from Advanced AI](https://arxiv.org/abs/2502.14143) (Hammond et al. 2025) | K | Cited in the swarm paper; collusion vs cooperation |

## Track 1: model epistemics and decision-making evals

| Source | Depth | Takeaway |
|---|---|---|
| [MASK](https://arxiv.org/abs/2503.03750) | K | Honesty separated from accuracy: elicit belief, then test whether the model contradicts it under pressure |
| [DarkBench](https://arxiv.org/abs/2503.10728) | K | Dark patterns (sycophancy, brand bias, sneaking ...), judged by an LLM |
| [SycEval](https://arxiv.org/abs/2502.08177) | K | Progressive vs regressive sycophancy under rebuttals; critiqued for counting every answer change as sycophancy |
| [ELEPHANT](https://arxiv.org/abs/2505.13995) | K | Social sycophancy (face-preserving), beyond factual agreement |
| [Why Language Models Hallucinate](https://arxiv.org/abs/2509.04664) | K | Binary grading rewards guessing over abstaining; calls for scoring that credits "I don't know" |
| [ForecastBench](https://arxiv.org/abs/2409.19839) | K | Dynamic forecasting benchmark on questions resolving after the model's cutoff |
| [Petri](https://www.anthropic.com/research/petri-open-source-auditing), [Bloom](https://www.anthropic.com/research/bloom) | K | Automated auditing and behaviour-eval generation (Anthropic) |
| [EU AI Act Art. 5](https://artificialintelligenceact.eu/article/5/) | K | 5(1)(a): manipulative techniques that materially distort behaviour |

### Prior work closest to P1 (found 9 Nov)

| Source | Depth | What it does, and the gap P1 fills |
|---|---|---|
| [SycoBench-600](https://aclanthology.org/2026.findings-acl.1759/) (Sinha, ACL Findings 2026) | F | 600 synthetic MCQ items in 8 domains (math, logic, facts ...); doubt, authority, wrong-suggestion and correct-suggestion pushback, the last only "I believe the correct answer is {X}"; "answer with exactly one letter", temperature 0, last-letter parser; 7 API models. Selectivity = Update − WrongFlip. *Gap:* no decisions, and no pushback carries new information |
| [Stubborn or Sycophantic?](https://neurips.cc/virtual/2026/165325) (NeurIPS 2026) | A | Anti-sycophancy scores can reward rejecting all feedback; no system prompt improves selectivity on all three models; report valid corrections and harmful reversals separately |
| [SPINE: sycophancy under sustained multi-turn pressure](https://arxiv.org/abs/2609.09090) | F | Items: 100 CREPE false presuppositions, 100 StereoSet prompts; judge: Claude Sonnet 5. The proxy user is "persistent but mistaken" by design. Adaptive mistaken user for up to 25 turns; collapse 20-97% by turn 25; the correct answer often remains in the reasoning trace. *Gap:* the user is always wrong; never brings valid evidence |
| [The Price of Agreement](https://arxiv.org/html/2604.24668v3) (Writer; ICLR 2026 FinAI workshop) | F (HTML) | Finance (FinanceBench, FinanceAgent): rebuttal, contradiction and preference injection; preference injection drops accuracy by up to about 70%; credibility hints partly recover it. *Gap:* pushback never carries valid information; reference answers come from existing benchmarks |
| [Beyond the Sycophancy Score](https://arxiv.org/abs/2610.08840) | F | Pressure conditions are repetition, eight fallacies and four emotional framings; "a pressure condition changes how the push is framed, not what is pushed"; two LLM judges; metric: decontaminated adoption (excludes turn-1 endorsements). 104k replies, 8 models, 13 pressure conditions: the task explains yielding most (anchored facts 1.3% vs personal choices 77%); yielding rises with verification cost; maximum reasoning removes concessions. *Gap:* personal choices have no right answer |
| [MUSE: conformity as a function of epistemic uncertainty](https://arxiv.org/abs/2605.27288) | F | 10-option MCQ (MedXPertQA, MMLU-Pro Economics and Business); pushback always a distractor; uncertainty from k = 100 samples, not logprobs ("skewed by prompt and output length, as well as syntax"); open models 24-70B (Mistral 3.2 Small, Gemma 3 27B, Qwen 2.5 32B, Olmo 3.1 32B ...). Separates sycophantic conformity (yields while certain) from uncertainty-driven conformity. P1 uses distance to the threshold as an exogenous uncertainty variable |
| [AI Sycophancy and Decisions](https://arxiv.org/abs/2607.28133) | F | Tasks from Enke et al. (2025), some with a computable optimum; GPT-5.2 and GPT-4o chatbots; sycophancy = share of supporting arguments, rated by Claude Sonnet 4; no model-side threshold, no pressure vs information. 1,500 humans, 30 decision environments, threshold choice in optimal stopping: the chatbot gives 63% more supporting arguments, yet pulls decisions together (depolarizing). A human-side complement to P1 |
| [BayesBench](https://arxiv.org/abs/2606.30850) | A | Belief trajectories against a Bayesian posterior under sequential evidence; no social pressure |
| [PPT-Bench / Beyond Social Pressure](https://arxiv.org/html/2604.07749) | A | Separates inconsistency from capitulation with clean, pressure-embedded and counter-argument versions |
| [Measuring Opinion Bias and Sycophancy via LLM-based Persuasion](https://arxiv.org/abs/2604.21564) | A | Debate-style pressure triggers sycophancy 2-3x more than direct questioning |

**Novelty check (full texts, 9 Nov):** none of these papers measures pressure against information on
decisions with a computable optimum. Two notes for the design: MUSE distrusts logprobs (it uses samples
instead), so the pilot checks the logprob readout against samples on a subset. SycoBench and "Beyond
the Sycophancy Score" exclude turn-1 agreements; the threshold-shift metric handles this by design.

## Track 2: trust infrastructure

| Source | Depth | Takeaway |
|---|---|---|
| [C2PA spec 2.4](https://spec.c2pa.org/specifications/specifications/2.4/index.html) | K | Signed manifests bound to assets; a manifest proves origin and edits, not truth |
| [Community Notes data](https://github.com/twitter/communitynotes), [From Birdwatch to Community Notes](https://arxiv.org/abs/2510.09585) | K | Bridging-based helpfulness; open data |
| [Credibility-aware generation (CAG)](https://arxiv.org/abs/2404.06809), [CrAM](https://arxiv.org/abs/2406.11497) | A | Credibility labels come from the system; no forged-label threat model |
| [GHOSTWRITER-style credibility gaming](https://aclanthology.org/2025.emnlp-main.1405.pdf), [Credibility drift attacks](https://dl.acm.org/doi/10.1145/3773966.3779403) | A | Content rewritten until a credibility judge rates it high; human-facing cue manipulation |
| [Worse than zero-shot? RAGuard](https://arxiv.org/abs/2502.16101), [MIRAGE](https://arxiv.org/abs/2607.05069) | A | Misleading retrievals reverse correct answers; defending long-form RAG against pollution |
| Practitioner note: [RAG citation integrity](https://haxoris.com/haxoris-wiki/llm-owasp-top-10/misinformation/rag-citation-integrity) | A | Chunk metadata (title, URI, date) is attacker-writable. This is the P2 threat model, so far stated only informally |

Not found: comparison of the same trust signal attached by the host vs written into the document.

## Track 3: epistemic products (K unless noted)

[Angels-on-the-Shoulder](https://www.forethought.org/research/design-sketches-angels-on-the-shoulder);
[Guardian Angels](https://gwern.net/guardian-angel); [Sycophancy in GPT-4o](https://openai.com/index/sycophancy-in-gpt-4o/);
[Sycophantic AI decreases prosocial intentions](https://www.science.org/doi/10.1126/science.aec8352) (Cheng et al.);
[Habermas Machine](https://www.science.org/doi/10.1126/science.adq2852) (Tessler et al.). Use: P1's framing
("advice people would later endorse" = the computed optimum under the objective the user stated).

## Track 4: open (K unless noted)

[The AI Adoption Gap](https://www.forethought.org/research/the-ai-adoption-gap);
[AI Tools for Existential Security](https://www.forethought.org/research/ai-tools-for-existential-security);
[Community Notes and engagement with misinformation](https://arxiv.org/abs/2307.07960);
[Accuracy of forecasts in strategic intelligence](https://www.pnas.org/doi/10.1073/pnas.1406138111);
FutureSearch, Swift Centre, Sentinel.

### Prior work for P3 (found 9 Nov, A)

CLEF 2025 CheckThat! Task 3 (numerical claims); [NumTemp](https://arxiv.org/abs/2403.17169); QuanTemp
(about 15.5k numerical claims from fact-checkers); claims checked against OECD statistics; [Canadian
Parliament Q&A claims (2018)](https://aclanthology.org/W18-5509); UK OSR code on the public use of statistics
([Full Fact](https://fullfact.org/politics/statistics-code-could-herald-crackdown/)). No 2025-2026 parliamentary
dataset matched to official releases found.
