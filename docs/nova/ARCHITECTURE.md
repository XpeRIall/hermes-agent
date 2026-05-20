# Nova Architecture

## Executive Summary

Nova is **Hermes + verified substrate composition runtime**: a Hermes fork that turns future-affecting reusable agent state into governed, evidence-backed artifacts before that state can influence later runs. The first implementation is deliberately smaller than the full target: a trusted promotion kernel embedded beside Hermes, not a replacement runtime [doc: docs/concept/00_research_brief.md:L3-L19] [doc: docs/concept/01_minimal_concept.md:L1-L13].

Hermes is a strong host because it already has the shell Nova needs: CLI/gateway/TUI entrypoints, tool execution, sessions, memory, skills, plugins, context-file loading, checkpoints, approvals, and background review [repo: run_agent.py:L326-L415] [repo: agent/conversation_loop.py:L85-L117] [doc: docs/concept/02_vendor_adoption_map.md:L20-L22]. Hermes is insufficient as an epistemic core because those surfaces can persist future influence without typed evidence, trust state, activation records, demotion, or regression blame [doc: docs/concept/13_vendor_dossiers.md:L1-L6].

## Core Thesis

A **verified substrate composition runtime** lets an agent propose task-specific cognitive substrate, verify it, promote it, compose it into later runs, and roll it back when it harms outcomes. Substrate artifacts are first-class because future influence must have scope, type, version, trust state, activation rules, evidence, and blameability [doc: docs/concept/01_minimal_concept.md:L7-L23].

The trusted kernel remains fixed and conservative:

| Kernel responsibility | Purpose |
|---|---|
| Run ledger | Append-only causal record of turns, tool calls, gates, activations, and outcomes. |
| Evidence bundle model | First-class pointers to messages, files, commands, checks, and retrieval refs. |
| Typed claim/state store | Scoped, versioned facts/decisions with validation and invalidation state. |
| Policy engine | Blocks or converts future-affecting writes into proposals. |
| Verification and promotion gates | Separate generation from trust. |
| Rollback and auditability | Support demotion, regression attribution, and replay. |

Nova is not just memory, skills, hooks, checkpoints, or evals. Each exists in adjacent systems, including Hermes, but none is equivalent unless it implements governed trust transition for reusable future influence [doc: docs/concept/00_research_brief.md:L11-L19] [doc: docs/concept/manifest/what_to_ignore.md:L91-L127].

## Existing Hermes Baseline

| Surface | Reuse | Nova boundary |
|---|---|---|
| Agent shell | `AIAgent` and `agent.conversation_loop.run_conversation` stay as the host loop [repo: run_agent.py:L3838-L3849] [repo: agent/conversation_loop.py:L532-L535]. | Do not replace the runtime in Phase 1. Insert ledger/evidence recording around the existing loop. |
| Tool execution | Existing sequential/concurrent tool paths, plugin pre-tool hooks, guardrails, and dangerous-command approvals remain [repo: agent/tool_executor.py:L64-L143] [repo: agent/tool_executor.py:L474-L610] [repo: tools/approval.py:L1-L9]. | Tool results are evidence; future-affecting tool calls need policy classification. |
| Sessions | `SessionDB` stores sessions/messages with SQLite, WAL retry, FTS, and tool-call metadata [repo: hermes_state.py:L190-L240] [repo: hermes_state.py:L309-L423] [repo: hermes_state.py:L1433-L1518]. | Useful history store, but not a causal ledger or artifact truth store. |
| Memory | Built-in memory persists `MEMORY.md`/`USER.md`; external providers prefetch and sync turns [repo: tools/memory_tool.py:L109-L260] [repo: run_agent.py:L1949-L1995]. | Advisory unless represented as governed typed state. No direct trusted memory mutation in MVP. |
| Skills | `skill_manage` can create/edit/patch/delete skills and supporting files [repo: tools/skill_manager_tool.py:L373-L458] [repo: tools/skill_manager_tool.py:L557-L785]. | Skill writes are the most practical first interception target. |
| Background review | A daemon fork can review completed turns and call memory/skill tools [repo: agent/background_review.py:L1-L17] [repo: agent/background_review.py:L430-L459]. | Must route to proposals, not trusted writes. |
| Context loading | Prompt builder loads `SOUL.md`, `.hermes.md`, `AGENTS.md`, `CLAUDE.md`, and cursor rules with injection scanning [repo: agent/prompt_builder.py:L55-L73] [repo: agent/prompt_builder.py:L1417-L1456]. | Later activation path for promoted artifacts; Phase 1 only records and reserves the seam. |
| Plugins/providers | Plugin and model-provider systems are discoverable and extensible [repo: model_tools.py:L175-L199] [repo: hermes_cli/plugins.py:L790-L930] [repo: providers/__init__.py:L1-L16]. | Plugin/provider outputs are untrusted unless gated. No adapter expansion in Phase 1. |
| Checkpoints/logs | Checkpoints and logs support recovery and debugging [repo: tools/checkpoint_manager.py:L623-L657] [repo: hermes_logging.py:L156-L252]. | Checkpoints are not blame; ledger must identify which active artifact influenced a run. |

