# Claude Code Docs Baseline Dossier

## Source status

Uploaded public repo/examples are not full product source. Treat as docs/provider baseline unless implementation code is available.

## Exact files/docs to inspect first

```text
README.md
examples/settings/README.md
examples/settings/settings-strict.json
examples/settings/settings-bash-sandbox.json
examples/mdm/managed-settings.json
examples/hooks/bash_command_validator_example.py
plugins/README.md
plugins/*/README.md
.claude/commands/*.md
```

## Candidate concepts to adopt as interop/spec inspiration

- `CLAUDE.md` project instruction convention;
- scoped settings;
- hooks;
- plugins;
- skills;
- commands;
- subagent/workflow conventions;
- managed policy surfaces.

## Components to avoid

- treating docs examples as implemented runtime proof;
- treating provider memory as canonical truth;
- depending on proprietary behavior.

## Nova multiplier

Render Nova-approved claims and skills into Claude-compatible surfaces. Claude Code is an interop target and benchmark, not the Nova brain.

## Recommendation

Docs-verified baseline and export target only.
