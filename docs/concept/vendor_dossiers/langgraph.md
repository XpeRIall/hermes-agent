# LangGraph Dossier

## Source status

Included as `02_repos/langgraph-main.zip`; source-inspectable.

## License and reuse status

MIT in the uploaded snapshot. Still perform normal license review before direct reuse.

## Exact files/modules to inspect first

```text
libs/langgraph/langgraph/graph/state.py
libs/langgraph/langgraph/pregel/
libs/langgraph/langgraph/runtime.py
libs/checkpoint/langgraph/checkpoint/
libs/checkpoint-postgres/langgraph/checkpoint/postgres/
libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/
libs/prebuilt/langgraph/prebuilt/
libs/cli/langgraph_cli/
```

## Candidate components to inspect
- durable execution;
- checkpoints;
- state graph;
- human-in-the-loop interrupts;
- memory/persistence primitives;
- replay/time travel;
- tracing.

## Candidate use

Use LangGraph as workflow/orchestration infrastructure only if Nova needs durable multi-step workflows.

## Components to avoid

- using graph workflow state as epistemic truth;
- importing a whole framework before the minimal kernel proves value.

## Nova multiplier

LangGraph checkpoints could manage workflow resume/replay while Nova owns claims, evidence, promotion, and demotion.

## Recommendation

Use as an optional orchestration/checkpointing candidate if Nova needs durable multi-step workflow infrastructure. Do not add to source pack; it is already included. Do not treat workflow state as epistemic truth.