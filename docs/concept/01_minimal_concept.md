The smallest useful Nova concept is:

**A promotion kernel, not a runtime.**

Its responsibilities should be limited to four invariants.

**Invariant one:** untrusted runs may **propose** future-affecting state, but may not directly create trusted future state. **`inferred`**

**Invariant two:** every proposal must carry machine- and human-auditable **evidence pointers** to concrete run artifacts. At minimum: source files touched, session/message IDs, tests/checks run, tool outputs, and any retrieved documents actually used. **`inferred`**

**Invariant three:** every promoted artifact must have explicit **scope**, **type**, **version**, **trust state**, and **activation rule**. **`inferred`**

**Invariant four:** every active artifact must be **demotable**, **rollbackable**, and **blameable** for later regressions. **`inferred`**

That leads to a first-cut artifact set that is intentionally narrow:

- **project instruction deltas**
- **repo facts / stable decisions**
- **task-class skills / workflows**
- **checks / eval guards**
- **context projectors**

It should **exclude general memory** in MVP unless memory is represented as the same typed governed object. Pure “remember the user likes X” memory does not prove the thesis. **`inferred`**

A minimal proposal object should look like this:

```text
ArtifactProposal
- id
- artifact_type
- title
- body or pointer
- evidence_refs[]
- scope
- activation_rule
- proposed_version
- parent_version
- trust_state = proposed|staged|active|demoted|rejected
- gate_result
- author = run / reviewer / evaluator
- created_at
- promoted_at
- demoted_at
- regression_links[]
```

That is the smallest layer that proves Nova’s distinct value.