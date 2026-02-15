# 数据库初始化指南

本文档说明如何使用 SQL 脚本初始化 Supabase 数据库。

---

## 前置条件

- 已创建 Supabase 项目 (当前项目: `supabase-stockai`, region: `us-east-1`)
- 有 Supabase Dashboard 或 SQL Editor 的访问权限
- 项目 ID: `cafxewiutozyyblmthiz`

---

## SQL 脚本目录

所有脚本位于 `scripts/db/` 目录:

| 脚本 | 用途 | 说明 |
|------|------|------|
| `001_extensions.sql` | 启用扩展 | pgvector (向量检索) + uuid-ossp (UUID 生成) |
| `002_create_tables.sql` | 创建表 | 38 张表, 覆盖 A 股/港股/美股/向量/用户/Agent 日志 |
| `003_create_indexes.sql` | 创建索引 | B-tree 索引 + IVFFlat 向量索引 |
| `090_truncate_all.sql` | 清空数据 | 保留表结构, 重置自增 ID |
| `091_drop_all.sql` | 删除全部表 | 完全重建时使用 |

---

## 首次初始化

**适用场景**: 全新 Supabase 项目, 数据库中无任何自定义表。

按顺序在 Supabase SQL Editor 中执行:

```bash
# Step 1: 启用扩展
scripts/db/001_extensions.sql

# Step 2: 创建所有表 (38 张)
scripts/db/002_create_tables.sql

# Step 3: 创建索引
scripts/db/003_create_indexes.sql
```

> [!NOTE]
> `003_create_indexes.sql` 中的 IVFFlat 向量索引 **需要表中有数据后才能创建**。首次运行时向量索引部分可能报错, 可安全忽略。数据入库后再执行一次 `003` 即可创建向量索引。

---

## 重置数据 (保留表结构)

**适用场景**: 清空已有数据, 重新运行数据管道。

```bash
scripts/db/090_truncate_all.sql
```

该脚本会:
- 清空所有 38 张表的数据
- 重置 SERIAL 自增计数器
- 通过事务保证原子性

---

## 完全重建

**适用场景**: 表结构变更, 需要从零开始。

```bash
# Step 1: 删除所有表
scripts/db/091_drop_all.sql

# Step 2: 重新初始化
scripts/db/001_extensions.sql
scripts/db/002_create_tables.sql
scripts/db/003_create_indexes.sql
```

> [!CAUTION]
> `091_drop_all.sql` 会**删除所有表结构和数据**, 操作不可逆!

---

## 表清单 (38 张)

### A 股 — 11 张表

| 表名 | 说明 |
|------|------|
| `stock_basic_info_a` | 基本信息 (旧版, Tushare) |
| `stock_basic_info` | 基本信息 (Akshare) |
| `stock_company_info` | 公司详情 |
| `stock_daily_price` | 日 K 线 |
| `stock_technical_indicators` | 技术指标 (MA/BOLL/KDJ/RSI/MACD) |
| `stock_technical_trend_signal_indicators` | 趋势信号 |
| `stock_technical_mean_reversion_signal_indicators` | 均值回归信号 |
| `stock_technical_momentum_signal_indicators` | 动量信号 |
| `stock_technical_volatility_signal_indicators` | 波动率信号 |
| `stock_technical_stat_arb_signal_indicators` | 统计套利信号 |
| `financial_metrics` | 财务指标 |

### 港股 — 10 张表

| 表名 | 说明 |
|------|------|
| `stock_daily_price_hk` | 日 K 线 |
| `stock_technical_indicators_hk` | 技术指标 |
| `stock_technical_trend_signal_indicators_hk` | 趋势信号 |
| `stock_technical_mean_reversion_signal_indicators_hk` | 均值回归信号 |
| `stock_technical_momentum_signal_indicators_hk` | 动量信号 |
| `stock_technical_volatility_signal_indicators_hk` | 波动率信号 |
| `stock_technical_stat_arb_signal_indicators_hk` | 统计套利信号 |
| `stock_index_basic_hk` | 指数基本信息 |
| `financial_metrics_hk` | 财务指标 |
| `stock_basic_hk` | 基本信息 (yfinance) |

### 美股 — 10 张表

| 表名 | 说明 |
|------|------|
| `stock_daily_price_us` | 日 K 线 |
| `stock_technical_indicators_us` | 技术指标 |
| `stock_technical_trend_signal_indicators_us` | 趋势信号 |
| `stock_technical_mean_reversion_signal_indicators_us` | 均值回归信号 |
| `stock_technical_momentum_signal_indicators_us` | 动量信号 |
| `stock_technical_volatility_signal_indicators_us` | 波动率信号 |
| `stock_technical_stat_arb_signal_indicators_us` | 统计套利信号 |
| `stock_index_basic_us` | 指数基本信息 |
| `financial_metrics_us` | 财务指标 |
| `stock_basic_us` | 基本信息 (yfinance) |

### 向量嵌入 — 3 张表

| 表名 | 向量维度 | 说明 |
|------|----------|------|
| `news_embeddings` | VECTOR(1536) | 新闻/公告向量 |
| `sql_examples_embeddings` | VECTOR(1536) | SQL 示例向量 (Text-to-SQL RAG) |
| `conversation_embeddings` | VECTOR(1536) | 对话历史向量 |

### 用户 & Agent — 4 张表

| 表名 | 说明 |
|------|------|
| `users` | 用户信息 |
| `chat_sessions` | 聊天会话 (FK → users) |
| `chat_messages` | 聊天消息 (FK → chat_sessions) |
| `agent_execution_logs` | Agent 执行日志 |

---

## 数据管道执行 (初始化后)

数据库初始化完成后, 按顺序执行数据管道填充数据:

```bash
# 1. A 股数据获取
python -m stock_agent.data_pipeline.akshare_fetcher

# 2. 港股/美股数据获取
python -m stock_agent.data_pipeline.yfinance_fetcher

# 3. 技术指标计算 (依赖上面两步)
python -m stock_agent.data_pipeline.indicator_calculator

# 4. 新闻获取
python -m stock_agent.data_pipeline.news_fetcher

# 5. 新闻向量化入库
python -m stock_agent.data_pipeline.embedding_pipeline

# 6. SQL 示例向量化入库
python -m stock_agent.data_pipeline.sql_examples_seeder
```

> [!IMPORTANT]
> 数据管道执行完成后, 再运行一次 `003_create_indexes.sql` 以创建 IVFFlat 向量索引。

---

## 常见问题

### Q: IVFFlat 索引创建失败?
A: IVFFlat 索引需要表中有一定数据量。数据管道执行完毕后再执行 `003_create_indexes.sql`。

### Q: 如何验证表是否创建成功?
```sql
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- 预期结果: 38
```

### Q: pgBouncer 连接报错 DuplicatePreparedStatementError?
A: 项目已在 `stock_agent/database/session.py` 中禁用了 asyncpg 预处理语句缓存,
通过 `connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0}`。
