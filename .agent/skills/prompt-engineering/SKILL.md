---
name: prompt-engineering
description: Prompt engineering templates and patterns for the Stock AI Agent project. Use when designing or modifying prompts for intent classification, entity extraction, Text-to-SQL generation with RAG few-shot examples, analysis synthesis, response formatting, or SQL example batch generation. Triggers on any prompt template, LLM structured output, few-shot example formatting, or system/user prompt construction task.
---

# Prompt Engineering Patterns

## Prompt File Organization

All prompts live in `stock_agent/agent/prompts/` as Python string constants.

```
agent/prompts/
├── intent.py          # INTENT_PROMPT, ENTITY_EXTRACTION_PROMPT
├── planner.py         # DECOMPOSITION_PROMPT
├── synthesis.py       # SYNTHESIS_PROMPT
├── responder.py       # RESPONSE_FORMAT_PROMPT
├── text_to_sql.py     # TEXT_TO_SQL_PROMPT, BASE_SYSTEM_PROMPT
└── sql_generation.py  # CATEGORY_GUIDANCE, USER_PROMPT_TEMPLATE
```

## Intent Classification Prompt

```python
INTENT_PROMPT = """你是一个股票分析 AI Agent 的意图分类器。

分析用户消息，判断查询意图类别和是否需要拆解：

## 意图类别
- simple_query: 单股票单指标 (如"茅台最新价格")
- comparison: 多股票横向对比 (如"对比苹果和微软的PE")
- complex_analysis: 需要多步骤分析 (如"综合分析Tesla的趋势和基本面")
- conversational: 闲聊或跟进 (如"上次说的那只股票呢")
- text_to_sql: 需自定义SQL (如"哪些股票今天涨幅超过5%")

## 判断 requires_decomposition
- True: 涉及多个指标/多个股票/需要多步分析
- False: 可一步获取的简单查询

## 输出
返回 JSON: {category, confidence, requires_decomposition, suggested_tools, reasoning}
"""
```

## Text-to-SQL Prompt Architecture

Text-to-SQL uses a 3-part prompt:

1. **BASE_SYSTEM_PROMPT**: Schema DDL + MVP stock pool + strict constraints
2. **CATEGORY_GUIDANCE**: Category-specific query pattern guidance
3. **Few-shot examples**: RAG-retrieved similar examples injected at runtime

For complete prompt templates, see [references/text-to-sql-prompts.md](references/text-to-sql-prompts.md).

## Synthesis Prompt Pattern

```python
SYNTHESIS_PROMPT = """你是一个专业股票分析师，负责综合多个数据源的结果。

## 已获取数据
{tool_results_json}

## 用户原始问题
{user_question}

## 要求
1. 用中文回答，语言专业但易懂
2. 引用具体数据 (日期、数值)
3. 给出分析结论和投资观点 (但不构成投资建议)
4. 如果数据不足，明确说明缺什么
5. 结尾附风险提示

## 输出格式
markdown 格式，包含:
- 📊 数据摘要 (关键数字)
- 📈 分析结论 (趋势判断)
- ⚠️ 风险提示
"""
```

## LLM Structured Output Pattern

Use `with_structured_output()` for Pydantic model extraction:

```python
from langchain_core.messages import SystemMessage, HumanMessage

intent = await llm.with_structured_output(IntentClassification).ainvoke([
    SystemMessage(content=INTENT_PROMPT),
    HumanMessage(content=user_message),
])
```

## Few-shot Example Formatting

```python
def format_sql_examples(examples: list[dict]) -> str:
    """Format RAG-retrieved SQL examples for prompt injection."""
    parts = []
    for i, ex in enumerate(examples, 1):
        parts.append(f"""### 示例 {i} (相似度: {ex.get('similarity', 'N/A'):.2%})
问题: {ex['question']}
SQL:
```sql
{ex['sql_query']}
```
说明: {ex.get('description', '')}
""")
    return "\n".join(parts)
```

## Key Constraints in All Prompts

1. **SQL safety**: Only SELECT. Never INSERT/UPDATE/DELETE/DROP
2. **Ticker source**: Only use tickers from MVP stock pool
3. **Field names**: Use exact DB column names (e.g., `macd_diff` not `macd`, `price_to_earnings_ratio` not `pe_ratio`)
4. **Date format**: `trade_date` is VARCHAR(10) format 'YYYY-MM-DD'
5. **Language**: All user-facing text in Chinese

## Reference Files

- **[references/text-to-sql-prompts.md](references/text-to-sql-prompts.md)**: Complete BASE_SYSTEM_PROMPT, CATEGORY_GUIDANCE for all 6 categories, and USER_PROMPT_TEMPLATE
