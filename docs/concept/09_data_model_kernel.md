A workable kernel needs surprisingly little schema.

| Object | Required fields | Why it exists |
|---|---|---|
| Artifact | `id`, `type`, `scope`, `activation_rule`, `trust_state`, `current_version` | Governs future influence |
| ArtifactVersion | `artifact_id`, `version`, `payload`, `created_from`, `evidence_bundle_id` | Versioned reusable content |
| EvidenceBundle | `run_id`, `message_refs`, `file_refs`, `command_refs`, `check_refs`, `retrieval_refs` | Makes proposals auditable |
| GateDecision | `proposal_id`, `gate_type`, `result`, `reviewer_or_eval_id` | Separates generation from trust |
| ActivationRecord | `run_id`, `artifact_version_ids` | Enables blame and replay |
| RegressionRecord | `artifact_id`, `run_id`, `symptom`, `linked_checks` | Enables demotion and attribution |

The most important modeling choice is to make **evidence first-class** rather than burying it in prose. That is **`inferred`** but load-bearing.