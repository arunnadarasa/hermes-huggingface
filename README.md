# hermes-huggingface

Hermes Agent skill for wiring the Hugging Face Hub ecosystem into Hermes
across three layers: the `hf` CLI, the official remote MCP server, and the
`hf skills` marketplace (25 skills).

Documentation sources:
[agents-cli](https://huggingface.co/docs/hub/en/agents-cli) ·
[agents-mcp](https://huggingface.co/docs/hub/main/en/agents-mcp) ·
[agents-skills](https://huggingface.co/docs/hub/main/en/agents-skills)

## Layers

1. **CLI** (`hf`) — Hub operations: download/upload, repos, datasets,
   models, papers, jobs, Spaces, buckets. May already be bundled inside a
   host agent's own venv — check before installing/upgrading (see
   Pitfalls in the SKILL.md).
2. **MCP server** — `https://huggingface.co/mcp`, Streamable HTTP,
   Bearer-token auth. Wires like any header-auth remote MCP server, no
   special client config needed despite the docs' web-UI-first framing.
3. **Marketplace skills** — `hf skills add <name> --global`, 25 skills
   covering CLI reference, AWS/SageMaker deployment, dataset/model
   exploration, LLM/vision training on HF Jobs, evals, experiment
   tracking, papers, Gradio/Spaces/ZeroGPU, and local-model selection.

## Verification

```bash
python skills/hermes-huggingface/scripts/hf_smoke_test.py
```

Live run (2026-10-02): **5/5 PASS** — CLI on PATH, version reports, auth
resolves a real identity, a live Hub API call (`hf papers ls`) returns
real data, and `hermes mcp test huggingface` connects.

## Security

No token values in this repository — env-var/token names only. The smoke
test never prints a token and expects `HF_TOKEN`/`hf auth login` to already
be configured. Run `scripts/guard_secrets.py` before every push. Never
`cat`/print a token to "verify" it — use `hf auth whoami` or a hash
comparison instead.
