# Hermes Fork Thesis

**Date:** 2026-05-18  
**Status:** Working thesis for comparative falsification / Deep Research source pack  
**Intended use:** Provide a concise but explicit statement of what Hermes Fork is trying to prove, what it is not trying to prove, and what must exist early for the project not to collapse into “better memory plus safer skills.”
**Final-pack status:** Retained as a claim stack for falsification. The current MVP should test only the minimal governed-promotion layer: run ledger, evidence, typed claims, proposal queue, promotion gate, demotion, one `SkillArtifact`, and a shadow/simple projection seam. Treat broader substrate-runtime claims as post-MVP hypotheses.
---

## 1. Executive Thesis

Hermes Fork is not primarily a “better memory” project.

The thesis is that a long-lived agent needs a trusted runtime kernel plus a governed, composable substrate layer. The agent may propose durable changes to what it remembers, how it interprets tasks, what procedural skills it uses, what context it projects, and what evals gate future promotion. The runtime, not the model, decides whether those proposals become persistent behavior.

The strongest formulation is:

> A general-purpose learning agent should not silently mutate memory, prompts, or skills. It should propose reusable, scoped, evidence-backed substrate artifacts. A trusted kernel should validate, activate, version, evaluate, promote, demote, and roll back those artifacts.

This is a stronger claim than “use traces, retrieval, memory, and evals.” It is a claim about the write/promotion plane of long-lived agents.

---

## 2. Problem Statement

Existing agent systems can already do many useful things:

- maintain memory;
- retrieve prior sessions;
- use tools and skills;
- run with approval gates;
- summarize context;
- integrate external memory providers;
- perform background review;
- run evals or benchmarks in some workflows.

The unresolved problem is different:

> Long-lived agents accumulate reusable abstractions, but today those persistent abstractions are often weakly typed, weakly evidenced, weakly evaluated, weakly scoped, weakly reversible, and weakly attributable.

In the Hermes case, the research reports converge on the same diagnosis:

- Hermes has a strong operator shell: CLI/gateway surface, prompt assembly, tool registry, session history/search, skill UX, plugin/config plumbing, and practical safety mechanisms.
- Hermes has a weak epistemic core: built-in memory is flat and prompt-injected; session search is transcript retrieval plus summarization; skills are mutable `SKILL.md` procedures; external providers can inject model-mediated recall; background review can mutate memory/skills directly.
- The current learning path is mostly model-mediated artifact maintenance, not replayable, evidence-backed state transition.

The fork is justified only if it replaces Hermes’ learning semantics while preserving much of Hermes’ shell.

---

## 3. Core Design Claim

The fork should be understood as:

> Hermes shell + verified learning kernel + substrate composition seam.

The shell provides the operator surface: CLI, tools, session search, skill ergonomics, context loading, gateways, and existing safety affordances.

The kernel provides non-negotiable invariants: run ledger, evidence, typed claims, policy, permissions, artifact verification, promotion, revocation, and rollback.

The substrate seam provides task-specific reasoning equipment: skills, lenses, context projectors, evals, schemas, analyzers, transforms, and eventually adapters. These are not trusted merely because an agent wrote them. They are versioned artifacts with manifests, trust states, permissions, evidence, eval history, and activation records.

---

## 4. What Hermes Fork Is

Hermes Fork is a runtime that can answer, for every durable thing it believes or uses:

1. What is it?
2. What type of thing is it?
3. Where did it come from?
4. What evidence supports it?
5. What task/repo/user/project scope does it apply to?
6. What eval or review justified promotion?
7. What permissions does it require?
8. When was it last verified?
9. What invalidates it?
10. How can it be rolled back or demoted?
11. Did using it improve or harm later runs?

The unit of governance is not “context” in general. The unit is:

> Persistent abstraction with behavioral influence.

---

## 5. What Hermes Fork Is Not

Hermes Fork is not:

- a universal cognitive operating system on day one;
- a proof that stochastic model behavior becomes deterministic;
- a replacement for good retrieval;
- a provider-memory wrapper;
- a graph-memory-first system;
- a live self-training / QLoRA system;
- a framework where everything is learnable immediately;
- a system that trusts external memory providers as truth;
- a system that auto-promotes tools, policies, or model adapters without explicit gates;
- a project whose success is established by architecture diagrams.

