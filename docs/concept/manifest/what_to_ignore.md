# What to Ignore / Defer

**Date:** 2026-05-18  
**Status:** Source-pack control file for comparative falsification / Deep Research  
**Purpose:** Prevent the next research run from wasting attention on low-signal material, speculative future work, feature-list comparisons, or implementation details that do not answer the central question.

---

## 1. Scope of This File

This file does **not** mean “hide negative evidence.”

It means:

> Do not spend research or implementation attention on material that does not help decide whether Hermes Fork’s verified substrate-composition thesis is additive, redundant, premature, or wrong.

The next research pass should be adversarial. It is allowed to conclude that the project is overbuilt. But it should not get distracted by every feature, file, provider, or future artifact type.

Use this file to keep the study focused on the core invariant question:

> Do existing serious agent systems already solve governed promotion of reusable abstractions, or is there a real missing write-governance layer?

---

## 2. Do Not Treat This as a Feature Comparison

Ignore shallow feature comparison unless the feature maps to an invariant.

Do not spend much time on questions like:

- Which project has the nicest CLI?
- Which project has more tools?
- Which project has more integrations?
- Which project has more model providers?
- Which project has more polished docs?
- Which project has better marketing language?
- Which project looks more mature as a product?

Only analyze a feature if it affects one of these invariants:

- execution state;
- persistence/checkpointing;
- traceability;
- evidence binding;
- memory model;
- context projection/retrieval;
- tool/action boundary;
- sandboxing;
- permission/human approval;
- eval or benchmark gating;
- rollback/recovery;
- skill/workflow packaging;
- artifact promotion;
- long-term learning;
- write governance;
- substrate activation.

A feature is relevant only if it changes how the system learns, persists, verifies, activates, or rolls back behavior.

---

## 3. Do Not Re-litigate the Basic Hermes Fork Decision Unless New Evidence Appears

The prior reports already converge on a baseline diagnosis:

- Hermes has a useful operator shell.
- Hermes has weak learning semantics relative to the target thesis.
- The fork is justified only if the learning core changes, not if it is just a plugin pack.
- Hermes’ shell should be preserved where possible.

Do not spend the next research run re-proving basic Hermes strengths unless comparing them to another system’s invariant.

Treat the following as background assumptions to test only if contradicted by new evidence:

- Hermes’ CLI/gateway/tool/session/skill shell is worth preserving.
- Hermes’ current memory/skill/provider learning path is not a verified substrate runtime.
- Provider outputs should not become canonical truth without kernel validation.
- The fork should preserve shell affordances while changing learning semantics.

Relevant, but do not over-focus on:

- ordinary CLI ergonomics;
- gateway UX;
- installation details;
- prompt-cache mechanics except where they affect context projection;
- existing skill UX except where it becomes artifact/permission/eval machinery;
- existing session search except where it becomes evidence or typed state.

---

## 4. Do Not Assume Known Primitives Prove the Composition

Ignore arguments of the form:

> “Run ledgers, typed claims, evals, skills, and policies are known patterns, therefore the substrate runtime will work.”

That is not valid.

The research question is not whether individual primitives are plausible. The question is whether their **composition** produces measurable value beyond overhead.

Do not accept these as proof:

- traces exist;
- memory exists;
- evals exist;
- skills exist;
- checkpoints exist;
- context retrieval exists;
- human approvals exist;
- sandboxing exists;
- a repo has “agents” in the name;
- a provider says it supports “learning.”

For every claimed equivalent, ask:

1. What persistent thing is being learned or promoted?
2. Is it typed?
3. Is scope explicit?
4. Is evidence attached?
5. Is there an eval or review gate?
6. Is provenance stored?
7. Can it be demoted or rolled back?
8. Does it automatically influence future runs?
9. Can future regressions be attributed to it?

If the answer is no, it is not equivalent to governed substrate promotion.

---

## 5. Do Not Treat Retrieval as Solving Write Governance

Ignore arguments that collapse the thesis into “just retrieve the right context.”

Good retrieval can solve:

> What should the model read right now?

It does not automatically solve:

> What should the system be allowed to learn, promote, reuse, and later roll back?

