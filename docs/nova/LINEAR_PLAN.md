# Nova Linear Plan

## Context Verification

| Check | Result |
|---|---|
| Repo root | `E:/Repositories/hermes-agent` from `git rev-parse --show-toplevel`. |
| Concept index | `docs/concept/INDEX.md` exists. |
| Nova docs directory | `docs/nova/` exists and this pass created the planning package. |
| Concept docs found | `00_research_brief.md`, `01_minimal_concept.md`, `02_vendor_adoption_map.md`, `03_first_primitives_to_take.md`, `04_mvp_shape.md`, `05_target_shape.md`, `06_stage_plan_evals_cutoffs.md`, `07_benchmark_design.md`, `08_integration_contracts.md`, `09_data_model_kernel.md`, `10_kill_criteria.md`, `11_risks_and_abstraction_errors.md`, `12_source_inspection_ledger.md`, `13_vendor_dossiers.md`, plus `manifest/`, `project_thesis/`, `vendor_dossiers/`, `appendices/`, and `archive/`. |
| Source precedence applied | `INDEX.md`, manifest controls, top-level numbered canonical docs, supporting `project_thesis/`, supporting `vendor_dossiers/`, archive/pre-shrink historical only. |
| Main repo entrypoints discovered | `cli.py`, `hermes_cli/main.py`, `gateway/run.py`, `tui_gateway/server.py`, `acp_adapter/session.py`, `batch_runner.py`, `mcp_serve.py`, `run_agent.py`. |
| Main execution seam | `run_agent.AIAgent` delegates to `agent.conversation_loop.run_conversation`; tool calls flow through `agent/tool_executor.py`, `model_tools.py`, and `tools/registry.py`. |
| Stateful / mutating surfaces discovered | `hermes_state.SessionDB`, `tools/memory_tool.py`, `tools/skill_manager_tool.py`, `agent/background_review.py`, `agent/memory_manager.py`, plugin hooks, provider plugins, prompt/context files, cron jobs, checkpoints, logs, config writes, terminal/file tools. |
| Evidence gaps | No runtime implementation found for append-only run ledger, typed claim store, evidence bundle model, substrate registry, activation record, artifact proposal, or promotion gate. Repo survey did not exhaustively inspect every gateway adapter, plugin, or test module. |

## Coordinator Synthesis Ledger

| Category | Current synthesis |
|---|---|
| Confirmed facts | Hermes is the first host; its shell/runtime stays intact. Existing memory, skill, background review, plugin, context, cron, and session paths can create future influence without Nova governance. |
| Architectural decisions | Start with trusted kernel: run ledger, evidence bundle, typed claim/state skeleton, append-only transitions, basic policy gate, proposal records, and schema-only artifact shells. |
| Assumptions | Phase 1 can run in disabled/shadow mode without changing existing Hermes behavior. Stable evidence references can be derived from session messages, tool calls, files, commands, checks, and retrieval refs. |
| Contradictions resolved | Canonical docs shrink the MVP to a minimal governed promotion layer while supporting thesis reserves a broader substrate taxonomy. Resolution: implement kernel-first and keep broader artifacts schema-only until benchmarks justify activation. |
| Evidence gaps | Exact upstream SHAs for research archives are unavailable; SWE-agent proper and OpenCode proper were not deeply source-inspected; Claude Code is docs-only. |
| Implementation candidates | Kernel DB/tables or sidecar DB, ledger interface, evidence bundle refs, claim/state skeleton, policy classifier, proposal records, mutation inventory. |
| Linear issue candidates | Six first-pass issues listed in the write plan; future verification/composition/adapter issues deferred. |
| Existing Linear inventory | Project `nova` exists in team `Restia`; no existing issues found. |
| Candidate Linear actions | Update project description/summary/priority; create six phase-mapped parent issues. No milestones or child issues in first pass. |
| Verification blockers | Verification Lead found one pre-mutation blocker: Coordinator GO/NO-GO was not yet recorded. This document now records GO before mutation. |
| Final go/no-go | GO for the documented six-issue first pass after verification; no deferred issues should be created in this pass. |

## Project Description

Proposed Linear project description:

Nova is a Hermes fork focused on a verified substrate composition runtime: future-affecting reusable agent state must move through evidence-backed proposal, validation, promotion, activation logging, and rollback/demotion instead of becoming trusted state directly.

Current goal: architecture and planning freeze before implementation.

Initial deliverables:

- `docs/nova/ARCHITECTURE.md`
- `docs/nova/ROADMAP.md`
- `docs/nova/LINEAR_PLAN.md`

