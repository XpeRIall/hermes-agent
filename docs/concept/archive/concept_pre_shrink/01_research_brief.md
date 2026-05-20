# Nova Final Research Pack

**Purpose:** revised final research package for defining Nova as a minimal governed-promotion layer, not a full substrate cathedral.

This pack is a revision of the uploaded `nova-research-pack.7z`. It preserves the original adversarial falsification posture, but incorporates the follow-up conclusion that Nova should adopt/fork/port mature open-source agent primitives and multiply them by its narrow niche: governed future influence.

## Core correction

The original pack was framed around a **verified substrate composition runtime**. The final framing should be stricter:

> Nova is a governed promotion layer for future-affecting agent state.

A future-affecting write is any persistent object that can influence later runs: memory, claim, repo fact, requirement interpretation, design decision, project instruction, skill, hook, context projection, eval/check, workflow template, policy, or artifact activation rule.

The kernel invariant is:

> No future-affecting write becomes trusted future influence without proposal, evidence, scope, type, version, trust state, promotion gate, activation record, demotion path, and regression-attribution path.

## Important changes from the uploaded pack

1. **Adopt OSS primitives aggressively.** Do not treat existing agents only as external baselines. Mine them for repo intelligence, git/diff discipline, event trajectories, sandboxing, planning, skills, hooks, eval harnesses, provider abstractions, and UI/runtime surfaces.
2. **Do not adopt their trust semantics.** Imported components may act, observe, rank, plan, edit, test, and propose. They may not directly create trusted future state.
3. **Shrink the MVP.** Keep the artifact seam structurally, but do not implement the full artifact universe. First live artifact should be `SkillArtifact`. `ContextProjectorArtifact` can start as shadow/projection logic. `EvalArtifact` should initially be a promotion-gate predicate, not a generalized artifact class. `LensArtifact` should be deferred unless evidence shows it is necessary.
4. **Fix the source manifest.** The uploaded manifest says Hermes source is missing, but the archive actually contains `02_repos/hermes-agent-main.zip`. LangGraph is also included as `02_repos/langgraph-main.zip`. Open SWE is included as `02_repos/open-swe-main.zip`; this is not SWE-agent proper. If SWE-agent remains in scope, add the actual SWE-agent source snapshot or instruct Deep Research to fetch official source/docs and label those findings accordingly.
5. **Rename the thesis operationally.** Prefer “governed promotion layer,” “future-influence governance,” or “promotion governance” over “cognitive substrate runtime” unless the benchmark proves the stronger substrate claim.

## Files in this revised pack

- `01_document_map.md` — final document list and required outputs.
- `02_revision_notes.md` — explicit edits to the original research pack.
- `03_minimal_concept.md` — minimal Nova concept.
- `04_vendor_adoption_map.md` — what to adopt/fork/port/imitate/avoid.
- `05_mvp_and_target_shape.md` — MVP, target architecture, and deferrals.
- `06_stage_plan_evals_cutoffs.md` — staged evals, thresholds, and kill gates.
- `07_benchmark_design.md` — repeated high-context benchmark design.
- `08_integration_contracts.md` — contracts for imported components.
- `09_data_model_kernel.md` — minimal schemas.
- `10_kill_criteria.md` — hard shrink/kill criteria.
- `11_risks_and_abstraction_errors.md` — adversarial risk register.
- `03_appendices/source_manifest_patch.md` — source-manifest corrections.
- `04_manifest/source_manifest.md` — corrected source inventory and evidence-confidence rules.\

## Source handling rule

Use the original source pack as primary evidence. For open-source systems, source code beats docs. For Claude Code and provider/cloud Codex behavior, use official docs for current product behavior unless implementation source is available. For LangGraph and Open SWE, use the included source snapshots for source-verified local claims. For SWE-agent proper, add/fetch official source/docs before making source-verified claims.
