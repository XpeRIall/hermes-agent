# Codex CLI Dossier

## Source status

Included as `02_repos/codex-main.zip`; source-inspectable for open repo/CLI. Current provider/cloud behavior may require official docs and should be `docs-verified` only.

## Exact files/modules to inspect first

```text
AGENTS.md
docs/agents_md.md
docs/sandbox.md
docs/skills.md
codex-rs/state/
codex-rs/hooks/
codex-rs/sandboxing/
codex-rs/rollout-trace/
codex-rs/skills/
codex-rs/mcp-server/
codex-rs/core/src/agent/
```

## Candidate components to take

- sandboxing concepts;
- hooks as evidence collectors;
- rollout trace/event model;
- state/log persistence;
- `AGENTS.md` convention;
- MCP/protocol ideas;
- skills convention.

## Components to avoid

- inferring Codex Web/cloud behavior from CLI source;
- treating Codex memory/thread state as Nova truth;
- adopting Rust-heavy modules before proving integration payoff.

## Nova multiplier

Codex traces/hooks feed Nova evidence. `AGENTS.md` is a projection/export target, not a truth source.

## Recommendation

Adopt concepts and possibly modules for hooks/sandbox/trace after source review; use `AGENTS.md` as interop surface.
