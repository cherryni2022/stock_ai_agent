# Stock Question → SQL Seeds（覆盖总结）

## 目标
为 Text-to-SQL few-shot 提供覆盖全面的种子示例：既覆盖“单股查明细”，也覆盖“聚合、筛选、排名、分组、跨市场统一口径、业务型汇总”等常见分析查询形态，并确保 SQL 可在 PostgreSQL 上安全执行且符合本项目表结构。

## LLM 角色
你是资深股票数据分析工程师与 PostgreSQL 专家，擅长把中文股票分析问题转换为严格只读、可执行、结果可控（有排序与行数限制）的 SQL。

## 允许的数据表（白名单）
仅允许对以下表执行单条 `SELECT` / `WITH ... SELECT` 查询：
- 价格（日K）：`stock_daily_price` / `stock_daily_price_hk` / `stock_daily_price_us`
- 技术指标：`stock_technical_indicators` / `stock_technical_indicators_hk` / `stock_technical_indicators_us`
- 技术策略信号：
  - 趋势：`stock_technical_trend_signal_indicators*`
  - 均值回归：`stock_technical_mean_reversion_signal_indicators*`
  - 动量：`stock_technical_momentum_signal_indicators*`
  - 波动率：`stock_technical_volatility_signal_indicators*`
  - 统计套利：`stock_technical_stat_arb_signal_indicators*`
- 财务指标：`financial_metrics` / `financial_metrics_hk` / `financial_metrics_us`
- 基本信息：`stock_basic_info` / `stock_basic_hk` / `stock_basic_us`

> 说明：`*` 表示支持对应市场后缀（`_hk` / `_us`）版本与 A 股无后缀版本。

## 数据库表结构（关键字段）
### 统一约束与连接键
- 时间字段：`trade_date` 是字符串（`YYYY-MM-DD`），按时间分组常用 `SUBSTRING(trade_date, 1, 7)`（月份）
- 日K / 指标 / 信号：通常用 `(ticker, trade_date)` 作为自然连接键
- 财务：`(ticker, report_period, period)` 唯一；取“最新一期”常用 `ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY report_period DESC)`
- 基本信息：以 `ticker` 唯一

### A 股（CN）
- `stock_daily_price`：`ticker`，`trade_date`，`open/high/low/close`，`volume`，`pct_change`
- `stock_technical_indicators`：`ticker`，`trade_date`，`ma5/ma10/ma20/ma30/ma60`，`boll_upper/boll_middle/boll_lower`，`kdj_k/kdj_d/kdj_j`，`rsi_6/rsi_12/rsi_24`，`macd_diff/macd_dea/macd_hist`
- `stock_technical_trend_signal_indicators`：`ticker`，`trade_date`，`ema_8/ema_21/ema_55`，`adx/plus_di/minus_di`，`short_trend/medium_trend`，`trend_strength`，`trend_signal`，`trend_confidence`
- `stock_technical_mean_reversion_signal_indicators`：`ticker`，`trade_date`，`z_score`，`price_vs_bb`，`mean_reversion_signal`，`mean_reversion_confidence`
- `stock_technical_momentum_signal_indicators`：`ticker`，`trade_date`，`mom_1m/mom_3m/mom_6m`，`momentum_score`，`volume_confirmation`，`momentum_signal`，`momentum_confidence`
- `stock_technical_volatility_signal_indicators`：`ticker`，`trade_date`，`hist_vol_21`，`atr_14`，`atr_ratio`，`volatility_signal`，`volatility_confidence`
- `stock_technical_stat_arb_signal_indicators`：`ticker`，`trade_date`，`skew_63/kurt_63/hurst_exponent`，`stat_arb_signal`，`stat_arb_confidence`
- `financial_metrics`：`ticker`，`report_period`，`price_to_earnings_ratio`，`price_to_book_ratio`，`revenue_growth`，`net_margin`，`return_on_equity`，`debt_to_assets`，`current_ratio`
- `stock_basic_info`：`ticker`，`stock_name`，`industry`，`listing_date`，`total_market_value`，`float_market_value`，`latest_price`

