---
name: bfs_node_check
description: BFS over the call graph from a symbol; returns the induced subgraph (definition, callers, callees) with code for every node.
---

# bfs_node_check

Scripts available to the agent via `run_skill_script`:

- `bfs_node_check.py <symbol> [--depth 1|2] [--side both|callers|callees] [--max-nodes 16] [--max-code-lines 40]` — BFS over the call graph from the symbol; returns the **induced call subgraph** as JSON:
  - `nodes`: the definition, caller functions, and callee definitions — each with `file`, `line`, `end_line`, `depth`, and its `code`
  - `edges`: `calls` edges connecting them
  - `--depth 2` adds one more ring (callers-of-callers / callees-of-callees); `--side` restricts expansion direction

Review all nodes in the one report: callers are candidate edits if the fix changes the symbol's contract; callees may hold the real defect. On a retry pass after a failed verify, expand (`--depth 2`, side chosen from the failure evidence) and report only new findings. Cross-check with `get_code_neighbors` for import-aliased references.