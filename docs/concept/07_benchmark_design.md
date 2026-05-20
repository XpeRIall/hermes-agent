Nova’s benchmark must be longitudinal and counterfactual, not just task-success-at-time-zero.

The benchmark should answer:

> Does governed promotion improve later runs more reliably than ordinary memory/skills/instructions alone?

A credible design has four arms:

| Arm | Description | Why |
|---|---|---|
| Baseline host | Hermes without Nova proposals/promotions | Control |
| Adjacent only | Hermes with ordinary memory/skills/instructions enabled | Adversarial counterfactual |
| Nova staged | Hermes with proposals recorded but not activated | Is proposal overhead itself useful? |
| Nova active | Hermes with promoted artifacts activated | Real treatment arm |

Use repeated tasks on the same repos over time, not one-shot benchmarks only.

Recommended benchmark families:
- repeated bug-fix classes in one repo
- repeated style / instruction-sensitive tasks
- repeated environment/setup repair classes
- repeated code-review / check-enforcement classes

Metrics that matter:
- later-run task success
- regression rate after activation
- artifact survival rate before demotion
- reviewer time per accepted artifact
- blame precision when regressions occur
- delta over ordinary memory/skills baseline

Helpful donor benchmark sources:
- aider benchmark harnesses for coding-task discipline. **`source-verified`**
- mini-SWE-agent / SWE-bench style repeated task runners. **`source-verified`**
- Open SWE reviewer eval structure for artifact-grade evaluation. **`source-verified`**