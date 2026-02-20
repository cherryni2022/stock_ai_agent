# Stock AI Agent — 任务进度跟踪

> **最后更新**: 2026-02-20
>
> **对应计划**: [开发计划](./plan.md)

---

## Phase 0: 项目骨架与基础设施

### 0.1 项目初始化
- [x] **0.1.1** 创建 `pyproject.toml`，声明所有依赖 → `pyproject.toml`
- [x] **0.1.2** 创建项目目录结构 → `stock_agent/` 全部 `__init__.py` 就位
- [x] **0.1.3** 配置 `ruff` / `mypy` / `pytest` → `pyproject.toml [tool.*]`
- [x] **0.1.4** 创建 `.env.example` 模板 → `.env.example`

### 0.2 配置管理
- [x] **0.2.1** 实现 `Settings` 类 (pydantic-settings) → `config/settings.py`
- [x] **0.2.2** 实现 `@lru_cache` 的 `get_settings()` 工厂 → `config/settings.py`
- [x] **0.2.3** `.env.example` 注释所有配置项 → `.env.example`

> ✅ **Phase 0 完成**: 2026-02-15

---

## Phase 1: 数据层 — 结构化数据

### 1.1 数据库 Schema、模型与 Repository
- [x] **1.1.1** 创建 SQLAlchemy `Base` 和 `async_session` 工厂 → `database/base.py`, `database/session.py`
- [x] **1.1.2** 迁移 A 股数据模型 (11 表) → `database/models/stock.py`
- [x] **1.1.3** 迁移港股数据模型 (11 表) → `database/models/stock_hk.py`
- [x] **1.1.4** 迁移美股数据模型 (11 表) → `database/models/stock_us.py`
- [x] **1.1.5** 创建向量嵌入表 (3 张) → `database/models/vector.py`
- [x] **1.1.6** 创建用户/会话/日志表 → `database/models/user.py`, `database/models/agent_log.py`
- [x] **1.1.7** 创建可观测性日志表 (llm_call_logs / tool_call_logs) → `database/models/`
- [x] **1.1.8** 实现 `LogRepository` + 通用写入接口 → `database/repositories/log.py`
- [x] **1.1.9** 验证全部表在 Supabase 中创建成功 → **37 张表确认** ✅
- [x] **1.1.10** 实现 Repository 基类 + `StockRepository` → `database/repositories/base.py`, `stock.py`
- [x] **1.1.11** 实现 `VectorRepository` + `UserRepository` → `database/repositories/vector.py`, `user.py`

> ✅ **Phase 1.1 完成**: 2026-02-20

### 1.2 数据获取管道
- [x] **1.2.1** A 股日 K 线获取 (akshare) → `data_pipeline/akshare_fetcher.py`
- [x] **1.2.2** 港股日 K 线获取 (yfinance) → `data_pipeline/yfinance_fetcher.py`
- [x] **1.2.3** 美股日 K 线获取 (yfinance) → `data_pipeline/yfinance_fetcher.py`
- [x] **1.2.4** A 股基本信息 / 公司信息获取 → `data_pipeline/akshare_fetcher.py`
- [x] **1.2.5** 港股/美股基本信息获取 → `data_pipeline/yfinance_fetcher.py`
- [x] **1.2.6** 财务数据获取 (akshare + yfinance) → `data_pipeline/financial_fetcher.py`

> ✅ **Phase 1.2 完成**: 2026-02-15

### 1.3 技术指标计算
- [x] **1.3.1** 实现指标计算引擎 (pandas + ta-lib + scipy) → `data_pipeline/indicator_calculator.py`
- [x] **1.3.2** 计算 MACD / RSI / KDJ / 布林带 / 均线 → `indicator_calculator.py`
- [x] **1.3.3** 计算 5 类策略信号 → `indicator_calculator.py`
- [x] **1.3.4** 全市场指标计算验证 ← *已运行 `run_pipeline` 并验证各表数据完整*

> ✅ **Phase 1.3 完成**: 2026-02-15

---

## Phase 2: 向量层 — Embedding & RAG

### 2.1 Embedding 服务 (3 天)
- [x] **2.1.1** 实现 `EmbeddingProvider` 抽象接口 → `services/embedding.py`
- [x] **2.1.2** 实现 `OpenAIEmbedding` + `GeminiEmbedding` + `ZhipuEmbedding` 三个实现（MVP 测试默认不启用 Zhipu Embedding）→ `services/embedding.py`
- [x] **2.1.3** 实现 `create_embedding_provider()` 工厂函数 (按 env 切换) → `services/embedding.py`
- [x] **2.1.4** 单元测试: 向量维度 / 批量 embed / 异常处理 → `tests/unit/test_embedding.py`