### 港股（HK）
- `stock_daily_price_hk`：`ticker`，`trade_date`，`open/high/low/close`，`volume`，`pct_change`
- `stock_technical_indicators_hk`：字段与 `stock_technical_indicators_us` 同结构（MA/BOLL/KDJ/RSI/MACD）
- `stock_technical_trend_signal_indicators_hk`：字段与趋势信号同结构（`trend_signal/trend_confidence/trend_strength` 等）
- `stock_technical_mean_reversion_signal_indicators_hk`：字段与均值回归同结构
- `stock_technical_momentum_signal_indicators_hk`：`momentum_signal/momentum_confidence/momentum_score` 等
- `stock_technical_volatility_signal_indicators_hk`：`volatility_signal/volatility_confidence/atr_14` 等
- `stock_technical_stat_arb_signal_indicators_hk`：`stat_arb_signal/stat_arb_confidence` 等
- `financial_metrics_hk`：结构与 `financial_metrics` 相同维度（按港股数据）
- `stock_basic_hk`：`ticker`，`long_name`，`industry`，`sector`，`currency`，`market_cap`，`current_price`

### 美股（US）
- `stock_daily_price_us`：`ticker`，`trade_date`，`open/high/low/close`，`volume`，`pct_change`
- `stock_technical_indicators_us`：`ticker`，`trade_date`，`ma*`，`boll_*`，`kdj_*`，`rsi_*`，`macd_*`
- `stock_technical_trend_signal_indicators_us`：趋势信号（同结构）
- `stock_technical_mean_reversion_signal_indicators_us`：均值回归信号（同结构）
- `stock_technical_momentum_signal_indicators_us`：动量信号（同结构）
- `stock_technical_volatility_signal_indicators_us`：波动率信号（同结构）
- `stock_technical_stat_arb_signal_indicators_us`：统计套利信号（同结构）
- `financial_metrics_us`：结构与 `financial_metrics` 相同维度（按美股数据）
- `stock_basic_us`：`ticker`，`long_name`，`industry`，`sector`，`currency`，`market_cap`，`current_price`

## 查询形态覆盖（种子示例应包含）
### A. 单只股票查明细（Detail / Time Series）
- 最近 N 日价格、成交量、涨跌幅
- 最近 N 日技术指标（MACD/RSI/BOLL/均线等）
- 最近 N 日策略信号（trend/momentum/mean_reversion/volatility/stat_arb）
- 最近 N 期财务指标（ROE、PE、营收增长、负债率等）

### B. 联表明细（Join Detail）
- 股票价格表 ↔ 技术指标表：按 `(ticker, trade_date)` 对齐
- 股票价格表 ↔ 策略信号表：按 `(ticker, trade_date)` 对齐
- 股票价格表/财务 ↔ 基本信息：按 `ticker` 对齐（用于行业/市值维度）

### C. 窗口函数与 CTE（Window / CTE）
- `ROW_NUMBER()` 取每个 ticker 的最新/最近 N 条记录
- 用 `WITH` 封装“先取最近 N 行再聚合”的稳定模式

### D. 聚合统计（Aggregation）
- 时间窗口聚合：`AVG/MAX/MIN/STDDEV_SAMP/SUM/COUNT`
- 均值/最大最小/标准差/区间涨跌幅、成交量均值、波动率等
- 区间收益与统计：近 N 日涨跌幅标准差（`STDDEV_SAMP(pct_change)` 近似）、上涨天数、放量天数

### E. 条件筛选（Screening）
- 用 WHERE + HAVING 做“找符合条件的股票/日期”
- 数值阈值筛选：例如最近20日内`rsi_6 < 30`的日期数量、最近 60 日出现买入信号 ≥ 3 次的股票、最近N日内`trend_confidence > 0.7`的日期数量
- 组合条件筛选：例如“趋势 + 动量同时满足”的天数/股票列表

