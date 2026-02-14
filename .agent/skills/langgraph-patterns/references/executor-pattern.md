# Executor Node Pattern

## Tool Registry

```python
TOOL_REGISTRY: dict[str, callable] = {
    "query_stock_price": query_stock_price_tool,
    "query_tech_indicator": query_tech_indicator_tool,
    "analyze_tech_signal": analyze_tech_signal_tool,
    "query_financial_data": query_financial_data_tool,
    "search_news": search_news_tool,
    "text_to_sql": text_to_sql_tool,
}
```

## Layer-by-Layer Parallel Execution

The executor processes tasks in topological layers. Tasks within the same layer run in parallel via `asyncio.gather`.

```python
async def executor_node(state: AgentState) -> dict:
    plan = state.get("plan")
    tool_results = dict(state.get("tool_results", {}))

    if not plan:
        # Simple query — single tool call
        tool_name = state["intent"].suggested_tools[0]
        tool_fn = TOOL_REGISTRY[tool_name]
        result = await tool_fn(state)
        tool_results["direct"] = result
        return {"tool_results": tool_results}

    # Execute tasks layer by layer
    for layer_idx, layer_task_ids in enumerate(plan.execution_order):
        if layer_idx < state.get("current_layer", 0):
            continue  # Skip completed layers

        ready_tasks = [
            t for t in plan.tasks
            if t.task_id in layer_task_ids and t.status == TaskStatus.PENDING
        ]

        # SSE status push
        if state.get("status_callback"):
            await state["status_callback"]({
                "type": "status",
                "status": "retrieving",
                "steps": [{"task_id": t.task_id, "tool": t.tool_name} for t in ready_tasks],
            })

        # Parallel execution within layer
        async def run_task(task: SubTask):
            tool_fn = TOOL_REGISTRY.get(task.tool_name)
            if not tool_fn:
                task.status = TaskStatus.FAILED
                task.error = f"Unknown tool: {task.tool_name}"
                return
            try:
                task.status = TaskStatus.RUNNING
                result = await asyncio.wait_for(
                    tool_fn(state, **task.tool_params),
                    timeout=get_settings().TOOL_TIMEOUT_SECONDS,
                )
                task.status = TaskStatus.COMPLETED
                task.result = result
                tool_results[task.task_id] = result
            except asyncio.TimeoutError:
                task.status = TaskStatus.FAILED
                task.error = "Tool execution timeout"
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)

        await asyncio.gather(*[run_task(t) for t in ready_tasks])

    return {
        "tool_results": tool_results,
        "current_layer": len(plan.execution_order),
        "plan": plan,
    }
```

## Adding a New Tool

1. Create `stock_agent/tools/{tool_name}.py`
2. Define `{ToolName}Params(BaseModel)` and `{ToolName}Result(BaseModel)`
3. Implement `async def {tool_name}_tool(state: AgentState, **kwargs) -> {ToolName}Result`
4. Register in `TOOL_REGISTRY` dict
5. Add tests in `tests/test_tools/test_{tool_name}.py`
