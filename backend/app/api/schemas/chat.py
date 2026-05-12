from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    query: str
    stream: bool = True


class Citation(BaseModel):
    title: str
    url: str = ""
    source_type: str


class AssetDataSchema(BaseModel):
    symbol: str
    price: float | None = None
    change: float | None = None
    change_pct: float | None = None
    trend: str | None = None
    market_metrics: dict | None = None
    chart_data: dict | None = None


class StructuredDataSchema(BaseModel):
    assets: list[AssetDataSchema]


class ChatResponse(BaseModel):
    answer_markdown: str
    structured_data: dict
    citations: list[dict]
    metadata: dict
