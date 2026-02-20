---
name: "pydanticai-langgraph-agent"
description: "Build PydanticAI + LangGraph agent graphs (state, nodes, fan-out, streaming, interrupts). Invoke when creating or refactoring an agent workflow using these libraries."
---

# PydanticAI + LangGraph Agent Builder

当用户希望用 **PydanticAI + LangGraph** 搭建/扩展一个多节点（可并行）Agent 工作流时，按以下流程执行，并尽量复用目标项目已有的约定与代码模式。

## 对齐目标项目的现有模式

先快速扫描目标项目，找出等价物并对齐风格：

- “Graph 编排入口”：通常包含 `StateGraph`、节点注册、路由/条件边、compile、run/ainvoke
- “Agent 定义模块”：通常包含 `Agent(...)`、`deps_type`、`result_type`、`@agent.tool`
- “模型/配置入口”：例如 `get_model()`、provider 初始化、环境变量加载

如果目标项目没有现成结构，就按本文的默认目录与命名建议创建最小可运行骨架。

## 典型架构（强约束）

### 1) 定义 LangGraph State（TypedDict）

- 使用 `TypedDict` 定义全局状态，包含：
  - `user_input: str`
  - `messages: Annotated[List[bytes], reducer]`（用于保存 PydanticAI message json，reducer 通常是拼接）
  - 领域结构化信息（如 `travel_details: Dict[str, Any]`）
  - 各子 Agent 的中间结果字段（string 或结构化 dict）
  - 最终汇总字段（例如 `final_plan: str`）

示例形态（按需改名与字段）：

```python
from typing import Annotated, Any, Dict, List
from typing_extensions import TypedDict

class DomainState(TypedDict):
    user_input: str
    messages: Annotated[List[bytes], lambda x, y: x + y]
    domain_details: Dict[str, Any]
    subtask_a_result: str
    subtask_b_result: str
    final_answer: str
```

### 2) 把 PydanticAI Agent 作为 LangGraph Node 执行单元

每个 node 尽量保持“纯函数形态”：

- 输入：`state`
- 输出：只返回要更新的字段 dict（不要返回整个 state）
- 支持 streaming 的 node 接收 `writer`，把增量输出写出去

PydanticAI 常见用法：

- 结构化抽取/补全：`Agent(..., result_type=SomePydanticModel)`
- 需要上下文依赖：`deps_type=SomeDataclassDeps` + `run(..., deps=...)`
- 需要 tool：`@agent.tool` 定义工具函数

当需要“边生成边显示”时：

- `async with agent.run_stream(...) as result:`
- 文本流：`result.stream_text(delta=True)`
- 结构化流：`result.stream_structured(...)` + `result.validate_structured_result(..., allow_partial=...)`
- 把 `result.new_messages_json()` 写入 `messages`，用于后续轮次上下文

### 3) 用 LangGraph 做路由与并行 fan-out

典型流程：

- 先运行一个“信息收集/意图解析”节点，决定是否需要用户补充信息
- 若信息不全：通过 `interrupt({})` 暂停图，拿到下一轮用户输入，再回到信息收集节点
- 若信息已全：路由函数返回一个 node name 列表，让多个推荐/检索节点并行执行

示例路由函数：

```python
def route_after_gather(state: DomainState):
    details = state["domain_details"]
    if not details.get("all_details_given", False):
        return "get_next_user_message"
    return ["subtask_a", "subtask_b"]
```

### 4) 使用 MemorySaver 作为 checkpointer

- `MemorySaver()` 适合本地/示例运行
- 编译：`graph.compile(checkpointer=memory)`

### 5) 提供一个 async run_* 入口

- 组装 `initial_state`（必须包含 TypedDict 的必需字段）
- `await graph.ainvoke(initial_state)`
- 返回最终字段（如 `final_answer`）

## 交付物清单（每次实现都要具备）

- 1 个或多个 PydanticAI 子 Agent 模块（至少：信息收集/规划汇总；可选：多个并行子任务 Agent）
- 1 个 LangGraph 编排模块（State、nodes、edges、compile、运行入口）
- 1 个可运行入口（CLI/UI/脚本均可），能触发一次端到端执行

## 实施步骤（执行顺序）

1. 先实现 PydanticAI Agent（放在项目已有的 agent 模块目录；没有就新建如 `agents/`）：
   - 明确 system prompt、输入/输出类型（是否结构化）、deps/tool（如需要）
2. 在图文件中定义 `TypedDict` State，并实现 node 函数：
   - 信息收集 node：写入 `domain_details` + 追加 `messages`
   - 并行子任务 nodes：写入各自结果字段
   - 汇总 node：把所有结果整合成 `final_answer`（可用 streaming）
3. 用 `StateGraph` 串起来：
   - `START -> gather`
   - `gather -> conditional edges`（需要用户补充 vs. 并行 fan-out）
   - 并行节点都连到汇总节点
   - 汇总节点到 `END` 或根据交互模式回到 `get_next_user_message`
4. 本地跑通一次示例输入，确保无 import/类型错误，并确保 streaming/interrupt 行为符合预期

## 常见坑（通用规避）

- 如果你把 message history 持久化为 `result.new_messages_json()`（bytes），下一次调用前要用 `ModelMessagesTypeAdapter.validate_json(...)` 还原为 `ModelMessage` 列表
- node 返回值要与 State 的字段类型一致（例如 `flight_results` 在 state 里定义成 `str` 就不要初始化成 `[]`）
- 条件路由返回 list 时会 fan-out，并行节点要能独立运行（不要互相依赖同一字段的写入顺序）
