The integration contracts should be minimal and explicit.

**Proposal contract**

```text
propose_artifact(
  artifact_type,
  candidate_payload,
  scope,
  evidence_refs[],
  originating_run_id,
  proposed_by
) -> proposal_id
```

**Activation contract**

```text
resolve_active_artifacts(
  repo_id,
  branch_or_branch_class,
  task_class,
  user_scope,
  toolchain_scope,
  model_scope
) -> active_artifact_set
```

**Outcome contract**

```text
record_run_outcome(
  run_id,
  active_artifact_ids[],
  checks_run[],
  checks_passed[],
  regressions[],
  reviewer_feedback[],
  diff_summary
)
```

**Demotion contract**

```text
demote_artifact(
  artifact_id,
  reason,
  linked_regression_ids[]
)
```

**Rollback contract**

```text
rollback_artifact_version(
  artifact_id,
  target_version
)
```

The host runtime may do many things, but it may not bypass this layer for trusted future-affecting state. That is the core contract. **`inferred`**