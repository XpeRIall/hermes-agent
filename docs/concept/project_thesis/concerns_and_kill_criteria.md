# Concerns and Kill Criteria

**Date:** 2026-05-18  
**Status:** Adversarial guardrail document for Hermes Fork  
**Purpose:** Capture the strongest concerns against the substrate-runtime thesis and define conditions under which the project should shrink, pivot, pause, or abandon parts of the architecture.

---

## 1. Founding Concern

The core concern is not merely “is this over-engineered?”

The deeper concern is:

> Am I overprojecting human meta-cognitive patterns—abstraction accumulation, compression, transfer, skepticism, recursive verification, contradiction sensitivity—into materialized runtime logic where they may become maladaptive bureaucracy?

This document treats that concern as valid.

The architecture must not assume that its substrate model is correct. It must make substrate models inspectable, testable, scoped, replaceable, and demotable.

---

## 2. Primary Risk: Abstraction Projection

### Concern

The project may be externalizing one human operator’s cognitive style into infrastructure:

- high contradiction sensitivity;
- distrust of shallow plausibility;
- recursive analysis;
- desire for evidence before persistence;
- abstraction compression;
- transfer of patterns across domains;
- concern about silent drift.

These patterns can be useful internally but harmful if materialized unfiltered.

### Failure mode

The runtime becomes a machine for enforcing a defensive cognitive style rather than a practical agent system.

### Mitigation

Keep the kernel minimal and boring. Treat speculative cognition-inspired mechanisms as replaceable artifacts, not as kernel law.

### Kill signal

If the system mostly exists to reduce epistemic discomfort rather than measurable task failures, shrink it.

---

## 3. Known Primitives Do Not Prove Composition

### Concern

Run ledgers, typed claims, evals, policy gates, signed artifacts, and retrieval systems are individually known patterns. Their combination does not prove that stochastic behavior will be contained or that future behavior will improve.

### Failure mode

The project mistakes engineering ingredients for an architectural theorem.

### Mitigation

State the guarantee narrowly:

> The runtime governs persistent effects. It does not make model reasoning deterministic.

### Kill signal

If project docs or implementation decisions rely on “this must work because all components are known,” stop and reframe as experiment.

---

## 4. Overhead and Bureaucracy

### Concern

The system may add more ceremony than value:

- manifests;
- trust states;
- proposals;
- eval gates;
- promotion records;
- activation plans;
- context projectors;
- rollback machinery.

### Failure mode

The user spends more time maintaining the substrate than benefiting from it.

### Mitigation

Measure saved rework, reduced repeated errors, and debug time against creation/verification/maintenance cost.

### Kill signal

If artifact creation, verification, and activation cost more than the rework/debug time they save over repeated tasks, demote the substrate layer to annotations or static domain packs.

---

## 5. Retrieval May Be Enough

### Concern

A strong retrieval/context system may solve most of the practical problem. Rich compressed context, session search, repo maps, skills, and evals may be enough.

### Failure mode

Substrate artifacts become a complicated substitute for good retrieval and prompt assembly.

### Mitigation

Always compare against a strong retrieval baseline.

### Kill signal

If normal retrieval plus traces plus typed claims matches substrate performance on repeated workloads, do not expand dynamic substrate composition.

---

## 6. Ledger and Claims May Be Enough

### Concern

The real missing layer may be only run ledger + evidence + typed claims + proposal-only learning. Dynamic substrate composition may be unnecessary.

### Failure mode

The project builds artifact composition when the value came from write governance only.

### Mitigation

Compare three modes:

1. baseline memory/retrieval;
2. ledger + typed claims;
3. ledger + typed claims + substrate artifacts.

### Kill signal

If mode 2 is equal to or better than mode 3 on quality, repeated-error reduction, and debug time, freeze substrate at schema level and focus on verified memory/skills.

---

## 7. Static Domain Pack May Beat Dynamic Activation

### Concern

A fixed software-engineering domain pack may be simpler and just as effective as dynamic substrate activation.

### Failure mode

Activation plans converge to the same bundle, adding no real adaptability.

### Mitigation

Track activation diversity and task-specific usefulness.

### Kill signal

If more than 80% of useful runs activate the same artifact bundle and dynamic activation does not improve outcomes over a static pack, replace dynamic activation with static domain packs plus manual configuration.

---

## 8. Artifact Metadata Without Operational Value

### Concern

Artifacts may become well-described objects that do not actually affect runtime behavior.

### Failure mode

The registry is mostly documentation, not a control surface.

### Mitigation

Every active artifact must have one of these effects:

