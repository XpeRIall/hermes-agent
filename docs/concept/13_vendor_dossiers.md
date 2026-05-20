**Hermes**

- What was actually inspected: `run_agent.py`, `agent/background_review.py`, `agent/prompt_builder.py`, `agent/memory_manager.py`, `tools/skill_provenance.py`, `tools/skill_manager_tool.py`, `tools/terminal_tool.py`, `hermes_state.py`, `LICENSE`. **`source-verified`**
- What matters: Hermes already has the exact adjacent mechanisms Nova wants to govern: background self-improvement, memory writes, skill writes, context files, approvals, sessions, and checkpoints. **`source-verified`**
- Non-equivalence result: missing typed evidence-backed proposal objects, explicit artifact scope and activation rules, formal trust states, rollback/demotion of promoted abstractions, and regression attribution. **`source-verified`**
- Adoption verdict: **best first host**.

**aider**

- What was inspected: `aider/coders/base_coder.py`, `aider/repomap.py`, `aider/repo.py`, `benchmark/README.md`, `LICENSE.txt`. **`source-verified`**
- What matters: mature repo map, Git-backed edit loop, and benchmark discipline.
- Non-equivalence result: no governed promotion layer.
- Adoption verdict: **imitate repo-map/benchmark patterns; do not use as Nova foundation**.

**OpenHands**

- What was inspected: `AGENTS.md`, `skills/agent_memory.md`, `openhands/app_server/app_conversation/skill_loader.py`, package/build files, license presence. **`source-verified`**
- What matters: microagent/repo-memory conventions and multi-source skill loading.
- Non-equivalence result: persistent repo guidance exists, but not governed promotion.
- Adoption verdict: **partial imitation / benchmark only**.

**Codex CLI**

- What was inspected: `codex-rs/config/src/hook_config.rs`, `permissions_toml.rs`, `skills_config.rs`, `core/src/lib.rs`, `ext/memories/src/local.rs`, `external-agent-sessions/src/lib.rs`, `execpolicy/src/policy.rs`, CLI entrypoints, license presence. **`source-verified`**
- What matters: strongest inspected source for permissions, hooks, AGENTS integration, session/rollout traces, and portable state.
- Non-equivalence result: plenty of adjacent primitives; no governed promotion registry.
- Adoption verdict: **port selected contracts; do not replace Hermes with Codex**.

**Plandex**

- What was inspected: `app/cli/lib/rewind.go`, `app/cli/cmd/rewind.go`, `app/server/model/plan/state.go`, `app/server/syntax/file_map/map.go`, hooks package, license presence. **`source-verified`**
- What matters: conflict-aware rewind and plan/apply/branch UX.
- Non-equivalence result: strong rollback machinery, but not trust-governed reusable abstractions.
- Adoption verdict: **imitate rewind/apply/blame UX for Nova artifacts**.

**LangGraph**

- What was inspected: checkpoint base, sqlite saver, store base, graph state, package manifests, license. **`source-verified`**
- What matters: durable execution, checkpoints, store abstraction, interrupts/resume.
- Non-equivalence result: persistence and orchestration, not governed promotion.
- Adoption verdict: **take interfaces later if host-neutral persistence becomes necessary**.

**Open SWE**

- What was inspected: `agent/server.py`, `agent/reviewer.py`, `evals/reviewer/README.md`, `AGENTS.md`, `CLAUDE.md`, manifests, license presence. **`source-verified`**
- What matters: sandboxed internal-coding-agent composition, middleware, reviewer eval design.
- Non-equivalence result: rich agent composition, but no future-state governance layer.
- Adoption verdict: **benchmark and reviewer-eval donor, not MVP base**.

**mini-SWE-agent**

- What was inspected: `agents/default.py`, `environments/local.py`, `run/benchmarks/swebench.py`, `run/utilities/inspector.py`, manifests, license presence. **`source-verified`**
- What matters: clean baseline loop and benchmark harness.
- Non-equivalence result: minimal agent, no governed promotion.
- Adoption verdict: **baseline and benchmark only**.

**SWE-agent proper**

- Pack status: not present as source in the uploaded archive; official upstream identity checked. citeturn1search3
- What matters: still in-scope, but not inspected deeply enough here for source-grounded primitive claims.
- Adoption verdict: **defer until source-inspected**. **`partial`**

**Crush / OpenCode**

- What was inspected for Crush: `internal/hooks/hooks.go`, `internal/permission/permission.go`, `internal/session/session.go`, `internal/skills/skills.go`, `docs/hooks/README.md`, `docs/hooks/FUTURE.md`, README/license. **`source-verified`**
- What matters: cleanest inspected implementation of Agent Skills and one of the best concrete hook/permission models.
- Identity finding: Crush is **not** OpenCode proper in this run; OpenCode proper was identified separately by official web lookup. citeturn1search1turn1search4
- Adoption verdict: **take skills and hook semantics from Crush; do not claim OpenCode equivalence without direct inspection**.

**Claude Code docs baseline**

- What was inspected: the uploaded `claude-code-main` repo contents and its license/docs/examples, plus official docs discovery. The uploaded repo did **not** establish source-inspectable product implementation. Official docs were therefore treated as the baseline surface. citeturn1search5turn1search6
- What matters: project memory/instruction and hooks are good counterfactuals, but only at docs level here.
- Non-equivalence result: docs baseline still does not establish governed promotion.
- Adoption verdict: **docs-only comparator; no implementation borrowing beyond public behavior concepts**.

**Adversarial final recommendation**

The smallest source-grounded recommendation is:

> **Proceed with a minimal Nova kernel inside Hermes.**  
> Intercept future-affecting writes. Convert them into evidence-backed proposals. Require promotion before activation. Record artifact activation per run. Support rollback and demotion.  
> Borrow skills format and hook semantics from Crush, permissions/traces/AGENTS patterns from Codex, rewind ideas from Plandex, and benchmark discipline from aider / mini-SWE-agent / Open SWE.  
> Do **not** build a new runtime, sandbox, orchestration graph, or generic memory layer first.
