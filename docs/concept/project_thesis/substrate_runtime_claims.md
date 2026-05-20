# Substrate Runtime Claims

**Date:** 2026-05-18  
**Status:** Claim stack for comparative falsification / Deep Research source pack  
**Purpose:** Decompose the Hermes Fork substrate thesis into testable claims, explicit confidence levels, expected evidence, and implementation implications.

---

## 1. Why This Document Exists

The architecture can sound plausible even when its strongest claims are not proven. This document prevents that by splitting the project into claims.

The key distinction is:

> Known primitives do not prove the composition.

Run ledgers, evidence stores, typed claims, evals, policy gates, skills, and context projectors are each individually plausible. The unproven question is whether their combination creates a useful governed learning loop rather than ceremony.

This document treats the substrate runtime as a hypothesis under evaluation.

---

## 2. Guarantee Boundary

### What the runtime can realistically guarantee

The runtime can enforce procedural invariants:

- no persistent update without a recorded proposal;
- no promoted artifact without a manifest;
- no artifact activation without trust/permission checks;
- no trusted claim without evidence binding;
- no provider output promoted directly as truth;
- no policy-elevating artifact without approval;
- all activation decisions are logged;
- rollback or demotion paths exist for promoted artifacts;
- future prompt projection can distinguish trusted claims, provisional claims, raw evidence, provider synthesis, and skill guidance.

### What the runtime cannot guarantee

The runtime cannot guarantee:

- model reasoning correctness;
- that an eval passing implies generalization;
- that a lens improves every future task;
- that a promoted artifact will not become stale;
- that stochastic behavior becomes deterministic;
- that all useful abstractions are discoverable;
- that the architecture is worth its overhead in every domain.

The runtime constrains persistent behavioral influence. It does not solve semantic truth in general.

---

## 3. Claim Confidence Scale

| Confidence | Meaning |
|---|---|
| High | Supported by source inspection, recurring industry patterns, or direct engineering logic. |
| Medium-high | Strongly plausible, but workload-dependent. |
| Medium | Plausible and testable, but not established. |
| Medium-low | Possible, but easy to overstate. |
| Unknown | Cannot be responsibly claimed without benchmark evidence. |

---

## 4. Claim Stack

### C0 — The problem exists

**Claim:** Long-lived agents accumulate persistent state and procedures in ways that are often weakly typed, weakly evidenced, weakly reversible, and weakly attributable.

**Confidence:** High.

**Rationale:** Hermes research found flat built-in memory, transcript search plus summarization, mutable skills, provider-mediated memory, and background self-improvement writes. These are useful, but they do not amount to a typed, evidence-backed, eval-gated learning substrate.

**How to test:** Inspect persistent mutation paths. Ask whether each future behavior-affecting update has evidence, scope, trust state, acceptance record, and rollback path.

**Implementation implication:** A governance layer is justified at least for persistent writes.

---

### C1 — Hermes has a strong shell and weak epistemic core

**Claim:** Hermes is worth forking because its operator shell is strong enough to preserve, while its learning semantics are weak enough to replace.

**Confidence:** High.

**Rationale:** Reports converge that Hermes has useful CLI/gateway/tool/session/skill/prompt infrastructure, but persistence is still mostly memory files, transcript summaries, skills, and provider-side conclusions/facts.

**How to test:** Map Hermes’ shell capabilities against its durable learning semantics.

**Implementation implication:** Fork Hermes rather than use only a plugin or start clean-room immediately.

---

### C2 — A trusted kernel is necessary

**Claim:** Persistent learning should be mediated by a trusted kernel that is not self-modified by ordinary runs.

**Confidence:** High.

**Rationale:** If the system can modify the rules that govern its own promotion, policy, evidence, or rollback without a stable boundary, trust collapses.

**How to test:** Attempt to describe how a learned artifact becomes trusted. If the same learned path can alter its own acceptance rules, the design fails.

**Implementation implication:** Kernel invariants must be boring and fixed: ledger, evidence, claims, policy, artifact validation, promotion, rollback.

---

### C3 — Proposal-only learning is safer than direct mutation

**Claim:** Background review/dreamer/extractor workers should emit proposals, not trusted writes.

**Confidence:** High.

**Rationale:** Direct background mutation can create stale memory, bad skills, or provider contamination without clear acceptance records.

**How to test:** Check whether any autonomous worker can directly write canonical claims, skills, policies, or artifacts.

**Implementation implication:** Convert background self-improvement into proposal generation plus promotion gate.

---

### C4 — Run ledger + evidence + typed claims can constrain persistent state

**Claim:** A run ledger, evidence store, and typed claim store can make persistent learned state auditable, scoped, and reversible.

**Confidence:** High for auditability; medium for capability improvement.

