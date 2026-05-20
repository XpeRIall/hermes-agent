# Revision Notes on Uploaded Research Pack

This file records concrete changes to make before the next Deep Research run.

## 1. Fix the manifest inconsistency

The uploaded `04_manifest/source_manifest.md` says no fresh Hermes source archive is present, but the uploaded archive actually includes:

```text
02_repos/hermes-agent-main.zip
```

The final source manifest must update the Hermes row to `Included: Yes` and treat Hermes source as source-inspectable.

## 2. Keep the original adversarial posture

The original `04_manifest/what_to_ignore.md` is valuable and should remain binding. Its strongest instructions are still correct:

- do not make a feature-list comparison;
- do not treat memory/retrieval/traces/evals/checkpoints/skills as equivalent to promotion governance;
- do not let provider memory become canonical truth;
- do not rely on cognition metaphors unless translated into contracts;
- do not build the full artifact universe before the falsification slice.

## 3. Fix stale `finding_doubts.md` references

The file has already been renamed in the pack:

```text
01_project_thesis/founding_doubts.md
```
Do not perform a file rename. Update any remaining text references from finding_doubts.md to founding_doubts.md.

## 4. Reframe the thesis language

Original language:

```text
verified substrate composition runtime
trusted kernel + governed composable substrate layer
cognitive substrate runtime
```

Recommended operational language:

```text
governed promotion layer
future-influence governance
promotion governance for future-affecting agent state
```

Keep “substrate” only as a hypothesis under test, not as the default implementation noun.

## 5. Shrink the MVP artifact set

The original thesis asks for four early artifact kinds:

- `SkillArtifact`
- `LensArtifact`
- `EvalArtifact`
- `ContextProjectorArtifact`

Recommended revision:

| Artifact / seam | MVP status | Reason |
|---|---|---|
| `ArtifactManifest` / base artifact seam | keep thin | Needed to prevent collapse into flat memory/skills. |
| `SkillArtifact` | first live artifact | Closest to existing OSS patterns and easiest to export into vendor surfaces. |
| `ContextProjectorArtifact` | shadow/projection seam | Needed to test category-fenced projection, but should not become a full artifact runtime yet. |
| `EvalArtifact` | defer as artifact; use as gate predicate | Promotion gates need checks, but a generalized EvalArtifact ontology is premature. |
| `LensArtifact` | defer | Highest risk of prompt-dressing/metaphor overbuild. |
| software-engineering domain pack v0 | keep as static seed | Useful benchmark scaffold, not evidence of dynamic substrate by itself. |

## 6. Add adoption strategy

The original pack mostly treats other systems as comparison baselines. The revised pack should also treat them as source-code donors:

```text
aider       → repo map, git/diff discipline, benchmark habits
OpenHands   → action/event model, sandbox/runtime, skills/microagents
Codex CLI   → sandboxing, hooks, rollout traces, AGENTS.md, state/logs
Plandex     → plan/apply/reject/rewind, branch/task state
LangGraph   → durable orchestration/checkpoints/human-in-loop; included as source snapshot
Open SWE    → LangGraph/Deep Agents coding-agent harness, sandbox lifecycle, Slack/Linear/GitHub invocation, reviewer evals; not SWE-agent
SWE-agent   → not included unless separately added/fetched; use only as benchmark/ACI reference after source verification
Crush       → hooks/events/permissions/skills/provider ideas; license caution
Claude Code → docs-verified UX conventions: CLAUDE.md, hooks, skills, plugins, scopes
Hermes      → shell, tools, prompt builder, skills, checkpoints, approvals; wrap memory/background writes
```

## 7. Add the non-negotiable integration rule

Every adopted component must obey:

> Imported components may act, observe, rank, plan, edit, test, and propose. They may not directly create trusted future state.

This is the main difference between “adopt open-source agent code” and “inherit open-source agent trust semantics.”

## 8. Clarify source inputs

LangGraph is included as:

```text
02_repos/langgraph-main.zip
```

SWE-agent proper is not included. Do not label open-swe-main.zip as SWE-agent.

Either:
- add actual SWE-agent source to 02_repos/, or
- explicitly exclude SWE-agent proper from this research pass, or
- instruct Deep Research to fetch official SWE-agent source/docs and label those findings accordingly.

## 9. Make eval thresholds explicit

The original pack has good qualitative kill criteria. The revised pack adds proposed default thresholds, such as:

- repeated-error reduction >= 20% over baseline;
- median debug-time reduction >= 15%;
- overhead <= 15% extra tokens/time;
- activation precision >= 70%;
- demotion removes bad influence in >= 80% of seeded stale-artifact cases;
- proposal survival rate >= 30% after initial tuning;
- artifact attribution identifies seeded bad artifact in >= 70% of cases.

Thresholds are proposed defaults, not evidence-proven. Deep Research should refine or reject them.
