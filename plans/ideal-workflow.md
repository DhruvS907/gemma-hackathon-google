# Ideal Workflow: How a Task Runs Through the Pipeline

This document describes the ideal execution of a task through the
orchestrator + 3-stage pipeline (localizer, repairer, verifier). Two
worked examples: a single-file edit and a multi-file edit.

## The Pipeline at a Glance

```
orchestrator (root, LlmAgent)
  |
  | 1. localizer_agent   (read-only: find root cause + every file that changes)
  | 2. repairer_agent    (edit-only: apply the minimal fix)
  | 3. verifier_agent    (run_command only: one targeted test)
  |
  v
submit_patch (free, always last)
```

Rules that shape the ideal run:

- The orchestrator does no work itself. It only routes reports between
  stages and calls `submit_patch`.
- Each stage's final text report is the only thing the next stage sees.
  Reports use a fixed format, so hand-offs are mechanical.
- All stages share one budget: 50 tool calls, 5 minutes, 100 turns.
  `submit_patch` and `get_status` are free.
- On a `FAIL` from the verifier, the queue runs once more: the verifier's
  evidence goes back to the localizer, which expands its subgraph one ring
  outward (`--depth 2`) and reports only NEW findings. A second `FAIL`
  submits the best patch anyway.

## The Agents (role, skills, tools)

All four agents run the same base model
(`gemma-4-12b-it-qat-w4a16-ct`, single-model rule) and share one budget.
Each agent's tool list is deliberately minimal: an agent can only do its
own stage's job.

### 1. `swe_orchestrator` (root, `agent.yaml`)
- **Role:** runs the queue in order (localizer -> repairer -> verifier),
  applies the bounded retry policy, and always ends with `submit_patch`.
  It does no file work itself.
- **Skills:** none.
- **Tools:** `get_status` (free budget readout), `submit_patch` (free,
  final action), and three `agent_tool` references (one per stage, each
  with `skip_summarization: true` so the stage's full report is passed
  through verbatim).

### 2. `localizer_agent` (`sub_agents/localizer.yaml`)
- **Role:** read-only fault localization. Finds the target symbol, builds
  the induced subgraph around it, judges every node, and reports the root
  cause plus every file that must change (1-3 findings).
- **Skills:** `bfs_node_check` (BFS over the call graph; returns the
  induced subgraph with code per node; `--depth 1|2`, `--side
  both|callers|callees`).
- **Tools:** `search_similar_code` (NL description -> symbol),
  `get_code_neighbors` (import-resolved cross-check), `read_file`
  (confirm truncated/ambiguous nodes), `run_command` (bounded grep entry
  point + fallbacks).
- **Caching:** `output_key: localizer_report` stores its report in
  `session.state` for the retry pass.

### 3. `repairer_agent` (`sub_agents/repairer.yaml`)
- **Role:** applies the minimal fix, one read + one edit per finding
  (max 3 findings). Never runs tests, never explores.
- **Skills:** none.
- **Tools:** `read_file` (verbatim source for `old_string`), `edit_file`
  (the fix), `write_file` (only for a genuinely new source file, rare).

### 4. `verifier_agent` (`sub_agents/verifier.yaml`)
- **Role:** runs the targeted test(s) from the repairer report and reports
  `PASS / FAIL / PRE_EXISTING` with evidence. Read-only; never edits.
- **Skills:** none.
- **Tools:** `run_command` only (at most 2 targeted `pytest` commands,
  batched across changed files; never a full-suite run).

## Stage Contracts

| Stage | Tools | Input | Output report |
|---|---|---|---|
| localizer | `search_similar_code`, `get_code_neighbors`, `read_file`, `run_command`, `bfs_node_check` skill | problem statement (+ hints, + failure evidence on retry) | `ROOT CAUSE / FINDINGS (1-3 files) / TEST` |
| repairer | `read_file`, `edit_file`, `write_file` | localizer report | `CHANGED / DIFF SUMMARY / TEST` |
| verifier | `run_command` | repairer report | `RESULT: PASS / FAIL / PRE_EXISTING + EVIDENCE` |

The localizer's report is cached in `session.state` under
`localizer_report` (`output_key`), so the retry pass can diff against it
and skip already-checked nodes.

---

## Example 1: Single-File Edit

**Problem statement:**
"FastAPI returns a 500 error instead of 404 when a route is not found.
The exception raised is `HTTPException(status_code=500)` in
`fastapi/routing.py`."