**Rationale:** These components do not make the agent smarter by themselves, but they can establish provenance, invalidation, rollback, and debugging.

**How to test:** Given a future behavior, reconstruct which claims/artifacts influenced it and what evidence justified them.

**Implementation implication:** Build these early even if substrate composition remains shadow-mode.

---

### C5 — Context projection is more than retrieval

**Claim:** A `ContextProjectorArtifact` is useful because it separates epistemic categories at prompt time instead of dumping mixed memory/provider outputs into context.

**Confidence:** Medium-high.

**Rationale:** Retrieval answers “what should the model see?” Projection answers “how should different classes of state be represented, fenced, and trusted?”

**How to test:** Compare outputs when the model receives blended context versus category-fenced trusted/provisional/evidence/provider/skill blocks.

**Implementation implication:** Context projection should be an early artifact type, not an afterthought.

---

### C6 — Provider outputs should be advisory, not canonical

**Claim:** Honcho, Hindsight, Holographic, Mem0, Graphiti, and similar systems may contribute useful recall or hypotheses, but should not define truth unless mediated by the kernel.

**Confidence:** High.

**Rationale:** Provider outputs can be model-mediated, graph-mediated, or heuristic. They may be useful evidence, but they are not automatically verified claims.

**How to test:** Attempt to trace a provider-derived future belief to evidence, scope, validation, and acceptance status.

**Implementation implication:** Providers become adapters and evidence/hypothesis sources, not sovereignty layers.

---

### C7 — Artifact constitution must exist early

**Claim:** The runtime needs `CapabilityArtifact`, `ArtifactManifest`, trust states, registry, activation plan, and activation logging early, even if many artifact kinds remain deferred.

**Confidence:** Medium-high.

**Rationale:** Without the artifact seam, the project naturally collapses into verified memory plus verified skills, losing the substrate-composition thesis.

**How to test:** Ask whether a run can explicitly state which substrate artifacts were considered, activated, denied, or shadowed.

**Implementation implication:** Add artifact base types and activation logging in the MVP.

---

### C8 — Minimal artifact set can prove the seam

**Claim:** One `SkillArtifact`, one `LensArtifact`, one `EvalArtifact`, and one `ContextProjectorArtifact` are enough to test whether substrate composition has operational shape.

**Confidence:** Medium.

**Rationale:** This set covers procedure, interpretation, verification, and prompt projection without building the full artifact universe.

**How to test:** Run repeated coding/repo tasks with and without these artifacts and compare outcomes.

**Implementation implication:** Do not start with ToolArtifact, PolicyArtifact, ModelAdapterArtifact, or a broad analyzer stack.

---

### C9 — Dynamic substrate activation may improve repeated high-context tasks

**Claim:** Task-specific activation of substrate artifacts can improve repeated high-context work compared with static prompts, retrieval, and generic memory.

**Confidence:** Medium-low until tested.

**Rationale:** The idea is plausible, especially for software engineering, but not proven. It may collapse into a static domain pack.

**How to test:** Compare dynamic activation against a fixed software-engineering domain pack across repo onboarding, bugfix, migration, and report tasks.

**Implementation implication:** Build activation in shadow mode first; only enforce if it changes behavior usefully.

---

### C10 — Eval-gated promotion can reduce repeated errors

**Claim:** Promoting claims/skills/artifacts only after evidence and evals can reduce repeated mistakes and bad persistence.

**Confidence:** Medium.

**Rationale:** Evals help, but evals can overfit, be brittle, or fail to capture future generalization.

**How to test:** Measure repeated-error rate after corrections under normal memory versus proposal/eval-gated promotion.

**Implementation implication:** Use evals as gates, but track regression and rollback outcomes.

---

### C11 — Software engineering is the right proving domain

**Claim:** Coding/repo work is a strong first domain because state can be anchored to files, commits, tests, symbols, diffs, and reproducible commands.

**Confidence:** High.

**Rationale:** The domain provides concrete evidence and evals. This reduces the risk of vague cognition metaphors.

**How to test:** Build golden tasks around repo onboarding, bugfixing, migration, and architecture analysis.

**Implementation implication:** Start with a software-engineering domain pack v0.

---

### C12 — The broad general-purpose substrate runtime is not yet proven

**Claim:** A general-purpose verified substrate composition runtime may become valuable, but broad generality is not established by the Hermes research alone.

**Confidence:** Unknown.

**Rationale:** The reports justify a problem and a plausible architecture, not a universal category.

**How to test:** After software-engineering success, repeat in a different task family and measure transfer.

**Implementation implication:** Avoid universal claims until multiple domain packs succeed.

---

## 5. Claim Matrix

