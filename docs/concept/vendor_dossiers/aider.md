# aider Dossier

## Source status

Included as `02_repos/aider-main.zip`; source-inspectable.

## Exact files/modules to inspect first

```text
aider/repomap.py
aider/repo.py
aider/commands.py
aider/coders/base_coder.py
aider/coders/context_coder.py
benchmark/
tests/basic/test_repomap.py
```

## Candidate components to take

- repo map/context ranking;
- git/diff/commit discipline;
- `/undo` and safe revert habits;
- benchmark harness patterns;
- practical terminal coding ergonomics.

## Components to avoid

- treating repo map output as learning;
- importing chat flow wholesale if Nova only needs context/evidence primitives.

## Nova multiplier

Repo map output becomes evidence-linked context and claim anchors. Git diffs become evidence for implementation claims and rollback.

## Recommendation

Port or wrap repo map and git discipline early.
