# Hermes Dossier

## Source status

Included in uploaded pack as `02_repos/hermes-agent-main.zip`; source-inspectable. The original source manifest should be corrected.

## Exact files/modules to inspect first

```text
run_agent.py
model_tools.py
hermes_state.py
agent/prompt_builder.py
agent/context_engine.py
agent/memory_manager.py
agent/background_review.py
agent/conversation_loop.py
tools/memory_tool.py
tools/skill_manager_tool.py
tools/skills_tool.py
tools/skill_provenance.py
tools/checkpoint_manager.py
tools/approval.py
acp_adapter/permissions.py
plugins/memory/*
```

## Candidate components to keep/adopt

- operator shell;
- tool registry and dispatch;
- context-file loading and prompt assembly;
- skill UX and skill manager as precursor to `SkillArtifact`;
- checkpoints;
- approval/permission machinery;
- provider plumbing as adapters;
- session/search/logging surfaces.

## Components to wrap or replace

- flat memory as authoritative context;
- background review direct writes;
- mutable skills without promotion gate;
- provider outputs treated as truth;
- prompt projection that mixes trust categories.

## Nova multiplier

Hermes becomes the shell. Nova governs every future-affecting write that Hermes currently lets memory, background review, skills, or providers mutate directly.

## Recommendation

Preserve shell; replace learning semantics.
