---
name: hermes-huggingface
description: "Wire Hugging Face (hf CLI, MCP server, marketplace skills) into Hermes."
version: 1.0.0
---

# Hermes Hugging Face

Wires the Hugging Face Hub ecosystem into Hermes across three independent
layers: the `hf` CLI, the official remote MCP server, and the `hf skills`
marketplace. All three verified live 2026-10-02.

## 1. CLI (`hf`)

Hermes bundles `huggingface_hub` (with the `hf` CLI) inside its own
internal venv as a transitive dependency — check before installing:

```bash
which hf
hf version
```

If present, **do not `pip install -U huggingface_hub` against the system
`pip3`** — on this kind of setup there can be TWO separate installs: one in
the system/user Python site-packages (used by unrelated tools, e.g.
`tokenizers<2.0` pins), and one inside Hermes's own bundled venv (the one
`hf` actually resolves to). Upgrading the wrong one either does nothing
(the `hf` binary still points at the old venv) or breaks an unrelated
package's version pin. Confirm `which hf` resolves to a path, inspect
which venv owns it, and only upgrade that specific venv's `pip` if you
must — otherwise leave a working pinned version alone.

### Auth

```bash
hf auth login --token "$HF_TOKEN"
hf auth whoami
```

`hf auth login --token` prints "Environment variable `HF_TOKEN` is set and
is the current active token independently from the token you've just
configured" if `HF_TOKEN` is exported — same env-var-shadows-stored-login
pattern as Modal's profile system. Verify `whoami` resolves correctly both
with and without the env var exported (`env -u HF_TOKEN hf auth whoami`)
before trusting either path.

### Skill install (CLI-generated, stays version-pinned to your `hf`)

```bash
hf skills add --global        # installs 'hf-cli' to ~/.agents/skills/hf-cli
```

This Skill is generated FROM your installed CLI version — it goes stale on
`hf` upgrade. `hf skills update -g` refreshes it.

## 2. MCP server

Hugging Face runs an official remote MCP server at `https://huggingface.co/mcp`,
Streamable HTTP transport, Bearer-token auth (same `HF_TOKEN`). Despite the
docs page recommending the web-UI flow at `huggingface.co/settings/mcp`
(client-specific copy-paste snippets), it wires identically to any other
header-auth remote MCP server via `hermes mcp add`:

```bash
hermes mcp add huggingface --url https://huggingface.co/mcp --auth header
```

then answer the two interactive prompts (auth: yes, paste the token when
asked; enable all tools: yes).

Verified tool set (2026-10-02, 6 tools): `hf_whoami`, `hub_repo_search`,
`hub_repo_details`, `hf_fs` (Hub semantic search/navigation), `dynamic_space`
(call community Gradio-MCP Spaces), `gr1_z_image_turbo_generate` (an
example dynamically-discovered Space tool — the exact long tail here will
drift as HF adds/removes featured Spaces; don't hardcode an expectation of
exactly 6 tools in future checks, just confirm `hf_whoami` et al. are
present).

Verify:
```bash
hermes mcp test huggingface
```

## 3. Marketplace skills (`hf skills add <name> --global`)

25 skills total as of 2026-10-02 (`hf skills list` is the live source of
truth — this count will drift). Install each with:

```bash
hf skills add <name> --global
```

Categories seen: core (`hf-cli`), cloud/AWS SageMaker (`hf-cloud-*`, 6
skills), and ML workflow skills (`huggingface-*`, `transformers-js`,
`train-sentence-transformers`, `trl-training`, `hf-mem`) covering dataset
exploration, LLM/vision training on HF Jobs, evals, Trackio tracking,
papers, Spaces/Gradio/ZeroGPU, and local-model selection.

Loop-install all of them:
```bash
hf skills list --format json | python3 -c \
  "import json,sys; [print(d['name']) for d in json.load(sys.stdin)]" \
  | while read -r s; do printf 'Y\n' | hf skills add "$s" --global; done
```

## Pitfalls (one line each)

- `hf` may already be bundled inside the HOST agent's own venv (not a
  separate user install) — upgrading it via system `pip3` upgrades the
  WRONG copy and can introduce real dependency conflicts in unrelated
  packages (e.g. `tokenizers` pinning `huggingface-hub<2.0`); always
  `which hf` and trace to its actual venv first, and prefer leaving a
  working pinned version alone over a speculative upgrade.
- `hermes mcp add` piping a bare `Y\nY\n` for the auth-prompt + token
  answers silently consumed the second `Y` as the literal bearer token
  the first time this was tried — the connection then fails with a
  Content-Type/HTML error (good: caught at the "Save anyway?" prompt,
  nothing bad persisted) but a wrong key can still land in `.env`.
  Always verify the saved `MCP_HUGGINGFACE_API_KEY` value's hash matches
  the real `HF_TOKEN`'s hash before trusting a `hermes mcp add` run that
  used piped stdin for a secret-bearing prompt.
- `HF_TOKEN` env var silently overrides a stored `hf auth login` session,
  same class of trap as Modal's `MODAL_TOKEN_ID`/`SECRET` vs profile.
- Never `cat`/print a token file or env var to verify a credential —
  use `hf auth whoami` (resolves identity) or a hash comparison
  (`shasum`) instead; both prove correctness without exposing the value.
- Key values never in repo/skill/commit — env-var/token names only; run
  the guard before push.