The research should not over-focus on retrieval quality unless it addresses persistent behavioral influence.

Specifically, do not count the following as full equivalents to substrate governance:

- vector search;
- semantic memory;
- repo maps;
- compressed summaries;
- context windows;
- tool search;
- dynamic tool loading;
- long-context models;
- transcript search;
- session summarization;
- just-in-time documentation loading.

These may be adjacent or necessary. They are not sufficient unless they include governed write/promotion semantics.

---

## 6. Do Not Treat Provider Memory as Canonical Truth

Do not let the research run drift into choosing a memory provider as the answer.

Honcho, Hindsight, Holographic, Mem0, Graphiti, Letta, LlamaIndex, or similar systems may be useful as:

- evidence sources;
- recall adapters;
- user/persona synthesis layers;
- project/entity memory layers;
- graph or temporal context layers;
- hypothesis generators.

They should not be treated as canonical truth unless they demonstrate all of the following:

- typed claims;
- evidence binding;
- validation state;
- scope;
- contradiction handling;
- promotion records;
- rollback/demotion;
- replayable influence on future runs;
- permission-aware activation.

In the next research pass, provider analysis should be subordinate to the core question:

> Does this provider solve governed promotion of reusable abstractions, or does it only store/retrieve/summarize memory?

Do not spend excessive time on provider deployment, pricing, or setup unless it directly affects the feasibility of the minimal architecture.

---

## 7. Do Not Build or Deeply Analyze the Full Artifact Universe Yet

Ignore or defer full implementation planning for broad artifact families that are not required to test the thesis.

The MVP should structurally reserve the artifact seam, but it should not deeply implement every artifact type.

### Keep as schema-only / future-reserved

- `ToolArtifact`
- `PolicyArtifact`
- `MemoryAdapterArtifact`
- `ModelAdapterArtifact`
- `AnalyzerArtifact`
- `TransformArtifact`
- broad domain packs beyond software engineering
- automatic tool creation
- live policy learning
- live model fine-tuning or QLoRA promotion
- multi-agent substrate negotiation
- autonomous provider selection as truth arbitration

### Reason

These may be valid later, but they are high-risk distractions for the next falsification pass. The early question is whether **any** minimal substrate artifact improves repeated high-context work beyond ledger/claims/retrieval alone.

The minimal live artifact set should stay closer to:

- one live `SkillArtifact`;
- one thin `ArtifactManifestEntry`;
- one projection/export path;
- one `ContextProjectorArtifact` only in shadow/compiler mode;
- promotion-gate eval predicates, not a generalized live `EvalArtifact`;
- no live `LensArtifact` unless benchmark evidence shows it is necessary.

---

## 8. Do Not Let “Dynamic Substrate Composition” Become Hand-Wavy

Ignore any version of substrate composition that is only naming and not operational.

A `Lens`, `Projector`, `Eval`, or `Skill` is not real unless it has:

- an explicit contract;
- declared inputs and outputs;
- a manifest;
- scope;
- permissions or side-effect profile;
- activation conditions;
- evidence/provenance when promoted;
- eval or review status;
- rollback/demotion path;
- measurable effect on future runs.

Do not count vague concepts as implemented substrate:

- “a way of looking at the repo”;
- “a useful reasoning pattern”;
- “a memory abstraction”;
- “a cognitive substrate”;
- “context engineering”;
- “agent learns patterns.”

Translate each concept into a runtime contract or ignore it for MVP purposes.

---

## 9. Do Not Confuse Procedural Control with Semantic Correctness

Ignore claims that imply the runtime can prove the model will reason correctly.

The architecture can enforce procedural constraints around persistent effects. It cannot generally prove semantic truth or future model behavior.

Do not make or accept these claims:

- “This contains stochasticity completely.”
- “This proves exact behavior.”
- “Eval passing proves generalization.”
- “A verified lens always improves reasoning.”
- “The agent becomes reliable because the ledger exists.”
- “A claim is true because it has provenance.”

The valid guarantee is narrower:

> No persistent abstraction should influence future behavior unless it passed a recorded, inspectable, reversible promotion path.

Anything stronger should be treated as hypothesis, not fact.

---

## 10. Do Not Overfit to Human Cognition Metaphors

