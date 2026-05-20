# Vendor / Open-Source Adoption Map

This map is not a final source-verified research result. It is the **research target**: what the next Deep Research run should verify in source and then accept, refine, or reject.

## Adoption principle

> Take mature OSS primitives. Do not inherit their trust semantics.

Imported components may:

- read repos;
- rank context;
- edit files;
- run commands;
- generate plans;
- collect logs;
- create candidate skills;
- summarize findings;
- propose memory/claims/instructions.

Imported components may not directly:

- create trusted memory;
- alter canonical requirements;
- promote design decisions;
- install active future skills;
- rewrite trusted `AGENTS.md` / `CLAUDE.md`;
- mark requirements satisfied;
- mutate promotion policy.

## Summary table

| System | Source status in uploaded pack | Reuse stance | What to take | What to avoid | Nova multiplier |
|---|---|---|---|---|---|
| Hermes | included, source-inspectable | preserve shell; replace learning semantics | prompt/context loading, tool registry, checkpoint manager, approvals, skills UX, provider plumbing | flat authoritative memory, direct background review writes, provider-as-truth | wrap writes into proposals; turn skills into governed artifacts |
| aider | included, source-inspectable | adopt/port selectively | repo map, git/diff discipline, benchmark patterns, coding-loop ergonomics | treating repo map as learning; no governance layer | convert repo relevance into evidence links and claim anchors |
| OpenHands | included, source-inspectable | adopt runtime/event pieces | action/observation model, event service, sandbox service, skill/microagent surfaces | treating event logs as causal ledgers; skill existence as trust | normalize events into RunLedger and proposals |
| Codex CLI | included, source-inspectable for CLI/repo; product claims need docs | adopt protocol/sandbox/hook/trace ideas | state/logs, sandboxing, hooks, rollout traces, AGENTS.md, MCP/protocol surfaces, skills | product/cloud behavior inferred from CLI source; memory as truth | use traces/hooks as evidence collectors; AGENTS.md as projection target |
| Plandex | included, source-inspectable | imitate/fork plan workflow | plan/apply/reject/rewind, context-by-path, branch/task state | treating plan success as requirement truth | attach claims/evidence/trust to plan nodes |
| Crush / OpenCode | included as `crush-main`; identity/license requires care | imitate mostly; adopt only after license review | hooks/events/permissions/skills/provider abstractions, terminal ergonomics | direct code adoption without FSL review; name confusion | use as design reference for event+permission surfaces |
| Claude Code | public repo/examples only; docs baseline | interop/spec inspiration | CLAUDE.md, hooks, skills, plugins, settings scopes, commands | treating proprietary product claims as source-verified | export Nova-approved state into Claude-compatible surfaces |
| LangGraph | included as `02_repos/langgraph-main.zip`; source-inspectable | optional orchestration/checkpointing only | durable execution, checkpointing, state graph, human-in-loop, replay/time travel | using workflow state as epistemic truth; importing a whole framework before the kernel proves value | use for durable workflows if Nova needs orchestration, while Nova owns claims/evidence/promotion |
| Open SWE | included as `02_repos/open-swe-main.zip`; source-inspectable; not SWE-agent | imitate/adapt coding-agent harness patterns | LangGraph/Deep Agents harness, sandbox lifecycle, Slack/Linear/GitHub invocation, curated tools, reviewer evals | treating Open SWE as SWE-agent; treating agent task success as governed promotion | use invocation/sandbox/reviewer patterns as evidence and executor surfaces |
| SWE-agent proper | not included | exclude or fetch official source/docs if still in scope | ACI, trajectories, SWE-bench-like workflow after verification | using Open SWE as a substitute without saying so | benchmark/trajectory reference only if source is added or fetched |

## Recommended first five adoption actions

1. **Patch Hermes source manifest and inspect Hermes source paths.** Verify current shell seams and direct persistent-write paths. Primary paths: `run_agent.py`, `agent/prompt_builder.py`, `agent/memory_manager.py`, `agent/background_review.py`, `tools/memory_tool.py`, `tools/skill_manager_tool.py`, `tools/checkpoint_manager.py`, `acp_adapter/permissions.py`.
2. **Mine aider for repo intelligence.** Inspect `aider/repomap.py`, `aider/repo.py`, `aider/commands.py`, and `benchmark/`. Decide whether to port repo map or wrap it as a context provider.
3. **Mine OpenHands for event/sandbox/action structure.** Inspect `openhands/app_server/event/`, `openhands/app_server/sandbox/`, `openhands/app_server/app_conversation/`, `openhands/app_server/user/skills_router.py`, and action/observation core modules.
4. **Mine Plandex for plan/apply/rewind.** Inspect `app/shared/data_models.go`, `app/shared/plan_config.go`, `app/cli/lib/rewind.go`, apply/reject APIs, and server DB plan/context helpers.
5. **Mine Codex for hooks/sandbox/trace/projection conventions.** Inspect `codex-rs/state/`, `codex-rs/hooks/`, `codex-rs/sandboxing/`, `codex-rs/rollout-trace/`, `codex-rs/skills/`, `docs/agents_md.md`, and `docs/sandbox.md`.
6. **Mine LangGraph only if durable workflow infrastructure is needed.** Inspect `libs/langgraph/langgraph/graph/state.py`, `libs/langgraph/langgraph/pregel/`, `libs/langgraph/langgraph/runtime.py`, `libs/checkpoint/langgraph/checkpoint/`, `libs/checkpoint-postgres/langgraph/checkpoint/postgres/`, and `libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/`.
7. **Mine Open SWE as a coding-agent harness reference, not as SWE-agent.** Inspect `README.md`, `AGENTS.md`, `langgraph.json`, `agent/server.py`, `agent/prompt.py`, `agent/utils/sandbox.py`, `agent/integrations/`, `agent/middleware/`, `agent/tools/`, `agent/reviewer*.py`, and `evals/reviewer/`.

## License caution

- MIT/Apache components are likely easier to reuse, subject to normal license review.
- OpenHands has an enterprise directory with separate licensing; avoid importing enterprise code unless explicitly cleared.
- Crush is FSL-1.1-MIT in the uploaded pack; treat as imitate/design-reference until legal review.
- Claude Code public repo is not a reusable implementation substrate; use as docs/provider baseline and interop surface only.
- LangGraph is MIT in the uploaded snapshot.
- Open SWE is MIT in the uploaded snapshot, but it should not be conflated with SWE-agent.

## Adoption decision rule

Adopt or fork a component only if it is:

1. source-inspectable;
2. license-compatible;
3. modular enough to extract or wrap;
4. useful to the ledger/evidence/proposal/promotion loop;
5. not a hidden trust-semantic dependency.

Otherwise, imitate the invariant rather than copying the code.
