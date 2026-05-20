# Plandex Dossier

## Source status

Included as `02_repos/plandex-main.zip`; source-inspectable.

## Exact files/modules to inspect first

```text
app/shared/data_models.go
app/shared/plan_config.go
app/shared/context.go
app/shared/plan_result*.go
app/cli/lib/rewind.go
app/cli/api/methods.go
app/server/db/*plan*
app/server/db/*context*
```

## Candidate components to take

- plan/apply/reject/rewind model;
- branch/task state;
- context-by-path representation;
- plan-result and apply-result discipline;
- rollback/recovery patterns.

## Components to avoid

- treating plan state as epistemic truth;
- adopting SaaS/product flows irrelevant to Nova governance.

## Nova multiplier

Plandex-style plans become claim-bearing plans: requirement claim → design claim → implementation evidence → promotion/demotion.

## Recommendation

Imitate or port plan/apply/rewind logic; use as model for rollback and staged work.
