# OpenHands Dossier

## Source status

Included as `02_repos/OpenHands-main.zip`; source-inspectable for open/core code. Enterprise subdirectory has separate licensing.

## Exact files/modules to inspect first

```text
openhands/app_server/event/
openhands/app_server/sandbox/
openhands/app_server/app_conversation/
openhands/app_server/user/skills_router.py
openhands/app_server/mcp/mcp_router.py
openhands/app_server/file_store/
skills/
.agents/skills/
AGENTS.md
```

## Candidate components to take

- action/event model;
- filesystem/cloud event stores;
- sandbox services;
- conversation/session service patterns;
- skills/microagents as carrier surfaces;
- MCP routing ideas.

## Components to avoid

- enterprise-only code unless cleared;
- treating event logs as causal ledgers;
- treating microagent existence as trust.

## Nova multiplier

OpenHands events become `RunEvent`s. Skills/microagents become export targets for promoted `SkillArtifact`s.

## Recommendation

Adopt/imitate event and sandbox structure; use skills as interop target.
