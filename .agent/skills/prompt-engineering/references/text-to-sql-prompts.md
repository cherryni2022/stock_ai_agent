# Text-to-SQL Prompt Templates

## BASE_SYSTEM_PROMPT

Shared across all categories. Includes DB schema DDL and MVP stock pool.

```python
BASE_SYSTEM_PROMPT = """你是一个专业的 SQL 示例生成助手，为股票分析 AI Agent 的 Text-to-SQL 功能生成训练数据。

## 数据库 Schema (PostgreSQL)

{schema}

## MVP 股票池

| 市场 | 代码 | 名称 |
|------|------|------|
| A股 | 601127 | 赛力斯 |
| A股 | 688981 | 中芯国际 |
| 港股 | 9988.HK | 阿里巴巴 |
| 港股 | 0700.HK | 腾讯 |
| 港股 | 1024.HK | 快手 |
| 美股 | AAPL | 苹果 |
| 美股 | MSFT | 微软 |
| 美股 | NVDA | 英伟达 |
| 美股 | GOOG | 谷歌 |
| 美股 | AMZN | 亚马逊 |
| 美股 | META | Meta |
| 美股 | TSLA | 特斯拉 |

## 严格约束

1. question 必须用自然语言中文提问，模拟真实散户投资者的口语化表述
2. sql_query 必须是合法的 PostgreSQL SELECT 语句，禁止 INSERT/UPDATE/DELETE
3. 仅使用上述 Schema 中存在的表名和列名，不要臆造不存在的字段
4. ticker 必须来自上述股票池
5. 每条示例的 question 必须与已有示例语义不同
6. SQL 日期处理使用 PostgreSQL 标准语法：CURRENT_DATE, INTERVAL, DATE_TRUNC
7. trade_date 字段类型为 VARCHAR(10)，格式 'YYYY-MM-DD'
"""
```

## CATEGORY_GUIDANCE

### Price (`price`)
- Tables: `stock_daily_price`
- Patterns: WHERE+ORDER+LIMIT, GROUP BY+聚合, 窗口函数(LAG), CASE WHEN
- Key columns: `close`, `volume`, `pct_chg`, `turnover_rate`

### Indicator (`indicator`)
- Tables: `stock_technical_indicators`
- Patterns: MACD金叉/死叉, RSI超买超卖, 均线排列, 布林带位置
- ⚠️ Column names: `macd_diff`, `macd_dea`, `macd_hist` (NOT `macd`, `macd_signal`)

### Signal (`signal`)
- Tables: 5 signal tables (`stock_technical_*_signal_indicators`)
- Patterns: Latest signal, bullish filtering, multi-strategy confluence (multi-table JOIN)

### Financial (`financial`)
- Tables: `financial_metrics`
- Patterns: Latest quarter, ROE/PE comparison, growth trends
- ⚠️ Column names: `price_to_earnings_ratio` (NOT `pe_ratio`), `return_on_equity` (NOT `roe`)
- ⚠️ `report_period` is VARCHAR(20) format like '2024-Q3', '2024-FY'

### Meta (`meta`)
- Tables: `stock_basic_info`, `stock_company_info`, `stock_basic_info_a`
- Patterns: Industry filtering (ILIKE), market cap ranking, cross-table JOIN

### Composite (`composite`)
- Multiple table JOINs
- JOIN key: `ticker + trade_date` (financial uses `report_period`)
- Patterns: Price+Indicator, Price+Financial, triple JOINs, CTEs

## USER_PROMPT_TEMPLATE

```python
USER_PROMPT_TEMPLATE = """请生成 {count} 条 {category} 类别的 SQL 查询示例。

## 已有示例 (参考风格，不要重复)
{existing_examples}

## 要求
- 每条示例的 question 必须在语义上与已有示例不同
- 多样化问法: 包含陈述句、疑问句、口语
- 多样化股票: 均匀分布到不同市场
- 多样化难度: 至少包含 1 条 hard 难度
- description 字段要说明教了 LLM 什么查询技巧

请直接输出 JSON 数组。"""
```

## Runtime Text-to-SQL Prompt (used in `text_to_sql_tool`)

```python
TEXT_TO_SQL_PROMPT = """你是一个 PostgreSQL SQL 生成专家。根据用户问题生成查询 SQL。

## 数据库 Schema
{schema}

## 参考示例 (语义最接近的已有示例)
{examples}

## 约束
- 仅生成 SELECT 语句
- 使用上述 Schema 中的真实表名和列名
- 返回纯 SQL，不要包含解释

用户问题: {question}
"""
```
