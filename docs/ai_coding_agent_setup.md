# AI Coding Agent 开发环境配置指南

> **目标**: 为 Stock AI Agent 项目配置最佳的 AI Coding Agent（Claude Code / Codex / Antigravity）开发环境
> 包括：MCP 服务器、Skills、开发规范（Rules）三大维度

---

## 一、MCP 服务器推荐

MCP (Model Context Protocol) 是连接 AI Agent 与外部工具的标准协议。以下按**本项目需求**排列优先级。

### 1.1 核心必装 MCP ⭐

| MCP Server | 用途 | 项目关联 | 来源 |
|---|---|---|---|
| **Supabase MCP** | 数据库 Schema 查询、SQL 执行、RLS 策略管理、Auth 管理 | 直接操作 Supabase PostgreSQL + pgvector | 已集成 / [supabase/mcp](https://github.com/supabase-community/supabase-mcp) |
| **Context7** | 实时拉取库文档 (LangGraph, FastAPI, SQLAlchemy 等) 注入 Prompt，避免幻觉 | 查询 LangGraph/LangChain/FastAPI 最新 API | 已集成 / [upstash/context7](https://github.com/upstash/context7) |
| **GitKraken** | Git 操作 (commit, branch, PR, blame, diff) | 版本控制与 PR 协作 | 已集成 |
| **Sequential Thinking** | 结构化分步推理，适合复杂架构决策和调试 | Agent Graph 设计、多步调试 | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) |

### 1.2 强烈推荐 MCP

| MCP Server | 用途 | 项目关联 | 来源 |
|---|---|---|---|
| **PostgreSQL MCP** | 直接连接 PostgreSQL，Schema 检查 + 查询（比 Supabase MCP 更底层） | 低层 DB 调试、pgvector 索引验证 | [modelcontextprotocol/server-postgres](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres) |
| **Fetch / Brave Search** | 获取网页内容 / 搜索文档 | 调研 akshare/yfinance API 变更、查找 bug fix | [modelcontextprotocol/servers/fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) |
| **Filesystem MCP** | 安全的文件系统读写操作 | 管理配置文件、数据 pipeline 输出 | [modelcontextprotocol/servers/filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) |

### 1.3 按需安装 MCP

| MCP Server | 用途 | 何时安装 |
|---|---|---|
| **Docker MCP** | 容器管理 | Phase 6 部署阶段 |
| **Sentry MCP** | 错误追踪 | Phase 6 可观测性阶段 |
| **Playwright MCP** | 浏览器自动化测试 | Phase 5 前端 Streamlit 测试 |
| **Memory MCP** | 知识图谱式长期记忆 | 跨会话保留项目上下文 |
| **LangSmith MCP** | Agent 执行追踪与调试 | Phase 3 Agent 核心开发阶段（如有官方 MCP 支持） |

### 1.4 MCP 配置示例

#### Antigravity / Claude Code 配置 (`~/.gemini/settings.json` 或项目级)

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
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequentialthinking"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/niwen/PycharmProjects/my_dev_agent/stock-ai-agent"]
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
技术栈: Python 3.11+ / FastAPI / LangGraph / SQLAlchemy 2.0 / Supabase (PostgreSQL + pgvector) / Streamlit

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

## 代码风格规范

### Python 通用
- 使用 Python 3.11+ 语法特性
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
- 主键统一用 UUID v4
- 时间字段统一用 UTC + `func.now()`

### LangGraph 专项
- State 使用 TypedDict 定义，字段添加 Annotator
- 节点函数签名: `async def node_name(state: AgentState) -> dict`
- 边和条件路由使用类型安全的字面量
- 每个节点单独文件，放在 `agent/nodes/` 目录
- Prompt 模板放在 `agent/prompts/` 目录