The statement names the file, the function area, and the exact wrong
value. This is the best case: no search needed.

### Turn-by-turn

**1. Orchestrator -> localizer** (1 agent_tool call)

**2. Localizer** (3 calls):
- `run_command`: `grep -rn "status_code=500" --include="*.py" .`
  -> `fastapi/routing.py:412`
- `run_skill_script`: `bfs_node_check.py route_handler --depth 1`
  -> induced subgraph: the definition plus its callers, each with code.
  The localizer confirms the 500 is the only wrong value and that no
  caller depends on it.
- `read_file`: `fastapi/routing.py` lines 382-442 (hit +/- 30) to copy
  the exact context.

Report:
```
ROOT CAUSE: route_handler raises HTTPException(status_code=500) for
unknown routes instead of 404.
FINDINGS:
  1. FILE: fastapi/routing.py | LINES: 410-414 | CHANGE:
     status_code=500 -> status_code=404
TEST: pytest tests/test_routing.py -k test_404
```

**3. Orchestrator -> repairer** (1 agent_tool call, report passed verbatim)

**4. Repairer** (2 calls):
- `read_file`: `fastapi/routing.py` lines 405-420 (verbatim source for
  `old_string`)
- `edit_file`: replace `status_code=500` with `status_code=404`
  (strategy: exact, 1 occurrence)

Report:
```
CHANGED:
  1. fastapi/routing.py (1 edit)
DIFF SUMMARY: status_code=500 -> status_code=404 in route_handler
TEST: pytest tests/test_routing.py -k test_404
```

**5. Orchestrator -> verifier** (1 agent_tool call)

**6. Verifier** (1 call):
- `run_command`: `pytest tests/test_routing.py -k test_404`
  -> 1 passed

Report:
```
RESULT: PASS
EVIDENCE: 1 passed in 0.42s
```

**7. Orchestrator -> `submit_patch`** (free)
-> `{"patch_size": 214, "files_changed": 1}`

**Total: 8 budgeted calls, ~4 minutes. One pass, no retry.**

---

## Example 2: Multi-File Edit

**Problem statement:**
"`parse_header` should return a dict of parsed key-value pairs instead of
a raw string. Existing behavior breaks callers that expect the string
format."

No exact file is named, but the symbol is. The fix changes the symbol's
contract, so every caller that depends on the old return type is a
candidate edit.

### Turn-by-turn

**1. Orchestrator -> localizer** (1 agent_tool call)

**2. Localizer** (4 calls):
- `run_command`: `grep -rn "def parse_header" --include="*.py" .`
  -> `http/headers.py:88`
- `run_skill_script`: `bfs_node_check.py parse_header --depth 1 --side both`
  -> induced subgraph with code for every node:
  - `parse_header` (definition, `http/headers.py:88`)
  - `request_handler` (caller, `http/server.py:120`)
  - `sse_stream` (caller, `http/sse.py:45`)
  - `split` (callee, stdlib, no action needed)
- The localizer reads the node code in the report: `request_handler`
  indexes the result as a string (`result[0]`), `sse_stream` passes it
  through unchanged. Both must change.
- `read_file`: `http/headers.py` lines 58-118 to confirm the return
  statement and copy verbatim context.

Report:
```
ROOT CAUSE: parse_header returns the raw header string; the spec requires
a dict. Two callers consume the string form and must be updated.
FINDINGS:
  1. FILE: http/headers.py | LINES: 88-96 | CHANGE:
     return raw -> return dict(pairs)
  2. FILE: http/server.py | LINES: 118-126 | CHANGE:
     result[0] -> result["host"]
  3. FILE: http/sse.py | LINES: 43-50 | CHANGE:
     pass dict through, no string coercion
TEST: pytest tests/test_headers.py -k test_parse
```

**3. Orchestrator -> repairer** (1 agent_tool call)

**4. Repairer** (6 calls, one read + one edit per finding):
- `read_file` + `edit_file` on `http/headers.py`
- `read_file` + `edit_file` on `http/server.py`
- `read_file` + `edit_file` on `http/sse.py`

Report:
```
CHANGED:
  1. http/headers.py (1 edit)
  2. http/server.py (1 edit)
  3. http/sse.py (1 edit)
DIFF SUMMARY: parse_header now returns dict; callers updated to dict access
TEST: pytest tests/test_headers.py -k test_parse
```

