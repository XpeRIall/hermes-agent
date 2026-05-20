### Corrected source inventory

The manifest needed correction against actual archive contents. The most important corrections were confirmed locally:

- `02_repos/hermes-agent-main.zip` **present** → Hermes is **source-inspectable**.
- `02_repos/langgraph-main.zip` **present** → LangGraph is **source-inspectable**.
- `02_repos/open-swe-main.zip` is **Open SWE**, not SWE-agent proper.
- `02_repos/mini-swe-agent-main.zip` is **mini-SWE-agent**, not SWE-agent proper.
- `02_repos/crush-main.zip` is **Crush**; do **not** equate it with OpenCode proper.
- `02_repos/claude-code-main.zip` is **not** evidence of official Claude Code product implementation source.

Current official upstream identity checks were additionally used for Hermes, Crush, mini-SWE-agent, SWE-agent proper, OpenCode proper, and Claude Code docs. citeturn1search0turn1search1turn1search2turn1search3turn1search4turn1search5turn1search6

| System | Archive path | Source status | Official upstream checked | Exact commit known | Archive hash available | License path | Notes |
|---|---|---|---|---|---|---|---|
| Hermes | `02_repos/hermes-agent-main.zip` | `source-inspectable` | Yes | `not found` | Yes | `hermes-agent-main/LICENSE` | Manifest correction required |
| aider | `02_repos/aider-main.zip` | `source-inspectable` | Local identity clear | `not found` | Yes | `aider-main/LICENSE.txt` | Inspected repo-map and benchmark sources |
| OpenHands | `02_repos/OpenHands-main.zip` | `source-inspectable` | Local identity clear | `not found` | Yes | `OpenHands-main/LICENSE` | Repo is broad platform surface |
| Codex CLI | `02_repos/codex-main.zip` | `source-inspectable` | Local identity clear | `not found` | Yes | `codex-main/LICENSE` | Strong source for hooks/permissions/traces |
| Plandex | `02_repos/plandex-main.zip` | `source-inspectable` | Local identity clear | `not found` | Yes | `plandex-main/LICENSE` | Strong source for rewind/apply |
| LangGraph | `02_repos/langgraph-main.zip` | `source-inspectable` | Local identity clear | `not found` | Yes | `langgraph-main/LICENSE` | Manifest correction required |
| Open SWE | `02_repos/open-swe-main.zip` | `source-inspectable` | Local identity clear | `not found` | Yes | `open-swe-main/LICENSE` | Not SWE-agent proper |
| mini-SWE-agent | `02_repos/mini-swe-agent-main.zip` | `source-inspectable` | Yes | `not found` | Yes | `mini-swe-agent-main/LICENSE.md` | Not SWE-agent proper citeturn1search2 |
| Crush | `02_repos/crush-main.zip` | `source-inspectable` | Yes | `not found` | Yes | `crush-main/LICENSE` | Not OpenCode proper citeturn1search1turn1search4 |
| Claude Code uploaded repo | `02_repos/claude-code-main.zip` | `partial` / `identity-ambiguous` | Docs baseline used instead | `not found` | Yes | `claude-code-main/LICENSE.md` | Plugins/scripts/examples, not product implementation |
| SWE-agent proper | not in pack | `missing` / `partial` | Yes | n/a | n/a | upstream only | Official repo identified but not deeply inspected citeturn1search3 |
| OpenCode proper | not in pack | `missing` / `partial` | Yes | n/a | n/a | upstream only | Official repo identified separately from Crush citeturn1search4 |
| Claude Code docs baseline | no product source in pack | `docs-only` | Yes | n/a | n/a | official docs | Docs-only baseline citeturn1search5turn1search6 |

### Inspection ledger