Direct mutation paths to intercept or inventory first: memory tool writes, external memory provider sync/mirroring, skill management, background review, context-engine/session-end hooks, plugin hooks, cron jobs, session title/history mutations, config/plugin/provider changes, and file/tool writes that alter future agent behavior.

## Target Architecture

| Layer | Responsibility | Phase 1 posture |
|---|---|---|
| Agent shell / orchestration surface | Existing Hermes CLI, gateway, TUI, ACP, batch runner, and tool loop. | Reuse unchanged. |
| Trusted runtime kernel | Owns ledger, evidence, claims, policy, gates, transitions, rollback metadata. | Build skeleton only. |
| Evidence and run ledger | Append-only transitions for runs, tool calls, proposals, gates, activations, outcomes. | Implement interface and storage shape. |
| Typed claim/state store | Scoped facts/decisions with status and evidence. | Minimal schema and write API. |
| Policy runtime | Classifies future-affecting writes and converts them to proposal flow. | Basic gate in shadow/block modes. |
| Substrate registry | Stores artifact shells and versions. | Schema-only shells for future artifact types. |
| Proposal / verification / promotion lifecycle | Proposal, evidence, gate decision, staged/active version. | Proposal records, no autonomous promotion. |
| Composition runtime | Resolves active artifacts into task context. | Reserved, not implemented in Phase 1. |
| Skill/tool/model/memory adapters | Host-specific activation and interception adapters. | Inventory only, except skill-write proposal seam if selected. |
| Evaluation harness | Deterministic and reviewer checks for promotion. | Design and smoke hooks, not full eval platform. |
| Activation/regression records | Which artifact versions influenced a run and what outcomes followed. | Record shape; full attribution later. |

Minimal implementation objects:

| Object | Required fields |
|---|---|
| `RunLedgerEntry` | `id`, `run_id`, `seq`, `kind`, `actor`, `subject_ref`, `args_hash`, `evidence_bundle_id`, `policy_decision_id`, `created_at`. |
| `EvidenceBundle` | `id`, `run_id`, `message_refs`, `file_refs`, `command_refs`, `tool_result_refs`, `check_refs`, `retrieval_refs`, `created_at`. |
| `TypedClaim` | `id`, `type`, `scope`, `statement`, `status`, `evidence_bundle_id`, `created_from`, `invalidated_by`, `created_at`. |
| `ArtifactProposal` | `id`, `artifact_type`, `scope`, `candidate_payload_ref`, `evidence_bundle_id`, `originating_run_id`, `proposed_by`, `status`. |
| `ArtifactVersion` | `artifact_id`, `version`, `payload_ref`, `trust_state`, `activation_rule`, `evidence_bundle_id`, `parent_version`. |
| `GateDecision` | `id`, `proposal_id`, `gate_type`, `result`, `reviewer_or_eval_id`, `reason`, `created_at`. |
| `ActivationRecord` | `id`, `run_id`, `artifact_version_ids`, `activation_context_hash`, `policy_snapshot_id`, `created_at`. |
| `RegressionRecord` | `id`, `run_id`, `artifact_id`, `symptom`, `linked_checks`, `decision`, `created_at`. |

This follows the canonical minimal kernel schema and keeps evidence first-class [doc: docs/concept/09_data_model_kernel.md:L1-L12].

## Artifact / Substrate Model

| Artifact type | Purpose | Minimum metadata | Verification | Runtime constraint |
|---|---|---|---|---|
| Lens | Task-specific interpretation frame. | `scope`, `inputs`, `outputs`, `activation_rule`, `evidence`. | Human review plus benchmark need. | Shadow-only until measurable value. |
| Schema | Typed structure for claims/artifacts. | `fields`, `validators`, `scope`, `version`. | Deterministic validation. | Kernel-owned; LLM may propose changes only. |
| Eval | Promotion or regression check. | `check_command/ref`, `expected_signal`, `scope`. | Deterministic run and false-positive review. | Gate input, not trusted by itself. |
| Context projector | Maps active artifacts into prompt/tool context. | `inputs`, `projection_target`, `budget`, `activation_rule`. | Snapshot comparison and injection scan. | No hidden prompt mutation. |
| Skill | Reusable procedure. | Skill payload, scope, evidence, tests/checks, trust state. | Syntax/security scan plus reviewer/eval gate. | First likely live artifact family. |
| Tool adapter | Governed tool boundary. | Tool schema, side-effect profile, permissions. | Static safety review and sandbox policy. | Deferred; no new tool promotion in Phase 1. |
| Analyzer | Reads outputs and emits claims/signals. | Inputs, claim schema, confidence policy. | Held-out checks against false claims. | Advisory until promoted. |
| Transform | Deterministic conversion or rewrite. | Input/output contract, idempotence, rollback. | Golden tests. | No silent state rewrite. |
| Policy | Rule controlling mutation or activation. | Rule text/code, scope, enforcement mode. | Deterministic policy tests and human approval. | Kernel policy cannot be directly LLM-generated. |
| Memory adapter | Provider recall/write bridge. | Provider, scope, evidence mapping, trust boundary. | Provider-output audit. | Provider memory stays advisory in MVP. |
| Model adapter | Provider/model behavior wrapper. | Provider, model scope, constraints. | Compatibility tests. | Deferred; no provider/model expansion in Phase 1. |