Ignore explanations that rely primarily on human-cognition analogy without translating into implementable contracts.

The founding intuition may come from human meta-cognition:

- abstraction accumulation;
- compression;
- transfer;
- contradiction sensitivity;
- recursive verification;
- frame selection;
- skepticism toward shallow plausibility.

But the runtime must not encode a personal cognitive style as unquestioned system law.

A cognition-inspired concept is admissible only if it becomes a bounded artifact, policy, eval, or claim schema.

Examples:

- “Lens” is acceptable only if it has input selectors, transformation rules, output schema, scope, failure modes, and evals.
- “Context projector” is acceptable only if it declares epistemic categories and projection rules.
- “Dreamer” is acceptable only if it emits proposals, not trusted writes.
- “Abstraction promotion” is acceptable only if it has evidence, eval/review, versioning, and rollback.

Do not let the next research run validate the architecture using metaphor alone.

---

## 11. Do Not Spend Time on Grand Long-Term Claims Before the Minimal Hypothesis

Ignore broad claims like:

- “This will become a new agent OS.”
- “This is the future of all agent learning.”
- “All serious AI systems need this.”
- “This is a general theory of cognition.”
- “This is the missing architecture for AGI agents.”

These claims are not needed.

The strong but testable hypothesis is narrower:

> In repeated high-context tasks, governed promotion of scoped, reusable abstractions reduces repeated mistakes and debugging time more than it adds overhead.

The next research run should judge whether that hypothesis is worth testing, and what the smallest test should be.

---

## 12. Do Not Let the Study Become a Repo-Size or Popularity Contest

Ignore GitHub stars, community hype, volume of files, and ecosystem size except where they affect engineering feasibility.

A small system may reveal a cleaner invariant than a large system.
A large system may contain many features without solving the write-governance problem.

For each compared project, focus on:

- what state persists;
- how it is created;
- how it is validated;
- how it affects future runs;
- how it is scoped;
- how it is revoked;
- what is inspectable;
- what remains stochastic/model-mediated;
- what invariants the system enforces mechanically.

---

## 13. Do Not Deeply Analyze Generated, Vendored, or Low-Signal Repo Material

When packaging repos for Deep Research or manual review, ignore or exclude ordinary low-signal material unless it is directly relevant.

### Exclude by default

```text
.git/
.github/workflows/     # include only if CI/eval architecture matters
node_modules/
venv/
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.cache/
dist/
build/
target/
coverage/
.next/
.turbo/
.parcel-cache/
.DS_Store
*.pyc
*.pyo
*.log
*.tmp
*.bak
*.lock           # include lockfiles only if dependency/runtime reproducibility matters
package-lock.json # include only if needed for runtime/dependency analysis
pnpm-lock.yaml    # include only if needed for runtime/dependency analysis
yarn.lock         # include only if needed for runtime/dependency analysis
poetry.lock       # include only if needed for runtime/dependency analysis
uv.lock           # include only if needed for runtime/dependency analysis
```

### Usually include

```text
README*
docs/
src/
lib/
packages/
agent*/
server*/
cli*/
tools*/
skills*/
memory*/
evals*/
benchmarks*/
examples/        # only representative examples
pyproject.toml
package.json
Cargo.toml
go.mod
schema files
manifest files
configuration examples
```

### Include tests selectively

Tests are useful when they expose invariants, not when they are just bulk.

Include tests related to:

- persistence;
- memory;
- checkpoints;
- tool execution;
- sandboxing;
- permissions;
- evals;
- workflows;
- rollback;
- agent state;
- artifacts/skills/plugins.

Ignore tests unrelated to agent-control semantics unless needed for understanding architecture.

---

## 14. Do Not Over-Focus on UI and Product Surface

Ignore most UI details unless they reveal a control invariant.

Relevant UI questions:

- Can a user inspect learned state?
- Can a user approve/reject/demote learned artifacts?
- Can a user replay or debug a run?
- Can a user see why a memory/skill/workflow was promoted?
- Can a user see what substrate was active for a run?

Low-priority UI questions:

- layout polish;
- chat aesthetics;
- editor integrations except where they alter agent state/action boundaries;
- onboarding screens;
- marketing examples;
- generic dashboard metrics.