- changes context projection;
- changes allowed procedure;
- changes observation/analysis;
- gates promotion;
- changes permission envelope;
- creates measurable evidence.

### Kill signal

If artifact manifests are not used in activation, prompt projection, evals, permissions, or promotion, remove or simplify the artifact layer.

---

## 9. Context Projector May Become Prompt Dressing

### Concern

`ContextProjectorArtifact` may just format context, not improve epistemic separation or behavior.

### Failure mode

Trusted claims, provisional hypotheses, provider synthesis, raw evidence, and skill guidance remain semantically blurred despite new labels.

### Mitigation

Run A/B tests: blended context versus category-fenced projection.

### Kill signal

If projectors do not reduce unsupported claims, stale-context use, or confusion between evidence and conclusion, replace them with simpler retrieval formatting.

---

## 10. Eval Overfitting and False Confidence

### Concern

Eval gates may create false confidence. Passing an eval does not prove broad generalization.

### Failure mode

Artifacts are promoted because they pass narrow tests but degrade future tasks.

### Mitigation

Use evals as conservative gates, not proof of truth. Track post-promotion regressions and require demotion paths.

### Kill signal

If promoted artifacts frequently regress outside their eval set, lower their trust state, narrow scope, or stop auto-promotion.

---

## 11. Provider Truth Leakage

### Concern

Honcho, Hindsight, Holographic, Mem0, Graphiti, or other providers may bypass the kernel and become de facto truth.

### Failure mode

Provider-generated synthesis enters prompts as authoritative memory without evidence, scope, validation, or contradiction handling.

### Mitigation

All provider outputs enter as raw evidence, recall suggestions, or hypotheses unless promoted through the kernel.

### Kill signal

If provider outputs can affect future behavior without claim/proposal/promotion records, disable that provider path.

---

## 12. Stale Project Memory

### Concern

Project/repo claims may survive code changes and become harmful folklore.

### Failure mode

The agent relies on old build commands, old architecture assumptions, old API constraints, or old test behavior after refactors.

### Mitigation

Attach claims to repo root, branch, commit, file hash, symbol, and invalidation rules.

### Kill signal

If stale claims are used repeatedly after file/commit changes that should invalidate them, stop promoting project claims until anchoring is fixed.

---

## 13. Policy Overconstraint

### Concern

A policy runtime may make the agent safe but useless.

### Failure mode

The agent cannot perform practical tasks because permission checks are too heavy or false-deny common workflows.

### Mitigation

Start in shadow mode. Enforce only high-risk actions first.

### Kill signal

If policy denials block normal workflows more often than they prevent real risk, keep policy in audit mode and narrow enforcement.

---

## 14. Promotion Bottleneck

### Concern

The promotion gate may create a queue of unresolved proposals and stall learning.

### Failure mode

The system generates many proposals but few are reviewed, evaluated, or used.

### Mitigation

Limit proposal generation, prioritize by repeated failure/value, and allow provisional low-risk scope.

### Kill signal

If the proposal queue grows without leading to promoted artifacts or improved future runs, reduce proposal sources and stop dreamer-style generation.

---

## 15. Local Dreamer Noise

### Concern

A Honcho-like local dreamer/extractor may generate plausible but low-value proposals.

### Failure mode

The project spends effort triaging noisy meta-cognitive suggestions.

### Mitigation

Dreamer must operate only on evidence and emit proposals with evidence IDs, expected use, and eval suggestions.

### Kill signal

If fewer than 20% of dreamer proposals survive review/eval over a meaningful sample, disable or narrow the dreamer.

---

## 16. Hermes Integration May Be Too Invasive

### Concern

The required changes may cut so deeply through Hermes that reuse no longer pays off.

### Failure mode

The fork becomes a fighting rewrite around Hermes’ assumptions.

### Mitigation

Track whether each Hermes seam is helpful or obstructive: run loop, prompt assembly, skill system, memory manager, provider interface, session DB.

### Kill signal

If core implementation spends more effort bypassing Hermes than reusing it, consider a clean runtime that imports only selected Hermes components.

---

## 17. Scope Intoxication

### Concern

Every part touches another part: memory, evidence, evals, policy, skills, context, providers, cognition, product value. The project can expand endlessly.

### Failure mode

The team produces more architecture than working behavior.

### Mitigation

Every research or design finding must remove, shrink, or reprioritize implementation.

### Kill signal

If a research cycle does not change the minimal implementation plan, stop that research loop and implement the falsification slice.

---

## 18. Non-Negotiable Guardrails

These must hold even in early prototypes:

