# MVP and Target Shape

## MVP decision

The MVP should be:

> a minimal governed promotion layer over adopted OSS agent primitives.

It should not be a full substrate runtime.

## MVP includes

```text
RunLedger
EvidenceStore
ClaimStore
ProposalStore
TrustState
PromotionGate
Demotion/RollbackEvent
RegressionAttribution record
thin ArtifactManifestEntry
activation/projection log
one imported/runtime path
one SkillArtifact
one projection/export path
one repeated-task benchmark
```

## MVP excludes

```text
live LensArtifact
generalized EvalArtifact ontology
AnalyzerArtifact / TransformArtifact catalogs
ToolArtifact / PolicyArtifact / ModelAdapterArtifact
provider memory as canonical truth
autonomous promotion
multi-agent governance
artifact marketplace/registry
general domain packs beyond software engineering
deep UI beyond inspection/approval basics
```

## MVP runtime loop

```text
1. User/task enters Nova.
2. Nova creates Run and scoped task spec.
3. Context provider/adopted repo primitive selects candidate context.
4. Nova projects accepted claims and scoped instructions.
5. Executor/adopted agent performs work.
6. Logs, diffs, tests, observations, tool calls become RunEvents and Evidence.
7. ProposalEmitter creates ProposedClaim or ProposedSkillArtifact.
8. PromotionGate accepts/rejects/stales/quarantines.
9. Accepted/trusted state is projected to future runs through controlled surfaces.
10. Later runs log activated items.
11. Regressions can trace back to activated claims/artifacts and demote them.
```

## First live artifact

Use `SkillArtifact` first because it is closest to existing serious-system patterns: skills, plugins, microagents, instructions, hooks, and task procedures.

Minimal `SkillArtifact`:

```text
id
name
version
scope
trigger_conditions
procedure
required_context
evidence_ids
promotion_decision_id
trust_state
risk_profile
allowed_side_effects
render_targets: AGENTS.md, CLAUDE.md, skill markdown, prompt block
activation_history
demotion_rules
```

## Projection/export path

The first projection path should render trusted state into one or more ordinary agent surfaces:

- `AGENTS.md` snippet;
- `CLAUDE.md` snippet;
- skill markdown;
- executor prompt block.

Important: these files are exports from Nova, not Nova truth sources.

## Near-term target after MVP success

Add only if MVP shows measurable value:

- multiple executor adapters;
- richer repo/file/symbol claim anchoring;
- shadow-to-active context projector;
- replay/counterfactual activation tests;
- stale-claim detection;
- CI/test evidence ingestion;
- human review UI for proposals;
- artifact health metrics.

## Medium-term target

Add only if repeated-task benchmark finds concrete bottlenecks:

- `ContextProjectorArtifact` as first-class object;
- `EvalArtifact` as reusable check object;
- limited `LensArtifact` for repo/test/build interpretation;
- multi-agent worker branches that cannot promote directly;
- organization/team policy layer;
- provider adapters that emit hypotheses/evidence only.

## Speculative target

Do not build unless strong evidence accumulates:

- analyzer/transform artifact catalogs;
- policy learning;
- tool/model adapter artifacts;
- artifact marketplace;
- autonomous substrate composition;
- live model fine-tuning promotion;
- broad non-software domain packs.

## Expansion rule

A new artifact class may be added only if all are true:

1. MVP metrics expose a bottleneck that the class directly addresses.
2. Existing OSS primitive or simpler claim/skill/projection mechanism cannot solve it.
3. The artifact changes runtime behavior, not just metadata.
4. Activation and demotion can be measured.
5. Bad influence can be attributed.
