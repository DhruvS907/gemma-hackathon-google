# Gemma 4 Developer Agent — Local Workspace

Workspace for studying and optimizing the Kaggle **Gemma 4 Developer Agent**
competition (post-train Gemma 4 into an offline SWE agent; score = % of
SWE-bench-style tasks resolved).

## Layout

```
.
├── getting-started-gemma-4-developer-agent-f7d1b6.ipynb   # Official notebook (runs on Kaggle only)
├── plans/           # Execution plan: Phase 0 (baseline) → 3 (LoRA) + score log
│   ├── README.md
│   ├── phase-0-baseline.md
│   ├── phase-1-prompt-config.md
│   ├── phase-2-subagents-skills.md
│   ├── phase-3-lora-adapters.md
│   └── score-log.md
├── reference/       # Authoritative docs + the real sample submission (when downloaded)
│   ├── HARNESS_README.md          # Official harness spec (tools, budgets, gotchas)
│   └── sample_submission/         # ← download from competition Data tab (TODO)
└── submission/      # LOCAL MIRROR of submission.zip contents — edit these, then zip & submit
    ├── agent.yaml             # REQUIRED: root agent config (must be at zip root)
    ├── eval_config.yaml       # Eval knobs: timeout_seconds, max_tool_calls, max_time_minutes, max_turns
    ├── configs/sampling.yaml  # Generation params (!include'd by agent.yaml)
    ├── prompts/               # System prompts (!include'd by agent YAMLs)
    ├── sub_agents/            # Sub-agent / AgentTool configs
    ├── adapters/              # LoRA adapters (weights added in Phase 3 — see its README)
    └── skills/                # ADK skills (scripts + domain knowledge)
```

## ⚠️ Scaffold vs. real files

`submission/` is a **scaffold** written from the official spec +
`reference/HARNESS_README.md`. The *real* reference agent is in the
competition's **Data tab** (`sample_submission`). Download it to
`reference/sample_submission/`, diff against the scaffold, and replace the
scaffold files with the real ones — then optimize on top (see
`plans/phase-0-baseline.md`).

## Workflow

1. Edit files in `submission/` locally (one variable at a time).
2. Local sanity: run notebook Cell 5 (2 tasks) on Kaggle.
3. Zip: `cd submission && zip -r ../submissions/<ID>.zip .` (agent.yaml at zip root).
4. Validate: no symlinks, ≤ 3 GiB unpacked, allowed extensions only
   (`.yaml/.yml/.md/.txt/.py/.json/.safetensors`).
5. Submit on Kaggle → record score in `plans/score-log.md`.

## Baseline context

- Public LB top: **~0.24**; top-49 floor: **~0.20**
- **B0 (baseline) = 0.01** (2026-10-24) — sample agent, 12B, no adapters.
  This is a *budget floor*, not a capability floor: the sample's
  `max_tool_calls: 10` / `max_time_minutes: 1` starve the agent. Phase 1
  (budgets + prompt) is the highest-leverage next step.
- Eval hardware: 4× NVIDIA L4 (96 GB), vLLM tp=4, 32,768-token context.
- Global budget: **12 hours** across all tasks (validation time excluded).