Non-MVP artifact types remain compact target-shape definitions. The MVP reserves the seam but does not implement the full artifact universe [doc: docs/concept/manifest/what_to_ignore.md:L195-L228].

## Lifecycle Flows

Normal run:

1. Hermes starts the turn and creates or resolves a `run_id`.
2. Nova appends `run.started`, input, model/context snapshot, and policy snapshot entries.
3. Existing memory/context prefetch and tool loop execute unchanged.
4. Tool calls and results become evidence refs.
5. Any active artifacts are recorded in `ActivationRecord` before influencing context.
6. Final response, checks, and outcomes are appended.

Proposal creation:

1. A memory/skill/background/plugin path attempts future-affecting state.
2. Policy classifies the write.
3. Trusted direct mutation is denied or shadowed.
4. `ArtifactProposal` is created with an `EvidenceBundle`.

Verification and promotion:

1. Static validation checks schema, scope, side-effect profile, and evidence completeness.
2. Human or evaluator gate records a `GateDecision`.
3. Passing proposals become staged or active `ArtifactVersion`s.
4. Activation rules determine future eligibility.

Regression and rollback:

1. Outcomes record checks, feedback, and artifact versions active during the run.
2. Regressions link symptoms to active artifacts where possible.
3. Demotion changes trust state; rollback points to a previous version.
4. Every transition is appended, never rewritten.

These flows implement the proposal, activation, outcome, demotion, and rollback contracts in the current research [doc: docs/concept/08_integration_contracts.md:L3-L62].

## Trust Model

LLMs may propose artifacts, claims, evidence links, and explanations. LLMs may not directly create trusted state, overwrite kernel schema, change policy enforcement, mark artifacts active, delete evidence, or rewrite the ledger.

Deterministic validation must check schema shape, scope, stable identifiers, evidence references, payload size, side-effect profile, and activation eligibility. Eval gates can promote only within their declared scope. Human review is required for trusted activation until benchmarks justify narrower automation.

Forbidden direct mutations:

- unverified memory writes that become future truth;
- background review landing trusted skills or memory;
- plugin/provider writes that bypass proposal records;
- hidden context/prompt activation;
- unlogged policy, config, or adapter changes;
- artifact promotion without a gate decision.

## MVP Boundary

MVP may implement only a subset of artifact types. It must still preserve substrate-compatible object shapes so lenses, schemas, evals, projectors, skills, tools, analyzers, transforms, policies, memory adapters, and model adapters fit later.

Phase 1 explicitly excludes generalized memory replacement, provider memory, generalized retrieval memory, new sandboxing, new repo map, new session runtime, autonomous promotion, multi-artifact composition runtime, model/provider adapter expansion, and workflow DAG execution [doc: docs/concept/04_mvp_shape.md:L5-L32].

## Non-Goals

- No autonomous self-modifying production runtime.
- No direct unverified memory mutation.
- No hidden state transitions.
- No learning without evidence.
- No tool/skill promotion without verification.
- No new runtime in Phase 1.
- No new sandbox in Phase 1.
- No workflow DAG engine in Phase 1.
- No generic memory replacement in Phase 1.

## Open Questions

| Question | Decision needed |
|---|---|
| First live artifact family | Skills are recommended because Hermes already has explicit skill objects and write tooling [doc: docs/concept/06_stage_plan_evals_cutoffs.md:L13-L25]. |
| Ledger storage | New SQLite tables beside `SessionDB` or a separate Nova DB? |
| Evidence refs | Which message/tool/file refs are stable enough for replay across compression and session rewrites? |
| Policy mode | Start in shadow-only, block direct writes, or convert writes immediately? |
| Benchmark cutoff | What reviewer burden and regression rate justify expansion beyond one artifact family? |

## Validation Criteria

Nova remains valid only if longitudinal benchmarks show governed promotion improving later runs beyond ordinary memory/skills/instructions and if activation regressions can be blamed and demoted [doc: docs/concept/07_benchmark_design.md:L1-L35]. Shrink or defer if gains come from retrieval/static docs, reviewer burden dominates, evidence refs are unstable, or integration requires replacing Hermes [doc: docs/concept/10_kill_criteria.md:L1-L10].
