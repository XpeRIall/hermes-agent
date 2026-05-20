The table below is the core architecture decision surface.

| System | Primitive actually found | Governance-equivalent | Adoption decision | Why |
|---|---|---:|---|---|
| Hermes | Background memory/skill review fork, context-file loading, approvals, checkpoints, session DB, provider abstraction | No | **Adopt host / fork selectively** | Strongest adjacent mechanism to Nova’s problem; already writes future-affecting state, which is precisely what Nova should govern. **`source-verified`** |
| aider | Repo map, Git-centric edit loop, commit discipline, benchmark harness | No | **Adopt/imitate** | High-value repo-context and benchmark patterns; not a promotion system. **`source-verified`** |
| OpenHands | App/server conversation and skill-loading baselines, microagent/repo-memory conventions | No | **Benchmark / partial imitation**, not foundation | Useful org-agent patterns, but the inspected repo is broader platform surface and not the sharpest minimal Nova host. **`source-verified`** |
| Codex CLI | Sandbox/permissions model, AGENTS integration, hooks, skills config, traces/rollouts, session import/export, memories extension | No | **Adopt/port concepts selectively** | Best mature source for permissioning, hook state, session traces, and instruction plumbing. **`source-verified`** |
| Plandex | Plan/apply/branch/rewind, conflict-aware rewind, file-map support | No | **Adopt/imitate** | Best inspected source for apply/rewind UX and plan-state rollback semantics. **`source-verified`** |
| LangGraph | Durable execution, interrupts/resume, checkpoint/store abstractions | No | **Port interface later; do not found MVP on it** | Valuable persistence contract, but Nova does not need a new orchestration substrate first. **`source-verified`** |
| Open SWE | Sandboxed internal-coding-agent composition, reviewer graph, eval design | No | **Benchmark / imitate reviewer-eval patterns** | Useful eval and org-integration patterns; overbuilt as Nova foundation. **`source-verified`** |
| mini-SWE-agent | Minimal linear agent loop, environment abstraction, benchmark harness, trajectory inspector | No | **Benchmark baseline** | Good control/baseline; not feature source for governed promotion. **`source-verified`** |
| SWE-agent proper | Official repo identified, not deeply source-inspected in this run | Incomplete | **Defer** | Do not rely on it for architecture until source-inspected in a follow-up. **`partial`** |
| Crush | Agent Skills standard implementation, permission service, hook aggregation and rewrite flow, session persistence | No | **Adopt/imitate skills + hook semantics** | Strong source for skills and hook contracts; not equivalent to OpenCode proper. **`source-verified`** |
| OpenCode proper | Official repo identified separately from Crush | Incomplete | **Defer** | Do not equate with Crush without direct inspection. **`partial`** |
| Claude Code | Official docs baseline only | No | **Docs baseline only** | Product behavior is not source-inspectable here; use as counterfactual only. **`docs-verified`** |

The most important source-grounded conclusion is that **Hermes is the best first host**, while **Codex, Crush, Plandex, and LangGraph** are the best donor systems for specific primitives. That is **`inferred`** from the combination of inspected Hermes self-improvement/state-writing paths and the donor systems’ tighter implementations for permissions, hooks, skills, rollback, and checkpoints.

Why Hermes should be the proving ground:

Hermes already contains the exact failure mode Nova cares about: future-affecting writes produced from ordinary runs. The inspected files show a **background review fork** that can save memory and skills, a **skill provenance** mechanism that distinguishes background self-improvement from foreground user-directed skill changes, a **skill manager** that performs create/edit/patch/delete operations, **context-file injection** into the system prompt, and **persistent session state / checkpoints**. That is a rich adjacent substrate, but it still lacks typed promotion, scope-checked activation, formal trust state, and regression attribution. **`source-verified`** via `run_agent.py`, `agent/background_review.py`, `tools/skill_provenance.py`, `tools/skill_manager_tool.py`, `agent/prompt_builder.py`, `hermes_state.py`.

Why not found Nova on LangGraph/OpenHands/Open SWE:

Those systems provide durable execution and platform surfaces, but the inspected evidence points to a different problem than Nova’s first problem. Nova’s differentiator is **governance of reusable state**, not graph orchestration, not org integrations, and not reviewer UX. Building on those systems first would likely recreate substrate work Nova explicitly said it should avoid. **`inferred`**