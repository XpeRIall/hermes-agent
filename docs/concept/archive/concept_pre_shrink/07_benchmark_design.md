# Benchmark Design

## Goal

Test whether governed future influence improves repeated high-context software work more than it adds overhead.

## Hypothesis to falsify

> In repeated high-context repository tasks, a governed promotion layer with typed claims and one promoted reusable artifact reduces repeated mistakes and debug time more than strong retrieval, traces, checkpoints, and ordinary skills alone.

## Required comparison arms

```text
A. baseline agent with normal retrieval/context/checkpoints
B. ledger + typed claims
C. ledger + typed claims + promotion gate
D. ledger + typed claims + one promoted SkillArtifact
E. optional: projection seam / context projector
```

## Task-chain shape

Each benchmark chain should include:

1. repo onboarding or architecture discovery;
2. first implementation/fix requiring a hidden repo convention;
3. second related task where the convention recurs;
4. refactor or migration touching the same abstraction;
5. deliberate requirement/code change that makes one earlier claim stale;
6. later task where stale state would harm output;
7. demotion/recovery test.

## Repos

Use multiple repositories with different languages and build/test systems. Each chain should expose at least one recurring latent convention:

- build command quirk;
- test harness pattern;
- migration convention;
- naming/routing pattern;
- state-management invariant;
- dependency constraint;
- security/permission convention;
- generated-code rule.

## Metrics

| Metric | Definition |
|---|---|
| quality | hidden tests, static checks, human rubric |
| repeated-error reduction | fewer repeats of known mistake class after first evidence |
| debug time | turns/time/commands from failure to passing state |
| rework | repeated edits caused by misunderstood convention |
| overhead | tokens, time, review actions, proposal maintenance |
| reuse | promoted item helps later related task |
| demotion usefulness | removing bad item improves next run |
| regression attribution | system identifies bad claim/artifact/projection |
| activation specificity | relevant items included, irrelevant excluded |
| context pollution | stale/unsupported/mixed-trust context in prompt |
| review burden | human time spent approving/rejecting proposals |

## Required stale-state test

Every benchmark suite must include seeded invalidation.

Example:

```text
Task 1 discovers: tests must be run with command X.
Task 3 changes repo so command X is obsolete.
Task 4 checks whether system marks old claim stale and stops projecting it.
Task 5 seeds a bad SkillArtifact and verifies demotion.
```

Without stale-state tests, the benchmark only rewards accumulation and will overstate the thesis.

## Evaluation outputs

Each run should produce:

- run ledger;
- evidence bundle;
- claim/proposal diff;
- promoted artifacts activated;
- projected context bundle;
- final code diff;
- test/log outputs;
- demotion decisions;
- regression-attribution report.

## Minimum success threshold

A successful MVP benchmark should show at least:

- >= 20% repeated-error reduction over baseline;
- >= 15% median debug-time reduction over baseline;
- overhead <= 15% of tokens/time;
- correct seeded-regression attribution >= 70%;
- bad artifact demotion improves subsequent run >= 70%;
- projection or artifact activation is not effectively static.

If these fail, shrink the architecture.
