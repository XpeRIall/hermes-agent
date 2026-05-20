# Data Model Kernel

Do not over-model. The MVP needs enough structure to test governed future influence.

## Run

```yaml
Run:
  id: string
  task_id: string
  repo_scope: Scope
  started_at: datetime
  ended_at: datetime?
  executor: string
  model: string?
  baseline_mode: string
  projected_context_id: string?
  activated_items: [ActivationRecord]
  result_summary: string?
```

## ActivationRecord

```yaml
ActivationRecord:
  id: string
  run_id: string
  item_type: claim | artifact | projection | project_instruction
  item_id: string
  item_version: integer
  trust_state_at_activation: accepted | trusted
  scope: Scope
  activation_reason: string
  projection_id: string?
  activated_at: datetime
  deactivated_at: datetime?
```

## RunEvent

```yaml
RunEvent:
  id: string
  run_id: string
  timestamp: datetime
  actor: user | model | tool | hook | executor | system
  event_type: model_message | tool_call | command | diff | test | context_select | projection | approval | error
  input_ref: string?
  output_ref: string?
  affected_paths: [string]
  evidence_ids: [string]
```

## Evidence

```yaml
Evidence:
  id: string
  kind: file_snapshot | diff | command_log | test_result | human_review | model_observation | provider_output | trace
  source_run_id: string
  source_event_id: string?
  scope: Scope
  content_ref: string
  hash: string?
  validity_hint: string?
  created_at: datetime
```

## Claim

```yaml
Claim:
  id: string
  kind: requirement | assumption | repo_fact | design_decision | test_oracle | risk | debugging_heuristic | user_preference
  statement: string
  scope: Scope
  evidence_ids: [string]
  status: proposed | accepted | trusted | stale | rejected | merged | quarantined
  version: integer
  introduced_by: string
  invalidation_rules: [string]
  created_at: datetime
  updated_at: datetime
```

## Proposal

```yaml
Proposal:
  id: string
  proposal_type: claim | skill_artifact | project_instruction | eval_check | demotion | staleness_mark
  payload_ref: string
  scope: Scope
  evidence_ids: [string]
  expected_future_effect: string
  risk: low | medium | high
  proposed_by: user | model | tool | hook | provider | background_worker
  created_from_run_id: string
  status: open | accepted | rejected | needs_review | superseded
```

## PromotionDecision

```yaml
PromotionDecision:
  id: string
  proposal_id: string
  decision: accept | trust | reject | stale | quarantine | request_more_evidence
  decided_by: user | policy | eval | reviewer | system
  reason: string
  evidence_ids: [string]
  eval_results: [string]
  resulting_trust_state: string
  created_at: datetime
```

## ArtifactManifestEntry

```yaml
ArtifactManifestEntry:
  id: string
  kind: skill
  name: string
  version: integer
  scope: Scope
  trust_state: proposed | accepted | trusted | stale | rejected | merged | quarantined
  evidence_ids: [string]
  promotion_decision_id: string?
  activation_conditions: [string]
  dependencies: [string]
  incompatibilities: [string]
  allowed_side_effects: [string]
  render_targets: [string]
  demotion_rules: [string]
```

## SkillArtifact

```yaml
SkillArtifact:
  manifest_id: string
  trigger_conditions: [string]
  procedure_markdown: string
  required_context: [string]
  verification_commands: [string]
  pitfalls: [string]
  examples: [string]
```

## Projection

```yaml
Projection:
  id: string
  run_id: string
  target: prompt_block | AGENTS.md | CLAUDE.md | skill_file
  included_claim_ids: [string]
  included_artifact_ids: [string]
  excluded_relevant_items: [string]
  reason: string
  content_ref: string
  created_at: datetime
```

## DemotionDecision

```yaml
DemotionDecision:
  id: string
  target_type: claim | artifact | projection
  target_id: string
  reason: string
  regression_evidence_ids: [string]
  attribution_confidence: low | medium | high
  new_trust_state: accepted | stale | quarantined | rejected
  created_at: datetime
```

## Scope

```yaml
Scope:
  level: global | user | org | repo | branch | module | file | symbol | task
  repo_root: string?
  branch: string?
  commit_sha: string?
  path: string?
  symbol: string?
  user_id: string?
  org_id: string?
```
