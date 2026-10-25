---
name: repo_navigation
description: Helper scripts for locating tests and mapping symbols in /workspace.
---

# repo_navigation

Scripts available to the agent via `run_skill_script`:

- `find_test_files.py <symbol_or_substring>` — lists test files that reference
  the given symbol, so the agent can run the right tests fast.

Resources available via `load_skill_resource`:

- `pytest_tips.md` — how to run a single test, interpret failures, and avoid
  collection errors in common repo layouts.