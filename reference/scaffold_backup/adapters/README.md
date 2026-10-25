# Adapters

Place PEFT LoRA adapter directories here, one per adapter:

```
adapters/
├── main_lora/
│   ├── adapter_config.json
│   └── adapter_model.safetensors
└── tool_lora/
    ├── adapter_config.json
    └── adapter_model.safetensors
```

- Reference them in agent YAMLs: `adapter: main_lora` (root coder),
  `adapter: tool_lora` (analyzer sub-agent).
- The vLLM server (notebook Cell 4) auto-discovers these and hot-swaps per request.
- Adapter names must match `[A-Za-z0-9][A-Za-z0-9._-]*`.
- The sample submission ships DUMMY 31B-shaped adapters; they are removed
  automatically when running a non-31B model (notebook Cell 2).
- Weights are NOT committed here — train/fine-tune separately and drop the
  resulting directories in before zipping.

## Training targets (see notes/04-optimization-plan.md)
- Tool-call formatting reliability (Gemma 4 chat template)
- SWE solve trajectory: orient → reproduce → fix → verify → submit
- Budget awareness (when to stop and submit)