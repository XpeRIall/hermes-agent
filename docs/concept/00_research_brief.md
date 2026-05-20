The narrow thesis survives **only in a reduced form**.

After source inspection and the required negative pass, the defensible Nova claim is not “agents need a new memory substrate” and not “agents need another skills system.” Those already exist in multiple mature forms as adjacent primitives. The surviving claim is narrower:

> **`inferred`**: coding-agent systems still lack a governed path for turning run-local observations into future-affecting trusted state with explicit evidence, scope, versioning, activation, rollback, and blame.

That is the smallest thesis that withstood falsification against the inspected pack.

What the negative pass found:

- **Memory already exists** in Hermes (`agent/memory_manager.py`), Codex (`codex-rs/ext/memories/...`), OpenHands skills and repo memory conventions (`skills/agent_memory.md`, `.openhands/microagents/repo.md` references), and Claude Code docs baselines. These are **adjacent**, not equivalent. They do not jointly implement typed proposal, trust state, activation rule, rollback/demotion, and regression attribution. **`source-verified` / `docs-verified`**
- **Skills already exist** in Hermes (`tools/skills_*`, `tools/skill_manager_tool.py`), Crush (`internal/skills/skills.go`), Codex (`core-skills`, `config/src/skills_config.rs`), OpenHands/Open SWE/microagent systems, and mini-SWE-agent configuration templates. These are reusable, but not governed promotion. **`source-verified`**
- **Project instruction files already exist** in Hermes (`agent/prompt_builder.py` scanning `AGENTS.md`, `.hermes.md`, `SOUL.md`), Codex (`agents_md` module in `codex-rs/core/src/lib.rs`), Open SWE (`AGENTS.md`), and Claude Code docs baseline. These are persistent future influence, but still not governed promotion. **`source-verified` / `docs-verified`**
- **Hooks already exist** in Codex and Crush. Crush currently exposes `PreToolUse` in source and documents future hook expansion in docs; Codex has a richer hook config surface. But hooks are runtime interception, not evidence-backed durable promotion. **`source-verified`**
- **Checkpoints and traces already exist** in Hermes, LangGraph, Codex, and Plandex. Those solve replay/resume/rollback/time-travel, not trust transitions for reusable abstractions. **`source-verified`**
- **Evals already exist** in aider benchmarks, mini-SWE-agent SWE-bench harnesses, Open SWE reviewer evals, and SWE-agent-family benchmarking culture. They can gate promotion, but they are not promotion systems by themselves. **`source-verified`**
- **Workflow plans and rewind/apply** already exist in Plandex, but plan history is still not a typed trusted artifact registry. **`source-verified`**

If Nova only restates memory, skills, instructions, or evals, the correct outcome would be **`defer thesis`** or **`abandon thesis for now`**. The thesis survives only because the inspected systems consistently stop short of a **governed trust transition** for future-affecting state.