### F. 排名与 TopN（Ranking）
- 用窗口函数或排序取“涨幅最高/成交量最大/信号最强”的 Top N
- 例如最新一日/最近 N 日统计的 TopN（涨幅、成交量、trend_strength 等）
- 多股票对比：同口径对比多 ticker 输出排序

### G. 分组维度（Group By by time / industry）
- 按时间分组:按月/周聚合（`SUBSTRING(trade_date, 1, 7)` 作为月份维度）
- 按行业聚合（通过 `stock_basic_us.industry` 等字段 join 后 group by）

### H. 跨市场统一口径（Union）
- 用户问“跨市场对比/同口径查询”，SQL 往往需要 UNION ALL 把 *_us/_hk 和 CN 表拼起来再做排序/聚合
- 统一输出 schema：`market/ticker/trade_date/close/pct_change/...`
- 使用 `UNION ALL` 汇总 CN/HK/US 不同股票市场的信息，便于同一问题跨市场比较

## 生成约束（必须遵守）
- SQL 必须是单条语句：以 `SELECT` 或 `WITH` 开头，不能包含分号
- 禁止任何写操作或 DDL：`INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/TRUNCATE/...`
- 仅使用白名单表；如需中间结果，使用 CTE 名称（CTE 名称不视为表）
- `trade_date` 为字符串（`YYYY-MM-DD`），按时间分组优先用 `SUBSTRING`
- 输出应尽量带 `ORDER BY ... DESC` 与 `LIMIT`（防止返回过多行）
- 优先选择“可执行且可控”的 SQL：避免返回超大结果集，避免无过滤的全表扫描
- 如做 TopN/筛选，优先基于“最新交易日/最新一期财报”构造子查询/CTE 保证口径一致

## 种子示例数据格式（JSON）
文件：`stock_agent/data_pipeline/stock_question_sql.json`  
结构：数组，每个元素为：
- `question`: string
- `sql_query`: string
- `description`: string | null
- `category`: one of `price|indicator|signal|financial|meta|composite`
- `tables_involved`: string[]
- `difficulty`: `easy|medium|hard`
- `market`: `CN|HK|US|ALL`

## 输出格式示例（必须严格仿照）
输出必须是一个 JSON 数组，不要使用 Markdown 包裹，不要额外输出解释文本。

[
  {
    "question": "AAPL 最近 20 个交易日的收盘价是多少？",
    "sql_query": "SELECT trade_date, close FROM stock_daily_price_us WHERE ticker = 'AAPL' ORDER BY trade_date DESC LIMIT 20",
    "description": "查询美股 AAPL 最近 20 个交易日收盘价。",
    "category": "price",
    "tables_involved": ["stock_daily_price_us"],
    "difficulty": "easy",
    "market": "US"
  },
  {
    "question": "美股 MVP 股票最近一个交易日涨跌幅(pct_change) 排名前 3 的是谁？",
    "sql_query": "WITH latest AS (SELECT ticker, MAX(trade_date) AS trade_date FROM stock_daily_price_us WHERE ticker IN ('AAPL','MSFT','NVDA','GOOG','AMZN','META','TSLA') GROUP BY ticker), rows AS (SELECT p.ticker, p.trade_date, p.close, p.pct_change FROM stock_daily_price_us p JOIN latest l ON p.ticker = l.ticker AND p.trade_date = l.trade_date) SELECT ticker, trade_date, close, pct_change FROM rows ORDER BY pct_change DESC LIMIT 3",
    "description": "用每个 ticker 的最新交易日数据做排名。",
    "category": "price",
    "tables_involved": ["stock_daily_price_us"],
    "difficulty": "hard",
    "market": "US"
  }
]
