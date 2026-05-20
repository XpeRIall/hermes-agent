The biggest abstraction errors are already visible from the inspected systems.

First, **confusing persistence with governance**. Hermes memory, Codex memories, repo instruction files, and Crush/OpenHands skills all persist future influence. That does not make them governed. **`source-verified`**

Second, **confusing checkpoints with blame**. LangGraph and Plandex show good persistence/rewind patterns, but checkpointing alone does not tell you which promoted artifact caused a regression. **`source-verified`**

Third, **confusing hooks with policy memory**. Hooks are runtime decision points, not reusable trusted knowledge. Crush and Codex make this clear. **`source-verified`**

Fourth, **trying to universalize too early**. OpenHands, Open SWE, LangGraph, and Codex all show how quickly platform scope expands. Nova should resist that. **`inferred`**

**Open questions / limitations**

A few important items remain incomplete in this run:

- **SWE-agent proper** was officially identified but not deeply source-inspected here. **`partial`**
- **OpenCode proper** was officially identified separately from Crush but not directly source-inspected here. **`partial`**
- **Claude Code** remained a docs-only baseline; no official product implementation source was available in the pack. **`docs-verified`**
- Exact upstream **commit SHAs** were not recoverable from the uploaded archive zips; archive hashes and local file paths were available instead. **`source-verified` for local archive state, `not found` for exact commits**
- The uploaded `.7z` could be unpacked and inspected locally, but its extracted contents are not render-citable in this interface. That is why file/module paths and labels are used explicitly throughout.