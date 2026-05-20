# Nova Mutation Inventory

Phase 1 treats future-affecting writes as governed candidates, not trusted
state. This inventory mirrors `agent/nova/policy.py` and covers the mutation
surfaces called out in `docs/nova/ARCHITECTURE.md`.

The policy gate is intentionally narrow: it records decisions in the Nova
ledger when a ledger is supplied, can shadow-record existing writes, and can
convert selected writes into proposal records. It does not replace Hermes'
terminal, file, checkpoint, or approval behavior.

## Surface Inventory

| Surface | Current Hermes paths | Future influence | Phase 1 policy |
|---|---|---|---|
| Memory | `tools/memory_tool.py`, `agent/memory_manager.py`, `plugins/memory/` | User facts, profile facts, provider recall, and memory-provider mirrors can steer later prompts. | Convert future-affecting writes to proposals when evidence exists; block trusted direct writes without evidence and an allow decision. |
| Skills | `tools/skill_manager_tool.py`, `skills/`, `optional-skills/` | Created or patched skills become reusable procedural guidance. | Convert create/edit/patch/delete/support-file writes to proposals when evidence exists. Skill writes remain the preferred first interception target. |
| Providers | `providers/`, `plugins/model-providers/`, provider config paths | Provider profiles and routing alter model behavior and trust boundaries. | Convert provider/profile/routing changes to proposals before activation. |
| Plugins | `hermes_cli/plugins.py`, `plugins/`, `.hermes/plugins/` | Hooks, tools, and installed plugins can affect tool execution, session lifecycle, and agent context. | Convert plugin install/enable/disable/tool-registration changes to proposals before trust. |
| Background review | `agent/background_review.py` | The review fork can write memory or skills after a turn without direct user interaction. | Route memory/skill outcomes to proposals, not trusted writes. |
| Cron | `cron/`, cron prompt mode in `agent/prompt_builder.py` | Scheduled jobs run unattended and can deliver or persist future state. | Convert schedule/config/output writes to proposals when they affect future behavior. Existing cron approval settings remain host behavior. |
| Config | `~/.hermes/config.yaml`, `cli.py`, `hermes_cli/config.py` | Model, toolset, approval, gateway, plugin, and provider settings alter later runs. | Convert future-affecting config writes to proposals before trusted activation. |
| Session | `hermes_state.py` | Session messages, titles, branches, and searchable history feed recall and debugging. | Shadow-record session mutations; the session DB is not treated as the causal ledger. |
| Checkpoint | `tools/checkpoint_manager.py`, `~/.hermes/checkpoints/` | Checkpoints and restores affect repo/filesystem state and recovery history. | Shadow-record checkpoint operations; checkpoint logic and rollback behavior remain unchanged. |
| Prompt/context | `AGENTS.md`, `CLAUDE.md`, `SOUL.md`, `.hermes.md`, `.cursor/rules/`, `agent/prompt_builder.py` | Context files and prompt snapshots directly influence later system prompts. | Convert hidden context activation or context-file writes to proposals. No hidden prompt mutation. |
| Terminal | `tools/terminal_tool.py`, `tools/approval.py`, `agent/tool_executor.py` | Commands can mutate repo, config, environment, or profile state. | Shadow-record policy decisions only. Existing dangerous-command approval remains authoritative. |
| File tools | `tools/file_tools.py`, `agent/tool_executor.py` | `write_file` and `patch` can modify code, docs, config, skills, plugins, and prompt files. | Classify known future-affecting paths to narrower surfaces; otherwise shadow-record generic file writes. Existing file tool, checkpoint, and approval behavior remains authoritative. |

## Gate Contract

- `gate_mutation()` is side-effect free unless a ledger is passed.
- With a ledger, every gate evaluation appends a `policy.decision` entry.
- `convert_to_proposal` decisions also append a `proposal.attempt` entry.
- Proposal conversion and direct trusted-state writes require evidence refs.
- Direct trusted-state mutation must pass `require_trusted_state_gate()` with an
  allow decision that cites the same evidence bundle.
- Shadow recording is not authorization. Terminal and file approvals continue to
  be enforced by Hermes' existing tool paths.

## Initial Classifiers

- `memory` tool calls map to the memory surface.
- `skill_manage` calls map to the skills surface.
- `write_file` and `patch` calls are classified by path when they touch skills,
  providers, plugins, cron, config, prompt/context, or checkpoint paths.
- `terminal` and `execute_code` calls map to terminal shadow records.
- Read-only calls such as `read_file`, `search_files`, and `skill_view` are not
  classified as mutation requests.