The next research pass is architectural, not product-design evaluation.

---

## 15. Do Not Treat Benchmarks as Sufficient Unless They Test Persistence

Ignore generic benchmark performance unless it speaks to the project hypothesis.

SWE-bench performance, coding task success, or generic agent benchmark scores may be useful background, but they do not automatically answer whether governed substrate promotion is useful.

The relevant benchmark shape is repeated and stateful:

1. The system performs a task.
2. It observes mistakes, corrections, tests, or new project facts.
3. It proposes durable state or substrate.
4. The system gates promotion.
5. Future runs reuse the promoted artifact.
6. Outcomes improve or regress.
7. The cause can be traced and rolled back.

Ignore benchmark evidence that only measures one-shot task success unless comparing baseline capability.

---

## 16. Do Not Let Provider or Framework Marketing Define Terms

Ignore marketing use of terms like:

- memory;
- learning;
- agentic;
- self-improving;
- autonomous;
- context engineering;
- eval-driven;
- persistent;
- substrate;
- skill;
- workflow;
- trace;
- governance.

For each term, ask what is concretely implemented.

Examples:

- “Memory” may mean raw transcript storage, vector search, profile cards, graph facts, or typed validated claims.
- “Skill” may mean prompt text, a tool wrapper, a package, a workflow, or an eval-gated capability.
- “Trace” may mean observability only, not a replayable causal ledger.
- “Eval” may mean benchmark reporting, not promotion gating.
- “Learning” may mean summarization, not governed write transitions.

Use implementation semantics, not product vocabulary.

---

## 17. Do Not Spend Early Research on Non-Coding Domains

The first falsification workload should be software/repo work because it gives concrete evidence anchors:

- files;
- diffs;
- tests;
- commits;
- build outputs;
- logs;
- dependency manifests;
- symbols;
- reproducible commands.

Ignore broad domain expansion for now:

- personal productivity agents;
- legal agents;
- medical agents;
- financial advisory agents;
- general research agents;
- broad enterprise workflow agents;
- social/persona companions;
- autonomous business operations.

Those may matter later, but they are weaker initial proving grounds because evaluation and evidence anchoring are harder.

The next research pass should keep asking:

> What is the minimal version that improves repeated repo/document/coding analysis?

---

## 18. Do Not Assume Providers Have Not Built This Internally

Ignore arguments based on “if providers have not shipped it, it must be wrong” or “if providers are adjacent, it must be right.”

Provider behavior is evidence, not proof.

Reasons providers may converge on adjacent planes instead:

- context/tool bloat has immediate product payoff;
- tracing, evals, and guardrails are broadly useful;
- memory is easier to sell than epistemic state transitions;
- generic providers avoid opinionated task-family contracts;
- verification loops are expensive;
- some systems may exist internally but not be exposed publicly.

The next research should compare public systems carefully, but not infer too much from absence.

---

## 19. Do Not Ignore Overhead

This is the opposite of “ignore.”

Do not ignore overhead.

But ignore vague overhead complaints that are not tied to measurement.

The research and MVP should measure:

- token overhead;
- latency overhead;
- implementation complexity;
- maintenance burden;
- user review burden;
- false-positive promotion blocks;
- false-negative accepted artifacts;
- context pollution;
- debugging time saved;
- repeated-error reduction;
- rollback usefulness;
- reuse across related tasks.

The architecture is not justified unless the saved rework/debugging/failure cost exceeds the governance cost.

---

## 20. Do Not Let the Output Become Another Affirmation Report

Ignore prompts or report sections that ask the model to praise the project.

The desired research output is not:

> “Hermes Fork is visionary and promising.”

The desired output is:

> “Here is what existing systems already solve, here is what they do not solve, here is the smallest additive layer, and here are the kill criteria.”

Any report should be allowed to recommend:

- build minimal promotion layer only;
- build ledger/claims only;
- use an existing framework instead;
- reduce substrate artifacts to annotations;
- defer the thesis;
- abandon the thesis for now.

Do not accept a report that cannot say “no.”

---

## 21. Short Ignore Checklist for the Next Deep Research Run

