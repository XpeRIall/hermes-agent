# Open SWE Dossier

## Source status

Included as `02_repos/open-swe-main.zip`; source-inspectable.

This is Open SWE from LangChain, not SWE-agent proper.

## License and reuse status

MIT in the uploaded snapshot. Still perform normal license review before direct reuse.

## Exact files/modules to inspect first

```text
README.md
AGENTS.md
langgraph.json
agent/server.py
agent/prompt.py
agent/utils/sandbox.py
agent/utils/sandbox_state.py
agent/integrations/
agent/middleware/
agent/tools/
agent/reviewer.py
agent/reviewer_diff.py
agent/reviewer_findings.py
agent/reviewer_publish.py
evals/reviewer/
tests/
```

## Candidate components to adopt/fork/port/imitate
- LangGraph/Deep Agents coding-agent harness;
- per-thread sandbox lifecycle;
- Slack/Linear/GitHub invocation routing;
- curated tool surface;
- middleware ordering discipline;
- reviewer/eval structure;
- PR/comment workflow patterns.

## Components to avoid
- treating Open SWE as SWE-agent;
- treating coding-agent task success as governed future influence;
- importing cloud-sandbox/provider assumptions before the Nova kernel proves value;
- letting Slack/Linear/GitHub workflow concerns dominate the MVP.

## What the system already solves

Open SWE is useful as a reference for coding-agent harness architecture: task invocation, sandbox creation/reconnection, middleware, curated tools, reviewer flows, and LangGraph app wiring.

## What it does not solve

It does not by itself establish Nova’s core invariant: evidence-bound promotion, trust states, scoped future activation, demotion, and regression attribution for future-affecting writes.

## Does it implement governed future influence?

adjacent

## Nova multiplier

Open SWE run outputs, tool calls, reviewer findings, sandbox events, and PR/comment artifacts can become Nova evidence. Its harness can act as an executor surface, while Nova owns claims, proposals, promotion, activation, and demotion.

## Recommendation

Imitate/adapt harness patterns; benchmark as executor candidate. Do not treat as SWE-agent.