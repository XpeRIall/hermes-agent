# Minimal Nova Concept

## One-line definition

Nova is a **governed promotion layer for future-affecting agent state**.

It is not primarily a memory system, coding agent, workflow engine, eval harness, or provider wrapper.

## Core invariant

> No persistent object that can influence future runs becomes trusted future influence unless it has proposal, evidence, scope, type, version, trust state, promotion decision, activation record, demotion path, and regression-attribution path.

## What counts as future-affecting state

A future-affecting write includes any persistent thing that can influence later behavior:

- memory;
- user preference;
- repo fact;
- requirement interpretation;
- assumption;
- design decision;
- project instruction;
- `AGENTS.md` / `CLAUDE.md` snippet;
- skill;
- hook;
- test/eval/check;
- workflow template;
- context projection rule;
- policy or permission profile;
- artifact activation rule;
- provider-derived conclusion.

## What Nova owns

Nova should own:

- run ledger;
- evidence store;
- typed claims;
- proposal queue;
- trust states;
- promotion gate;
- demotion/rollback records;
- regression attribution;
- projection/export of trusted state into agent surfaces;
- minimal artifact manifest and activation log.

## What Nova should borrow

Nova should borrow or fork:

- repo maps and context ranking;
- git/diff/commit discipline;
- action/event/trajectory logging;
- sandboxing and permissions;
- plan/apply/reject/rewind workflows;
- skills/plugins/microagents as carrier formats;
- hook systems;
- benchmark harnesses;
- orchestration/checkpointing if needed;
- terminal/UI/provider surfaces later.

## Non-goals

Nova should not initially build:

- a full coding agent from scratch;
- a universal cognitive operating system;
- autonomous promotion;
- generalized Lens/Eval/Analyzer/Transform artifact universes;
- provider memory as canonical truth;
- live policy learning;
- model fine-tuning promotion;
- multi-agent substrate negotiation;
- a broad product UI before the kernel proves value.

## Minimal promotion flow

```text
agent run
  → run events + diffs + logs + tests captured
  → evidence objects created
  → candidate claims/artifacts proposed
  → promotion gate checks type, scope, evidence, risk, eval/review
  → accepted item receives trust state and version
  → projection/export layer makes it available to future runs
  → later run logs whether it was activated
  → bad influence can be attributed and demoted
```

## Minimal trust-state model

```text
proposed     # emitted by agent/tool/provider/user but not accepted
accepted     # allowed as usable but low confidence or human-approved note
trusted      # eligible for future activation under explicit scope
stale        # previously accepted/trusted but invalidation signal exists
rejected     # reviewed and denied
merged       # superseded by another claim/artifact
quarantined  # suspected harmful; cannot activate
```

## Operational meaning of “substrate”

Do not use “substrate” as a metaphor. It is admissible only if it means:

> A scoped, versioned, promoted, future-activatable artifact that changes context projection, procedure, evaluation, permissions, or interpretation, and whose use is logged and reversible.

If an object does not change behavior or projection, it is metadata, not substrate.

## Minimal artifact stance

MVP should include:

- thin `ArtifactManifestEntry`;
- activation logging;
- one live `SkillArtifact`;
- one projection/export path;
- context projector in shadow or simple compiler mode.

MVP should not include live generalized:

- `LensArtifact`;
- `EvalArtifact`;
- `AnalyzerArtifact`;
- `TransformArtifact`;
- `ToolArtifact`;
- `PolicyArtifact`;
- `ModelAdapterArtifact`.

Those can be post-MVP only if benchmark evidence shows a concrete bottleneck.