Use this checklist while reviewing outputs:

- Ignore feature lists not mapped to invariants.
- Ignore “memory” claims without write-governance semantics.
- Ignore “eval” claims without promotion-gating semantics.
- Ignore “trace” claims without replay/provenance implications.
- Ignore “skill” claims without manifest, scope, permissions, evals, or rollback.
- Ignore provider synthesis as truth unless evidence/promotion semantics exist.
- Ignore cognition metaphors unless translated into contracts.
- Ignore broad artifact families not needed for the minimal falsification slice.
- Ignore UI polish unless it changes inspectability/approval/rollback.
- Ignore one-shot benchmark scores unless they compare against stateful learning.
- Ignore popularity/hype as evidence.
- Ignore grand claims until the minimal repeated-task hypothesis is tested.

---

## 22. What Must Not Be Ignored

For clarity, the following must **not** be ignored:

- evidence that existing systems already implement governed artifact promotion;
- evidence that retrieval/checkpoints/evals are enough without substrate artifacts;
- evidence that substrate activation adds overhead without behavioral gain;
- evidence that Hermes integration is more invasive than expected;
- evidence that the artifact seam is unnecessary if a fixed domain pack works just as well;
- evidence that the architecture is mostly encoding one operator’s cognitive style;
- evidence that the minimum useful form is smaller than the current thesis.

Negative evidence is high-value. The goal is to shrink the project until only the necessary layer remains.

---

## 23. Final Instruction for Researchers

When in doubt, ask:

> Does this material help decide whether governed promotion of reusable abstractions is a real missing layer?

If no, ignore or defer it.

If yes, analyze it through the invariant matrix and connect it to a concrete recommendation:

- keep;
- shrink;
- defer;
- replace with existing system;
- test experimentally;
- kill.

---

## 24. Source Packing and Documentation Inflation Control

For the next comparative run, code should be the primary evidence whenever source code is available.

### Prefer code over docs when both exist

For open-source systems such as Hermes, aider, Plandex, OpenHands, LangGraph, and Open SWE, use code as primary evidence. For Crush/OpenCode, verify identity before equating them. For SWE-agent proper, use source only if actual SWE-agent source is added or fetched.

Use documentation only as:

- an orientation map;
- confirmation of public intent;
- a guide to entrypoints;
- a source for features not obvious from code;
- a way to resolve terminology after code inspection.

If source code and docs disagree, code wins.

### Keep docs only for systems without usable source

Claude Code and provider/cloud Codex behavior are not fully code-reviewable in the same way as open-source repos. Codex CLI source in this pack can be source-inspected for local mechanics. For provider/cloud behavior, official docs or current web research are acceptable, but every conclusion should be labelled as `docs-verified` unless backed by public source, API behavior, or reproducible examples.

Do not mix doc-only provider claims with source-verified open-source claims in the same confidence bucket.

### Do not upload duplicated docs if web research is allowed

If the research prompt allows official web research, it is acceptable to omit bulky provider docs from the upload pack and instruct the model to fetch only official docs when needed.

If provider docs are uploaded, keep them minimal:

```text
claude_code_official_summary.md
codex_official_summary.md
codex_skills_official_summary.md
```

Each should contain only architecture-relevant facts: state, tools, memory, skills, approvals, sandboxing, evals, traces, persistence, rollback, and write governance.

### Do not let docs dominate the evidence budget

For each open-source repo, the research run should inspect code paths related to:

- agent loop / orchestration;
- persistent state;
- memory;
- context assembly;
- tool registry and tool execution;
- sandboxing / approvals;
- skills / workflows / plugins;
- traces / logs / checkpoints;
- evals / benchmarks;
- rollback / recovery;
- learned or persisted artifacts.

Documentation should not be used to infer governed substrate promotion when the code does not implement it.

### Require source-confidence labels

Every major finding should be labelled as one of:

- `source-verified`: supported by inspected source code;
- `docs-verified`: supported by official docs only;
- `inferred`: reasoned from code/docs but not directly stated;
- `unverified`: plausible but not evidenced;
- `not found`: searched for and absent in reviewed materials.

This prevents context inflation from turning into false confidence.