The system does not prove semantic correctness. It enforces controlled persistent effects.

A realistic guarantee is:

> No persistent artifact that can influence future behavior is promoted without a recorded proposal, evidence, scope, trust state, and acceptance path.

A non-realistic guarantee is:

> The agent will always reason correctly.

---

## 6. Three-Layer Architecture

### 6.1 Trusted Kernel

The kernel is not self-modified by ordinary runs. It owns:

- run ledger;
- evidence store;
- typed claim store;
- proposal store;
- artifact registry;
- policy runtime;
- permission broker;
- eval registry;
- promotion gate;
- revocation and rollback manager;
- context projection boundary;
- audit and replay semantics.

The kernel’s job is to constrain persistent mutation, not to make the model deterministic.

### 6.2 Artifact Constitution

The artifact constitution defines what a capability artifact is and how it is handled.

Every artifact needs:

- identity;
- kind;
- version;
- scope;
- manifest;
- permissions;
- dependencies;
- incompatibilities;
- side-effect profile;
- required evals;
- trust state;
- provenance;
- activation history;
- revocation path.

This constitution must exist early. Otherwise the system risks becoming only “typed memory plus safer skills.”

### 6.3 Dynamic Substrate

The dynamic substrate is the run-specific bundle of activated artifacts.

For a coding task, this may include:

- repo lens;
- git lens;
- build/test lens;
- bugfix skill;
- test eval;
- epistemic context projector;
- project claims;
- failure-pattern memory.

For a research task, it may include:

- evidence-first projector;
- source reliability rubric;
- citation eval;
- document-synthesis skill.

The important claim is not that every run needs many artifacts. The claim is that task-specific substrate should be explicit, logged, validated, and reversible.

---

## 7. Minimal Artifact Set

The first implementation should not include every possible artifact family. It should include the smallest set that proves substrate composition is real.

### Required early artifact kinds

1. **SkillArtifact**  
   A versioned, permissioned, eval-gated procedural capability.

2. **LensArtifact**  
   A scoped way to observe or interpret a task domain, such as a repo lens or test-failure lens.

3. **EvalArtifact**  
   A reusable check that can gate claims, skills, artifacts, or promotions.

4. **ContextProjectorArtifact**  
   A contract for compiling trusted claims, provisional hypotheses, raw evidence, provider synthesis, active artifacts, and task-local state into prompt-ready overlays without collapsing epistemic categories.

### Kernel-owned objects

Claims, evidence, run events, proposals, trust decisions, and policy decisions should be kernel-owned objects, not just artifacts written by the agent.

### Deferred artifact kinds

The following should exist only as reserved schema kinds or future extension points in the MVP:

- ToolArtifact;
- PolicyArtifact;
- MemoryAdapterArtifact;
- AnalyzerArtifact;
- TransformArtifact;
- ModelAdapterArtifact.

These may become important later, but they are too risky or speculative for early active learning.

---

## 8. Minimal Runtime Flow

The intended runtime flow is:

```text
user task
→ kernel creates run ledger entry
→ task classifier/planner proposes SubstrateActivationPlan
→ activator checks manifests, trust states, dependencies, evals, permissions
→ activation result is logged
→ context projector compiles category-fenced context overlay
→ model/tool loop executes inside bounded substrate
→ tool outputs, file snapshots, user corrections, and evals become evidence
→ extractor/dreamer proposes claims or artifact updates
→ promotion gate accepts, rejects, leaves provisional, or requests review
→ promoted state affects future runs only through the kernel
```

This is the core differentiator. Without it, Hermes Fork is merely safer Hermes.

---

## 9. Relationship to Hermes

Hermes should be preserved where it is already strong:

- CLI and gateway operator surface;
- tool registry;
- session database and FTS search;
- context-file loading;
- prompt-caching strategy;
- progressive skill disclosure;
- plugin/config plumbing;
- existing safety checks and approvals.

Hermes should be replaced or wrapped where its learning semantics are weak:

