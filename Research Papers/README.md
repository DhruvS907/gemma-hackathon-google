# Research Papers — Reference Library

PDFs for the **Gemma 4 Developer Agent Paper Track** writeup. Each is tagged with
the paper-track topic it supports and the section it feeds. Read the "core" set
first; the rest are for the Related Work section.

> **Lever → paper mapping:** see `../plans/levers.md` — every tunable in the
> submission is mapped to the paper(s) that justify it.

## How to use
- **Core (read first):** the 4–5 papers your method directly builds on.
- **Related Work:** the rest — 1–2 sentences each in the writeup, cited.
- All are arXiv preprints; cite by arXiv ID (in the filename).

---

## A. SWE agents & benchmarks (the problem + prior art)

| File | arXiv | What it is | Use for |
|---|---|---|---|
| `SWE-bench_2407.10605.pdf` | 2407.10605 | The benchmark: 2,294 real GitHub issues, resolution-rate metric | Setup section — defines the task & metric we're scored on |
| `SWE-agent_2405.15793.pdf` | 2405.15793 | Agent-Computer Interface (ACI) design; 12.5% SWE-bench | Related Work — the "interface design matters" line; our prompt/tool design sits here |
| `Agentless_2407.01489.pdf` | 2407.01489 | 3-phase localize→repair→validate, no autonomous loop; 32% at $0.70 | Related Work — the "simple pipeline beats complex agent" counterpoint; motivates why we ablate agent complexity |
| `OpenHands_2407.16741.pdf` | 2407.16741 | Open-source software dev agent platform (CodeAct) | Related Work — closest open agent framework to our harness |
| `AutoCodeRover_2404.05427.pdf` | 2404.05427 | Repo-level code search + fault localization for SWE | Related Work — code-navigation / localization prior art |

## B. Tuning & optimization (Phase 3 — LoRA / RL)

| File | arXiv | What it is | Use for |
|---|---|---|---|
| `LoRA_2106.09685.pdf` | 2106.09685 | Low-rank adaptation; freeze base, train rank-decomp matrices | Methods — the adapter mechanism we use in Phase 3 |
| `QLoRA_2305.14314.pdf` | 2305.14314 | 4-bit quantized fine-tuning on a single GPU | Methods — why a 12B/31B QAT model is fine-tunable on consumer hardware (the offline thesis) |
| `ToolLLM_2307.16789.pdf` | 2307.16789 | Tool-use instruction tuning + ToolBench + ToolEval | Methods/Related — the precedent for fine-tuning *tool-calling* behavior specifically |
| `SWE-RL_2502.18449.pdf` | 2502.18449 | RL (GRPO) for SWE agents; SWE-Search | Methods — the RL alternative/complement to LoRA for agent capability |
| `SWE-smith_2504.21798.pdf` | 2504.21798 | Synthetic SWE task generation at scale (500k tasks) | Methods — a data source for fine-tuning; "Best New Resource" angle |
| `SWE-Lancer_2502.12115.pdf` | 2502.12115 | Real freelance software tasks; economic framing | Related Work — real-world task distribution beyond SWE-bench |

## C. Code comprehension & graphs (the provided graphs/embeddings)

| File | arXiv | What it is | Use for |
|---|---|---|---|
| `GraphCodeBERT_2009.08366.pdf` | 2009.08366 | Pre-training code reps with data-flow structure | Related Work — structure-aware code understanding; grounds the code-graph tools |
| `CodeT5_2109.00859.pdf` | 2109.00859 | Identifier-aware encoder-decoder for code | Related Work — code embeddings / comprehension prior art |

---

## Suggested citation order for the writeup (Related Work, ~300 words)

1. SWE-bench (task + metric)
2. SWE-agent → OpenHands → AutoCodeRover (agent frameworks)
3. Agentless (the "do we need an agent?" counterpoint)
4. LoRA → QLoRA → ToolLLM (parameter-efficient + tool-use tuning)
5. SWE-RL → SWE-smith (RL + synthetic data)
6. GraphCodeBERT → CodeT5 (code structure / embeddings)

> **Gap to fill (our novelty):** none of the above study a *12B offline* model
> under a *fixed 32K context + tight budgets* with *code-graph sub-agent context
> isolation*. That intersection is the claim our ablation ladder proves.