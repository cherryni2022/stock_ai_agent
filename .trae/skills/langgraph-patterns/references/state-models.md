# Agent State Models

All Pydantic models used in `AgentState` for the Stock AI Agent.

## Intent Classification

```python
class IntentCategory(str, Enum):
    SIMPLE_QUERY = "simple_query"        # Single stock, single metric
    COMPARISON = "comparison"            # Multi-stock comparison
    COMPLEX_ANALYSIS = "complex_analysis" # Multi-step analysis
    CONVERSATIONAL = "conversational"    # Chat, follow-up
    TEXT_TO_SQL = "text_to_sql"          # Custom SQL query

class IntentClassification(BaseModel):
    category: IntentCategory
    confidence: float = Field(ge=0, le=1)
    requires_decomposition: bool
    suggested_tools: list[str]
    reasoning: str
```

## Entity Extraction

```python
class MarketType(str, Enum):
    CN = "CN"   # A-shares
    HK = "HK"   # Hong Kong
    US = "US"   # US stocks

class StockEntity(BaseModel):
    name: str                    # Display name ("苹果")
    ticker: str                  # Resolved ticker ("AAPL")
    market: MarketType
    raw_input: str | None = None # Original user input

class TimeRange(BaseModel):
    start: str | None = None
    end: str | None = None
    description: str  # "最近30天", "今年以来"

class ExtractedEntities(BaseModel):
    stocks: list[StockEntity] = []
    time_range: TimeRange | None = None
    metrics: list[str] = []      # ["MACD", "RSI", "收盘价"]
    comparison_type: str | None = None
```

## Task Decomposition

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SubTask(BaseModel):
    task_id: str
    tool_name: str
    tool_params: dict
    description: str
    depends_on: list[str] = []
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None

class DecompositionPlan(BaseModel):
    tasks: list[SubTask]
    execution_order: list[list[str]]  # [[layer0_ids], [layer1_ids], ...]
    reasoning: str
```

## MVP Stock Universe

```python
MVP_STOCKS = {
    "CN": [("601127", "赛力斯"), ("688981", "中芯国际")],
    "HK": [("9988.HK", "阿里巴巴"), ("0700.HK", "腾讯"), ("1024.HK", "快手")],
    "US": [("AAPL", "苹果"), ("MSFT", "微软"), ("NVDA", "英伟达"),
           ("GOOG", "谷歌"), ("AMZN", "亚马逊"), ("META", "Meta"), ("TSLA", "特斯拉")],
}
```
