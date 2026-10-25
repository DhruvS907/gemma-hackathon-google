# Phase 0 — Baseline (first number, zero optimizations)

**Goal:** one clean public-LB score from the unmodified sample agent. This is the
"before" every later delta is measured against.

## Step 1 — Get the real sample submission locally

The sample submission is in the competition's **Data tab** (data explorer).

1. Download the dataset (or the `sample_submission/` folder) from the Data tab.
2. Place it at `reference/sample_submission/` in this workspace.
3. Diff it against the current `submission/` scaffold:
   - Replace scaffold `agent.yaml`, `prompts/*`, `sub_agents/*`, `eval_config.yaml`
     with the real files.
   - Keep a copy of the scaffold (it's git-trackable history anyway).

## Step 2 — Run the notebook on Kaggle (unmodified)

1. Open the getting-started notebook on Kaggle (competition-attached).
2. Attach inputs: competition dataset + model input (`gemma-4-12b-it-qat-w4a16-ct`)
   + wheelhouse dataset.
3. Accelerator: any GPU (12B W4A16 fits a single T4; L4×4 if available).
4. Run Cells 1–6 in order.
   - Cell 2 auto-rewrites YAMLs to 12B and **deletes the dummy 31B adapters**
     → the resulting zip has NO adapters (valid minimal submission).
   - Cell 5 runs 2 sample tasks (local sanity signal: `resolved` per task).
   - Cell 6 produces `/kaggle/working/submission/submission.zip`.
5. Download `submission.zip`.

## Step 3 — Submit & record

1. Submit `submission.zip` via the competition UI.
2. Record the public-LB score in `score-log.md` as **B0 (baseline)**.

## Expected

- Below the top-49 floor (~0.20). Likely low-to-mid teens.
- If Cell 5's 2 tasks both show `resolved=False` with huge `tool_calls` or
  timeouts, the agent is misbehaving — check the transcript in
  `/kaggle/working/results/` before submitting.

## Definition of done

- [x] Real sample files in `reference/sample_submission/`
- [x] `submission/` = real sample (12B, no adapters)
- [x] `submission.zip` built and submitted
- [x] B0 score recorded in `score-log.md` → **0.01** (2026-10-24)

## Result & read

**B0 = 0.01.** The unmodified sample agent resolves ~1% of tasks. This is the
"before" number. Interpretation:

- The sample's `eval_config.yaml` is deliberately minimal (`max_tool_calls: 10`,
  `max_time_minutes: 1`, `timeout_seconds: 60`). At 10 tool calls / 1 minute, the
  agent almost certainly cannot locate the file, edit it, run a targeted test,
  and call `submit_patch` — so most tasks end with no patch or a broken patch.
- 0.01 is *not* a model-capability floor; it's a **budget floor**. The 12B model
  is fine — the harness is starving it.
- This makes Phase 1 (budgets + prompt) the highest-leverage next step, and gives
  the paper a clean story: "the sample baseline is budget-limited, not
  capability-limited."

**Next:** Phase 1 — raise budgets to harness defaults (100 calls / 60 min / 300s)
and tighten the prompt. Expect the largest single delta of the whole ladder.