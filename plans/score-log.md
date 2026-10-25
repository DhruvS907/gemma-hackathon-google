# Score Log

Public LB = % of tasks resolved (computed on ~50% of test data).
Leaderboard context (2026-10-23): top ≈ 0.24, top-49 floor ≈ 0.20.

| ID | Date | Model | Change vs. previous | Local 2-task sanity | Public LB | Notes |
|----|------|-------|---------------------|---------------------|-----------|-------|
| B0 | 2026-10-24 | 12B | baseline (sample agent, no adapters) | — | **0.01** | Sample budgets are the prime suspect: `max_tool_calls: 10`, `max_time_minutes: 1`, `timeout_seconds: 60`. ~1% resolved ≈ agent rarely finishes a valid patch. Headroom to top-49 floor (~0.20) is ~20×. |
| B1 | — | — | prompt/sampling/budgets | — | — | |
| B2 | — | — | analyzer AgentTool + skills | — | — | |
| B3 | — | — | LoRA adapters | — | — | |

## Rules
- One variable per row.
- "Local 2-task sanity" = Cell 5 resolved/failed on tasks[:2] (proxy only).
- Keep the zip for every row (name: `submissions/<ID>.zip`).