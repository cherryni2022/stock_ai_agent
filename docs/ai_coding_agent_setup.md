# AI Coding Agent 开发环境配置指南

> **目标**: 为 Stock AI Agent 项目配置最佳的 AI Coding Agent（Claude Code / Codex / Antigravity）开发环境
> 包括：MCP 服务器、Skills、开发规范（Rules）三大维度

---

## 〇、Review 总结：充分必要性评审

> [!IMPORTANT]
> 以下是针对原文档中 MCP、Skills、Rules 三大维度的 **充分必要性审查** 结果。
> 评审标准：**1) 与 technical_design.md 中的技术栈和模块的直接关联性；2) 开发阶段的实际需求；3) 是否存在功能重叠或缺失。**

### ✅ 保留（充分且必要）

| 项目 | 类型 | 理由 |
|------|------|------|
| **Supabase MCP** | MCP | 核心数据库，项目唯一 DB 方案，直接操作 PostgreSQL + pgvector |
| **Context7** | MCP | LangGraph/FastAPI/SQLAlchemy 等框架的实时文档查询，避免幻觉 |
| **GitKraken** | MCP | 版本控制必须，PR 协作 |
| **CLAUDE.md / AGENTS.md** | Rules | 开发规范核心文件 |
| **pyproject.toml 工具配置** | Rules | ruff / mypy / pytest 质量标准 |
| **Workflows** | Rules | 标准化开发流程 |

### ⚠️ 调整（不必要或需降级）

| 项目 | 类型 | 原推荐 | 建议 | 理由 |
|------|------|--------|------|------|
| **PostgreSQL MCP** | MCP | 强烈推荐 | ❌ **移除** | 与 Supabase MCP 功能高度重叠。Supabase MCP 已提供 `execute_sql`、`list_tables`、`list_columns` 等工具，可满足 Schema 查询、SQL 调试、pgvector 索引验证等所有需求。引入两个 DB 操作 MCP 反而增加上下文噪声 |
| **Filesystem MCP** | MCP | 强烈推荐 | ❌ **移除** | Claude Code / Antigravity 内置了完整的文件系统操作能力（`view_file`, `write_to_file`, `list_dir`, `grep_search` 等），无需额外 MCP |
| **Fetch MCP** | MCP | 强烈推荐 | ⬇️ **降级为按需** | Antigravity 内置 `read_url_content` 和 `search_web` 工具。仅在需要复杂的 HTTP 请求场景（如 cookie 管理、自定义 header）时才需要 |
| **Sequential Thinking** | MCP | 核心必装 | ⬇️ **降级为按需** | LLM 的 chain-of-thought 推理能力已足够完成架构设计和多步调试。此 MCP 增加上下文开销但收益有限。仅在遇到极其复杂的设计决策时按需安装 |
| **Memory MCP** | MCP | 按需 | ❌ **移除** | Antigravity 已内置 Knowledge Items (KI) 系统实现跨会话记忆；Claude Code 有 CLAUDE.md 作为项目记忆。无需额外 MCP |
| **Playwright MCP** | MCP | 按需 (Phase 5) | ⬇️ **保留但注意** | Antigravity 已内置 `browser_subagent` + `webapp-testing` skill。仅 Claude Code 场景需要 |
| `webapp-testing` | Skill | 可直接使用 | ✅ 保留 | Phase 5 Streamlit 前端测试有用 |
| `pdf/docx/xlsx` | Skill | 可直接使用 | ⬇️ **降级** | 非核心路径，仅在需要导出金融报告时使用 |
| `mcp-builder` | Skill | 可直接使用 | ⬇️ **降级** | 除非需要自建 MCP，否则不需要 |

### 🔴 补充（必要但缺失）

