# Score Log

Public LB = % of tasks resolved (computed on ~50% of test data).
Leaderboard context (2026-10-23): top ≈ 0.24, top-49 floor ≈ 0.20.

| ID | Date | Model | Change vs. previous | Local 2-task sanity | Public LB | Notes |
|----|------|-------|---------------------|---------------------|-----------|-------|
| B0 | 2026-10-24 | 12B | baseline (sample agent, no adapters) | — | **0.01** | Sample budgets are the prime suspect: `max_tool_calls: 10`, `max_time_minutes: 1`, `timeout_seconds: 60`. ~1% resolved ≈ agent rarely finishes a valid patch. Headroom to top-49 floor (~0.20) is ~20×. Local 129-task run: 5/129 (3.88%); 87/129 timed out at 1 min, 81/129 hit the 10-call cap, 106/129 ended with no patch. |
| B1 | 2026-10-26 | 12B | budgets + system prompt (merged, functionally coupled): `timeout_seconds 60→300`, `max_tool_calls 10→40`, `max_time_minutes 1→5`, `max_turns 50→100`; prompt rewrite: budget framing, locate decision tree (exact symbol→grep, vague→semantic→graph, known symbol→graph), targeted reads (grep -n then ±30 lines, max 2/file), early delegation policy, always-submit rule | — | — | Budgets derived from 12h global ÷ ~120 test tasks ≈ 6 min/task ceiling; 5 min leaves 2h margin. Prompt and budgets are coupled (prompt's "40 calls / 5 min" framing is wrong under B0 budgets), so submitted together. Fixes B0 failure modes: 87/129 timeouts, 81/129 call-cap, 106/129 NO_PATCH, 114 BudgetExceeded sub-agent errors, sequential large-file reads. |
| B2 | — | — | analyzer prompt rewrite + delegation tuning | — | — | |
| B3 | — | — | LoRA adapters | — | — | |

## Rules
- One variable per row (exception: B1 merged budgets + prompt because they are functionally coupled — the prompt's budget framing is invalid under B0 budgets).
- "Local 2-task sanity" = Cell 5 resolved/failed on tasks[:2] (proxy only).
- Keep the zip for every row (name: `submissions/<ID>.zip`).