| ID | Claim | Confidence | Evidence Needed | Success Signal | Failure Signal | Build Implication |
|---|---|---:|---|---|---|---|
| C0 | Persistent abstraction drift is real | High | Mutation path audit | Writes lack type/evidence/scope today | Existing systems already fully govern writes | Build governance layer |
| C1 | Hermes shell is worth preserving | High | Repo/interface audit | Shell features save implementation effort | Seams are too invasive | Fork Hermes |
| C2 | Trusted kernel is necessary | High | Threat model | Stable invariants protect promotion | Learned rules alter promotion logic | Keep kernel non-learnable |
| C3 | Proposal-only learning is safer | High | Background mutation audit | Direct writes converted to proposals | Autonomous writes continue | Add proposal store/gate |
| C4 | Ledger/evidence/claims improve auditability | High | Replay/debug tasks | Can explain future behavior | Ledger cannot reconstruct decisions | Build early |
| C5 | Context projection adds value | Medium-high | A/B prompt tests | Better grounding/category separation | Same or worse outputs | Keep projector artifact |
| C6 | Providers are advisory | High | Provider output audit | Provider outputs become evidence/hypotheses | Provider output bypasses claims | Adapter-only strategy |
| C7 | Artifact seam must exist early | Medium-high | Architecture pressure test | Activation logged before model loop | System becomes memory+skills only | Add artifact constitution MVP |
| C8 | Minimal artifact set is enough | Medium | MVP tasks | Four artifacts shape runs usefully | Artifacts are metadata-only | Shrink or redesign |
| C9 | Dynamic activation improves tasks | Medium-low | Golden tasks | Dynamic beats static pack | Static pack equal/better | Use fixed domain pack |
| C10 | Eval-gated promotion reduces repeated errors | Medium | Repeated-correction tests | Fewer repeats/regressions | Evals brittle/overhead high | Keep evals conservative |
| C11 | Coding is right first domain | High | Golden coding set | Anchors/evals work well | Coding too special to generalize | Still valid MVP |
| C12 | General runtime category emerges | Unknown | Multi-domain evidence | Transfer across domains | Only coding works | Limit claims |

---

## 6. Minimal Experiment

### Workload

Use repeated high-context software-engineering tasks:

1. repo onboarding;
2. failing-test bugfix;
3. migration plan;
4. architecture report;
5. repeated correction followed by future synthesis.

### Modes

Compare at least five modes:

1. Baseline agent with normal prompt/context/retrieval.
2. Hermes-style memory and session search.
3. Ledger + typed claims, no substrate artifacts.
4. Static software-engineering domain pack.
5. Dynamic substrate activation with skill/lens/eval/projector artifacts.

### Metrics

- final task quality;
- repeated-error reduction;
- claim grounding;
- stale-memory rate;
- debug time;
- rollback success;
- artifact reuse rate;
- activation diversity;
- cost and latency;
- user correction frequency;
- regression after promotion.

### Expected conclusion types

The experiment is allowed to conclude:

- dynamic substrate is useful;
- static domain packs are enough;
- ledger/claims are enough;
- only verified skills are useful;
- the overhead is not justified.

---

## 7. Strong Project Hypothesis

The strongest version worth testing is:

> In repeated high-context software-engineering work, a Hermes-derived agent with a trusted kernel and a minimal substrate artifact seam will reduce repeated errors and improve debuggability over normal memory/retrieval by governing the promotion and activation of persistent abstractions.

This is narrower than the grand thesis and strong enough to test.

---

## 8. Weaker Fallback Hypotheses

If the strong hypothesis fails, useful fallback products may remain.

### Fallback A — Verified Memory Runtime

Run ledger + evidence + typed claims + context projection, without dynamic substrate composition.

### Fallback B — Verified Skills Runtime

Existing Hermes skills wrapped in manifests, tests, permissions, and promotion gates.

### Fallback C — Static Domain Pack

A fixed software-engineering pack with repo/test/git/projector components, without dynamic activation.

### Fallback D — Agent Debugging Layer

Run ledger, evidence, and replay tooling for existing agents.

These are not failures if they solve real problems. They are narrower products.

---

## 9. Claims Not Yet Allowed

The project should not claim the following without evidence:

- “This controls stochasticity completely.”
- “This proves future behavior.”
- “This is the universal architecture for agents.”
- “All high-context work needs substrate composition.”
- “Providers have ignored an obvious solution.”
- “Evals prove generalization.”
- “Memory retrieval is insufficient in all cases.”
- “Dynamic activation will beat a well-designed static domain pack.”

---

## 10. Current Rational Position

The rational position is:

> The problem hypothesis is strong. The kernel is justified. The artifact/substrate seam is plausible and should be tested early. The broad general-purpose runtime is unproven.

Build only what is needed to test that statement.