| 项目 | 类型 | 缺失原因 | 建议 |
|------|------|---------|------|
| **`.claude/settings.json` 项目级 MCP 配置** | Rules | 未提及项目级 MCP 配置管理 | 建议在项目根目录创建 `.claude/settings.json`，统一管理项目级 MCP 配置 |
| **Supabase RLS 策略规范** | Rules | technical_design 中有 Auth 设计，但 Rules 中未覆盖 RLS 最佳实践 | 在 CLAUDE.md 中增加 Supabase 安全规范 |
| **数据管道 Workflow** | Workflow | 有 6 个数据管道脚本（§8.1），但没有对应的 workflow | 创建 `run-data-pipeline.md` workflow |
| **环境变量管理规范** | Rules | `.env` 包含 LLM/Embedding/Supabase 三组 key，但未在 Rules 中强调管理策略 | CLAUDE.md 中明确 `.env` 管理规范 |

---

## 一、MCP 服务器推荐

MCP (Model Context Protocol) 是连接 AI Agent 与外部工具的标准协议。以下按**本项目需求**排列优先级。

### 1.1 核心必装 MCP ⭐

| MCP Server | 用途 | 项目关联 | 来源 |
|---|---|---|---|
| **Supabase MCP** | 数据库 Schema 查询、SQL 执行、Migration 管理、RLS 策略、Auth 管理、Edge Function 部署 | 直接操作 Supabase PostgreSQL + pgvector。覆盖 technical_design 中 §3.2 (36+ 张表)、§3.3 (3 张向量表)、pgvector 索引管理 等全部 DB 操作 | 已集成 / [supabase/mcp](https://github.com/supabase-community/supabase-mcp) |
| **Context7** | 实时拉取库文档 (LangGraph, FastAPI, SQLAlchemy, pgvector, akshare, yfinance 等) 注入 Prompt，避免幻觉 | 查询 LangGraph/LangChain 最新 API (Agent Graph §4)、FastAPI SSE (§7)、SQLAlchemy 2.0 async (§3.2)、pgvector 索引语法 (§3.3) | 已集成 / [upstash/context7](https://github.com/upstash/context7) |
| **GitKraken** | Git 操作 (commit, branch, PR, blame, diff) | 版本控制与 PR 协作 | 已集成 |

> [!NOTE]
> **关于 Sequential Thinking MCP**：原文档列为「核心必装」，经评审建议 **降级为按需安装**。
> 理由：LLM 自带的 chain-of-thought 推理在本项目的架构设计（Agent Graph 设计、多步调试）场景中已足够。
> Sequential Thinking MCP 增加约 ~2K token 的上下文开销，但在实际开发中很少被主动调用。
> 建议仅在遇到「需要超过 5 步推理的复杂架构决策」时临时安装。

### 1.2 按需安装 MCP

| MCP Server | 用途 | 何时安装 | 替代方案 |
|---|---|---|---|
| **Playwright MCP** | 浏览器自动化测试 | Phase 5 前端 Streamlit 测试时 (仅 Claude Code 环境需要) | Antigravity 已内置 `browser_subagent` |
| **Docker MCP** | 容器管理 | Phase 6 部署阶段 | 命令行 `docker` / `docker-compose` |
| **Sentry MCP** | 错误追踪 | Phase 6 可观测性阶段，若选用 Sentry | N/A |
| **LangSmith MCP** | Agent 执行追踪与调试 | Phase 3 Agent 核心开发阶段（如有官方 MCP 支持） | LangSmith Web UI |

> [!WARNING]
> **已移除的 MCP 及理由**：
> - ~~PostgreSQL MCP~~ — 与 Supabase MCP 功能完全重叠 (`execute_sql`, `list_tables`, `list_columns`)
> - ~~Filesystem MCP~~ — AI Coding Agent (Claude Code / Antigravity) 内置完整文件操作能力
> - ~~Fetch MCP~~ — Agent 内置 `read_url_content` / `search_web` 工具
> - ~~Memory MCP~~ — Antigravity 内置 KI 系统；Claude Code 有 CLAUDE.md 记忆机制
> - ~~Sequential Thinking~~ — 降级为按需，LLM chain-of-thought 已能覆盖

### 1.3 MCP 配置

#### 当前 Antigravity 已配置 (`~/.gemini/antigravity/mcp_config.json`)

```json
{
  "mcpServers": {
    "supabase-mcp-server": {
      "command": "/Users/niwen/.nvm/versions/node/v22.21.1/bin/npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--access-token", "${SUPABASE_ACCESS_TOKEN}"]
    },
    "context7": {
      "command": "/Users/niwen/.nvm/versions/node/v22.21.1/bin/npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

#### Claude Code 项目级配置 (`.claude/settings.json`)

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--supabase-access-token", "${SUPABASE_ACCESS_TOKEN}"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

> **查找更多 MCP**: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | [appcypher/awesome-mcp-servers](https://github.com/appcypher/awesome-mcp-servers) | [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers)

---

## 二、开发规范 (Rules)

不同 AI Coding Agent 使用不同的规范文件，但内容可大量复用。

### 2.1 规范文件对照表

| AI Coding Agent | 规范文件 | 位置 | 说明 |
|---|---|---|---|
| **Claude Code** | `CLAUDE.md` | 项目根目录 | 项目记忆文件，指导 Claude 的行为 |
| **Antigravity** | `CLAUDE.md` | 项目根目录 | 同 Claude Code |
| **OpenAI Codex** | `AGENTS.md` | 项目根目录 (支持嵌套) | AI Agent 专用的机器可读指令 |
| **Cursor** | `.cursor/rules/*.mdc` | `.cursor/rules/` 目录 | 按文件模式自动附加规则 |
| **通用** | `.editorconfig` + `pyproject.toml` | 项目根目录 | 编辑器 & linter 配置 |

### 2.2 推荐的 `CLAUDE.md` / `AGENTS.md` 内容模板

以下是针对本项目定制的规范模板，可同时作为 `CLAUDE.md` 和 `AGENTS.md` 使用：

```markdown
# Stock AI Agent — 开发规范

## 项目概述
基于 LangGraph 的多市场股票 AI Agent，支持 A 股 / 港股 / 美股查询与分析。
技术栈: Python 3.12+ / FastAPI / LangGraph / SQLAlchemy 2.0 / Supabase (PostgreSQL + pgvector) / Streamlit

## 快速命令

### 环境管理
- 安装依赖: `uv sync`
- 激活环境: `source .venv/bin/activate`
- 添加依赖: `uv add <package>`

### 代码质量
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy stock_agent/`
- 测试: `pytest tests/ -v`
- 单文件测试: `pytest tests/test_xxx.py -v -k "test_name"`

### 运行
- API 服务: `uvicorn stock_agent.main:app --reload --port 8000`
- Streamlit 前端: `streamlit run stock_agent/frontend/app.py`
- 数据管道: `python -m stock_agent.data_pipeline.akshare_fetcher`

### 数据管道（手动执行，按顺序）
```bash
python -m data_pipeline.akshare_fetcher         # A股数据
python -m data_pipeline.yfinance_fetcher         # 港股/美股数据
python -m data_pipeline.indicator_calculator     # 技术指标 (依赖上面两步)
python -m data_pipeline.news_fetcher             # 新闻获取
python -m data_pipeline.embedding_pipeline       # 新闻向量化
python -m data_pipeline.sql_examples_seeder      # SQL 示例向量化入库
```

## 代码风格规范

### Python 通用
- 使用 Python 3.12+ 语法特性
- 所有函数必须有 **type hints**
- 使用 `async def` 处理所有 I/O 操作（数据库调用、API 请求、文件 I/O）
- 变量命名: `snake_case`；类名: `PascalCase`；常量: `UPPER_SNAKE_CASE`
- 字符串使用双引号 `"`
- 导入排序: stdlib → third-party → local (ruff 自动处理)

### FastAPI 专项
- 使用 Pydantic v2 BaseModel 做请求/响应 Schema
- 使用 FastAPI 依赖注入管理 DB Session 和 Settings
- 所有 endpoint 必须有 response_model 和 status_code
- 错误处理统一使用 HTTPException
- 路由命名: `/api/v1/{resource}` RESTful 风格

### SQLAlchemy 专项
- 使用 SQLAlchemy 2.0 声明式映射 (Mapped, mapped_column)
- 使用 async session (`AsyncSession`)
- 表名使用 snake_case
- 用户/会话表主键用 UUID v4；行情/指标表用自增 id
- 时间字段统一用 UTC + `func.now()`
- trade_date 类型为 VARCHAR(10)，格式 'YYYY-MM-DD'

### LangGraph 专项
- State 使用 TypedDict 定义，字段添加 Annotator
- 节点函数签名: `async def node_name(state: AgentState) -> dict`
- 边和条件路由使用类型安全的字面量
- 每个节点单独文件，放在 `agent/nodes/` 目录
- Prompt 模板放在 `agent/prompts/` 目录

### Supabase / pgvector 专项
- 所有向量表统一使用 `VECTOR(1536)` 维度
- MVP 阶段使用 IVFFlat 索引 + `vector_cosine_ops`
- 向量索引配置: `lists = 50~100`, `probes = 10`
- 数据库变更必须通过 migration (Supabase MCP 的 `apply_migration`)
- 变更后运行 `get_advisors` 检查安全/性能建议

## 项目结构
stock_agent/
├── config/settings.py        # Pydantic Settings
├── database/                  # SQLAlchemy models + session
├── agent/                     # LangGraph 图、节点、Prompt
│   ├── graph.py              # StateGraph 定义
│   ├── state.py              # AgentState TypedDict
│   ├── nodes/                # intent, planner, executor, synthesizer, responder
│   └── prompts/              # Prompt 模板
├── tools/                     # Agent 使用的工具函数 (6 个: price, indicator, signal, financial, news, text_to_sql)
├── services/                  # Embedding / RAG / LLM 服务
├── data_pipeline/             # 数据获取与处理管道 (6 个脚本)
├── api/                       # FastAPI 路由 (chat SSE, session)
├── frontend/                  # Streamlit UI
└── main.py                    # FastAPI 入口

## 重要约定
1. 不要修改 `docs/` 目录中的设计文档，除非明确要求
2. 新增功能前先查看 `docs/plan.md` 确认当前阶段
3. 数据库变更必须通过 migration (或 Supabase MCP 的 apply_migration)
4. 敏感信息（API Key、DB URL）只能放在 `.env`，不得硬编码
5. 每个 PR 必须包含对应的测试
6. 提交信息格式: `<type>(<scope>): <description>`
   - type: feat / fix / refactor / test / docs / chore
7. 使用 Context7 MCP 查询库文档，避免使用过时 API
8. SQL 工具仅允许生成 SELECT 语句，禁止 INSERT/UPDATE/DELETE/DROP

## MVP 股票池
- A股: 601127 (赛力斯), 688981 (中芯国际)
- 港股: 9988.HK (阿里巴巴), 0700.HK (腾讯), 1024.HK (快手)
- 美股: AAPL, MSFT, NVDA, GOOG, AMZN, META, TSLA
共 12 支股票

## 关键设计文档
- 产品需求: docs/PRD_stock_ai_agent.md
- 系统架构: docs/architecture.md
- 技术设计: docs/technical_design.md
- 开发计划: docs/plan.md
```

> [!NOTE]
> **Review 建议**：相比原模板，新增了以下关键内容：
> 1. **数据管道命令**：完整的 6 步手动执行命令（对应 technical_design §8.1）
> 2. **Supabase / pgvector 专项规范**：向量维度、索引策略、migration 规范
> 3. **MVP 股票池**：方便 Agent 在开发测试中使用正确的 ticker
> 4. **SQL 安全约束**：仅允许 SELECT（对应 technical_design §5.3 validate_sql_safety）
> 5. **Python 版本修正**：从 3.11 → 3.12+（与 pyproject.toml `requires-python = ">=3.12"` 保持一致）
> 6. **主键策略分化**：UUID 用于用户/会话表，自增 id 用于行情/指标表（对应 §3.2.4 约定）

### 2.3 Cursor Rules (`.cursor/rules/`)

若同时使用 Cursor IDE，可创建以下规则文件：

| 规则文件 | 类型 | glob 模式 | 内容 |
|---|---|---|---|
| `python-general.mdc` | Auto Attached | `*.py` | Python 代码风格、type hints、async |
| `fastapi.mdc` | Auto Attached | `stock_agent/api/**/*.py` | FastAPI 路由规范、Pydantic 校验 |
| `sqlalchemy.mdc` | Auto Attached | `stock_agent/database/**/*.py` | SQLAlchemy 2.0 映射规范 |
| `langgraph.mdc` | Auto Attached | `stock_agent/agent/**/*.py` | LangGraph State/Node/Edge 规范 |
| `testing.mdc` | Auto Attached | `tests/**/*.py` | pytest 测试规范、fixtures |
| `data-pipeline.mdc` | Auto Attached | `stock_agent/data_pipeline/**/*.py` | 数据管道错误处理与重试 |

> **参考**: [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) — 包含大量现成的 Python / FastAPI / SQLAlchemy 规则模板

---

## 三、Skills 推荐

Skills 是扩展 AI Coding Agent 能力的插件式知识包。

### 3.1 Antigravity 已安装 Skills（可直接使用）

| Skill | 本项目用途 | 使用阶段 | 必要性 |
|---|---|---|---|
| `webapp-testing` | Playwright 测试 FastAPI & Streamlit | Phase 5-6 | ⭐ 推荐 |
| `doc-coauthoring` | 协作编写技术文档、API 文档 | 全阶段 | ⭐ 推荐 |
| `mcp-builder` | 如需自建 MCP Server（如封装 akshare API） | 按需 | 可选 |
| `pdf` / `docx` / `xlsx` | 处理金融报告、数据导出 | 按需 | 可选 |

> [!NOTE]
> **Review 建议**：已安装的 Skills 中，`webapp-testing` 和 `doc-coauthoring` 对本项目最有价值。
> `pdf/docx/xlsx` 在 MVP 阶段不是必需的，可以在需要生成报告时再使用。

### 3.2 建议自定义 Skills（可基于 skill-creator 创建）

以下按 **对本项目的开发效率影响** 排序：

| 优先级 | Skill 名称 | 描述 | 推荐内容 | 关联 technical_design 章节 |
|---|---|---|---|---|
| 🔴 P0 | `supabase-pgvector` | Supabase + pgvector 最佳实践 | 向量表设计模板、IVFFlat/HNSW 索引创建 SQL、相似度搜索 query 模板、RLS 策略模板、Embedding 维度管理 | §3.3 向量数据模型、§3.3.4 向量索引策略 |
| 🔴 P0 | `langgraph-patterns` | LangGraph 开发模式 | State TypedDict 模板、Node 函数签名模板、条件路由 (add_conditional_edges) 示例、executor 并行执行模式、SSE status_callback 集成模式 | §4.1-4.3 Agent Graph 实现 |
| 🟡 P1 | `stock-data-pipeline` | 股票数据管道模式 | akshare API 用法 (A股日K、基本信息、新闻)、yfinance API 用法 (港美股日K、info、news)、数据清洗模板、增量更新 (UPSERT) 模式、错误重试 (tenacity)、pandas + ta 指标计算 | §8.1-8.2 数据管道 |
| 🟡 P1 | `prompt-engineering` | Prompt 工程模板 | 意图分类 Prompt (§9.1)、实体提取 Prompt、Text-to-SQL System+User Prompt (§8.3.5)、综合分析 Prompt (§9.2)、Few-shot 示例格式化 | §9 Prompt 工程 |
| 🟢 P2 | `sse-streaming` | SSE 流式响应模式 | FastAPI StreamingResponse + asyncio.Queue 模式、事件类型定义 (status/result/DONE)、客户端 (Streamlit/JS) SSE 消费、心跳机制、错误处理 | §7.1 聊天 API SSE |

> [!NOTE]
> **Review 建议 — 自定义 Skills 充分性分析**：
>
> ✅ **覆盖完整**：5 个自定义 Skill 覆盖了 technical_design 中的全部核心开发场景：
> - 数据层 (Phase 1-2) → `supabase-pgvector` + `stock-data-pipeline`
> - Agent 核心 (Phase 3) → `langgraph-patterns` + `prompt-engineering`
> - API 层 (Phase 4) → `sse-streaming`
>
> ❌ **不建议添加的 Skill**：
> - ~~`error-handling` Skill~~ — 错误处理模式 (tenacity, 异常层级) 已在 CLAUDE.md 和 technical_design 中充分定义
> - ~~`testing-patterns` Skill~~ — pytest 规范已在 pyproject.toml 和 CLAUDE.md 中配置
> - ~~`docker-deployment` Skill~~ — Phase 6 才需要，且 Docker 知识 LLM 已有充分掌握

### 3.3 GitHub 社区热门 Skills 资源

| 资源 | 链接 | 说明 |
|---|---|---|
| Anthropic 官方 Skills 合集 | [anthropic-cookbook/skills](https://github.com/anthropics/anthropic-cookbook) | 50+ 官方维护的 Skills |
| Claude Code Skills 目录 | [awesome-claude-code](https://github.com/search?q=awesome+claude+code+skills) | 社区分享的 Claude Code Skills |
| Cursor Rules 合集 | [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | 500+ Cursor 规则，按框架分类 |
| cursor.directory | [cursor.directory](https://cursor.directory) | 在线浏览 & 搜索 Cursor 规则 |

---

## 四、推荐工作流配置

### 4.1 项目 `.agent/workflows/` 建议

```
.agent/workflows/
├── dev-setup.md              # 开发环境初始化流程
├── add-feature.md            # 添加新功能标准流程
├── add-database-table.md     # 新增数据库表流程 (Supabase MCP apply_migration)
├── add-tool.md               # 新增 Agent Tool 流程
├── add-langgraph-node.md     # 新增 LangGraph Node 流程
├── run-data-pipeline.md      # 数据管道执行流程 (6 步)
├── run-tests.md              # 测试执行流程
└── deploy.md                 # 部署流程
```

> [!NOTE]
> **Review 新增**：`run-data-pipeline.md` — 对应 technical_design §8.1 的 6 步数据更新流程，
> 是 Phase 1-2 最频繁使用的 workflow。

### 4.2 示例 Workflow: `add-tool.md`

```markdown
---
description: 如何为 Agent 添加新的 Tool
---

1. 在 `docs/technical_design.md` §5 确认 Tool 的设计规范
2. 在 `stock_agent/tools/` 创建新文件 `{tool_name}.py`
3. 定义 Pydantic Model: `{ToolName}Params` 和 `{ToolName}Result`
4. 实现 Tool 函数，签名为 `async def {tool_name}_tool(state: AgentState, **kwargs) -> {ToolName}Result`
5. 在函数上添加详细 docstring（LLM 用于理解工具用途）
6. 在 `stock_agent/tools/__init__.py` 的 `TOOL_REGISTRY` 中注册新 Tool
// turbo
7. 运行 `ruff check stock_agent/tools/{tool_name}.py`
8. 在 `tests/test_tools/` 添加对应测试文件
// turbo
9. 运行 `pytest tests/test_tools/test_{tool_name}.py -v`
10. 更新 `agent/nodes/executor.py` 的 TOOL_REGISTRY（如尚未自动注册）
11. 验证 Agent 能正确调用该 Tool
```

### 4.3 示例 Workflow: `run-data-pipeline.md`

```markdown
---
description: 执行数据管道更新 MVP 股票数据
---

// turbo-all

1. 确认虚拟环境已激活: `source .venv/bin/activate`
2. 获取 A 股日 K 线数据: `python -m data_pipeline.akshare_fetcher`
3. 获取港股/美股日 K 线数据: `python -m data_pipeline.yfinance_fetcher`
4. 计算技术指标 (依赖步骤 2-3): `python -m data_pipeline.indicator_calculator`
5. 获取新闻: `python -m data_pipeline.news_fetcher`
6. 新闻向量化入库: `python -m data_pipeline.embedding_pipeline`
7. 验证数据: 使用 Supabase MCP 执行 `SELECT COUNT(*) FROM stock_daily_price`
```

### 4.4 示例 Workflow: `add-database-table.md`

```markdown
---
description: 在 Supabase 中新增数据库表
---

1. 在 `docs/technical_design.md` §3 确认表设计规范
2. 在 `stock_agent/database/models/` 中创建或修改 SQLAlchemy 模型文件
3. 使用 Supabase MCP `apply_migration` 工具执行 DDL:
   - migration name 使用 snake_case
   - 必须包含完整的 CREATE TABLE 语句
   - 必须包含索引和约束
4. 使用 Supabase MCP `get_advisors` 检查安全和性能建议
5. 如果是向量表，创建 pgvector 索引:
   - IVFFlat: `CREATE INDEX ... USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)`
6. 验证: 使用 Supabase MCP `list_tables` 确认表已创建
// turbo
7. 运行 `ruff check stock_agent/database/models/`
```

---

## 五、`pyproject.toml` 工具配置

确保以下质量工具在 `pyproject.toml` 中配置，让 AI Agent 和人工开发者使用统一标准：

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "ASYNC", # flake8-async
]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

> [!NOTE]
> **Review 修正**：`target-version` 和 `python_version` 从 `3.11` 修正为 `3.12`，与 technical_design §11 的 `requires-python = ">=3.12"` 保持一致。

---

## 六、总结：逐阶段配置清单

| 阶段 | 需要的 MCP | 需要的 Rules/Skills | 优先级 |
|---|---|---|---|
| **Phase 0** 项目骨架 | Supabase, Context7, GitKraken | `CLAUDE.md` / `AGENTS.md` 基础规范 | 🔴 立即 |
| **Phase 1** 数据层 | 同上 | + `sqlalchemy.mdc` (Cursor), `stock-data-pipeline` Skill | 🔴 立即 |
| **Phase 2** 向量层 | 同上 | + `supabase-pgvector` Skill | 🟡 本阶段 |
| **Phase 3** Agent 核心 | 同上 | + `langgraph.mdc`, `langgraph-patterns` Skill, `prompt-engineering` Skill | 🟡 本阶段 |
| **Phase 4** API 层 | 同上 | + `fastapi.mdc`, `sse-streaming` Skill | 🟡 本阶段 |
| **Phase 5** 前端 | + Playwright MCP (仅 Claude Code) | + `webapp-testing` Skill | 🟢 按需 |
| **Phase 6** 部署 | + Docker MCP (可选) | + `deploy.md` Workflow | 🟢 按需 |

> [!NOTE]
> **Review 变更 vs 原文档**：
> 1. Phase 1 不再需要额外安装 PostgreSQL MCP（Supabase MCP 已覆盖）
> 2. Phase 2 不再需要 Fetch MCP（Agent 内置能力已覆盖）
> 3. Phase 3 不再需要单独安装 Sequential Thinking（降级为按需）
> 4. 所有阶段的核心 MCP **仅需 3 个**：Supabase + Context7 + GitKraken

---

## 附录 A：MCP 能力矩阵 vs 项目需求

| 开发场景 | 所需能力 | 覆盖方 |
|---------|---------|--------|
| 创建/修改数据库表 | DDL 执行 | Supabase MCP `apply_migration` |
| 查询数据验证 | SQL 执行 | Supabase MCP `execute_sql` |
| 查看表结构 | Schema 查询 | Supabase MCP `list_tables` + `list_columns` (Aliyun) |
| 管理 pgvector 索引 | SQL 执行 | Supabase MCP `execute_sql` |
| 检查安全/性能 | 安全审计 | Supabase MCP `get_advisors` |
| 查询框架 API | 文档检索 | Context7 MCP |
| 版本控制 | Git 操作 | GitKraken MCP |
| 读写项目文件 | 文件操作 | Agent 内置 (view_file, write_to_file 等) |
| 搜索网页/调研 | Web 访问 | Agent 内置 (search_web, read_url_content) |
| 浏览器测试 | 自动化测试 | Agent 内置 browser_subagent (Antigravity) / Playwright MCP (Claude Code) |

## 附录 B：关键参考链接

- **CLAUDE.md 编写指南**: [Anthropic 官方文档](https://docs.anthropic.com/en/docs/claude-code/memory)
- **AGENTS.md 规范**: [agents.md](https://agents.md) | [agentsmd.io](https://agentsmd.io)
- **Awesome MCP Servers**: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- **Awesome Cursor Rules**: [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
- **LangGraph 文档**: [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **Supabase MCP**: [supabase-community/supabase-mcp](https://github.com/supabase-community/supabase-mcp)
- **Context7 MCP**: [upstash/context7](https://github.com/upstash/context7)
