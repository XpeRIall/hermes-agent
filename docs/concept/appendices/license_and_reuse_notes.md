# License and Reuse Notes

This is not legal advice. It is a research checklist.

## Uploaded-pack license signals

- `aider-main/LICENSE.txt`: Apache-2.0.
- `codex-main/LICENSE`: Apache-2.0.
- `hermes-agent-main/LICENSE`: MIT.
- `plandex-main/LICENSE`: MIT.
- `OpenHands-main/LICENSE`: MIT for non-enterprise content; enterprise directory has separate licensing.
- `crush-main/LICENSE.md`: FSL-1.1-MIT in uploaded pack; treat as imitate/design-reference until reviewed.
- `claude-code-main/LICENSE.md`: Anthropic commercial terms; use as docs/examples baseline, not reusable implementation source.
- `langgraph-main/LICENSE`: MIT.
- `open-swe-main/LICENSE`: MIT; this is Open SWE, not SWE-agent.

## Reuse categories

```text
direct adopt  = copy/import code with license compatibility and low coupling
fork          = maintain modified codebase or module
port          = reimplement algorithm/module in Nova language/style
imitate       = copy invariant/design, not code
benchmark     = use as comparison target only
avoid         = do not depend on or copy
```

## Rule

Do not let licensing convenience override architectural fit. The best primitive is the one that feeds the ledger/evidence/proposal/promotion loop with minimal hidden trust semantics.
