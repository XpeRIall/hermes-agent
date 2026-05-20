# Crush Dossier

## Source status

Included as `02_repos/crush-main.zip`; source-inspectable. Do not equate with OpenCode unless separately verified.

## License caution

Uploaded pack shows FSL-1.1-MIT. Treat as design-reference/imitate unless legal review approves direct adoption.

## Exact files/modules to inspect first

```text
internal/agent/
internal/event/
internal/hooks/
internal/permission/
internal/skills/
internal/backend/
internal/proto/
internal/pubsub/
internal/server/events.go
AGENTS.md
README.md
schema.json
```

## Candidate components to imitate

- hooks;
- permission model;
- skills tracker;
- event/pubsub patterns;
- provider abstractions;
- terminal ergonomics.

## Components to avoid

- direct code adoption without license clearance;
- relying on ambiguous branding/name equivalence.

## Nova multiplier

Use event/permission/skills ideas as implementation references for Nova wrapper contracts.

## Recommendation

Imitate; do not directly fork until license and identity are cleared.
