# Final Document Map

This is the revised document list for the next Nova research pass.

```text
nova-final-research-pack/
  00_README.md
  01_research_brief.md
  01_document_map.md
  02_revision_notes.md
  03_minimal_concept.md
  04_vendor_adoption_map.md
  05_mvp_and_target_shape.md
  06_stage_plan_evals_cutoffs.md
  07_benchmark_design.md
  08_integration_contracts.md
  09_data_model_kernel.md
  10_kill_criteria.md
  11_risks_and_abstraction_errors.md

  01_project_thesis/
    hermes_fork_thesis.md
    substrate_runtime_claims.md
    concerns_and_kill_criteria.md
    founding_doubts.md
    previous_deep_research_summaries/
      1.md
      2.md
      3.md
      4.md
      5.md

  02_repos/
    aider-main.zip
    claude-code-main.zip
    codex-main.zip
    crush-main.zip
    hermes-agent-main.zip
    langgraph-main.zip
    open-swe-main.zip
    OpenHands-main.zip
    plandex-main.zip

  03_appendices/
    source_manifest_patch.md
    license_and_reuse_notes.md
    terminology.md
    research_output_template.md

  04_manifest/
    source_manifest.md
    what_to_ignore.md

  05_vendor_dossiers/
    aider.md
    openhands.md
    codex_cli.md
    hermes.md
    plandex.md
    langgraph.md
    open_swe.md
    swe_agent.md
    crush_opencode.md
    claude_code_docs_baseline.md
```

## Required sections in the final Deep Research output

1. **Executive verdict** — one decision, not a vague “promising” judgment.
2. **Minimal concept specification** — define Nova’s smallest coherent form.
3. **Vendor/open-source adoption map** — what to adopt/fork/port/imitate/avoid.
4. **First primitives to take** — ranked by value, risk, and fit to governance.
5. **MVP shape** — buildable scope and explicit exclusions.
6. **Target shape** — post-MVP only, conditional on evidence.
7. **Stage plan, evals, and cutoffs** — thresholds and shrink decisions.
8. **Benchmark design** — repeated high-context work with stale-state tests.
9. **Integration contracts** — imported components may propose, not trust.
10. **Data model kernel** — minimal schemas only.
11. **Risk and abstraction mistakes** — adversarial register.
12. **Final recommendation** — choose one of: full substrate runtime, minimal governed promotion layer, ledger/claims only, adopt existing framework and add governance, defer thesis, abandon for now.

## Recommended vendor dossiers

Each dossier should answer:

```text
# System

## Source status
source-verified / docs-verified / partial / missing

## License and reuse status

## Mature primitives

## Exact source files/modules to inspect

## Candidate components to adopt/fork/port/imitate

## Components to avoid

## What the system already solves

## What it does not solve

## Does it implement governed future influence?
equivalent / partial / adjacent / no

## Nova multiplier
How Nova turns this primitive into governed future influence.

## Recommendation
take / fork / port / imitate / benchmark-only / avoid
```