**5. Orchestrator -> verifier** (1 agent_tool call)

**6. Verifier** (1 call, batched: one command covers both test files):
- `run_command`: `pytest tests/test_headers.py tests/test_sse.py -k "test_parse or test_stream"`
  -> 4 passed

Report:
```
RESULT: PASS
EVIDENCE: 4 passed in 0.81s
```

**7. Orchestrator -> `submit_patch`** (free)
-> `{"patch_size": 1180, "files_changed": 3}`

**Total: 13 budgeted calls, ~4.5 minutes. One pass, no retry.**

### The retry variant (what happens on FAIL)

Suppose the verifier returned:
```
RESULT: FAIL
EVIDENCE: AssertionError: expected dict, got str at http/client.py:77
```

The orchestrator re-runs the queue once, sending the evidence to the
localizer:

- **Localizer (retry):** the evidence names a caller the first pass
  missed (`http/client.py`). It runs
  `bfs_node_check.py parse_header --depth 2 --side callers` to expand one
  ring outward, cross-checks with `get_code_neighbors("parse_header")`
  (the pre-built graph resolves import aliases the AST scan missed), and
  reports only the NEW finding:
  ```
  FINDINGS:
    1. FILE: http/client.py | LINES: 75-80 | CHANGE:
       result[0] -> result["host"]
  TEST: pytest tests/test_client.py -k test_header
  ```
- **Repairer:** applies only the new finding (2 calls).
- **Verifier:** runs the new test (1 call) -> PASS.
- **Orchestrator:** `submit_patch`.

Retry cost: ~6 calls. Grand total for this task: ~19 calls, still well
inside the 50-call budget.

---

## Budget Summary

| Scenario | Calls | Passes |
|---|---|---|
| Single-file, exact symbol in statement | ~8 | 1 |
| Multi-file (3 findings), clean pass | ~13 | 1 |
| Multi-file + one retry (depth-2 expansion) | ~19 | 2 |
| Worst case (2 full passes, no pass) | ~30-34 | 2, then submit best patch |

The design target: a typical task resolves in one pass with 8-15 calls,
leaving headroom for one evidence-driven retry.

---

## Tool Reference (what each tool is for)

### Orchestrator (root)
| Tool | Job |
|---|---|
| `get_status` | Free budget readout. Used when unsure how many calls remain. |
| `submit_patch` | Free. Captures `git diff` as the final patch; always the last action. |
| `agent_tool` (x3) | Invokes one pipeline stage; the stage's final text report is returned verbatim (`skip_summarization: true`). |

### Localizer (read-only)
| Tool | Job |
|---|---|
| `run_command` | Entry point when the statement has an exact symbol/error string: one bounded `grep -rn`. Also the fallback for call-site greps. |
| `search_similar_code` | Only when the statement is pure natural language: distill it to a symbol-like keyword, get top-k similar symbols with code. |
| `bfs_node_check` (skill) | The core step: BFS over the call graph from the target symbol, returning the induced subgraph (definition + caller functions + callee definitions) with code for every node, in one call. `--depth 2` expands one more ring on retry; `--side` steers the direction from failure evidence. |
| `get_code_neighbors` | Cross-check for import aliases and cross-module references that the AST scan misses (the pre-built graph resolves imports). |
| `read_file` | Confirm only truncated or ambiguous nodes (hit +/- 30 lines, max 2 per file). |

### Repairer (edit-only)
| Tool | Job |
|---|---|
| `read_file` | Get verbatim source for `old_string` (one per finding). |
| `edit_file` | Apply the minimal fix (one per finding, max 3 findings). |
| `write_file` | Only if a genuinely new source file is required (rare). |

### Verifier
| Tool | Job |
|---|---|
| `run_command` | Run at most 2 targeted `pytest` commands (batched across changed files). Never a full-suite run. |

### `bfs_node_check.py`: does it form the induced subgraph?
Yes. The script builds the induced subgraph as part of its run:
1. One pass over the repo's `.py` files indexes every definition and
   every call site (pure stdlib `ast`, no external deps).
2. BFS from the target symbol's definition, ring by ring
   (`--depth`, capped at 2), in the chosen direction(s) (`--side`).
3. The output is the induced subgraph on the visited nodes: `nodes`
   (each with `file`, `line`, `end_line`, `depth`, and its `code`) plus
   `edges` (`calls` relations between them).

So "BFS" is the traversal and "induced subgraph" is the output; the
script does both in a single call.