1. Kernel rules are not self-modified by ordinary runs.
2. Providers do not define truth.
3. Background workers emit proposals, not trusted writes.
4. Every promoted claim has evidence and scope.
5. Every active artifact has a manifest and trust state.
6. Activation decisions are logged.
7. Elevated permissions require explicit approval.
8. Bad artifacts can be revoked or demoted.
9. Project claims can become stale.
10. The architecture is allowed to shrink if evidence does not support it.

---

## 19. Kill Criteria Table

| Kill / Shrink Criterion | Measurement | Threshold / Signal | Action |
|---|---|---|---|
| Substrate adds no quality | Dynamic substrate vs ledger+claims baseline | No meaningful quality/repeated-error/debug-time improvement | Defer substrate; keep ledger/claims |
| Dynamic activation is static in practice | Activation bundle diversity | Same bundle used in >80% of useful runs | Replace with static domain pack |
| Verification overhead dominates | Time/cost to create/eval/promote vs saved rework | Overhead exceeds saved time across repeated tasks | Reduce promotion requirements or demote artifacts |
| Artifacts are metadata-only | Runtime use of manifests | Manifests not used for projection/eval/permission/activation | Remove/simplify artifact layer |
| Projectors do not help | Blended vs category-fenced context A/B | No reduction in unsupported/stale/category-confused outputs | Simplify projection |
| Evals overfit | Post-promotion regression | Artifacts pass evals but fail adjacent tasks repeatedly | Narrow scope, add evals, or stop auto-promotion |
| Providers leak truth | Provider-derived future behavior | Provider output affects runs without promotion record | Disable provider truth path |
| Claims go stale | Invalidated code/file state | Stale claims repeatedly used after invalidating changes | Stop promoting project claims until anchoring fixed |
| Policy blocks usefulness | Denial logs and task completion | False denials common in normal workflows | Return policy to shadow mode |
| Proposal queue bloats | Proposal survival rate | Many proposals, few promotions, no measured benefit | Reduce generators/dreamer |
| Dreamer is noisy | Proposal survival through eval/review | <20% useful over meaningful sample | Disable or narrow dreamer |
| Hermes fork fights the shell | Implementation effort | More bypassing than reuse | Consider clean runtime |
| Architecture grows without evidence | Roadmap churn | New abstractions added before MVP metrics | Freeze scope |
| User cannot explain artifacts | Operator comprehension | Persistent substrate becomes inscrutable | Improve UI or shrink model |
| Rollback fails | Revocation tests | Bad promoted artifact cannot be cleanly disabled | Stop promotion until fixed |

---

## 20. Decision States

### Continue

Continue full minimal substrate path if:

- substrate artifacts improve repeated tasks;
- activation plans vary usefully;
- overhead is acceptable;
- rollback works;
- context projection improves grounding;
- evals reduce bad promotion.

### Narrow

Narrow to verified memory/skills if:

- ledger + claims solve most repeated failures;
- dynamic activation adds little;
- artifact creation is too expensive;
- static domain pack performs as well.

### Pause

Pause substrate expansion if:

- evals are too weak;
- stale claims are common;
- policy blocks workflows;
- provider truth leakage appears;
- proposal queues grow without promotions.

### Pivot

Pivot away from Hermes fork if:

- integration becomes more expensive than reuse;
- critical seams cannot be inserted cleanly;
- Hermes assumptions fight the trusted kernel.

### Abandon stronger thesis for now

Abandon the full verified substrate composition thesis if:

- strong retrieval + traces + typed claims + verified skills match dynamic substrate across repeated high-context tasks;
- artifacts do not create measurable behavioral improvement;
- the useful product is clearly a debugging/governance layer rather than a learning-substrate runtime.

---

## 21. What Would Prove the Thesis Worth Continuing

A good early result would show:

1. A repo bugfix or onboarding task fails or repeats mistakes under baseline.
2. Ledger + typed claims help but still miss a reusable operating frame.
3. A lens/projector/skill/eval artifact bundle improves the next runs.
4. The improvement is traceable to activated substrate.
5. The artifact has evidence, eval result, and scope.
6. The artifact can be disabled and the behavior difference is observable.
7. The overhead is less than the saved debugging/rework cost.

That would not prove the universal architecture. It would prove the minimal thesis has teeth.

---

## 22. Final Adversarial Position

The project is rational only as a falsification program.

The correct posture is:

> Build the smallest substrate-aware runtime that can prove, shrink, or kill the substrate thesis.

If the system cannot demonstrate value over strong retrieval, traces, typed claims, and verified skills, it should not become a cathedral.