## 项目结构
stock_agent/
├── config/settings.py        # Pydantic Settings
├── database/                  # SQLAlchemy models + session
├── agent/                     # LangGraph 图、节点、Prompt
├── tools/                     # Agent 使用的工具函数
├── services/                  # Embedding / RAG / LLM 服务
├── data_pipeline/             # 数据获取与处理管道
├── api/                       # FastAPI 路由
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
```

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

| Skill | 本项目用途 |
|---|---|
| `webapp-testing` | Playwright 测试 FastAPI & Streamlit |
| `pdf` / `docx` / `xlsx` | 处理金融报告、数据导出 |
| `mcp-builder` | 如需自建 MCP Server |
| `doc-coauthoring` | 协作编写技术文档 |

### 3.2 建议自定义 Skills（可基于 skill-creator 创建）

| Skill 名称 | 描述 | 推荐内容 |
|---|---|---|
| `langgraph-patterns` | LangGraph 开发模式 | State 定义模板、Node 编写模板、条件路由示例、Human-in-the-loop 模式 |
| `supabase-pgvector` | Supabase + pgvector 最佳实践 | 向量表设计、IVFFlat/HNSW 索引、相似度搜索、RLS 策略模板 |
| `stock-data-pipeline` | 股票数据管道模式 | akshare/yfinance API 用法、数据清洗、增量更新、错误重试 |
| `sse-streaming` | SSE 流式响应模式 | FastAPI SSE 实现、客户端接收、错误处理、心跳机制 |
| `prompt-engineering` | Prompt 工程模板 | 意图分类 Prompt、Text-to-SQL Prompt、综合分析 Prompt |

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
├── dev-setup.md          # 开发环境初始化流程
├── add-feature.md        # 添加新功能标准流程
├── add-database-table.md # 新增数据库表流程
├── add-tool.md           # 新增 Agent Tool 流程
├── add-langgraph-node.md # 新增 LangGraph Node 流程
├── run-tests.md          # 测试执行流程
└── deploy.md             # 部署流程
```

### 4.2 示例 Workflow: `add-tool.md`

```markdown
---
description: 如何为 Agent 添加新的 Tool
---

1. 在 `docs/technical_design.md` 确认 Tool 的设计规范
2. 在 `stock_agent/tools/` 创建新文件 `{tool_name}.py`
3. 实现 Tool 函数，签名为 `async def tool_name(params) -> ToolResult`
4. 在函数上添加 `@tool` 装饰器和详细 docstring
5. 在 `stock_agent/agent/graph.py` 注册新 Tool
// turbo
6. 运行 `ruff check stock_agent/tools/{tool_name}.py`
7. 在 `tests/tools/` 添加对应测试文件
// turbo
8. 运行 `pytest tests/tools/test_{tool_name}.py -v`
9. 验证 Agent 能正确调用该 Tool
```

---

## 五、`pyproject.toml` 工具配置

确保以下质量工具在 `pyproject.toml` 中配置，让 AI Agent 和人工开发者使用统一标准：

```toml
[tool.ruff]
target-version = "py311"
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
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## 六、总结：逐阶段配置清单

| 阶段 | 需要的 MCP | 需要的 Rules/Skills | 优先级 |
|---|---|---|---|
| **Phase 0** 项目骨架 | Supabase, Context7, GitKraken | CLAUDE.md / AGENTS.md 基础规范 | 🔴 立即 |
| **Phase 1** 数据层 | + PostgreSQL MCP | + `sqlalchemy.mdc`, `data-pipeline` Skill | 🔴 立即 |
| **Phase 2** 向量层 | + Fetch (查文档) | + `supabase-pgvector` Skill | 🟡 本阶段 |
| **Phase 3** Agent 核心 | + Sequential Thinking | + `langgraph.mdc`, `langgraph-patterns` Skill, `prompt-engineering` Skill | 🟡 本阶段 |
| **Phase 4** API 层 | 同上 | + `fastapi.mdc`, `sse-streaming` Skill | 🟡 本阶段 |
| **Phase 5** 前端 | + Playwright MCP | + `webapp-testing` Skill | 🟢 按需 |
| **Phase 6** 部署 | + Docker MCP, Sentry MCP | + `deploy.md` Workflow | 🟢 按需 |

---

## 附录：关键参考链接

- **CLAUDE.md 编写指南**: [Anthropic 官方文档](https://docs.anthropic.com/en/docs/claude-code/memory)
- **AGENTS.md 规范**: [agents.md](https://agents.md) | [agentsmd.io](https://agentsmd.io)
- **Awesome MCP Servers**: [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- **Awesome Cursor Rules**: [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules)
- **LangGraph 文档**: [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)
- **Supabase MCP**: [supabase-community/supabase-mcp](https://github.com/supabase-community/supabase-mcp)
- **Context7 MCP**: [upstash/context7](https://github.com/upstash/context7)
