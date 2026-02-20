---
name: langgraph-patterns
description: LangGraph development patterns and templates for the Stock AI Agent project. Use when building StateGraph definitions, creating agent nodes (intent/planner/executor/synthesizer/responder), defining conditional edges and routing logic, implementing parallel task execution in executor nodes, or integrating SSE status callbacks into LangGraph workflows. Triggers on any LangGraph state management, node function, graph construction, or agent orchestration task.
---

# LangGraph Development Patterns

## Project Architecture Overview

The Stock AI Agent uses a 5-node LangGraph StateGraph:

```
intent → [planner] → executor → [result_check] → synthesizer → responder → END
           ↑                         │
           └─── (needs_more_data) ───┘
```

- `intent`: Intent classification + entity extraction + stock resolution
- `planner`: Decompose complex queries into sub-tasks (conditional)
- `executor`: Run tools (parallel within layers, sequential across layers)
- `synthesizer`: LLM-powered analysis of tool results
- `responder`: Format final response + risk disclaimer

## AgentState Definition

```python
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    session_id: str
    user_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    intent: IntentClassification | None
    entities: ExtractedEntities | None
    resolved_stocks: list[StockEntity]
    plan: DecompositionPlan | None
    current_layer: int
    tool_results: dict[str, Any]
    status_callback: Any  # async callable for SSE
    analysis_result: str
    data_sources: list[str]
    risk_disclaimer: str
```

**Key rules**:
- Use `Annotated[list[BaseMessage], add_messages]` for message accumulation
- All node return dicts are **partial updates** — only include changed keys
- `status_callback` is an async callable injected by the API layer for SSE

## Node Function Template

Every node follows this pattern:

```python
async def node_name(state: AgentState) -> dict:
    """Node docstring describing purpose."""
    # 1. Read from state
    user_message = state["messages"][-1].content

    # 2. Do work (LLM call, DB query, tool execution)
    result = await some_operation(...)

    # 3. Push SSE status (optional)
    if state.get("status_callback"):
        await state["status_callback"]({"type": "status", "status": "processing"})

    # 4. Return partial state update
    return {"key": result}
```

**File organization**: Each node in `agent/nodes/{name}.py`, single async function per file.

## Graph Construction

```python
from langgraph.graph import StateGraph, END

def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("intent", intent_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("result_check", lambda s: s)  # passthrough
    graph.add_node("synthesizer", synthesizer_node)
    graph.add_node("responder", responder_node)

    # Entry point
    graph.set_entry_point("intent")

    # Conditional routing
    graph.add_conditional_edges("intent", should_decompose, {
        "planner": "planner",
        "executor": "executor",
    })
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "result_check")
    graph.add_conditional_edges("result_check", needs_more_data, {
        "executor": "executor",
        "synthesizer": "synthesizer",
    })
    graph.add_edge("synthesizer", "responder")
    graph.add_edge("responder", END)

    return graph.compile()
```

## Conditional Edge Functions

Return a **string literal** matching one of the edge targets:

```python
def should_decompose(state: AgentState) -> str:
    if state["intent"] and state["intent"].requires_decomposition:
        return "planner"
    return "executor"

def needs_more_data(state: AgentState) -> str:
    plan = state.get("plan")
    if plan:
        incomplete = [t for t in plan.tasks if t.status == "pending"]
        if incomplete:
            return "executor"
    return "synthesizer"
```

## Executor Parallel Execution Pattern

For details on the executor's layer-by-layer parallel execution with `asyncio.gather`, tool registry, and error handling, see [references/executor-pattern.md](references/executor-pattern.md).

## Reference Files

- **[references/executor-pattern.md](references/executor-pattern.md)**: Complete executor node implementation with TOOL_REGISTRY, parallel task execution, timeout handling, and SSE status callbacks
- **[references/state-models.md](references/state-models.md)**: All Pydantic models used in AgentState (IntentClassification, ExtractedEntities, SubTask, DecompositionPlan, etc.)