### 2.2 新闻获取 & 向量化 (4 天)
- [x] **2.2.1** A 股新闻获取 (akshare 个股新闻) → `data_pipeline/news_fetcher.py`
- [x] **2.2.2** 港股/美股新闻获取 (yfinance news) → `data_pipeline/news_fetcher.py`
- [x] **2.2.3** 实现文本分块 `chunk_text()` (~500 token/块, 50 token 重叠) → `data_pipeline/embedding_pipeline.py`
- [x] **2.2.4** 实现新闻向量化 pipeline: 分块 → Embedding → INSERT → `data_pipeline/embedding_pipeline.py`
- [x] **2.2.5** pgvector IVFFlat 索引创建 + 检索验证 → SQL migration

### 2.3 SQL 示例预生成 (3 天)
- [x] **2.3.1** 编写 6 类种子示例 (≥ 15 条) → `data_pipeline/sql_examples_seeder.py`
- [x] **2.3.2** 实现 `--seed-only` 模式: 种子 → Embedding → UPSERT → `data_pipeline/sql_examples_seeder.py`
- [x] **2.3.3** 实现 LLM 扩充模式: Prompt 设计 + JSON 解析 + 质量校验 → `data_pipeline/sql_examples_seeder.py`
- [x] **2.3.4** 实现语义去重 (Embedding 余弦相似度 > 0.92 剔除) → `data_pipeline/sql_examples_seeder.py`
- [ ] **2.3.5** 执行完整入库 (种子 + 扩充), 目标 50-80 条

### 2.4 RAG 检索服务
- [x] **2.4.1** 实现 `RAGService.search_news()` — 新闻向量检索 → `services/rag.py`
- [x] **2.4.2** 实现 `RAGService.search_sql_examples()` — SQL 示例检索 → `services/rag.py`
- [x] **2.4.3** 单元测试: 检索精度 / 过滤条件 / 空结果处理 → `tests/unit/test_rag.py`

> 🟦 **Phase 2 进行中**: 16/17 完成

---

## Phase 3: Agent 核心 — 意图理解 + 工具 + 图编排

### 3.1 LLM 服务层 (2 天)

> **分工**: 3.1.1~3.1.3 用于数据管道等非 Agent 场景；Agent 节点统一通过 3.1.4 的 PydanticAI Model 工厂，结构化输出和重试由 PydanticAI 原生处理。

- [x] **3.1.1** 实现 LLM Provider 抽象 + 工厂 (OpenAI / Gemini / Zhipu) — *数据管道 + 非 Agent 场景* → `services/llm.py`
- [x] **3.1.2** 实现 `structured_output()` — *数据管道专用*，手动 JSON Schema + Pydantic 校验 → `services/llm.py`
- [x] **3.1.3** 实现 `llm_call_with_retry()` — *数据管道专用*，tenacity 网络级重试 → `services/llm.py`
- [ ] **3.1.4** 实现 `create_pydantic_ai_model()` — **Agent 核心入口**，返回 PydanticAI Model 实例 + 默认 model settings → `services/llm.py`

### 3.2 Prompt 工程 (2 天)
- [ ] **3.2.1** 实现意图分类 Prompt (`INTENT_PROMPT`) → `agent/prompts/intent_prompt.py`
- [ ] **3.2.2** 实现实体提取 Prompt (`ENTITY_EXTRACTION_PROMPT`) → `agent/prompts/intent_prompt.py`
- [ ] **3.2.3** 实现综合分析 Prompt (`SYNTHESIS_PROMPT`) → `agent/prompts/synthesis_prompt.py`
- [ ] **3.2.4** 实现 Text-to-SQL Prompt + `build_few_shot_section()` → `agent/prompts/text_to_sql_prompt.py`
- [ ] **3.2.5** 实现计划生成 Prompt (`PLANNER_PROMPT`) → `agent/prompts/planner_prompt.py`

### 3.3 数据模型 & 状态定义 (1 天)
- [ ] **3.3.1** 定义 `AgentState` TypedDict（含 `user_input/messages_json/event_writer/execution_log_id`）→ `agent/state.py`
- [ ] **3.3.2** 定义 Pydantic 模型: IntentClassification, ExtractedEntities, DecompositionPlan, SynthesisOutput, FinalResponse, ExecutorOutput 等 → `agent/state.py`
- [ ] **3.3.3** 定义 `AgentDeps` dataclass（含 settings / db_session_factory / embedding_service / rag_service）→ `agent/state.py`

