---
description: 如何为项目创建一个新的 Antigravity Skill（项目级，非全局）
---

## 前置条件

- `skill-creator` 已安装在全局 Skills 目录 (`~/.gemini/antigravity/skills/skill-creator/`)
- 项目 `.agent/skills/` 目录已存在（如不存在，Step 2 会自动创建）

## 创建流程

### Step 1: 明确 Skill 的定位

在创建之前，回答以下问题：

1. **Skill 名称**：小写 + 连字符，如 `supabase-pgvector`
2. **触发场景**：用户问什么问题时应该激活这个 Skill？
3. **知识来源**：这些知识从哪里获取？
   - 项目设计文档（如 `docs/technical_design.md` 的具体章节）
   - Context7 MCP 查询框架最新文档
   - 项目已有的代码实现
   - Web 搜索或 API 文档
4. **内容规划**：
   - `SKILL.md`：核心指令和模板（< 500 行）
   - `references/`：详细参考文档（按需加载，节省上下文窗口）
   - `scripts/`：可执行脚本（如果有重复性操作）
   - `assets/`：模板文件、图片等资源

### Step 2: 初始化 Skill 骨架

// turbo
```bash
python3 ~/.gemini/antigravity/skills/skill-creator/scripts/init_skill.py <skill-name> --path .agent/skills/
```

这会在 `.agent/skills/<skill-name>/` 生成模板目录结构。

### Step 3: 收集知识上下文

根据 Step 1 确定的知识来源收集信息：

- **项目文档**：使用 `view_file` 读取 `docs/technical_design.md` 中的相关章节
- **框架文档**：使用 Context7 MCP 查询最新 API
  ```
  1. mcp_context7_resolve-library-id: 查找库 ID
  2. mcp_context7_query-docs: 获取具体 API 用法
  ```
- **已有代码**：使用 `grep_search` 和 `view_code_item` 查看项目中已有的实现模式
- **Web 搜索**：使用 `search_web` 或 `read_url_content` 获取最新最佳实践


### Step 4: 编写 SKILL.md

编写核心指令文件，遵循以下原则：

**Frontmatter（最关键）**：
```yaml
---
name: <skill-name>
description: <清晰描述 Skill 做什么 + 什么场景下触发>。Use when <具体触发场景列表>。Triggers on <关键词列表>。
---
```

- `description` 是 **唯一的触发机制**，必须包含所有「何时使用」的信息
- 不要在 body 中再写 "When to Use" 章节（body 只在触发后加载）

**Body 编写规则**：
1. **只写 AI 不知道的**：Claude 已知的通用知识不要重复
2. **项目特定知识优先**：表名、字段名、架构约定、MVP 配置等
3. **代码模板 > 文字描述**：用具体代码示例代替冗长的文字说明
4. **控制在 500 行以内**：详细内容放 `references/` 目录
5. **引用 references 文件**：使用相对路径链接，说明何时应该加载

### Step 5: 编写 References 文件（如需要）

将详细的参考内容放在 `references/` 目录下：

- 每个文件聚焦一个主题（如 `index-strategies.md`、`executor-pattern.md`）
- 超过 100 行的文件在顶部加目录
- 在 SKILL.md 中用 `[references/xxx.md](references/xxx.md)` 引用并说明加载时机

### Step 6: 验证 Skill

// turbo
```bash
head -4 .agent/skills/<skill-name>/SKILL.md
```

确认 frontmatter 格式正确（`---` 包裹，包含 `name` 和 `description`）。

// turbo
```bash
find .agent/skills/<skill-name> -type f
```

确认文件结构合理，没有多余文件。

如果全局安装了 pyyaml，可运行完整验证：
```bash
python3 ~/.gemini/antigravity/skills/skill-creator/scripts/quick_validate.py .gemini/skills/<skill-name>
```

### Step 7:（可选）打包分发

如果需要将 Skill 分享给其他人：
```bash
python3 ~/.gemini/antigravity/skills/skill-creator/scripts/package_skill.py .agent/skills/<skill-name>
```

生成 `<skill-name>.skill` 文件（实际是 zip 包）。

## 最终目录结构示例

```
.agent/skills/<skill-name>/
├── SKILL.md                    # 核心指令（< 500 行）
├── references/                 # 按需加载的详细文档
│   ├── topic-a.md
│   └── topic-b.md
├── scripts/                    # 可执行脚本（可选）
│   └── helper.py
└── assets/                     # 模板/资源文件（可选）
    └── template.sql
```

## 常见错误

| 错误 | 修正 |
|------|------|
| description 太短，不够具体 | 列出所有触发场景和关键词 |
| SKILL.md 超过 500 行 | 把详细内容拆到 references/ |
| 重复 Claude 已知的知识 | 只写项目特定知识 |
| references 文件互相引用 | 保持一层引用深度，全部从 SKILL.md 链接 |
| 忘记清理 example 占位文件 | Step 4 |