- flat built-in memory as truth;
- direct background learning writes;
- mutable skills as trusted capabilities;
- provider outputs treated too authoritatively;
- session summaries treated as knowledge rather than evidence;
- absence of run-level causal ledger;
- absence of eval-gated promotion.

This is a fork, not a plugin pack, because the required changes cut through runtime, prompt projection, persistence, skill activation, provider integration, and review loops.

---

## 10. Provider Strategy

External memory providers are useful, but they must not define truth.

### Honcho

Honcho is useful as concept evidence for persona synthesis and background cognitive modelling. It should be treated as an optional user/persona hypothesis layer, not as canonical truth.

### Hindsight / Graph Memory

Graph/project memory may be useful later for entity-heavy recall and long-lived domain continuity. It should enter as an adapter that emits evidence or hypotheses, not as the kernel.

### Holographic

Holographic is useful seed code for local structured memory: SQLite, FTS5, entities, trust, inspectability. It is not sufficient as a verified claim store because it lacks full evidence, scope, validation, lifecycle, promotion, and rollback semantics.

### Governing rule

> Providers may emit evidence, summaries, hypotheses, or recall suggestions. They do not silently promote truth.

---

## 11. MVP Scope

The corrected MVP is not the whole cathedral. It is the smallest implementation that proves the substrate thesis has runtime shape.

Required MVP components:

1. append-only run ledger skeleton;
2. evidence object model;
3. typed claim schema;
4. proposal store;
5. `CapabilityArtifact` base type;
6. `ArtifactManifest`;
7. artifact trust states;
8. minimal artifact registry;
9. `SubstrateActivationPlan`;
10. shadow-mode `SubstrateActivator`;
11. activation logging;
12. one `SkillArtifact`;
13. one `LensArtifact`;
14. one `EvalArtifact`;
15. one `ContextProjectorArtifact`;
16. software-engineering domain pack v0;
17. legacy memory bridge into claim/proposal flow;
18. policy shadow mode around file writes, shell, network, and provider writes.

The first artifact set can be simple:

- repo lens;
- bugfix/onboarding skill;
- test/build eval;
- epistemic context projector.

---

## 12. First Proving Domain

The first domain should be software engineering because the most concrete workload is high-context repo work.

Initial task families:

- repo onboarding;
- bugfix with failing test evidence;
- migration planning;
- architecture report over a repo;
- repeated document/repo synthesis;
- Spark/dataflow diagnosis if relevant to the user’s actual work.

Every project claim should be anchored to:

- repo root;
- branch/worktree;
- commit SHA;
- file path;
- line range or symbol where possible;
- validation command;
- file hash invalidation rule.

The goal is to prevent project memory from becoming stale folklore.

---

## 13. Strong Hypothesis

The strongest testable hypothesis is:

> In repeated high-context software-engineering tasks, governed promotion of scoped substrate artifacts reduces repeated mistakes, improves debuggability, and preserves operating-frame continuity better than normal retrieval, traces, and memory alone, without adding prohibitive overhead.

This is not yet proven. The architecture is justified only as a test vehicle for this hypothesis.

---

## 14. Comparison Baselines

Hermes Fork must be compared against:

1. normal agent with prompt/context/retrieval;
2. Hermes-style memory and session search;
3. ledger + typed claims without dynamic substrate;
4. static software domain pack;
5. dynamic substrate activation with artifacts.

If dynamic substrate does not outperform the simpler variants, the fork should shrink.

---

## 15. Success Conditions

Early success means:

- the system can explain why a future behavior changed;
- persistent state has evidence and scope;
- bad learned artifacts can be demoted or rolled back;
- project claims become stale when code changes invalidate them;
- context projection separates trusted claims, provisional hypotheses, raw evidence, and provider synthesis;
- at least one promoted artifact improves a repeated task family;
- activation plans differ meaningfully across task classes;
- overhead does not dominate saved rework/debug time.

---

## 16. Thesis Boundary

The thesis is valid only if it remains humble:

> Build the smallest runtime that can test whether governed substrate promotion is useful.

Do not assume the general architecture is already proven. The project should be allowed to conclude that the useful product is only:

- run ledger;
- evidence;
- typed claims;
- verified skills;
- static domain packs.

The stronger substrate-composition claim must earn its place.
