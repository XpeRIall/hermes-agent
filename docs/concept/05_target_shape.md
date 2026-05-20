The target state is still not a new substrate. It is a **host-neutral governed influence layer** with adapter surfaces.

The target shape has three layers:

**Runtime host layer**  
Hermes first. Potential later adapters for Codex-like or Crush-like hosts. The runtime host owns execution, tools, sessions, and sandboxes. **`inferred`**

**Nova kernel**  
Owns proposals, evidence references, policy, trust state, activation, rollback, and blame. **`inferred`**

**Artifact consumers**  
Prompt builders, skill loaders, check runners, repo-context projectors, and provider-specific wrappers that can activate trusted artifacts for a run. **`inferred`**

This target shape is only justified if the MVP proves that governed promotion beats baseline memory/skills/instructions in longitudinal repeated-work settings.