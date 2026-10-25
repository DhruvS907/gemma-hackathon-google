# Levers — What We Can Change, and What Backs It

Every tunable in the submission, mapped to the file that controls it, the
current (B0) value, the usable range, and the research paper(s) in
`Research Papers/` that justify or inform the change.

Legend: 📄 = PDF in `Research Papers/` (filename in parens).

---

## Tier 1 — Prompt & Config (Phase 1)

| # | Lever | File | B0 value | Range / options | Why it matters | Reference papers |
|---|---|---|---|---|---|---|
| 1 | **System prompt** | `prompts/system.md` | generic "fast minimal fix" template | free text (≤ 1M chars) | The single biggest behavioral lever: workflow order, tool-choice policy, test strategy, when to `submit_patch` | 📄 SWE-agent (`SWE-agent_2405.15793.pdf`) — the core result that *interface/prompt design* moves SWE performance more than model choice; 📄 Agentless (`Agentless_2407.01489.pdf`) — explicit 3-phase prompt structure (localize → repair → validate); 📄 OpenHands (`OpenHands_2407.16741.pdf`) — CodeAct action-space prompting |
| 2 | **Analyzer sub-agent prompt** | `prompts/analyzer.md` | 3-line stub | free text | What the sub-agent reports back determines the root agent's context quality | 📄 SWE-agent (ACI design); 📄 AutoCodeRover (`AutoCodeRover_2404.05427.pdf`) — how to structure fault-localization output |
| 3 | **Temperature** | `configs/sampling.yaml` | `0.2` | `0.0`–`1.0` | Lower = more deterministic tool-call sequences (fewer hallucinated tools); too low = stuck loops | 📄 ToolLLM (`ToolLLM_2307.16789.pdf`) — generation settings for reliable tool use; 📄 SWE-RL (`SWE-RL_2502.18449.pdf`) — decoding config in SWE agent training/eval |
| 4 | **Thinking budget** | `configs/sampling.yaml` | `4096` | `0`–`32768` | Planning quality vs. tokens-per-turn; interacts with `max_output_tokens` (truncated `<\|tool_call>` risk) | 📄 SWE-RL (reasoning/decoding trade-offs); harness README §2.4 (mechanics) |
| 5 | **Max output tokens** | `configs/sampling.yaml` | `16384` | `1`–`32768` | Large `edit_file` payloads get cut off at the limit → broken patches | 📄 SWE-agent (ACI: keep tool payloads small); harness README §10.1 |
| 6 | **Tool-call budget** | `eval_config.yaml` | `10` ⚠️ | up to `100` (harness default) | B0's prime suspect: 10 calls can't cover locate→edit→test→submit | 📄 SWE-bench (`SWE-bench_2407.10605.pdf`) — original agent budgets; 📄 Agentless — cost/efficiency framing (32% at $0.70) |
| 7 | **Time budget** | `eval_config.yaml` | `1 min` ⚠️ | up to `60 min` | Same as above — wall-clock starvation | 📄 SWE-bench; 📄 SWE-Lancer (`SWE-Lancer_2502.12115.pdf`) — cost/time economics of real tasks |
| 8 | **Turn budget** | `eval_config.yaml` | `50` | up to `500` | Each LLM round-trip = 1 turn; caps multi-step debugging | 📄 SWE-bench; 📄 OpenHands (long-horizon event streams) |
| 9 | **Command timeout** | `eval_config.yaml` | `60s` ⚠️ | up to `300s` | Targeted `pytest` runs can exceed 60s → false "test failed" signals | 📄 SWE-bench (harness mechanics) |

> ⚠️ = B0 value is almost certainly below what the task needs. Lever 6+7+9
> together are the expected B1 delta.

---

## Tier 2 — Architecture (Phase 2)

