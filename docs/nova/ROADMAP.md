# Nova Roadmap

## Delivery Principles

- Kernel first: build the trusted ledger/evidence/claim/policy skeleton before substrate composition.
- Evidence before memory: future influence must cite run artifacts.
- Proposal before mutation: untrusted runs create proposals, not trusted state.
- Eval-gated promotion: trust changes require deterministic checks and/or human review.
- Substrate-compatible MVP: reserve artifact shells now, implement only the minimum live family later.
- Small verifiable increments: each PR must preserve existing Hermes runtime behavior unless explicitly gated.

## Phase 0: Context Verification And Architecture Freeze

Objective: freeze the planning boundary before code.

Deliverables:

- Repo survey and persistent-mutation inventory.
- `docs/nova/ARCHITECTURE.md`.
- `docs/nova/ROADMAP.md`.
- `docs/nova/LINEAR_PLAN.md`.
- Linear project description and first-pass issues after verification.

Acceptance criteria:

- Source precedence from `docs/concept/INDEX.md` is followed.
- Existing Hermes entrypoints and mutation paths are cited.
- Phase 1 exclusions are explicit.
- Linear plan has existing issue inventory, duplicate check, and no more than 8 first-pass issues.

Linear issue candidates:

- NOVA-Architecture: Freeze verified substrate runtime architecture.

Risks / decisions:

- Do not let Phase 0 drift into implementation.
- Treat `archive/concept_pre_shrink/` as historical only.

## Phase 1: Trusted Kernel MVP

Objective: add a trusted-kernel skeleton beside Hermes without changing runtime behavior.

Deliverables:

- Trusted-kernel data model skeleton.
- Append-only run/evidence ledger interface.
- Evidence bundle model.
- Typed claim/state skeleton.
- Basic policy gate for future-affecting writes.
- Schema-only artifact shells for reserved substrate types.
- Persistent-mutation inventory across memory, skills, providers, plugins, background review, cron, config, session, and prompt/context paths.
- `docs/nova/MUTATION_INVENTORY.md`.
- Ledger concurrency contract for sequential and concurrent tool execution.
- Replay/debug read surfaces for ledger entries.

Acceptance criteria:

- Existing Hermes conversations behave the same when Nova is disabled or in shadow mode.
- A run can record ordered ledger entries around turn start, tool call, tool result, proposal attempt, and outcome.
- Evidence refs can point to session messages, tool calls/results, files, commands, checks, and retrieval refs.
- Claim/state records cannot be marked trusted without a gate decision.
- Parallel tool calls produce deterministic ledger ordering or explicit parent/child sequence metadata.
- Future-affecting write classes are classified by policy, even if only shadow-recorded.

Linear issue candidates:

- NOVA-Kernel: Create trusted-kernel model skeleton and append-only ledger interface.
- NOVA-Evidence: Implement evidence bundle capture for runs and tool outputs.
- NOVA-Claims: Add typed claim/state skeleton and trust transitions.
- NOVA-Policy: Inventory and gate future-affecting mutation paths.
- NOVA-Substrate: Add proposal records and schema-only artifact shells.

Risks / decisions:

- Decide whether Nova tables live in `state.db` or a separate profile-scoped DB.
- Do not implement substrate composition, memory migration, new sandboxing, provider/model adapters, or autonomous promotion.

## Phase 2: Proposal-Only Learning Loop

Objective: convert selected future-affecting writes into reviewable proposals.

Deliverables:

- `ArtifactProposal` creation API.
- Evidence completeness checks.
- Reviewable proposal diffs.
- Rejection and rollback metadata.
- First intercepted write path, likely skill creation/update from background review.

Acceptance criteria:

- Direct selected write path can be converted to a proposal with evidence.
- Rejection leaves existing Hermes state unchanged.
- Proposal payloads remain small enough for review.
- One artifact family is selected; no multi-family promotion yet.

Linear issue candidates:

- Extend NOVA-Substrate after Phase 1 acceptance.

Risks / decisions:

- Stage plan recommends promoting only project instructions or skills, not both; skills are preferred because Hermes already has explicit skill tooling [doc: docs/concept/06_stage_plan_evals_cutoffs.md:L13-L25].

## Phase 3: Verification And Promotion Gates

Objective: separate generated proposals from trusted artifacts.

Deliverables:

- Static schema validation.
- Scope validation.
- Deterministic checks for the first artifact family.
- Human review record.
- Promotion criteria and trust-level transitions.

Acceptance criteria:

- No artifact reaches staged/active state without a `GateDecision`.
- False-positive promotion risk is measured.
- Promotion can be reverted or demoted with an audit trail.

Linear issue candidates:

- NOVA-Verification: Implement validation, evals, and promotion gates.

Risks / decisions:

- If evaluator acceptance has high regression cost, revert to human-only gating.

## Phase 4: Composition Runtime

Objective: compose verified substrate into later run contexts.

Deliverables:

- `resolve_active_artifacts` implementation.
- Activation records before context influence.
- Context projector support for one narrow activation path.
- Runtime policy enforcement for activation.
- Regression attribution loop.

Acceptance criteria:

- Every active artifact that affects a run is logged.
- A promoted artifact can be demoted and excluded from later runs.
- Context projection is inspectable and does not create hidden prompt mutation.

Linear issue candidates:

- NOVA-Composition: Implement verified substrate composition runtime.

Risks / decisions:

- Do not expand artifact families if regression attribution is too noisy [doc: docs/concept/06_stage_plan_evals_cutoffs.md:L37-L42].

## Phase 5: Adapter Expansion

Objective: harden boundaries around memory, model, tool, and richer skill adapters.

Deliverables:

- Memory adapter boundary.
- Model adapter boundary.
- Tool adapter boundary.
- Richer skill registry integration.
- Integration hardening across CLI/gateway/TUI.

Acceptance criteria:

- Provider memory remains advisory unless converted to typed governed state.
- Adapter activation is policy-checked and logged.
- No adapter bypasses evidence/promotion/activation records.

Linear issue candidates:

- NOVA-Adapters: Implement initial skill/tool/memory/model adapter boundaries.

Risks / decisions:

- This phase is not ready for first-pass Linear implementation issues until the kernel and first artifact family prove value.

## Recommended First Coding Task

Create the trusted-kernel data model skeleton and append-only run/evidence ledger interface without changing existing Hermes runtime behavior.

This task is exactly one PR-sized implementation task. It explicitly excludes substrate composition, multi-artifact activation, autonomous promotion, memory migration, new sandboxing, and provider/model adapter work.
