The MVP should be **tiny**.

It should sit beside Hermes’ existing runtime and intercept only a few write classes.

**MVP scope**

- Host: **Hermes fork**
- Artifact types:
  - project instructions
  - repo facts / decisions
  - skills
  - checks / eval guards
- Not in MVP:
  - free-form user memory
  - provider memory
  - generalized retrieval memory
  - workflow DAG engine
  - new sandbox
  - new repo map
  - new session runtime

**MVP flow**

A normal run executes exactly as today. When the run tries to create or update future-affecting reusable state, Nova intercepts it and converts it into a **proposal**, not a trusted write. The proposal must attach evidence from the run. A reviewer or evaluator then promotes or rejects it. Only promoted artifacts are eligible for future activation. **`inferred`**

In Hermes terms, this means:
- do **not** let background review directly land trusted memory/skills;
- do route those writes into `ArtifactProposal`s with evidence bundles;
- do maintain an active-artifact registry that the prompt builder can read;
- do log which active artifacts influenced each future run. **`inferred` from inspected Hermes write paths**

That is enough to test the thesis without building a new agent.