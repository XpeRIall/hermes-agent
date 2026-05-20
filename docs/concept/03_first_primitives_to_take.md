The first primitives to take are:

**Take first from Hermes as host-adjacent code paths**
1. Background review and skill/memory write paths as the **interception point** for Nova proposals. **`source-verified`**
2. Session DB and checkpoint surfaces as the first evidence store and replay context. **`source-verified`**
3. Context-file loading and scope discovery as the first activation-context input. **`source-verified`**

**Take first from Codex**
1. Hook configuration shape and per-hook trust-state ideas (`trusted_hash` present in hook config state). **`source-verified`**
2. Permission/profile model for runtime actions and sandbox write/network boundaries. **`source-verified`**
3. Rollout/session import-export and trace-oriented persistence patterns. **`source-verified`**
4. AGENTS.md handling as a mature instruction-loading baseline. **`source-verified`**

**Take first from Crush**
1. Agent Skills file-format discipline and discovery model. **`source-verified`**
2. Hook aggregation semantics: allow / deny / halt / context / input rewrite. **`source-verified`**
3. Permission-service short-circuiting for pre-approved calls. **`source-verified`**

**Take first from Plandex**
1. Rewind semantics for artifact rollback. **`source-verified`**
2. Conflict-aware “revert to target state” analysis. **`source-verified`**
3. Branch/apply/log UX conventions for human-readable state history. **`source-verified`**

**Take later from LangGraph**
1. Checkpoint and store interfaces if Nova needs host-neutral persistence. **`source-verified`**
2. Interrupt/resume semantics if promotion review becomes asynchronous or multi-step. **`source-verified`**

**Use only for benchmarking, not implementation**
1. aider benchmark culture and repo-map comparisons. **`source-verified`**
2. Open SWE reviewer eval design. **`source-verified`**
3. mini-SWE-agent and SWE-agent-family longitudinal coding benchmarks. **`source-verified`**

**Do not take first**
- OpenHands as base substrate. **`inferred`**
- Open SWE as base substrate. **`inferred`**
- Claude Code product behavior as implementation reference. **`docs-verified`**
- OpenCode proper until directly source-inspected. **`partial`**
- SWE-agent proper until directly source-inspected. **`partial`**