| # | Lever | File | B0 value | Range / options | Why it matters | Reference papers |
|---|---|---|---|---|---|---|
| 10 | **Tool selection** | `agent.yaml` `tools:` | all 9 tools + agent_tool | any subset of the 9 | Fewer, better-chosen tools = fewer hallucinated calls; SWE-agent's central finding is that the *interface* (which tools, what they return) drives performance | 📄 SWE-agent (ACI design ablations); 📄 ToolLLM (tool selection at scale); 📄 OpenHands (CodeAct: unified action space) |
| 11 | **Sub-agent topology** | `sub_agents/*.yaml`, `agent.yaml` | 1 read-only analyzer via `agent_tool` | add agents; `SequentialAgent` / `ParallelAgent` / `LoopAgent`; depth ≤ 50 | Context isolation: keep exploration out of the root agent's 32K window; structured workflows (localize → repair → verify) | 📄 Agentless (pipeline decomposition beats free-form agency); 📄 SWE-agent (context management); 📄 OpenHands (memory/event-stream design) |
| 12 | **Code-graph tool usage** | prompt + `code_analyzer.yaml` | 3 graph tools available | prompt policy for *when* to use them | Graph tools skip expensive grep-walks; only offered when the repo has graph data | 📄 GraphCodeBERT (`GraphCodeBERT_2009.08366.pdf`) — structure-aware code understanding; 📄 CodeT5 (`CodeT5_2109.00859.pdf`) — code embeddings; 📄 AutoCodeRover (repo-level search + fault localization) |
| 13 | **Skills** | `skills/<name>/SKILL.md` | none | add skill dirs (≤ 1,000) | On-demand domain knowledge / scripts without bloating the system prompt | 📄 SWE-agent (ACI: giving the agent the right "applications"); 📄 OpenHands (capability packaging) |
| 14 | **Context management knobs** | agent YAMLs | defaults | `skip_summarization`, `include_contents`, `output_key` | Controls what survives into the root agent's context across turns | 📄 SWE-agent (context window management); harness README §7.2 (compaction mechanics) |

---

## Tier 3 — Model & Weights (Phase 3)

| # | Lever | File | B0 value | Range / options | Why it matters | Reference papers |
|---|---|---|---|---|---|---|
| 15 | **Base model** | `agent.yaml` `model:` | `gemma-4-12b-it-qat-w4a16-ct` | 31b / 12b / e4b / e2b (single-model rule) | 31B smarter but slower per token on 4×L4; 12B is the speed/quality sweet spot | 📄 SWE-bench (model-scale vs. resolution rate); 📄 SWE-Lancer (capability vs. cost) |
| 16 | **LoRA adapters** | `adapters/<name>/` | none | rank 16–128, `.safetensors`, < 3 GiB total; per-agent adapters allowed | Post-train tool-calling + SWE behavior into the 12B base | 📄 LoRA (`LoRA_2106.09685.pdf`) — the mechanism; 📄 QLoRA (`QLoRA_2305.14314.pdf`) — fine-tuning quantized (QAT) models on consumer hardware — *this is the offline thesis*; 📄 ToolLLM (fine-tuning for tool use specifically) |
| 17 | **RL fine-tuning** | (training pipeline, not in zip) | none | GRPO-style RL on resolved-task trajectories | Alternative/complement to SFT-LoRA; reward = test pass | 📄 SWE-RL (`SWE-RL_2502.18449.pdf`) — RL for SWE agents + SWE-Search |
| 18 | **Training data** | (training pipeline) | none | published tasks, SWE-smith-style synthetic generation | Data is the bottleneck for 12B post-training | 📄 SWE-smith (`SWE-smith_2504.21798.pdf`) — synthetic SWE task generation at scale; 📄 SWE-Lancer (real-task distribution) |

---

## Quick map: paper → which levers it informs

| Paper | Levers |
|---|---|
| SWE-bench | 6, 7, 8, 9, 15 (budgets, model scale, the metric itself) |
| SWE-agent | 1, 2, 5, 10, 11, 13, 14 (prompt/ACI design, context) |
| Agentless | 1, 2, 6, 11 (pipeline structure, efficiency) |
| OpenHands | 1, 8, 10, 11, 13 (action space, long-horizon, capabilities) |
| AutoCodeRover | 2, 12 (fault localization, repo search) |
| LoRA | 16 (adapter mechanism) |
| QLoRA | 16 (fine-tuning quantized models offline) |
| ToolLLM | 3, 10, 16 (tool-use tuning, generation config) |
| SWE-RL | 3, 4, 17 (decoding, RL) |
| SWE-smith | 18 (training data) |
| SWE-Lancer | 7, 15, 18 (cost economics, task distribution) |
| GraphCodeBERT | 12 (code structure understanding) |
| CodeT5 | 12 (code embeddings) |

## Suggested reading order for each phase

- **Before Phase 1:** SWE-agent (skim §ACI design), Agentless (method + cost table)
- **Before Phase 2:** OpenHands (architecture), AutoCodeRover (localization), GraphCodeBERT (why graphs help)
- **Before Phase 3:** LoRA → QLoRA → ToolLLM → SWE-RL → SWE-smith (in that order)