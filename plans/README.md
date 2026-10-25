# Plans — Gemma 4 Developer Agent

Execution plan for going from **zero** to a **competitive submission**.

## Phases

| Phase | Goal | Output |
|---|---|---|
| **0 — Baseline** | First leaderboard number, zero optimizations | Baseline score recorded in `score-log.md` |
| **1 — Prompt & Config** | Better system prompt, sampling, budgets | Delta vs. baseline |
| **2 — Sub-agents & Skills** | Context isolation via analyzer AgentTool, custom skills | Delta vs. Phase 1 |
| **3 — LoRA Adapters** | Post-trained `main_lora` / `tool_lora` | Delta vs. Phase 2 |

## Rules of the road

1. **One variable at a time.** Each phase changes one thing; record the score delta.
2. **Local sanity check before every submission** — run the notebook's 2-task eval (Cell 5) to confirm the agent still functions.
3. **Leaderboard submissions are rate-limited** — batch changes, don't spray single tweaks.
4. **The real sample submission is the ground truth** — it's in the competition's Data tab. Download it into `reference/sample_submission/` and diff against `submission/` before Phase 1.

## Files

- `levers.md` — **all tunable levers** (prompt, sampling, budgets, tools, sub-agents, skills, model, LoRA/RL) mapped to the research paper that backs each one
- `phase-0-baseline.md` — get the first number (done: B0 = 0.01)
- `phase-1-prompt-config.md` — prompt/sampling/budget tuning
- `phase-2-subagents-skills.md` — multi-agent + skills
- `phase-3-lora-adapters.md` — post-training
- `score-log.md` — the running score ledger

## Key references

- `reference/HARNESS_README.md` — official harness spec (tools, budgets, gotchas)
- `submission/` — the editable submission (currently a scaffold; replace with real sample files)
- Notebook — the Kaggle-only run harness (Cells 1–6)