| System | File/module inspected | Why inspected | Primitive checked | Finding | Label |
|---|---|---|---|---|---|
| Hermes | `README.md` | Orientation | overall surface | Claims approvals, memory, skills, checkpoints; used only as orientation | `source-verified` |
| Hermes | `run_agent.py` | Core loop | execution, provider abstraction, checkpoints, background review | Agent init includes provider routing and checkpoint flags; background review fork is wired here | `source-verified` |
| Hermes | `agent/background_review.py` | Future-affecting writes | memory/skills proposal-adjacent path | Background review explicitly evaluates conversation and can save memory/skills | `source-verified` |
| Hermes | `tools/skill_provenance.py` | Write-origin semantics | trust/provenance | Distinguishes background-review-created skills from foreground creations | `source-verified` |
| Hermes | `tools/skill_manager_tool.py` | Trusted write path | create/edit/patch/delete skills | Direct skill mutation exists, but no typed promotion gate | `source-verified` |
| Hermes | `agent/prompt_builder.py` | Context activation | `AGENTS.md`, `.hermes.md`, `SOUL.md`, skills | Loads repo/project context files into prompt; includes injection scanning | `source-verified` |
| Hermes | `agent/memory_manager.py` | Memory baseline | provider memory | Memory context/provider abstraction exists, but it is not governed promotion | `source-verified` |
| Hermes | `tools/terminal_tool.py` | Sandbox/permissions | approval and execution backends | Multiple execution backends and dangerous-command approval flow exist | `source-verified` |
| Hermes | `hermes_state.py` | Persistence | session DB/checkpointing | Persistent SQLite state exists; not artifact governance | `source-verified` |
| aider | `aider/coders/base_coder.py` | Core loop | execution/edit loop | Mature Git-centric edit loop with summarization and multi-format coders | `source-verified` |
| aider | `aider/repomap.py` | Context | repo map/retrieval | Strong repo-map primitive exists | `source-verified` |
| aider | `aider/repo.py` | Apply/commit discipline | git/apply/commit | Git-backed workflow and attribution patterns exist | `source-verified` |
| aider | `benchmark/README.md` | Evals | benchmark harness | Serious coding benchmark harness exists | `source-verified` |
| OpenHands | `AGENTS.md` | Project instructions | repo instructions | Strong project-instruction baseline exists | `source-verified` |
| OpenHands | `skills/agent_memory.md` | Memory baseline | repo memory/microagents | Explicit repo memory convention exists | `source-verified` |
| OpenHands | `openhands/app_server/app_conversation/skill_loader.py` | Skills loading | microagents/skills | Loads and merges skills from multiple sources | `source-verified` |
| Codex CLI | `codex-rs/config/src/hook_config.rs` | Hook model | hooks | Rich hook event model and per-hook state are implemented | `source-verified` |
| Codex CLI | `codex-rs/config/src/permissions_toml.rs` | Permission model | permissions/sandbox boundaries | Permission profiles cover filesystem and network domains | `source-verified` |
| Codex CLI | `codex-rs/config/src/skills_config.rs` | Skills config | skill activation | Explicit skills configuration exists | `source-verified` |
| Codex CLI | `codex-rs/core/src/lib.rs` | Architecture surface | sessions, rollouts, AGENTS, sandboxing | Core exposes agents_md, rollout, sandboxing, thread management, skills | `source-verified` |
| Codex CLI | `codex-rs/ext/memories/src/local.rs` | Memory baseline | memory store | Local memory backend exists; still adjacent | `source-verified` |
| Codex CLI | `codex-rs/external-agent-sessions/src/lib.rs` | Session portability | traces/imports | External-agent session import/export helpers exist | `source-verified` |
| Plandex | `app/cli/lib/rewind.go` | Rollback | rewind/conflict detection | Conflict-aware rewind and required-change analysis are implemented | `source-verified` |
| Plandex | `app/cli/cmd/rewind.go` | UX | rewind/apply | CLI rewind UX, revert options, and log-based selection exist | `source-verified` |
| Plandex | `app/server/model/plan/state.go` | Plan lifecycle | execution state | Persistent active plan state exists | `source-verified` |
| Plandex | `app/server/syntax/file_map/map.go` | Context | file map | File-map primitive exists | `source-verified` |
| LangGraph | `libs/checkpoint/langgraph/checkpoint/base/__init__.py` | Persistence model | checkpoints | Full checkpoint abstraction exists with metadata and parents | `source-verified` |
| LangGraph | `libs/checkpoint-sqlite/.../sqlite/__init__.py` | Durable storage | sqlite checkpointer | SQLite saver implements checkpoint persistence | `source-verified` |
| LangGraph | `libs/checkpoint/langgraph/store/base/__init__.py` | Long-term store | store/memory | Store abstraction exists for long-term memory | `source-verified` |
| LangGraph | `libs/langgraph/langgraph/graph/state.py` | Runtime model | stateful graph | Stateful graph/update model exists | `source-verified` |
| Open SWE | `agent/server.py` | Runtime composition | deep agent, middleware, sandbox | Composes deep agent with middleware and sandbox provider backends | `source-verified` |
| Open SWE | `agent/reviewer.py` | Eval-friendly agent form | reviewer graph | Separate reviewer graph exists | `source-verified` |
| Open SWE | `evals/reviewer/README.md` | Benchmark design | reviewer evals | Serious offline review eval design exists | `source-verified` |
| mini-SWE-agent | `src/minisweagent/agents/default.py` | Minimal control loop | core agent loop | Very small query/act/observe loop exists | `source-verified` |
| mini-SWE-agent | `src/minisweagent/environments/local.py` | Execution baseline | environment abstraction | Minimal environment abstraction exists | `source-verified` |
| mini-SWE-agent | `src/minisweagent/run/benchmarks/swebench.py` | Benchmarking | SWE-bench harness | Dedicated SWE-bench batch runner exists | `source-verified` |
| mini-SWE-agent | `src/minisweagent/run/utilities/inspector.py` | Trajectory tooling | trace inspection | Trajectory inspector exists | `source-verified` |
| Crush | `internal/hooks/hooks.go` | Hook semantics | allow/deny/halt/context/rewrite | Concrete hook aggregation semantics are implemented | `source-verified` |
| Crush | `internal/permission/permission.go` | Permissioning | request/grant/deny/auto-approve | Permission service integrates with hook approval shortcuts | `source-verified` |
| Crush | `internal/session/session.go` | Persistence | session state | Session persistence exists | `source-verified` |
| Crush | `internal/skills/skills.go` | Skills | Agent Skills implementation | Agent Skills open-standard implementation exists | `source-verified` |
| Crush | `docs/hooks/README.md` | Hook docs | hook behavior | Docs align with implemented hook semantics; future docs separated in `FUTURE.md` | `source-verified` |
| Claude Code uploaded repo | `README.md`, `plugins/*`, `scripts/*`, `examples/*`, `LICENSE.md` | Identity audit | official product source? | Pack repo is plugin/doc/example material under Anthropic terms, not evidence of official product implementation source | `source-verified` |
| Claude Code docs baseline | official docs search | Docs baseline | hooks/settings/memory official baseline | Treated as docs-only; no product source inspected | `docs-verified` |