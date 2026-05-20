# Stage Plan, Evals, and Cutoffs

Thresholds below are proposed defaults. The research run should refine them or reject them.

## Stage 0 — Source adoption triage

**Goal:** identify source-verified, license-compatible primitives to adopt/fork/port/imitate.

**Build scope:** no product code; source analysis and small extraction experiments only.

**Eval:**

- at least 3 high-value primitives identified;
- at least 1 low-risk direct adoption or port path;
- license status understood;
- LangGraph and Open SWE inputs triaged; SWE-agent proper added, fetched, or explicitly excluded.

**Continue if:** there is a credible path to reuse/port mature primitives.

**Cutoff:** if direct reuse is legally or structurally blocked, use adapter/imitation strategy instead of forks.

## Stage 1 — Run ledger and evidence capture

**Goal:** capture runs, events, diffs, commands, tests, context selection, and observations.

**Build scope:** append-only RunLedger and EvidenceStore, instrumented around one agent/runtime path.

**Eval:**

- every run has task spec, selected context, tool/action events, diffs, test/log evidence;
- a human can inspect why a claim/proposal exists;
- event volume remains manageable.

**Suggested thresholds:**

- >= 95% of tool/action events captured in test runs;
- <= 10% overhead on baseline run time before claim/proposal logic;
- no trusted-state mutation yet.

**Cutoff:** if ledger capture is too expensive or too noisy to inspect, reduce to smaller event schema before proceeding.

## Stage 2 — Typed claims and proposal-only learning

**Goal:** agent/adopted components can propose future-affecting writes but cannot trust them.

**Build scope:** ClaimStore, ProposalStore, basic claim types, proposal emitter.

**Eval:**

- proposals contain type, scope, evidence, expected future effect, risk, invalidation hints;
- direct memory/skill/project-instruction writes are intercepted or bridged to proposals;
- proposal review is understandable.

**Suggested thresholds:**

- >= 80% of accepted proposals have evidence links reviewers consider relevant;
- proposal false-positive rate after tuning <= 50%;
- proposal survival to accepted/trusted >= 30% for targeted generators;
- review overhead <= 15 minutes per task chain or <= 15% of run time, whichever is smaller.

**Cutoff:** if proposals are mostly noise, reduce emitters and keep manual annotations only.

## Stage 3 — Promotion gate and trust states

**Goal:** future-affecting writes require a promotion decision.

**Build scope:** PromotionGate, TrustState, minimal policy checks, rejection/stale/demotion states.

**Eval:**

- no accepted/trusted future influence bypasses gate;
- gate records who/what decided, evidence considered, scope, version, and invalidation rule;
- direct provider memory does not enter canonical truth.

**Suggested thresholds:**

- 100% of future-affecting writes in test harness pass through gate or are flagged;
- reviewers can reconstruct promotion reason in >= 90% of accepted items;
- gate overhead <= 15% of task-chain time.

**Cutoff:** if gate blocks useful work or becomes queue bureaucracy, reduce to manual gate for high-risk writes only.

## Stage 4 — One promoted SkillArtifact

**Goal:** test whether a promoted reusable artifact beats claims-only.

**Build scope:** one `SkillArtifact`, manifest, version, evidence, projection/export path, activation log.

**Eval metrics:**

- repeated-error reduction;
- debug-time reduction;
- activation specificity;
- overhead;
- demotion usefulness;
- comparison against ordinary ungated skill.

**Suggested thresholds:**

- repeated-error reduction >= 20% over baseline;
- median debug-time reduction >= 15%;
- overhead <= 15% extra tokens/time;
- activation precision >= 70%;
- ordinary skill baseline does not match promoted-skill arm;
- bad skill demotion removes harmful behavior in >= 80% of seeded cases.

**Cutoff:** if claims-only or ordinary skills match the promoted artifact, stop substrate expansion and keep governed skills/claims only.

## Stage 5 — Projection seam / context projector shadow mode

**Goal:** test whether scoped projection reduces context pollution and preserves epistemic categories.

**Build scope:** category-fenced projection into prompt/AGENTS/CLAUDE/skill surfaces, initially shadow or lightly active.

**Eval metrics:**

- relevant trusted items included;
- irrelevant items excluded;
- stale/provisional/evidence/provider synthesis not collapsed;
- behavior changes are attributable.

**Suggested thresholds:**

- relevant promoted items included in >= 75% of applicable tasks;
- irrelevant promoted items included in <= 15% of non-applicable tasks;
- context pollution reduced by >= 20%;
- no evidence of projection becoming static same-bundle injection across >80% of useful runs.

**Cutoff:** if projection is static or does not change behavior, replace it with ordinary static project instructions.

## Stage 6 — Regression attribution and demotion

**Goal:** prove bad future influence can be traced and removed.

**Build scope:** activation-to-outcome linkage, seeded bad artifacts, demotion/replay comparison.

**Eval:**

- seeded bad claim/artifact causes measurable regression;
- system identifies likely culprit;
- demotion improves subsequent run;
- replay/counterfactual can compare with and without activation.

**Suggested thresholds:**

- correct artifact/claim attribution >= 70% of seeded cases;
- demotion improves quality or removes repeated error in >= 70% of cases;
- demotion record is inspectable in >= 90% of cases.

**Cutoff:** if attribution is weak, forbid autonomous promotion and keep human-only governance.

## Stage 7 — Multi-repo repeated-task benchmark

**Goal:** evaluate net value against strong baselines.

**Arms:**

1. baseline agent with normal retrieval/context/checkpoints;
2. ledger + typed claims;
3. ledger + claims + promotion gate;
4. ledger + claims + promoted `SkillArtifact`;
5. optional projection seam.

**Metrics:**

- quality/hidden tests;
- repeated-error reduction;
- debug time;
- rework;
- overhead;
- reuse across related tasks;
- rollback/demotion usefulness;
- regression attribution;
- activation specificity;
- context pollution.

**Suggested continue condition:** at least one governed-promotion arm shows practical net improvement after overhead.

**Cutoff:** if strong retrieval/checkpoints/evals plus ordinary skills match the governed layer, shrink to ledger/claims or use existing framework.

## Stage 8 — Expansion decision

**Goal:** decide whether to add LensArtifact, EvalArtifact, richer ContextProjectorArtifact, multi-agent governance, or provider adapters.

**Rule:** no new artifact class without a measured bottleneck.

**Cutoff:** no expansion based on elegance, analogy, or ontology completeness.