Implementation principle: trusted kernel first, substrate-compatible MVP. Phase 1 starts with run ledger, evidence bundle model, typed claim/state skeleton, append-only transitions, basic policy gates, mutation inventory, and schema-only artifact shells.

## Existing Linear Inventory

Read-only Linear inspection performed on 2026-05-20 and refreshed immediately before mutation:

- Project: `nova`
- Project ID: `e0035177-3a10-4c8c-9d05-58e72715ad83`
- Team: `Restia` (`RES`)
- Current summary: `Custom fork of the hermes agent`
- Current description: `[TBD]`
- Current status: `Backlog`
- Current milestones: none
- Existing issues in project: none found via `list_issues(project="nova", includeArchived=true, limit=250)`.

| Existing issue | Key | Status | Scope summary | Action |
|---|---|---|---|---|
| None found | n/a | n/a | n/a | Create first-pass issue set after verification. |

## Linear Write Plan

Status after verification and mutation: completed for the documented first pass.

Coordinator go/no-go before Linear mutation: **GO**.

### Project Update

Update project `nova`:

- Summary: `Verified substrate composition runtime for Hermes`
- Description: use the Project Description section above.
- Priority: Medium (`3`)

### Issues To Create Now

First-pass issue count: 6.

| Title | Type | Phase | Needed now | Dependencies |
|---|---|---|---|---|
| NOVA-Architecture: Freeze verified substrate runtime architecture | Parent issue | Phase 0 | Captures planning freeze, evidence basis, and Linear/doc handoff. | None |
| NOVA-Kernel: Create trusted-kernel model skeleton and append-only ledger interface | Parent issue | Phase 1 | First coding task; anchors implementation in kernel instead of substrate registry alone. | Architecture freeze |
| NOVA-Evidence: Implement evidence bundle capture for runs and tool outputs | Parent issue | Phase 1 | Evidence is the central trust boundary and must exist before promotion. | NOVA-Kernel |
| NOVA-Claims: Add typed claim/state skeleton and trust transitions | Parent issue | Phase 1 | Prevents memory/skills from becoming untyped truth. | NOVA-Kernel, NOVA-Evidence |
| NOVA-Policy: Inventory and gate future-affecting mutation paths | Parent issue | Phase 1 | Prevents direct writes from bypassing proposals. | NOVA-Kernel, NOVA-Evidence |
| NOVA-Substrate: Add proposal records and schema-only artifact shells | Parent issue | Phase 1 / Phase 2 seam | Preserves substrate architecture without implementing composition. | NOVA-Kernel, NOVA-Evidence |

### Acceptance Criteria Summaries

NOVA-Architecture:

- `docs/nova/ARCHITECTURE.md`, `ROADMAP.md`, and `LINEAR_PLAN.md` exist and cite repo/research evidence.
- Phase 1 exclusions are explicit.
- Linear first-pass issue set is verified and no duplicate issues exist.
- No implementation code is included.

NOVA-Kernel:

- Adds data model skeleton and interface for append-only run/evidence ledger.
- Records stable entry kinds for run start/end, tool call/result, policy decision, proposal attempt, activation snapshot, and outcome.
- Defines deterministic ordering for sequential and concurrent tool execution.
- Runtime behavior is unchanged when the kernel is disabled or shadow-only.
- Excludes substrate composition, multi-artifact activation, autonomous promotion, memory migration, new sandboxing, and provider/model adapter work.

NOVA-Evidence:

- Defines `EvidenceBundle` refs for messages, files, commands, tool results, checks, and retrieval refs.
- Can attach evidence to a proposal or claim.
- Fails closed on missing required refs for trusted transitions.
- Does not store raw secrets or unbounded payloads.

NOVA-Claims:

- Defines typed claim/state skeleton with scope, status, evidence, source, invalidation, and trust state.
- No claim can become trusted without a gate decision.
- Claims are queryable for audit/debug.
- Does not replace general memory.

NOVA-Policy:

- Produces persistent-mutation inventory for memory, skills, providers, plugins, background review, cron, config, session, and prompt/context surfaces.
- Classifies future-affecting writes.
- Provides a basic policy gate that can shadow-record, block, or convert selected writes to proposals.
- Does not introduce a new sandbox or permission platform.

NOVA-Substrate:

- Defines proposal records and schema-only artifact shells for lens, schema, eval, context projector, skill, tool adapter, analyzer, transform, policy, memory adapter, and model adapter.
- Implements only proposal/shell records, not composition or activation.
- Includes trust states and activation-rule fields needed by future phases.
- Keeps broad artifact families future-reserved unless Phase 2 selects one.

### Candidate Issues Intentionally Not Created

