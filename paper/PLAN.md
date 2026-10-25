# Paper Track — Plan & Outline

**Competition:** Google - The Gemma 4 Developer Agent Paper Track
**Deadline:** 2026-11-12, 11:59 PM UTC (19 days from 2026-10-24)
**Format:** Kaggle Writeup (markdown), **3,000 words max**, original unpublished research
**Non-archival:** submitting here does NOT block a later conference/arXiv submission
**Awards:** Best Paper $15k · Best New Resource $10k · Best New Application $10k

---

## 1. How it's judged (this drives everything)

Five criteria, **equal weight**, each 0–5, final = average:

| Criterion | What the judge is actually asking | How we score high |
|---|---|---|
| **Novelty** | New insight, not "we ran the sample agent" | A *finding* (e.g., "budget X is the binding constraint for 12B SWE agents", or "LoRA on tool-calls transfers to unseen repos") — not just a leaderboard number |
| **Quality** | Does it generalize beyond this competition? | Frame every result as a property of *offline small-model SWE agents in general*; discuss where the method would/wouldn't transfer (other harnesses, other model sizes) |
| **Relevance** | Impact on SWE + agentic learning | Tie to the offline/consumer-hardware thesis: "what does it take for a 12B model to fix real bugs with no cloud" |
| **Verifiability** | Can a stranger reproduce this? | Exact configs, per-ablation scores, public notebook, zips, hyperparameters, failure transcripts. **This is where most writeups die — over-invest here** |
| **Clarity** | Is it well written? | One figure per claim, tables over prose, ≤ 3,000 words, no filler |

> **Strategy:** a 3,000-word writeup cannot win on breadth. Pick **one central claim**, prove it with a clean ablation ladder, and make it trivially reproducible. Our one-variable-at-a-time score log (`plans/score-log.md`) is *exactly* the experiment design the Verifiability criterion rewards — every row becomes a table row in the paper.

---

## 2. Central claim (pick ONE before writing)

Candidate angles, ranked by fit with what we're actually doing:

1. **"A systematic ablation of the levers that make a 12B offline model a working SWE agent"** — prompt design, budgets, context isolation via sub-agents, LoRA. Empirical, fully verifiable, directly built from our score log. *(Recommended backbone.)*
2. **"LoRA post-training for tool-calling behavior in small SWE agents"** — if Phase 3 produces a real adapter with a measurable delta, this is the novelty headline.
3. **"Code-graph + sub-agent context isolation for 32K-context SWE agents"** — if the analyzer AgentTool shows a measurable effect, this is a Code Comprehension / Graph Reasoning angle (explicitly encouraged topic).

**Recommendation:** angle 1 as the paper, with angle 2 or 3 as the *highlight result* inside it. The claim should be a sentence like:

> "We show that for a 12B offline SWE agent, [X] contributes the largest share of resolution rate (+Δ), while [Y] is negligible, and that [Z] transfers to unseen repositories."

---

## 3. Structure & word budget (3,000 max — budget is binding)

| Section | Words | Content |
|---|---|---|
| Title + subtitle | 20 | Specific, claim-bearing (e.g., "How Far Can a 12B Offline Agent Go? An Ablation Study of the Gemma 4 Developer Agent") |
| Abstract | 200 | Problem → method → **headline numbers** → one-sentence takeaway. Write last. |
| Introduction | 350 | Offline-agent motivation (3 sentences max), the question, our approach in one paragraph, contributions as 3 bullets |
| Related work | 300 | SWE-bench/agent harnesses, PEFT for tool-calling, code-graph navigation. 8–12 citations, 1–2 sentences each. No survey-style filler |
| Setup: harness & task | 300 | Two-phase eval (agent sandbox → hermetic pytest), 4×L4, 32K context, the 9 tools, budgets. Cite the harness README; do NOT re-derive it |
| Methods | 600 | The levers we manipulated, one paragraph each: prompt design, sampling/thinking, budgets, sub-agent context isolation, LoRA (data, rank, targets, schedule). Exact values in a table |
| Experiments | 800 | The ablation ladder = score-log rows. One table: ID / change / local sanity / public LB. Then 2–3 focused result paragraphs, each tied to a figure |
| Analysis & failures | 400 | **This is the novelty engine.** What failed and why (truncated tool calls, budget exhaustion, context overflow, patch-apply failures). Failure transcripts > success stories for insight |
| Conclusion + generalization | 150 | What transfers beyond this competition, limitations, future work |
| References | ~250 | 10–15 refs, tight |

**Total ≈ 3,000.** If over budget, cut Related work and Setup first — never the failure analysis.

---

## 4. What to INCLUDE

- **The ablation table** (from `plans/score-log.md`): one variable per row, B0 → B1 → B2 → B3. This is the spine of the paper.
- **Headline deltas with the baseline number** — every claim needs a Δ vs B0.
- **2–3 figures max**, each answering one question:
  1. Ablation ladder (bar chart: resolution rate per phase)
  2. One failure-mode breakdown (e.g., % tasks lost to timeout vs bad patch vs no patch)
  3. (If LoRA) train/val curve or per-repo transfer plot