### 3.4 意图分类 & 实体提取节点 (4 天)
- [ ] **3.4.1** 实现 `intent_node()`（PydanticAI Agent: deps_type/output_type）→ `agent/nodes/intent.py`
- [ ] **3.4.2** 实现实体提取: 股票名称/代码/时间范围 → `agent/nodes/intent.py`
- [ ] **3.4.3** 实现 `StockResolver` — 股票名称模糊解析 + `TABLE_MAPPING` 市场表路由 + `get_table_name()` → `tools/stock_resolver.py`
- [ ] **3.4.4** 单元测试: 意图分类准确率 / 实体提取完整性（覆盖 6 大类）→ `tests/test_intent.py`

### 3.5 工具实现 (5 天)
- [ ] **3.5.1** `query_stock_price_tool` — 股票价格查询 → `tools/stock_price.py`
- [ ] **3.5.2** `query_tech_indicator_tool` — 技术指标查询 → `tools/tech_indicator.py`
- [ ] **3.5.3** `analyze_tech_signal_tool` — 策略信号查询 → `tools/tech_signal.py`
- [ ] **3.5.4** `query_financial_data_tool` — 财务数据查询 → `tools/financial_data.py`
- [ ] **3.5.5** `search_news_tool` — 新闻 RAG 语义检索 → `tools/news_search.py`
- [ ] **3.5.6** `text_to_sql_tool` — 自然语言 → SQL → 执行（市场感知：根据 market 使用对应 DDL）→ `tools/text_to_sql.py`
- [ ] **3.5.7** `validate_sql_safety()` — SQL 安全校验 (仅 SELECT) → `tools/text_to_sql.py`
- [ ] **3.5.8** 构建 `build_executor_agent()` — PydanticAI executor_agent，工具通过 `@executor_agent.tool` 注册 → `tools/__init__.py` 或 `agent/nodes/tools.py`
- [ ] **3.5.9** 工具级容错包装 `safe_tool_execute()` → `tools/base.py`
- [ ] **3.5.10** 单元测试: 每个工具独立测试 → `tests/test_tools/`

### 3.6 LangGraph 编排 & 综合分析 (4 天)
- [ ] **3.6.1** 实现 `planner_node()`（PydanticAI 输出 `DecompositionPlan`）→ `agent/nodes/planner.py`
- [ ] **3.6.2** 实现 `executor_node()` — 双模式执行（确定性/LLM驱动）+ DAG 拓扑并行 → `agent/nodes/executor.py`
- [ ] **3.6.3** 实现 `synthesizer_node()`（PydanticAI 输出 `SynthesisOutput`，可选 token streaming）→ `agent/nodes/synthesizer.py`
- [ ] **3.6.4** 实现 `responder_node()`（PydanticAI 输出 `FinalResponse`）→ `agent/nodes/responder.py`
- [ ] **3.6.5** 实现 `build_agent_graph()` — 组装 StateGraph, 条件路由 → `agent/graph.py`
- [ ] **3.6.6** 条件路由函数: `should_decompose()`, `needs_more_data()` → `agent/graph.py`
- [ ] **3.6.7** 集成测试: 端到端 Agent 调用 → `tests/test_agent.py`

> 🟦 **Phase 3 进行中**: 3/31 完成

---

## Phase 4: API 层 — FastAPI + SSE

### 4.1 聊天 API (4 天)
- [ ] **4.1.1** FastAPI App 入口 + CORS / 异常处理中间件 → `main.py`
- [ ] **4.1.2** `POST /api/chat` — SSE 流式推送 → `api/chat.py`
- [ ] **4.1.3** SSE 事件类型实现: status / step / token / result / [DONE] → `api/chat.py`
- [ ] **4.1.4** `event_writer` 注入 Agent: 各节点实时推送 status/step/token → `api/chat.py` + `agent/nodes/*.py`
- [ ] **4.1.5** SSE 事件关联 `execution_log_id` → `api/chat.py`

### 4.2 会话管理 API (2 天)
- [ ] **4.2.1** `GET /api/sessions` — 会话列表 → `api/session.py`
- [ ] **4.2.2** `GET /api/sessions/{id}` — 会话详情 + 消息历史 → `api/session.py`
- [ ] **4.2.3** `DELETE /api/sessions/{id}` — 归档会话 → `api/session.py`
- [ ] **4.2.4** API 层单元测试 → `tests/test_api.py`