| Candidate | Reason deferred | Ready when |
|---|---|---|
| NOVA-Verification: Implement validation, evals, and promotion gates | Requires kernel/evidence/proposal records first; otherwise it becomes a vague eval placeholder. | Phase 1 ledger and proposal records exist. |
| NOVA-Composition: Implement verified substrate composition runtime | Future-placeholder-only before activation records and first artifact family are validated. | One artifact family passes gated promotion and activation logging. |
| NOVA-Adapters: Implement initial skill/tool/memory/model adapter boundaries | Adapter expansion is explicitly out of Phase 1. | Policy inventory shows which adapter seam is needed first. |
| NOVA-DevEx: Add replay, debugging, and developer workflows | Initial replay/debug surfaces are included in NOVA-Kernel; broader DevEx should wait for real ledger data. | Ledger entries exist and need user-facing inspection. |
| NOVA-Memory: Replace or migrate memory | Excluded from Phase 1; general memory does not prove the thesis. | Memory is represented as governed typed state and benchmark need is proven. |
| NOVA-Sandbox: Add new sandboxing | Explicit Phase 1 non-goal. | Separate security requirement appears after kernel MVP. |

### Noise Check

- Duplicate issues: none found.
- Future-placeholder-only issues: none proposed for creation.
- Every created/updated issue maps to a roadmap phase.
- Every created/updated issue has concrete acceptance criteria.
- First-pass issue count: 6, under the 8-issue hard cap.
- No child issues proposed in the first pass; hierarchy is flat until implementation-ready child tasks exist.

## Roadmap Phase To Linear Mapping

| Phase | Linear issues |
|---|---|
| Phase 0 | NOVA-Architecture |
| Phase 1 | NOVA-Kernel, NOVA-Evidence, NOVA-Claims, NOVA-Policy, NOVA-Substrate |
| Phase 2 | Extend NOVA-Substrate or create one artifact-family issue after Phase 1 |
| Phase 3 | Deferred NOVA-Verification |
| Phase 4 | Deferred NOVA-Composition |
| Phase 5 | Deferred NOVA-Adapters |

## Verification Findings

Verification Lead review completed before Linear mutation:

- Docs go/no-go: GO.
- Linear updates go/no-go: GO after this Coordinator GO/NO-GO record.
- Blockers addressed: Coordinator GO/NO-GO was missing and is now recorded above.
- Warnings: Linear duplicate inventory was read-only and found no issues; do not create deferred verification, composition, adapter, memory, or sandbox issues in this first pass.
- Issue-count challenge: passed. The first-pass plan contains six parent issues, each phase-mapped with concrete acceptance criteria.

## Created / Updated Linear Issues

Project updated:

- Project: `nova`
- Project URL: https://linear.app/restia/project/nova-c1609e1ac20a
- Summary: `Verified substrate composition runtime for Hermes`
- Description: updated to the Project Description section above.
- Priority: Medium (`3`)

Issues created:

| Key | Title | URL | Notes |
|---|---|---|---|
| RES-5 | NOVA-Architecture: Freeze verified substrate runtime architecture | https://linear.app/restia/issue/RES-5/nova-architecture-freeze-verified-substrate-runtime-architecture | Phase 0 planning freeze. |
| RES-6 | NOVA-Kernel: Create trusted-kernel model skeleton and append-only ledger interface | https://linear.app/restia/issue/RES-6/nova-kernel-create-trusted-kernel-model-skeleton-and-append-only | Recommended first coding task; blocked by RES-5. |
| RES-7 | NOVA-Evidence: Implement evidence bundle capture for runs and tool outputs | https://linear.app/restia/issue/RES-7/nova-evidence-implement-evidence-bundle-capture-for-runs-and-tool | Phase 1 evidence model; blocked by RES-6. |
| RES-8 | NOVA-Claims: Add typed claim/state skeleton and trust transitions | https://linear.app/restia/issue/RES-8/nova-claims-add-typed-claimstate-skeleton-and-trust-transitions | Phase 1 typed state; blocked by RES-6 and RES-7. |
| RES-9 | NOVA-Policy: Inventory and gate future-affecting mutation paths | https://linear.app/restia/issue/RES-9/nova-policy-inventory-and-gate-future-affecting-mutation-paths | Phase 1 policy gate and mutation inventory; blocked by RES-6 and RES-7. |
| RES-10 | NOVA-Substrate: Add proposal records and schema-only artifact shells | https://linear.app/restia/issue/RES-10/nova-substrate-add-proposal-records-and-schema-only-artifact-shells | Phase 1 / Phase 2 seam; blocked by RES-6 and RES-7. |

No milestones, cycles, or child issues were created.

## Skipped Duplicate Issues

None. Existing inventory found no issues in project `nova`.

## Failed Linear Actions / Manual Follow-Up

None.
