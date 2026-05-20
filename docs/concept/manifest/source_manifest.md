# Source Manifest

**Pack:** `nova-research-pack`  
**Manifest date:** 2026-05-19  
**Outer archive:** ``nova-final-research-pack.7z`  
**Purpose:** inventory the sources for a comparative architectural falsification study of Nova as a governed promotion layer for future-affecting agent state.

---

## 1. Study Goal

This pack is for evaluating whether Nova as a **minimal governed promotion layer for future-affecting agent state** is:

- genuinely additive over existing agent systems;
- redundant with existing mechanisms such as memory, retrieval, traces, checkpoints, skills, tools, evals, sandboxes, and human approval;
- premature / overbuilt;
- or wrong.

The study should not praise Nova. It should falsify, shrink, or validate the smallest useful form.

---

## 2. Source Priority Rules

Use the following hierarchy when resolving conflicts:

| Priority | Source type | Treatment |
|---:|---|---|
| 1 | Source code in included repo archives | Highest-confidence implementation evidence for included open-source systems. Use this for invariants, control boundaries, persistence, execution flow, tool policy, memory, evals, and rollback. |
| 2 | Current official docs / official repositories fetched during research | Use only to fill gaps, verify current product surfaces, or handle systems whose full source is not included. Label as `docs-verified` unless source code is inspected. |
| 3 | Included project thesis docs | Treat as Hermes Fork design intent and hypotheses, not implementation truth. |
| 4 | Previous deep-research summaries | Treat as prior analysis and hypothesis scaffolding. Useful for convergent findings, but not a substitute for current code inspection. |
| 5 | README / marketing / feature lists | Use for orientation only. Do not count as implementation unless source confirms it. |

**Core rule:** for open-source systems, code beats docs. For proprietary/provider systems or incomplete repositories, label conclusions as `docs-verified`, `source-verified`, `inferred`, `unverified`, or `not found`.

---

## 3. Required Evidence Labels

Every substantive claim in the final research should carry one of these labels:

| Label | Meaning |
|---|---|
| `source-verified` | Confirmed by inspecting implementation source in the pack or official source repo. |
| `docs-verified` | Confirmed only by official docs, README, release notes, or product pages. |
| `inferred` | Reasonable architectural inference from code/docs, but not directly stated. |
| `unverified` | Mentioned in source material, but not confirmed strongly enough. |
| `not found` | Searched for and not found in inspected sources. |

Do not use vague equivalence. For example, a system having “memory” does not mean it has typed claims, evidence binding, promotion gates, or rollbackable substrate.

---

## 4. Actual Pack Inventory

### 4.1 Top-level control files

| Path | Kind | Size | Role | Treatment |
|---|---:|---:|---|---|
| `00_README.md` | control/readme | 383 B | States the falsification-study goal. | Use as study framing only. |
| `01_research_brief.md` | control/brief | recompute after final edits | Defines final Nova framing and source-handling rules. | Use as the starting brief. |
| `04_manifest/what_to_ignore.md` | control/scope | recompute after final edits  | Defines what not to waste attention on. | Must be obeyed as scope control. |
| `04_manifest/source_manifest.md` | control/manifest | generated | generated | Use to understand source priority and pack contents. |

### 4.2 Hermes Fork thesis and adversarial framing

| Path | Kind | Size  | Role | Treatment |
|---|---:|---:|---|---|
| `01_project_thesis/hermes_fork_thesis.md` | thesis | 13,819 B | Main candidate thesis for Hermes Fork. | Treat as design intent, not proof. |
| `01_project_thesis/substrate_runtime_claims.md` | claim stack | 16,099 B | Decomposes the thesis into testable claims. | Use to structure falsification. |
| `01_project_thesis/concerns_and_kill_criteria.md` | adversarial criteria | 15,464 B| Defines concerns, overhead risks, kill criteria. | Use as mandatory adversarial lens. |
| `01_project_thesis/founding_doubts.md` | founding doubts / self-critique | 619 B | Captures the concern that the thesis may project human meta-cognition into runtime logic. | Use to prevent affirmation bias. |


### 4.3 Previous deep-research summaries

### 4.3 Previous deep-research summaries

| Path | Title | Size | Role | Treatment |
|---|---|---:|---|---|---|
| `01_project_thesis/previous_deep_research_summaries/1.md` | Hermes Fork Architectural Decision Report | 40,738 B | Prior source-grounded Hermes fork assessment. | Secondary analysis; useful for pressure points, not implementation truth unless code/source is rechecked. |
| `01_project_thesis/previous_deep_research_summaries/2.md` | Honcho and Holographic in Hermes Agent | 30,897 B | Prior provider audit focused on Honcho/Holographic. | Secondary analysis; use for provider hypotheses and caveats. |
| `01_project_thesis/previous_deep_research_summaries/3.md` | Hermes Fork Verified Learning Runtime Assessment | 52,068 B | Prior kernel-first assessment. | Secondary analysis; important for source-reliability posture. |
| `01_project_thesis/previous_deep_research_summaries/4.md` | Corrected Hermes Fork Architecture: Verified Substrate Composition Runtime | 49,249 B | Prior correction that moves artifact/substrate seam earlier. | Secondary analysis; use to test whether artifact seam survives comparison. |
| `01_project_thesis/previous_deep_research_summaries/5.md` | Comparative Architectural Falsification Study of Hermes Fork Nova | recompute after stale-reference edit | Latest prior comparative falsification result; supports minimal promotion seam, not full substrate runtime. | Secondary analysis; use as latest framing, not implementation truth unless code/source is rechecked. |

These five files are useful because they frame the prior convergence: Hermes has a strong shell but weak verified learning semantics; Honcho/Holographic are useful but not canonical truth; and the latest comparison supports a minimal governed promotion layer over a full substrate runtime.

---

## 5. Included Repository Archives

All repository archives are branch snapshot zips, not checked-out git repositories. They do **not** include `.git` metadata. Their exact commit SHAs are not derivable from the archive alone unless separately recorded. Treat the archive SHA256 as the reproducibility anchor for this research run.

| Path | System | Top-level dir | Size | Files | Uncompressed size | Primary use in study | Caveats |
|---|---|---|---:|---:|---:|---|---|---|
| `02_repos/aider-main.zip` | aider | `aider-main` | 67,799,048 B | 691 | 77,744,297 B | Repo maps, edit loops, git/diff discipline, benchmark habits. | Branch snapshot only; commit SHA not recorded. |
| `02_repos/plandex-main.zip` | Plandex | `plandex-main` | 28,797,651 B | 696 | 32,198,212 B | Plan/apply/reject/rewind, context and plan state. | Branch snapshot only; commit SHA not recorded. |
| `02_repos/OpenHands-main.zip` | OpenHands | `OpenHands-main` | 4,902,752 B | 2,327 | 16,654,468 B | Action/event model, sandbox/runtime, file store, skills/microagents. | Enterprise directory has separate licensing; avoid unless cleared. |
| `02_repos/crush-main.zip` | Crush | `crush-main` | 1,957,901 B | 888 | 7,220,090 B | Terminal coding-agent baseline: sessions, LSP context, provider/tool extensibility, MCP, permissions. | FSL-1.1-MIT; imitate/design-reference unless legal review approves direct reuse. Do not silently equate with OpenCode. |
| `02_repos/codex-main.zip` | OpenAI Codex CLI / Codex repo snapshot | `codex-main` | 10,116,039 B | 4,552 | 41,883,195 B | CLI/runtime structure, skills, sandbox/devcontainer, hooks, state/logs. | Product/cloud behavior may require official docs; label accordingly. |
| `02_repos/claude-code-main.zip` | Claude Code public repo snapshot | `claude-code-main` | 11,295,633 B | 192 | 12,310,985 B | Provider baseline for settings, hooks, plugins, skills, examples, commands. | Not full proprietary implementation source. Treat as docs/examples baseline. |
| `02_repos/hermes-agent-main.zip` | Hermes | `hermes-agent-main` | 30,418,911 B | 3,508 | 70,558,744 B | Hermes shell/source: prompt builder, context engine, memory manager, skills, approvals, checkpoints, tools. | Use source for implementation evidence; thesis docs remain design intent. |
| `02_repos/langgraph-main.zip` | LangGraph | `langgraph-main` | 4,251,872 B | 569 | 12,666,058 B | Durable orchestration, graph state, checkpoints, human-in-loop/replay infrastructure. | Use as orchestration candidate only; workflow state is not epistemic truth. |
| `02_repos/open-swe-main.zip` | Open SWE | `open-swe-main` | 631,300 B | 182 | 1,917,304 B | LangGraph/Deep Agents coding-agent harness, sandbox lifecycle, Slack/Linear/GitHub invocation, reviewer evals. | This is Open SWE, not SWE-agent proper. Do not use it for SWE-agent claims. |

---

## 6. Expected Systems vs Actual Pack Contents

| System | Included? | Evidence level available from this pack | Notes |
|---|---:|---|---|
| Hermes / Hermes Fork source | Yes | Source snapshot + thesis docs + prior reports | Use source code for implementation evidence. Treat thesis docs as design intent and prior reports as secondary analysis. |
| aider | Yes | Source snapshot | Good source-verified baseline. |
| Plandex | Yes | Source snapshot | Good source-verified baseline. |
| OpenHands | Yes | Source snapshot | Good source-verified baseline; avoid enterprise-only code unless cleared. |
| Crush | Yes | Source snapshot | Identity/license caution; do not silently equate with OpenCode. |
| Codex / Codex CLI | Yes | Source snapshot + current docs likely needed | Use code for local mechanics; use official docs for current provider/cloud/product behavior. |
| Claude Code | Yes | Public repo/examples + current docs likely needed | Use as docs/examples/provider baseline, not full implementation source. |
| LangGraph | Yes | Source snapshot | Use as durable orchestration/checkpointing candidate only. |
| Open SWE | Yes | Source snapshot | Coding-agent harness reference. Not SWE-agent proper. |
| SWE-agent proper | No | Not included | Add actual source/docs or explicitly exclude from this pass. |
| Provider docs | No standalone docs included | Not available | Web research may be needed for current provider claims. |

---

## 7. What Each Repo Should Be Used to Test

| Repo | Invariants to inspect first | Do not over-focus on |
|---|---|---|
| Hermes | Prompt/context loading, memory manager, background review writes, skills, approvals, checkpoints, tools, provider plumbing, persistent-write paths. | Thesis language unless source confirms implementation semantics. |
| aider | Repo map/context selection, edit flow, git/diff workflow, prompt construction, command execution, file update loop, model interaction boundaries. | UI polish, marketing, model leaderboard claims unless relevant to invariants. |
| Plandex | Long-running plan state, context management, diff review, rollback/recovery, task decomposition, branch/file handling, eval or test gates. | Product positioning or SaaS features unless they change persistence/governance. |
| OpenHands | Event stream, sandbox, runtime isolation, app/server state, file store, action/observation model, multi-agent or collaboration primitives. | Benchmark badges or cloud feature claims unless source/docs connect to invariants. |
| Crush | Session state, LSP context, provider switching, MCP/tool boundary, persistence, permission model, extensibility. | Branding/name confusion; verify before equating with OpenCode. |
| Codex | Local CLI control loop, skill packaging, sandbox/devcontainer, agent graph/store, app-server protocols, policy/approval surfaces if present. | Do not infer Codex Web/cloud behavior from CLI code unless supported. |
| Claude Code | Hooks/settings/plugins/skills examples, command surfaces, policy-like settings, repo/task automation patterns. | Do not treat public examples as full product implementation. |
| LangGraph | Graph state, durable execution, checkpoint storage, interrupts, replay/time travel, persistence boundaries. | Treating workflow state as truth or importing orchestration before Nova proves value. |
| Open SWE | Coding-agent harness, sandbox lifecycle, Slack/Linear/GitHub invocation, middleware ordering, curated tools, reviewer evals. | Treating Open SWE as SWE-agent proper or treating task success as governed promotion. |

---

## 8. Main Research Questions This Manifest Supports

The comparative study should answer:

1. Which invariants recur across serious agent systems?
2. Which invariants are source-verified versus docs-verified?
3. Do any systems implement an equivalent to governed promotion of future-affecting state?
4. Are Nova concepts redundant with existing memory, retrieval, skills, checkpoints, traces, workflows, evals, and sandboxes?
5. What is the smallest additive Nova layer that survives comparison?
6. What should be killed, deferred, or reduced to ordinary memory/skills?

---

## 9. Missing or Weak Inputs

These gaps should be visible in the final research, not silently papered over:

- **No `repo_commit_shas.md` is present.** Repository zips are reproducible by archive hash, but exact upstream commits are not recorded.
- **No SWE-agent proper source/docs are included.** `open-swe-main.zip` is Open SWE, not SWE-agent.
- **No standalone provider docs are included.** Official web docs may be needed for Claude Code/Codex current product behavior.
- **`crush-main.zip` identity/license needs care** if the intended comparison target is OpenCode or if direct reuse is considered.
- **Upstream freshness is not verified.** The zips are branch snapshots; use archive hashes as local reproducibility anchors.

---

## 10. Research Handling Instructions

When running Deep Research over this pack:

1. Start with repo source inspection for included open-source repos.
2. Use `what_to_ignore.md` to avoid feature-list drift.
3. Treat thesis docs as claims to test, not claims to validate.
4. Treat prior reports as secondary scaffolding.
5. Use official web docs only for gaps, current product behavior, or missing systems.
6. Keep a hard distinction between:
   - context selection and learning;
   - traces and evidence binding;
   - storage and promotion;
   - eval passing and generalization;
   - user memory and reusable cognitive substrate;
   - product feature and runtime invariant.
7. For every system, explicitly answer whether it has:
   - artifact proposal;
   - evidence requirement;
   - eval gate;
   - promotion state;
   - scope/type metadata;
   - automatic future-run influence;
   - rollback/demotion.

---

## 11. Recommended Final Research Output Constraint

The final research should not end with a vague “promising” judgement. It must choose one:

- build full substrate runtime;
- build minimal governed promotion layer;
- build ledger/claims only;
- adopt existing framework and add governance;
- defer thesis;
- abandon thesis for now.

The answer can be conditional, but the minimum implementation must be explicit.

---

## 12. Manifest Caveat

This manifest is based on the contents of the uploaded `nova-final-research-pack.7z` as unpacked on 2026-05-19. It does not verify upstream freshness of the repo snapshots. If exact commit identity matters, add `04_manifest/repo_commit_shas.md` before the research run. Recompute mutable text-file hashes and the outer archive hash after final manual edits.