- **Exact configs** for every variant (the YAMLs are tiny — a table of the changed fields is enough; full files go in the notebook).
- **Failure transcripts** (anonymized, 5–10 lines each): the single most "novel insight" content available to us.
- **Reproducibility block:** Kaggle notebook link, submission zip IDs, model alias, GPU config, seed/temperature, task split.
- **Public notebook** (optional but strongly recommended): our `getting-started` notebook + the eval cells = the Project Links code artifact. It directly serves Verifiability.
- **A "what we would do differently" paragraph** — judges reward honest negative results.

## 5. What NOT to include

- ❌ Generic LLM / SWE-agent background — judges are experts; 3 sentences of motivation is the ceiling.
- ❌ Full prompt text in the body — it's 40 lines of markdown; put it in the notebook, reference it.
- ❌ Re-explaining the harness README — cite it, use one compact table.
- ❌ "We believe / we think" without a number. Every claim → a table cell or a transcript.
- ❌ More than one variable changed per experiment row (breaks the ablation logic).
- ❌ Leaderboard-spraying anecdotes, submission-count stats, prize talk.
- ❌ Code dumps in the writeup body (notebook is for that).
- ❌ Unverified local-only results presented as findings — label 2-task sanity checks as *proxy signals*, public LB as the evidence.
- ❌ Anything that would block a later arXiv/conference submission (keep it non-archival-friendly: no venue-specific formatting).

---

## 6. Verifiability checklist (the criterion most likely to separate us)

- [ ] Public Kaggle notebook that reproduces B0 → B3 end-to-end
- [ ] Every score in the paper traceable to a `submissions/<ID>.zip` + score-log row
- [ ] Full YAML diffs between phases (they're < 100 lines total)
- [ ] LoRA: training data source, rank, target modules, lr, steps, eval protocol
- [ ] Failure analysis: raw transcripts in notebook, summarized in paper
- [ ] Statement of what we did NOT test (honest scope)

---

## 7. Timeline (deadline 2026-11-12)

| Date | Milestone |
|---|---|
| Oct 24–26 | B0 submitted + recorded (unblocks everything) |
| Oct 27 – Nov 2 | Phase 1 (prompt/budgets) + Phase 2 (sub-agents/skills) runs → B1, B2 scores |
| Nov 3–7 | Phase 3 (LoRA) if feasible; else paper pivots to angles 1+3 with B1/B2 as the ladder |
| Nov 5 | **Freeze the claim** (section 2) once B1/B2 land — outline the paper around the actual deltas |
| Nov 7–9 | Draft full writeup (3,000 words), figures from score log |
| Nov 10 | Notebook finalized + public; verifiability checklist pass |
| Nov 11 | Edit pass for Clarity (cut 10%), submit with ≥ 1 day buffer |

**Risk note:** if LoRA (Phase 3) doesn't land by Nov 7, do NOT wait — submit the ablation paper on prompt/budgets/context-isolation. A clean 3-rung ladder with a strong failure analysis beats a 4-rung ladder missed by a day.

---

## 8. Secondary prize angles (decide by Nov 5)

- **Best New Resource ($10k):** if we build a LoRA training dataset from the published tasks, or a tool (e.g., a budget/failure analyzer over harness traces), it can be highlighted as a resource in the same writeup.
- **Best New Application ($10k):** only if we do something genuinely new with the provided code graphs/embeddings (e.g., graph-based task routing). Don't force it.

---

## 9. Open questions to resolve before drafting

1. ~~What is the B0 score?~~ **Resolved: B0 = 0.01** (2026-10-24). This is a *budget floor*, not a capability floor — the sample's `max_tool_calls: 10` / `max_time_minutes: 1` starve the agent. **This is the paper's opening hook:** "the unmodified sample agent resolves 1% of tasks; we show the gap is dominated by harness budgets and prompt design, not model capability."
2. Which single delta is biggest after B1/B2? (that becomes the headline claim)
3. Do we have LoRA training infra by Nov 3? (yes → angle 2 headline; no → angle 1+3)
4. One figure style: matplotlib bars from score-log CSV — keep it consistent across all figures.

### B0 = 0.01 → implications for the paper

- **Intro framing:** start from 0.01, not from "the sample works." The narrative is *diagnosis* — decompose the 0.01 → 0.20+ gap into budget / prompt / context-isolation / fine-tuning contributions.
- **Figure 1** is now almost certain: the ablation ladder starting at 0.01. Even a 3-rung ladder (0.01 → B1 → B2) is a strong, honest figure.
- **Failure analysis** (section 7 of the outline) is now the *most important* section: at 0.01, nearly every task is a failure transcript. Categorize them (no patch / patch-apply failure / test failure / budget exhaustion) and the category distribution *is* the finding.
- **Verifiability:** the 0.01 number + the exact sample `eval_config.yaml` makes B0 trivially reproducible — a clean anchor for the whole ladder.