> ⬜ **Phase 4 未开始**: 0/9 完成

---

## Phase 5: 前端 — Streamlit MVP

### 5.1 Streamlit 实现 (5 天)
- [ ] **5.1.1** 对话界面: 消息列表 + 输入框 + 发送按钮 → `frontend/app.py`
- [ ] **5.1.2** SSE 客户端: 消费 `/api/chat` 流式事件 → `frontend/app.py`
- [ ] **5.1.3** 进度状态展示: 分析中 → 获取数据 → 综合分析 → 完成 → `frontend/app.py`
- [ ] **5.1.4** 分析结果展示: Markdown 渲染、数据源引用、风险提示 → `frontend/app.py`
- [ ] **5.1.5** 会话管理: 侧边栏会话列表 / 新建 / 切换 → `frontend/app.py`
- [ ] **5.1.6** 错误提示 & 重试 → `frontend/app.py`

> ⬜ **Phase 5 未开始**: 0/6 完成

---

## Phase 6: 质量保障 & 部署

### 6.1 测试 (4 天)
- [ ] **6.1.1** 端到端集成测试: 6 类意图各 2 个用例 → `tests/test_e2e.py`
- [ ] **6.1.2** Text-to-SQL 精度测试: 预设问题 → 生成 SQL → 结果校验 → `tests/test_text_to_sql.py`
- [ ] **6.1.3** 意图分类准确率测试: 30 个测试问题 → `tests/test_intent_accuracy.py`
- [ ] **6.1.4** 工具容错测试: 模拟超时/异常/空数据 → `tests/test_error_handling.py`
- [ ] **6.1.5** 性能基准: 单轮对话延迟 < 15s → `tests/test_performance.py`

### 6.2 错误处理 (1 天)
- [ ] **6.2.1** 定义全局异常层级: `AgentExecutionError` / `ToolExecutionError` / `LLMProviderError` → `exceptions.py`
- [ ] **6.2.2** API 层全局异常处理中间件 → `main.py`

### 6.3 可观测性 & 部署 (2 天)
- [ ] **6.3.1** 结构化日志 (structlog): 每步输出 JSON 日志 → 各模块
- [ ] **6.3.2** `AgentExecutionLog` 持久化: 每步操作写入审计表 → `agent/nodes/*.py`
- [ ] **6.3.3** Dockerfile + docker-compose.yml → `Dockerfile`, `docker-compose.yml`
- [ ] **6.3.4** 健康检查端点 `GET /api/health` → `main.py`

> ⬜ **Phase 6 未开始**: 0/11 完成

---

## 统计

| Phase | 总任务 | 已完成 | 进度 |
|-------|--------|--------|------|
| Phase 0 — 项目骨架 | 7 | 7 | 100% ✅ |
| Phase 1.1 — Schema & Repository | 11 | 11 | 100% ✅ |
| Phase 1.2 — 数据获取管道 | 6 | 6 | 100% ✅ |
| Phase 1.3 — 技术指标计算 | 4 | 4 | 100% ✅ |
| Phase 2 — 向量层 (Embedding & RAG) | 17 | 16 | 94% 🟦 |
| Phase 3 — Agent 核心 | 31 | 3 | 10% 🟦 |
| Phase 4 — API 层 | 9 | 0 | 0% ⬜ |
| Phase 5 — 前端 | 6 | 0 | 0% ⬜ |
| Phase 6 — 质量保障 & 部署 | 11 | 0 | 0% ⬜ |
| **总计** | **102** | **47** | **46%** |
---

## 下一步行动

> 当前阻塞项: 无

**建议并行推进:**
- **2.3.5** SQL 示例完整入库（目标 50–80 条）— 补齐 Phase 2 最后一个任务
- **3.1.4** `create_pydantic_ai_model()` — Agent 核心依赖
- **3.2.x** Prompt 工程（5 份模板，纯模板开发，无依赖）
- **3.3.x** 状态与数据模型定义（含 `AgentDeps`）

**推荐交付顺序:**
1. `2.3.5` + `3.1.4` + `3.2.x` + `3.3.x`（可并行）
2. `3.4.x`（意图理解 + StockResolver）
3. `3.5.x`（工具实现）
4. `3.6.x`（LangGraph 编排）
5. `4.x` → `5.x` → `6.x`
