# Integration Contracts

## Core rule

> Adopted components may act, observe, rank, plan, edit, test, and propose. They may not directly create trusted future state.

## ExecutorAdapter

**Purpose:** run an agent/tooling loop using a scoped task spec.

**Input:**

- task spec;
- allowed tools;
- permission profile;
- projected context bundle;
- workspace/repo path;
- baseline execution settings.

**Output:**

- RunEvents;
- diffs;
- command logs;
- test results;
- observations;
- proposed claims/artifacts;
- error/failure records.

**Allowed side effects:**

- edit working tree under permission policy;
- run commands under sandbox/approval policy;
- emit proposals.

**Forbidden side effects:**

- trusted memory writes;
- promotion-state mutation;
- canonical requirement/design updates;
- unmediated skill installation;
- unmediated project-instruction rewrites.

## ContextProvider

**Purpose:** select candidate context from repo/history/docs.

**Input:** task, repo state, optional claim/evidence query.

**Output:** candidate context items with source paths, hashes, relevance reason, and confidence.

**Forbidden:** marking context as learned truth.

## EventLogger

**Purpose:** normalize logs/events from adopted systems into Nova RunLedger.

**Input:** tool calls, action/observation events, diffs, command outputs, model messages, hook events.

**Output:** append-only RunEvents with stable IDs and evidence links.

**Forbidden:** interpreting event occurrence as correctness.

## EvidenceCollector

**Purpose:** create evidence objects from source files, diffs, tests, logs, human reviews, and tool outputs.

**Input:** RunEvents and artifacts.

**Output:** Evidence records with source type, scope, hash, and validity hints.

**Forbidden:** promoting evidence into trusted claims without gate.

## ProposalEmitter

**Purpose:** propose future-affecting writes.

**Output types:**

- ProposedClaim;
- ProposedSkillArtifact;
- ProposedProjectInstruction;
- ProposedEvalCheck;
- ProposedDemotion;
- ProposedStalenessMark.

**Required fields:** type, scope, evidence IDs, expected future effect, risk, invalidation hints.

**Forbidden:** trusted writes.

## PromotionGate

**Purpose:** decide whether a proposal may influence future runs.

**Input:** proposal, evidence, scope, risk, tests/evals, human review if required.

**Output:** PromotionDecision with status, reason, reviewer/gate, version, activation eligibility.

**Forbidden:** self-modification by ordinary agent runs.

## SkillExporter

**Purpose:** render trusted `SkillArtifact` into executor-compatible formats.

**Targets:**

- skill markdown;
- `AGENTS.md` snippet;
- `CLAUDE.md` snippet;
- prompt block;
- OpenHands/Codex/aider-compatible instruction if supported.

**Forbidden:** exporting proposed/stale/rejected artifacts as trusted instructions.

## ProjectInstructionExporter

**Purpose:** compile accepted/trusted claims into project instruction surfaces.

**Rule:** generated files are projections from Nova truth, not truth sources.

## DemotionController

**Purpose:** deactivate bad/stale claims/artifacts and record why.

**Input:** regression evidence, attribution report, human review or eval result.

**Output:** DemotionDecision, updated trust state, projection invalidation.

**Forbidden:** deleting evidence/history.
