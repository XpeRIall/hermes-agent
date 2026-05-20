# Nova Concept Index

This directory contains the research inputs for Nova / Hermes Fork.

## Source precedence

Codex must use this precedence order:

1. `docs/concept/INDEX.md`
2. `docs/concept/manifest/what_to_ignore.md`
3. `docs/concept/manifest/source_manifest.md`
4. `docs/concept/manifest/source_manifest_patch.md`
5. Current canonical synthesis docs:
   - `00_research_brief.md`
   - `01_minimal_concept.md`
   - `02_vendor_adoption_map.md`
   - `03_first_primitives_to_take.md`
   - `04_mvp_shape.md`
   - `05_target_shape.md`
   - `06_stage_plan_evals_cutoffs.md`
   - `07_benchmark_design.md`
   - `08_integration_contracts.md`
   - `09_data_model_kernel.md`
   - `10_kill_criteria.md`
   - `11_risks_and_abstraction_errors.md`
   - `12_source_inspection_ledger.md`
   - `13_vendor_dossiers.md`
6. `project_thesis/` files as supporting thesis context.
7. `vendor_dossiers/` files as detailed comparator evidence.
8. `archive/concept_pre_shrink/` as historical material only.

## Canonical reading order

Read these first and treat them as the current research synthesis:

1. `00_research_brief.md`
2. `01_minimal_concept.md`
3. `04_mvp_shape.md`
4. `05_target_shape.md`
5. `08_integration_contracts.md`
6. `09_data_model_kernel.md`
7. `06_stage_plan_evals_cutoffs.md`
8. `07_benchmark_design.md`
9. `10_kill_criteria.md`
10. `11_risks_and_abstraction_errors.md`
11. `02_vendor_adoption_map.md`
12. `03_first_primitives_to_take.md`
13. `12_source_inspection_ledger.md`
14. `13_vendor_dossiers.md`

## Archive rule

Do not cite or rely on `archive/concept_pre_shrink/` as primary evidence unless:
- a current canonical doc is ambiguous;
- the archive is needed to explain how the concept changed;
- the output explicitly labels the archive evidence as historical.

## Vendor dossier rule

Use `13_vendor_dossiers.md` for the summary position.
Use `vendor_dossiers/*.md` only when detailed comparator evidence is needed.

## Research conclusion to preserve

The defensible Nova thesis is narrow:

Nova is a governed promotion kernel for future-affecting reusable agent state.

It is not:
- a new agent runtime;
- a generic memory system;
- a sandbox;
- a workflow DAG;
- a broad self-modification platform.

The first implementation path should remain kernel-first:
- run ledger;
- evidence bundle model;
- typed claim/state skeleton;
- append-only transition model;
- basic policy gate.