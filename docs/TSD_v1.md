# TSD.md — Financial Asset QA System
# Part 1 — Core System Architecture & Engineering Specification

---

# 1. Project Overview

## 1.1 Project Name

Financial Asset QA System

---

## 1.2 Project Goal

Design and implement an AI-native fullstack financial question-answering system powered by
LLMs, external market APIs, RAG pipelines, and LangGraph orchestration.

The system focuses on:

- Financial asset price analysis
- Market trend explanation
- Financial knowledge QA
- Structured and data-driven responses
- Real-time and streaming interaction

The system is intentionally designed as:

- AI-native
- modular
- testable
- engineering-oriented
- suitable for academic evaluation

This is NOT intended to be a production-grade distributed system.

The architecture prioritizes:

- development speed
- engineering clarity
- maintainability
- explainability
- testability

over:

- high availability
- horizontal scaling
- enterprise infrastructure

---

# 2. Finalized Technical Stack

## 2.1 Frontend

| Category | Technology |
|---|---|
| Framework | Next.js 15 |
| Language | TypeScript |
| UI Library | React 19 |
| Styling | TailwindCSS |
| Component System | shadcn/ui |
| Theme | next-themes (dark mode support) |
| Markdown Rendering | react-markdown |
| Markdown Extensions | remark-gfm |
| Syntax Highlighting | rehype-highlight |
| State Management | Zustand |
| Server State | TanStack Query |
| Charts | Recharts |
| E2E Testing | Playwright |

---

## 2.2 Backend

| Category | Technology |
|---|---|
| API Framework | FastAPI |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy |
| Database | SQLite |
| Vector Database | langchain-chroma (persist mode) |
| Embedding Model | langchain-huggingface (BAAI/bge-small-zh-v1.5) |
| Text Splitting | langchain-text-splitters |
| Document Loading | langchain-community (PyPDFLoader) |
| PDF Parsing | pypdf |
| Streaming | SSE |
| Web Search | langchain-tavily (TavilySearch) |
| Web Extract | langchain-tavily (TavilyExtract) |
| Testing | pytest |
| Async Testing | pytest-asyncio |
| HTTP Testing | httpx |

---

## 2.3 External Services

| Service | Usage |
|---|---|
| Yahoo Finance | Market data (via `yfinance`) |
| Tavily Search | Web search for financial news |
| Tavily Extract | Web content extraction for full article text |
| MiniMax API (OpenAI-compatible) | LLM inference (MiniMax-M2.7 model) |

---

## 2.4 LLM Model Configuration

During development and testing, all LLM tasks use **MiniMax-M2.7**:

| Task | Model | Method |
|---|---|---|
| Intent Classification | MiniMax-M2.7 | function_calling |
| Ticker Extraction | MiniMax-M2.7 | function_calling (two-phase: direct + Tavily search) |
| Response Generation | MiniMax-M2.7 | chat completion + streaming |
| Merge (Hybrid Flow) | MiniMax-M2.7 | chat completion |
| Title Generation | MiniMax-M2.7 | chat completion |
| Unsupported Query Rejection | MiniMax-M2.7 | chat completion |

All model configuration is externalized to `.env`:

```
MINIMAX_API_KEY=...
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7
TAVILY_API_KEY=...
```

The LLM provider abstraction supports any OpenAI-compatible API — switching
to a different provider only requires changing environment variables.

---

# 3. High-Level System Architecture

## 3.1 Architecture Philosophy

The project follows:

```text
Thin FastAPI + Fat LangGraph
```

FastAPI acts as:

- transport layer
- request validation layer
- streaming layer

LangGraph acts as:

- application core
- orchestration engine
- agent workflow runtime

---

## 3.2 High-Level Architecture Diagram

```text
+--------------------------------------------------+
|                  Frontend (Next.js)              |
|--------------------------------------------------|
| Session Sidebar | Chat UI | Market Info Panel    |
+--------------------------|-----------------------+
                           |
                           v
+--------------------------------------------------+
|                 FastAPI Backend                  |
|--------------------------------------------------|
| REST API | SSE Streaming | Validation | Routing  |
+--------------------------------------------------+
                           |
                           v
+--------------------------------------------------+
|               LangGraph Workflow                 |
|--------------------------------------------------|
| Intent Router (LLM-based)                        |
|   ├── Market Data Flow                           |
|   ├── RAG Flow                                   |
|   ├── Hybrid Flow (market + news + RAG sequential)    |
|   └── Unsupported Query Flow                     |
+--------------------------------------------------+
                           |
         +-----------------+-----------------+
         |                                   |
         v                                   v
+--------------------+        +--------------------------+
| Market Data Tools  |        | RAG Pipeline             |
|--------------------|        |--------------------------|
| Yahoo Finance      |        | Chroma Vector Search     |
| Tavily Search      |        | Embedding Retrieval      |
| Tavily Extract     |        | Local CrossEncoder Rerank |
+--------------------+        +--------------------------+
         |                                   |
         +-----------------+-----------------+
                           |
                           v
+--------------------------------------------------+
|                 Persistence Layer                |
|--------------------------------------------------|
| SQLite | ChromaDB (persist) | Local File Storage |
+--------------------------------------------------+
```

---

# 4. Core Architectural Decisions

## 4.1 Frontend-Backend Separation

The system uses strict frontend-backend separation.

Frontend responsibilities:

- rendering
- UI state
- streaming rendering
- chart visualization
- session navigation

Backend responsibilities:

- orchestration
- LLM interaction
- RAG
- market retrieval
- memory reconstruction
- persistence

---

## 4.2 Single LangGraph Workflow

The system intentionally avoids:

```text
multiple independent agents
```

Instead, it uses:

```text
single graph + multiple tool nodes
```

Reasoning:

- simpler orchestration
- easier debugging
- lower development complexity
- more suitable for 3-4 day implementation timeline

---

## 4.3 Hybrid Structured Response Strategy

The backend response format is:

```json
{
  "answer_markdown": "...",
  "structured_data": {},
  "citations": [],
  "metadata": {}
}
```

This combines:

| Capability | Solution |
|---|---|
| Natural UI rendering | Markdown |
| Structured testing | JSON |
| Financial visualization | Structured data |
| Streaming UX | Markdown |
| Engineering reliability | Typed metadata |

---

## 4.4 Fail-Fast Architecture

The system intentionally follows:

```text
fail-fast philosophy
```

No fallback behavior will be implemented.

Example:

- market API failure → explicit error
- vector DB failure → explicit error
- LLM parsing failure → explicit error

Reasoning:

- easier debugging
- lower implementation complexity
- more deterministic behavior
- appropriate for academic project scope

---

# 5. Frontend Architecture

## 5.1 Frontend Layout

The frontend follows a 3-panel architecture:

```text
+---------------------------------------------------------+
| Sidebar |                Chat Area        | Market Info |
+---------------------------------------------------------+
```

---

## 5.2 Sidebar Responsibilities

The left sidebar manages:

- conversation list
- session switching
- new chat creation
- auto-generated titles (via LLM after first user message)

---

## 5.3 Chat Area Responsibilities

The center chat area manages:

- markdown rendering (react-markdown + remark-gfm + rehype-highlight)
- streaming response rendering (fetch + ReadableStream, NOT EventSource)
- user input
- loading states (thinking indicator during tool execution)
- citations display
- tool execution status (driven by SSE `status` events: "Fetching market data...", "Searching latest news...", etc.)

---

## 5.4 Market Panel Responsibilities

The right market panel displays per-asset market data.

**Single asset:** Shows PriceCard, TrendChart, and MetricsCard for the detected ticker.

**Multiple assets:** A Tab bar appears at the top of the panel (e.g., `TSLA | AAPL | BABA`).
Each tab displays a full set of PriceCard + TrendChart + MetricsCard for the selected ticker.
The first asset in the list is selected by default.

The panel updates dynamically based on:

```text
structured_data.assets
```

returned by backend responses. `assets` is a list of `AssetData` objects (one per ticker).

---

## 5.5 Dark Mode

Implemented via `next-themes` + Tailwind `dark:` classes.

- Theme switcher in the header/footer
- System preference detection on first load
- All shadcn/ui components automatically support dark mode

---

# 6. Backend Architecture

## 6.1 Backend Layers

```text
api/           (routes + schemas + dependencies)
  ↓
graph/         (LangGraph orchestration)
  ↓
tools/         (external service integrations)
  ↓
services/      (business logic: session_service, rag_service, streaming_service, title_service)
  ↓
repositories/  (DB access abstraction)
  ↓
database/      (SQLAlchemy ORM + SQLite)
```

---

## 6.2 Layer Responsibilities

| Layer | Responsibility |
|---|---|
| api | transport + SSE + validation |
| graph | LangGraph orchestration: nodes, edges, state |
| tools | external API wrappers (stateless) |
| services | business workflows, streaming lifecycle, title generation |
| repositories | DB CRUD, query abstraction, transaction isolation |
| database | SQLAlchemy models, engine, migrations |

---

## 6.3 Backend Design Principles

The backend enforces:

- strict typing (Python type hints everywhere)
- repository abstraction (graph nodes never touch DB directly)
- isolated tool layer (graph nodes never call external APIs directly)
- graph-based orchestration
- Pydantic v2 validation
- async-first design (`async def` for all endpoints)
- all structured output via `model.with_structured_output(schema, method="function_calling")`

---

# 7. LangGraph Workflow Design

## 7.1 Graph Overview

```text
User Query
    ↓
Intent Router (LLM-based, function_calling)
    ├── "market" → Market Query Flow
    ├── "rag"    → RAG Query Flow
    ├── "hybrid" → Hybrid Query Flow
    └── "unsupported" → Unsupported Query Flow
```

---

## 7.2 Intent Classification

Intent classification uses **LLM with function_calling** (NOT keyword matching).

```python
class IntentOutput(BaseModel):
    intent: Literal["market", "rag", "hybrid", "unsupported"]

# Usage:
intent_result = model.with_structured_output(
    IntentOutput,
    method="function_calling",
).invoke(intent_prompt + user_query)
```

The LLM directly classifies the intent — no confidence threshold is needed. The intent
determines the graph route. Ticker extraction is a **separate two-phase process** inside market_node
(not part of intent classification):
1. **Phase 1 (Decision):** LLM with `TickerDecision` schema decides `action="direct"`
   (confidently maps company/product to ticker) or `action="search"` (uncertain,
   provides a Chinese search query)
2. **Phase 2 (Search → Extract):** Only triggered when `action="search"` — backend
   runs Tavily search with the LLM-provided query, then LLM with `TickerList`
   schema extracts tickers from the search results. Cannot loop back.

Intent examples:
- **market**: "特斯拉当前股价是多少？", "显示苹果的市值和市盈率", "英伟达这周股价表现如何？"
- **rag**: "什么是市盈率？", "解释现金流折现估值法", "EBITDA 是什么意思？"
- **hybrid**: "为什么特斯拉股价上涨了？市盈率能说明什么？", "基于英伟达的当前市盈率解释其估值"
- **unsupported**: "写一首关于股票的诗", "给我讲个笑话"

---

## 7.3 Market Query Flow

```text
User Query → Intent Node (routes to "market")
    ↓
Market Data Tool Node (market_node)
    ├── Phase 1 — LLM Decision (TickerDecision schema): mapping table fed as context
    │   (not gate). LLM evaluates every company/product in the query: action="direct"
    │   (confident → output all tickers, skipping unlisted companies) or action="search"
    │   (any uncertainty → output Chinese search query)
    ├── Phase 2 — Tavily Search + LLM Extract (TickerList schema): only triggered
    │   by action="search". Single Tavily search (pure query, no "stock news" suffix),
    │   feeds results to LLM for ticker extraction. Schema prevents another search
    ├── Data Fetching: for each ticker, fetch price + history from Yahoo Finance
    │   (multi-asset = asyncio.gather for parallel fetching)
    ├── Normalize + cache results per ticker (TTLCache, 60s TTL)
    └── Store in state.market_data (dict keyed by symbol), state.tickers (list)
    ↓
News Node (Tavily Search)
    ├── Search for "[TICKER] stock news" for each ticker
    └── Return top 5 results per ticker with URLs and snippets
    ↓
Extract Node (Tavily Extract)
    ├── Extract full article text from top 2 news URLs per ticker
    └── Store extracted content in state.extracted_articles
    ↓
Response Generation Node (generation_node)
    ├── Build market analysis prompt with fetched data + news + extracted articles
    ├── LLM generates markdown response (streaming tokens to frontend)
    └── Extract citations via function_calling (LLM only extracts citations)
    ↓
Structured Formatter Node (formatter_node)
    ├── Build structured_data.assets[] from state.market_data (ALL from real data:
    │   symbol, price, change, change_pct, trend, market_metrics, chart_data)
    ├── Assemble + normalize citations
    └── Set final_response
    ↓
Stream to Frontend via SSE
```

---

## 7.4 RAG Query Flow

```text
User Query → Intent Node (routes to "rag")
    ↓
Retrieval Node
    ├── Embed user query
    ├── Similarity search in Chroma (top-k = 8)
    └── Return retrieved chunks with metadata (may be empty if no relevant docs)
    ↓
Local CrossEncoder Rerank Node
    ├── BGE-reranker-base scores each chunk against query (output top-4)
    ├── If retrieval returned no chunks: skip rerank, set empty context
    └── Discard irrelevant chunks
    ↓
Context Builder
    ├── Assemble final context from reranked chunks
    ├── If context is empty: clearly mark "RAG knowledge base has no relevant content"
    └── Include document source metadata for non-empty context
    ↓
Response Generation Node
    ├── Build RAG prompt with context + user query
    ├── If context is empty: LLM uses its own knowledge, but response MUST
    │   explicitly state that no relevant documents were found in the knowledge base
    ├── LLM generates grounded markdown response
    └── Extract citations
    ↓
Stream to Frontend via SSE
```

---

## 7.5 Hybrid Query Flow

Hybrid queries combine market data AND RAG retrieval sequentially:

```text
User Query → Intent Node (routes to "hybrid")
    ↓
Phase 1: Market Data Node (Yahoo Finance)
    ↓
Phase 2: News Node (Tavily Search)
    ↓
Phase 3: Extract Node (Tavily Extract — top 2 articles)
    ↓
Phase 4: Retrieval Node (Chroma search)
    ↓
Phase 5: Rerank Node (CrossEncoder selects best chunks)
    ↓
Phase 6: Merge Node (LLM synthesizes all context: market + news + extracted articles + RAG)
    ↓
Phase 7: Response Generation Node
    (LLM generates final markdown response)
    ↓
Phase 8: Structured Formatter Node
    ↓
Stream to Frontend via SSE
```

The hybrid flow runs both phases sequentially (market data + news + extract first, then RAG).
All gathered raw data — market metrics, news articles, extracted article full text, and
retrieved document chunks — is passed directly to generation_node for the final answer.
No intermediate LLM-based summarization step; the generation prompt includes all first-hand
data to preserve information fidelity.

Example hybrid query:

```text
"为什么特斯拉股价下跌？市盈率能说明什么含义？"
```

---

## 7.6 Unsupported Query Flow

Unsupported queries still route through LLM for a friendly, helpful rejection:

```text
User Query → Intent Node (routes to "unsupported")
    ↓
Rejection Node
    ├── LLM generates friendly, helpful message
    ├── Explains the system's scope (market data + financial knowledge)
    └── Suggests rephrasing or trying a different question
    ↓
Stream to Frontend via SSE
```

The rejection message should be polite and informative, not a cold error.

---

## 7.7 Multi-Asset Query Support

The system supports queries involving multiple stock tickers (e.g., "Compare TSLA and AAPL").

### Backend

- **Ticker Extraction:** Two-phase LLM: mapping table as context (not gate) →
  `TickerDecision` (direct or search). All companies evaluated by LLM; unlisted
  ones are skipped. If search needed, Tavily runs once (pure query, no suffix).
- **Data Fetching:** Yahoo Finance data is fetched **in parallel** for all tickers
  via `asyncio.gather(asyncio.to_thread(...) for each ticker)`. Results are stored
  in `state["market_data"]` keyed by symbol.
- **News Search:** Tavily search runs for each ticker individually. Results are merged
  into `state["news_data"]`.
- **Structured Output:** `StructuredData.assets` is a `list[AssetData]`, one entry per ticker.
  Each `AssetData` includes `symbol`, `price`, `change`, `change_pct`, `trend`,
  `market_metrics`, and `chart_data`.

### Frontend Market Panel

- **Single asset:** No change from the base design — PriceCard, TrendChart, MetricsCard
  render directly for the single ticker.
- **Multiple assets:** A Tab bar appears at the top of the Market Panel with one tab
  per ticker (e.g., `TSLA | AAPL | BABA`). The first asset is selected by default.
  Each tab displays a complete set of PriceCard + TrendChart + MetricsCard.
  Tab switching is purely client-side with no additional API calls.

### Design Principle

No backward compatibility layer is needed. The `assets` list is the single source of
truth. Single-asset queries produce a list of length 1; multi-asset queries produce a
list of length N. The frontend renders tabs conditionally: tabs hidden when N=1, shown
when N>1.

---

## 7.8 Dual-Track Streaming Architecture

The system uses a **dual-track** streaming design — the frontend receives tokens in
real-time while the graph internally retains the complete markdown for post-processing.

### Design Rationale

```
Track 1 (SSE):  tokens forwarded to frontend as soon as LLM produces them
Track 2 (Graph): complete markdown accumulated in state.answer_markdown,
                 then post-processed by formatter_node after generation
```

This avoids the common pitfall where structured extraction blocks streaming UX.
The formatter and structured extraction execute AFTER the full markdown is generated,
but the frontend has already been rendering tokens incrementally throughout.

### Mechanism

1. **`_token_queue` injection**: an `asyncio.Queue` is attached to `GraphState` at
   invocation time. It is NOT serialized by LangGraph — it exists only for the
   duration of one graph execution.

2. **generation_node** is the core of both tracks:
   - Uses `model.astream_events()` to iterate over tokens
   - Immediately `await _token_queue.put({"type": "token", "content": token})` for each
   - Accumulates the full markdown string in `state["answer_markdown"]`
   - After generation completes: calls `model.with_structured_output()` to extract
     ONLY `list[Citation]` (market data is NOT extracted from LLM — see formatter_node)

3. **formatter_node** receives the complete `answer_markdown` and fills in ALL
   market-related fields in `structured_data.assets[]` from `state.market_data`
   (Yahoo Finance actual data):
   - `symbol`, `price`, `change`, `change_pct`, `trend`, `market_metrics`, `chart_data`
   - All of these come from real yfinance data, never LLM-generated.
   - Also normalizes citations into final format.

4. **SSE endpoint** (`POST /api/chat`) runs the graph in a background `asyncio.Task`
   while simultaneously reading from `_token_queue` and yielding SSE events.

### Streaming Timeline

```
T=0ms     User clicks Send → POST /api/chat → SSE connection opened
T=50ms    intent_node completes
T=100ms   status: {node: "market_data", status: "running"} → frontend shows "Fetching market data..."
T=500ms   market_node completes
T=550ms   status: {node: "news", status: "running"} → frontend shows "Searching latest news..."
T=1000ms  news_node completes
T=1050ms  status: {node: "extract", status: "running"} → frontend shows "Extracting article content..."
T=2000ms  extract_node completes
T=2050ms  status: {node: "generation", status: "running"} → frontend shows "Generating response..."
T=2100ms  generation_node starts → LLM begins streaming tokens
          first "token" event clears status indicator → incremental markdown rendering begins
T=2100-4000ms  Tokens stream to frontend in real-time (incremental rendering)
T=4000ms  LLM generation complete → citations extraction runs
T=4050ms  formatter_node runs → all market data injected into structured_data
T=4100ms  Graph reaches END → structured_data + citations + done events sent → SSE closes
```

### SSE Endpoint Implementation

```python
@router.post("/api/chat")
async def chat(request: ChatRequest):
    token_queue: asyncio.Queue = asyncio.Queue()

    # Build initial state with queue injected
    initial_state = build_initial_state(request, token_queue)

    async def event_stream():
        # Run graph in background task
        task = asyncio.create_task(run_graph(initial_state))

        # Forward events from queue to SSE
        while True:
            item = await token_queue.get()
            if item["type"] == "status":
                yield f"event: status\ndata: {json.dumps({'node': item['node'], 'status': item['status']})}\n\n"
            elif item["type"] == "token":
                yield f"event: token\ndata: {json.dumps({'content': item['content']})}\n\n"
            elif item["type"] == "done":
                yield f"event: structured_data\ndata: {json.dumps(item['structured_data'])}\n\n"
                yield f"event: citations\ndata: {json.dumps(item['citations'])}\n\n"
                yield f"event: done\ndata: {json.dumps({'session_id': item['session_id']})}\n\n"
                break
            elif item["type"] == "error":
                yield f"event: error\ndata: {json.dumps(item['error'])}\n\n"
                break

        await task  # ensure graph fully completes

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

### generation_node Internal Logic

```python
async def generation_node(state: GraphState) -> GraphState:
    if state.get("error"):
        return state

    messages = build_generation_messages(state)  # system prompt + history + context
    queue = state["_token_queue"]
    model = get_llm_provider().get_model()

    # Emit status before generation starts
    await queue.put({"type": "status", "node": "generation", "status": "running"})

    # Track 1 + Track 2: stream tokens AND accumulate
    full_response = ""
    async for event in model.astream_events(messages, version="v2"):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                full_response += chunk.content
                await queue.put({"type": "token", "content": chunk.content})

    state["answer_markdown"] = full_response

    # Extract citations only (market data comes from real yfinance data in formatter_node)
    citations_result = await model.with_structured_output(
        CitationList, method="function_calling"
    ).ainvoke(citation_prompt + full_response)
    state["citations"] = [c.model_dump() for c in citations_result.citations]

    return state
```

### Node Status Events

Each graph node emits a `status` event to `_token_queue` at the start of its execution
(before doing any work). This allows the frontend to show a real-time tool execution
indicator. Example from `market_node`:

```python
async def market_node(state: GraphState) -> GraphState:
    if state.get("error"):
        return state
    queue = state["_token_queue"]
    await queue.put({"type": "status", "node": "market_data", "status": "running"})
    # ... fetch market data ...
```

Every node follows this pattern. The `generation_node` emits its status event immediately
before starting `astream_events`; the first `token` event clears the indicator on the
frontend side. Nodes that are skipped (e.g., `market_data` in RAG-only flow) never emit
status events.

### Graph Runner

```python
async def run_graph(state: GraphState) -> None:
    compiled_graph = get_compiled_graph()
    queue = state["_token_queue"]
    try:
        result = await compiled_graph.ainvoke(state)
        # Signal SSE stream to complete
        await queue.put({
            "type": "done",
            "structured_data": result.get("structured_data"),
            "citations": result.get("citations"),
            "session_id": result["session_id"],
        })
    except Exception as e:
        logger.error(f"Graph execution failed: {e}", exc_info=True)
        await queue.put({
            "type": "error",
            "error": {"type": type(e).__name__, "message": str(e)},
        })
```

### Error Handling in Streaming

When a node sets `state["error"]`, subsequent nodes detect it and skip work
(fail-fast). The graph still reaches END. The `run_graph` function catches
exceptions at the graph level and sends an SSE `error` event, which immediately
terminates the stream. The frontend **keeps any partially rendered markdown**
from tokens already received, then displays the error via a toast notification
with a retry button. Partial content is preserved so the user can see what was
generated before the failure.

---

# 8. Typed Graph State

## 8.1 Strict Typed State

LangGraph state must use:

```python
TypedDict
```

No untyped state objects are allowed.

---

## 8.2 GraphState Schema

```python
from typing import TypedDict, Optional


class GraphState(TypedDict):
    """LangGraph workflow state.

    All fields serializable EXCEPT _token_queue, which is injected at
    runtime and used only for real-time SSE token forwarding.
    """

    session_id: str

    user_query: str

    # Reconstructed conversation history (loaded from DB at start)
    # OpenAI format: [{"role": "user"|"assistant", "content": "..."}]
    # system prompt is dynamically prepended, not stored in messages
    messages: list[dict]

    # Intent routing
    intent: str                      # "market" | "rag" | "hybrid" | "unsupported"

    # RAG
    retrieved_docs: list[dict]       # top-k chunks from Chroma (k=8)
    reranked_docs: list[dict]        # top-N chunks after CrossEncoder rerank (N=4)

    # Market data
    tickers: list[str]               # detected ticker symbols from query (e.g. ["TSLA", "AAPL"])
    market_data: dict                # raw normalized market data per ticker
    news_data: list[dict]            # Tavily search results
    extracted_articles: list[dict]   # Tavily Extract full article text per URL

    # Citations
    citations: list[dict]            # [{"title": "...", "url": "...", "source_type": "..."}]

    # Structured data for frontend panel/charts
    structured_data: dict            # active_asset, price, change_pct, trend, metrics, chart_data

    # Final output
    final_response: str              # markdown answer (complete, set by formatter_node)
    answer_markdown: str             # raw markdown from generation_node (before formatting)

    # Error state (fail-fast)
    error: Optional[dict]            # {"type": "...", "message": "..."}

    # Runtime-only: asyncio.Queue for real-time SSE token forwarding
    # NOT serialized by LangGraph — injected at graph invocation time
    _token_queue: Any                # asyncio.Queue[dict]
```

---

## 8.3 State Design Principles

State objects must remain:

- serializable (all values JSON-serializable, no lambdas, no complex objects)
- deterministic
- debuggable
- minimal (don't carry data between nodes that don't need it)
- explicit (no hidden state mutations across nodes)

---

# 9. Persistence Architecture

## 9.1 Databases

| Database | Usage | Path |
|---|---|---|
| SQLite | relational persistence | `./backend/data/sqlite.db` (created at runtime) |
| Chroma | vector retrieval (persist mode) | `./backend/chroma_db/` (via langchain-chroma) |

---

## 9.2 SQLite Responsibilities

SQLite stores:

- sessions
- messages
- document metadata
- ingestion jobs

SQLite does NOT store:

- embeddings
- market cache (in-memory TTLCache only)
- raw vector data

---

## 9.3 Chroma Responsibilities

Chroma (via `langchain-chroma`, persist mode) stores:

- document chunks
- embeddings
- vector metadata

Chroma is initialized via:

```python
from langchain_chroma import Chroma

vector_store = Chroma(
    collection_name="financial_knowledge",
    embedding_function=embeddings,  # HuggingFaceEmbeddings("BAAI/bge-small-zh-v1.5")
    persist_directory="./backend/chroma_db",
)
```

The collection is **created on first use** if it does not already exist — no manual
setup required. Chroma data persists across restarts — no need to re-ingest
documents on every startup.

---

# 10. Database Schema

## 10.1 chat_sessions

```sql
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,              -- UUID4
    title TEXT NOT NULL,              -- auto-generated via LLM after first query
    created_at TEXT NOT NULL,         -- UTC ISO 8601
    updated_at TEXT NOT NULL          -- UTC ISO 8601
);
```

---

## 10.2 chat_messages

```sql
CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,              -- UUID4
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,               -- "user" | "assistant" | "system"
    content TEXT NOT NULL,            -- markdown for assistant, plain text for user
    metadata_json TEXT,               -- JSON string of structured_data + citations
    created_at TEXT NOT NULL,         -- UTC ISO 8601

    FOREIGN KEY(session_id)
    REFERENCES chat_sessions(id)
);
```

---

## 10.3 knowledge_documents

```sql
CREATE TABLE knowledge_documents (
    id TEXT PRIMARY KEY,              -- UUID4
    title TEXT NOT NULL,
    source TEXT NOT NULL,             -- original file name
    chunk_count INTEGER NOT NULL,
    created_at TEXT NOT NULL          -- UTC ISO 8601
);
```

---

## 10.4 ingestion_jobs

```sql
CREATE TABLE ingestion_jobs (
    id TEXT PRIMARY KEY,              -- UUID4
    file_name TEXT NOT NULL,
    status TEXT NOT NULL,             -- "pending" | "processing" | "completed" | "failed"
    error_message TEXT,
    created_at TEXT NOT NULL          -- UTC ISO 8601
);
```

---

## 10.5 ID Generation

All primary keys use **UUID4** (generated via Python `uuid.uuid4()` or equivalent in TypeScript).
No auto-increment integers. No custom prefixes.

---

# 11. Conversation Memory Design

## 11.1 Memory Strategy

The system supports:

```text
multi-turn conversational memory
```

using:

```text
database reconstruction
```

instead of persistent agent memory runtime.

---

## 11.2 Memory Flow

```text
User sends query
    ↓
Load session messages from SQLite (via MessageRepository)
    ↓
Reconstruct conversation history as list[dict]
    ↓
Inject into GraphState.messages
    ↓
Graph executes (intent → tools → generation)
    ↓
Persist user message + assistant response + metadata to SQLite
```

---

## 11.3 Session Switching

Frontend supports:

- switching sessions via sidebar
- restoring previous conversations (load messages from SQLite)
- continuing old conversations (append new messages to existing session)

---

# 12. RAG Architecture

## 12.1 Supported File Types

Supported:

- `.pdf`
- `.md`
- `.txt`

Not supported:

- `.docx`
- `.pptx`
- `.html`

---

## 12.2 RAG Pipeline

```text
Documents (uploaded via API)
    ↓
Parse (extract text based on file type)
    ↓
Chunk (split text into overlapping chunks)
    ↓
Embed (BAAI/bge-small-zh-v1.5, local model)
    ↓
Chroma Storage (persist to disk)
    ↓
Similarity Retrieval (cosine similarity, top-k=8)
    ↓
Local CrossEncoder Rerank (BAAI/bge-reranker-base selects top-4)
    ↓
Context Builder (assemble final context)
    ↓
LLM Generation (grounded in retrieved context)
```

---

## 12.3 Chunking Strategy

```text
chunk_size = 800 characters
chunk_overlap = 150 characters
```

Use LangChain's `RecursiveCharacterTextSplitter`.

---

## 12.4 Embedding Model

```text
BAAI/bge-small-zh-v1.5
```

Chinese-optimized local model (24M params, 512 dimensions) loaded via
`langchain_huggingface.HuggingFaceEmbeddings` with query instruction:
`"为这个句子生成表示以用于检索相关文章："`

```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-zh-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
```

---

## 12.5 Chroma Collection

All documents are stored in a single Chroma collection:

```text
collection_name = "financial_knowledge"
```

The collection is created on first use and persisted to disk under `CHROMA_PATH`.

---

## 12.6 Local CrossEncoder Rerank Strategy

The rerank stage uses a local CrossEncoder model:

```text
BAAI/bge-reranker-base (HuggingFace, 278M params)
```

Loaded via `sentence_transformers.CrossEncoder`, runs entirely on local CPU — no API calls.

Workflow:

```text
Top-8 chunks from Chroma
    ↓
CrossEncoder scores each (query, chunk) pair
    ↓
Sort by relevance score descending, select top-4
    ↓
Final context assembly (ordered by relevance)
```

---

## 12.7 Chunk Metadata

Every chunk stored in Chroma must include:

```json
{
  "document_id": "<UUID4>",
  "document_name": "financial_glossary.md",
  "chunk_index": 0,
  "source": "uploaded"
}
```

---

## 12.8 Knowledge Base Auto-Ingestion on Startup

On first startup (or when `knowledge_base/` directory has files not yet ingested),
the system automatically ingests all supported files:

```text
On FastAPI startup event:
    ↓
Scan knowledge_base/ for .pdf, .md, .txt files
    ↓
For each file not already tracked in knowledge_documents table:
    ├── Parse text from file
    ├── Chunk (800 char chunks, 150 char overlap)
    ├── Embed using BAAI/bge-small-zh-v1.5
    ├── Store chunks in Chroma collection "financial_knowledge"
    └── Create KnowledgeDocument record in SQLite
    ↓
Log ingestion summary (files processed, chunks created)
```

If `knowledge_base/` is empty or all files are already ingested, the startup is a no-op.

This ensures the RAG system has pre-loaded knowledge documents available for retrieval
without requiring manual uploads via the upload API. The upload API is still available
for adding new documents at runtime.

---

# 13. Market Data Architecture

## 13.1 Market Data Source

Primary source:

```text
Yahoo Finance
```

using:

```python
yfinance
```

---

## 13.2 Market Data Capabilities

The system supports:

- current price
- daily change (absolute and percentage)
- 7-day historical prices (for charts)
- 30-day historical prices (for charts)
- PE ratio
- market cap
- trading volume

---

## 13.3 Simple TTL Cache

Market data caching uses:

```python
cachetools.TTLCache
```

Configuration:

```python
market_data_cache = TTLCache(maxsize=128, ttl=60)  # 60 seconds TTL
```

No Redis or distributed cache will be used.

---

## 13.4 News Search

Market queries automatically trigger news search via **Tavily Search** (official `langchain-tavily` package):

```python
from langchain_tavily import TavilySearch

search_tool = TavilySearch(
    max_results=5,
    tavily_api_key=settings.tavily_api_key,
)
```

- Search for "[TICKER] stock news" for each ticker
- Return top 5 results with URLs and snippets
- Extract full content via **Tavily Extract** (`langchain-tavily` `TavilyExtract`) for top 2 articles per ticker

---

# 14. API Architecture

## 14.0 Streaming vs Non-Streaming

The `/api/chat` endpoint supports two modes via `stream` parameter:

- **Streaming (`stream=True`, default):** Returns `text/event-stream`. The full LangGraph
  workflow executes, and results are delivered incrementally via SSE events. Used by the
  frontend for real-time UX.

- **Non-Streaming (`stream=False`):** Returns `application/json`. Uses a simpler path:
  the graph executes via `compiled_graph.ainvoke()` directly (no `_token_queue`, no
  SSE), and the final state is serialized as `ChatResponse`. Used for testing and
  programmatic API consumption.

Both modes execute the SAME graph nodes — only the delivery mechanism differs.
Non-streaming skips the SSE infrastructure entirely; streaming adds the dual-track
queue layer on top.

---

## 14.1 API Design Principles

All APIs must:

- use Pydantic v2 schemas
- be fully typed (request + response)
- support async execution
- return deterministic structures
- use UTC ISO 8601 timestamps
- use JSON exclusively

---

## 14.2 Main API Categories

| Category | Purpose |
|---|---|
| Chat APIs | conversation + streaming |
| Session APIs | session CRUD |
| RAG APIs | document upload + ingestion |
| Health APIs | system diagnostics |

---

## 14.3 Main Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/chat` | send message, returns SSE stream or JSON |
| GET | `/api/sessions` | list all sessions |
| POST | `/api/sessions` | create new session (title defaults to "新对话") |
| GET | `/api/sessions/{id}` | load session detail + messages |
| PATCH | `/api/sessions/{id}/title` | update session title (used after async title generation) |
| DELETE | `/api/sessions/{id}` | delete session + all messages |
| POST | `/api/rag/upload` | upload document for ingestion |
| GET | `/api/health` | system health check |

---

# 15. SSE Streaming Protocol

## 15.1 Streaming Strategy

The system uses:

```text
event-based SSE (text/event-stream)
```

instead of raw token streaming.

Frontend consumes via `fetch` + `ReadableStream` (NOT `EventSource`):
- Supports POST requests
- Supports custom headers (future auth expansion)
- Supports cancellation via `AbortController`

---

## 15.2 SSE Event Types

### Status Event (sent when a graph node starts executing)

```text
event: status
data: {"node": "market_data", "status": "running"}
```

Frontend uses this to show a tool execution indicator (e.g., "Fetching market data...").
Each graph node emits a status event when it begins work. The frontend clears the
indicator when `token` events start arriving (generation has begun).

Node names sent via status events:
- `market_data` → "Fetching market data..."
- `news` → "Searching latest news..."
- `extract` → "Extracting article content..."
- `retrieval` → "Searching knowledge base..."
- `rerank` → "Selecting most relevant information..."
- `generation` → "Generating response..." (briefly shown before first token arrives)

---

### Token Event

```text
event: token
data: {"content": "特斯拉"}

event: token
data: {"content": "当前"}
```

---

### Structured Data Event (sent once, after generation)

```text
event: structured_data
data: {"assets": [{"symbol": "TSLA", "price": 221.13, "change": 5.20, "change_pct": 2.4, "trend": "bullish", "market_metrics": {...}, "chart_data": {...}}]}
```

For multi-asset queries, `assets` array contains multiple entries (one per ticker).

---

### Citation Event (sent after structured_data)

```text
event: citations
data: [{"title": "Tesla Stock Today", "url": "https://...", "source_type": "web"}, {"title": "PE Ratio Explained", "url": "", "source_type": "rag"}]
```

---

### Completion Event (sent last)

```text
event: done
data: {"session_id": "550e8400-e29b-41d4-a716-446655440000"}
```

---

### Error Event (sent on failure, terminates stream)

```text
event: error
data: {"type": "MarketAPIError", "message": "Failed to retrieve market data for TSLA"}
```

---

# 16. Repository Pattern

## 16.1 Repository Structure

```text
repositories/
├── session_repository.py    # ChatSession CRUD
├── message_repository.py    # ChatMessage CRUD + query by session_id
├── document_repository.py   # KnowledgeDocument CRUD
└── ingestion_repository.py  # IngestionJob CRUD
```

---

## 16.2 Repository Responsibilities

Repositories ONLY manage:

- DB CRUD operations
- query abstraction
- transaction isolation

Repositories must NOT contain:

- LLM logic
- orchestration logic
- business workflows
- external API calls

---

# 17. Tool Layer Design

## 17.1 Tool Layer Purpose

All external services must be isolated under:

```text
tools/
```

This includes:

- market APIs (Yahoo Finance)
- web search (Tavily)
- web content extraction (Tavily Extract)
- vector retrieval (Chroma)
- local rerank
- embedding

---

## 17.2 Tool Structure

```text
tools/
├── market_data_tool.py      # Yahoo Finance wrapper
├── tavily_search_tool.py    # Tavily Search API wrapper
├── tavily_extract_tool.py   # Tavily Extract API wrapper
├── retrieval_tool.py        # Chroma vector search
├── rerank_tool.py           # Local CrossEncoder reranking
├── embedding_tool.py        # Embedding model (BAAI/bge-small)
└── llm_tool.py              # LLM provider factory (reads config, returns provider)
```

---

## 17.3 Tool Design Rules

Tools must:

- be stateless (pure functions or class with no mutable state)
- be independently testable (mock at boundary)
- expose typed interfaces (Pydantic input/output)
- avoid side effects
- never import from `repositories/` or `graph/`

---

# 18. Frontend State Management

## 18.1 State Strategy

Frontend state management uses:

| Tool | Responsibility |
|---|---|
| Zustand | UI state only |
| TanStack Query | server state (API data, cache, refetching) |

---

## 18.2 Zustand Responsibilities

Zustand stores ONLY UI state:

- `activeSessionId: string | null`
- `sidebarOpen: boolean`
- `streamingTokens: string` (accumulated during SSE streaming)
- `statusMessage: string | null` (current tool execution status, cleared on first token)
- `isStreaming: boolean`
- `theme: "light" | "dark" | "system"`

---

## 18.3 TanStack Query Responsibilities

TanStack Query manages ONLY server state:

- session list (`useQuery` for GET /api/sessions)
- session detail + messages (`useQuery` for GET /api/sessions/{id})
- mutation hooks for POST/DELETE operations
- cache invalidation on mutations

---

## 18.4 Streaming State Flow

```text
User clicks "Send"
    ↓
Zustand: isStreaming = true, streamingTokens = ""
    ↓
POST /api/chat with fetch + ReadableStream
    ↓
"status" SSE event: Zustand sets statusMessage (e.g., "Fetching market data...")
    ↓ (repeated for each node: market_data → news → extract → retrieval → rerank → etc.)
    ↓
"token" SSE event: Zustand clears statusMessage, appends to streamingTokens
    ↓ (subsequent token events just append)
    ↓
"structured_data" event: Zustand stores for market panel
    ↓
"citations" event: Zustand stores citations
    ↓
"done" event: Zustand isStreaming = false
              TanStack Query invalidates session messages cache
```

---

# 19. Markdown Rendering

## 19.1 Markdown Stack

```text
react-markdown
remark-gfm          (GitHub Flavored Markdown: tables, strikethrough, task lists)
rehype-highlight    (syntax highlighting for code blocks)
```

---

## 19.2 Supported Markdown Features

- headings (H1-H6)
- tables
- bullet lists (ordered + unordered)
- code blocks with syntax highlighting
- inline code
- links
- bold / italic
- blockquotes

---

## 19.3 Security Rules

Markdown rendering must:

- sanitize HTML (no raw HTML passthrough)
- disable `dangerouslySetInnerHTML` equivalents
- use `rehype-sanitize` if raw HTML support is needed later

---

# 20. Charting

## 20.1 Chart Library

```text
Recharts
```

---

## 20.2 Supported Charts

- 7-day price line chart
- 30-day price line chart
- (Charts rendered in Market Panel using `structured_data.chart_data`)

---

## 20.3 Chart Data Flow

Charts use historical data returned by the backend in `structured_data.chart_data`:

```json
{
  "chart_data": {
    "7d": [
      {"date": "2026-05-05", "close": 218.50},
      {"date": "2026-05-06", "close": 220.10},
      "..."
    ],
    "30d": [
      {"date": "2026-04-12", "close": 205.30},
      "..."
    ]
  }
}
```

The frontend does NOT call Yahoo Finance directly — all data flows through the backend.

---

# 21. Auto Session Title Generation

## 21.1 Title Generation Strategy

After the first user query in a new session:

```text
1. Persist user message + assistant response
2. Fire-and-forget via FastAPI BackgroundTasks:
   LLM (MiniMax-M2.7) with Chinese prompt:
   "根据以下对话，生成一个简短的标题（不超过15个中文字）：
    用户问题：{user_query}
    助手回答摘要：{response_summary}"
3. PATCH /api/sessions/{id}/title to update session title in SQLite
4. Frontend observes title update via TanStack Query cache invalidation
```

Title generation is a fire-and-forget background task — the user's chat response
is never delayed by title generation. If title generation fails, the title
remains permanently as "新对话" (no retry mechanism). The user can manually
rename via PATCH if desired.

The `{response_summary}` is the first ~200 characters of the assistant's response
(truncated, not a separate LLM call) — sufficient for the LLM to understand the topic.

Example titles (all Chinese):

```text
"特斯拉股价分析"
"市盈率概念解释"
"NVIDIA 2026年市场走势"
```


---

# 22. Startup Strategy

## 22.1 Single Startup Script

Project root includes:

```text
start_project.bat
```

Responsibilities:

- activate backend virtual environment
- install dependencies if needed
- start FastAPI server on port 8000
- start Next.js dev server on port 3000
- open both in separate terminal windows

---

## 22.2 Port Configuration

| Service | Port |
|---|---|
| Backend (FastAPI) | 8000 |
| Frontend (Next.js) | 3000 |

---

## 22.3 Environment Requirements

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 20 LTS+ |
| npm | 10+ |
| OS | Windows |

### CORS Configuration

For local development, the backend allows requests from `http://localhost:3000`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

No production CORS hardening is needed (academic scope).

### yfinance Async Wrapper

Since `yfinance` is a synchronous library, all calls are wrapped with `asyncio.to_thread()`
to avoid blocking the async event loop:

```python
import asyncio

async def fetch_market_data(symbol: str) -> dict:
    return await asyncio.to_thread(_fetch_market_data_sync, symbol)
```

---

# 23. Testing Philosophy

## 23.1 Testing Scope

Focus:

- backend correctness
- orchestration correctness
- API correctness
- E2E workflow validation

Not focused on:

- frontend unit testing
- visual regression testing

---

## 23.2 Testing Categories

```text
tests/
├── unit/           # isolated: repos, tools, services, graph nodes
├── integration/    # RAG pipeline, market data, graph flows
├── api/            # endpoint correctness
├── e2e/            # Playwright real browser tests
└── fixtures/       # test documents, mock data, graph states
```

---

## 23.3 Testing Order

All testing happens AFTER the full software implementation is complete:

```text
Implementation → Testing → Debug → Fix bugs
```

---

# 24. Logging Strategy

## 24.1 Logging Philosophy

Logging prioritizes:

- debugging clarity
- graph visibility
- tool execution traceability

---

## 24.2 Required Logged Events

- incoming requests (method, path, session_id)
- graph routing (intent classification result)
- node execution (node name, duration)
- tool invocation (tool name, arguments)
- retrieval results (k, latency)
- rerank decisions (chunks kept/discarded)
- market API latency
- SSE lifecycle (start, events sent, termination)
- API failures (full error details)

---

## 24.3 Log Format

Structured logs preferred. Use Python `logging` with consistent format:

```text
[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s
```

---

# TSD.md — Financial Asset QA System
# Part 2 — File Structure, API Contracts, Graph Logic, Prompt System, and Detailed Engineering Specification

---

# 25. Monorepo Structure

## 25.1 Repository Strategy

The project uses:

```text
single monorepo
```

Reasoning:

- simpler local development
- easier AI agent generation
- easier debugging
- simpler startup scripts

---

## 25.2 Root Structure

```text
financial-asset-qa-system/
├── backend/
├── frontend/
├── knowledge_base/          # uploaded documents stored here
├── scripts/
├── tests/
├── docs/
├── start_project.bat
├── README.md
├── .env
├── .gitignore
└── requirements.txt
```

---

# 26. Backend File Structure

## 26.1 Backend Structure

The backend uses an `app/` package for clean imports:

```python
from app.api.routes import chat
from app.graph.builder import create_graph
from app.config.settings import settings
```

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py              # POST /api/chat (SSE streaming)
│   │   │   ├── sessions.py          # Session CRUD + PATCH title
│   │   │   ├── rag.py               # POST /api/rag/upload
│   │   │   └── health.py            # GET /api/health
│   │   │
│   │   ├── schemas/
│   │   │   ├── chat.py              # ChatRequest, ChatResponse
│   │   │   ├── session.py           # SessionResponse, SessionDetailResponse
│   │   │   ├── rag.py               # UploadResponse
│   │   │   └── common.py            # ErrorResponse, HealthResponse
│   │   │
│   │   └── dependencies.py          # Depends() for DB session, LLM provider, config
│
│   ├── graph/
│   │   ├── builder.py               # Create, register nodes/edges, compile graph
│   │   ├── state.py                 # GraphState TypedDict
│   │   ├── intent_classifier.py     # LLM-based intent classification
│   │   ├── nodes/
│   │   │   ├── intent_node.py       # Classify intent, set state.intent
│   │   │   ├── market_node.py       # Fetch Yahoo Finance data, set state.market_data
│   │   │   ├── news_node.py         # Tavily search, set state.news_data
│   │   │   ├── extract_node.py      # Tavily Extract full article text
│   │   │   ├── retrieval_node.py    # Chroma similarity search
│   │   │   ├── rerank_node.py       # CrossEncoder rerank top-k chunks
│   │   │   ├── generation_node.py   # LLM response generation + token streaming
│   │   │   ├── formatter_node.py    # Normalize structured_data + citations
│   │   │   └── rejection_node.py    # Friendly rejection for unsupported queries
│   │   │
│   │   └── edges/
│   │       ├── router.py            # Conditional edge: intent → next node
│   │       └── conditions.py        # Edge condition functions
│
│   ├── tools/
│   │   ├── market_data_tool.py      # Yahoo Finance via yfinance
│   │   ├── tavily_search_tool.py    # Tavily Search via langchain-tavily TavilySearch
│   │   ├── tavily_extract_tool.py   # Tavily Extract via langchain-tavily TavilyExtract
│   │   ├── retrieval_tool.py        # Chroma vector search via langchain-chroma
│   │   ├── rerank_tool.py           # Local CrossEncoder rerank
│   │   ├── embedding_tool.py        # BAAI/bge-small via langchain-huggingface
│   │   └── llm_tool.py              # LLM provider factory (ChatOpenAI for MiniMax)
│
│   ├── repositories/
│   │   ├── session_repository.py
│   │   ├── message_repository.py
│   │   ├── document_repository.py
│   │   └── ingestion_repository.py
│
│   ├── services/
│   │   ├── session_service.py       # Session lifecycle + title generation
│   │   ├── rag_service.py           # Document parsing, chunking, ingestion orchestration
│   │   ├── streaming_service.py     # SSE event formatting + lifecycle
│   │   └── title_generation_service.py  # Async LLM title generation
│
│   ├── database/
│   │   ├── base.py                  # SQLAlchemy Base
│   │   ├── models/
│   │   │   ├── chat_session.py
│   │   │   ├── chat_message.py
│   │   │   ├── knowledge_document.py
│   │   │   └── ingestion_job.py
│   │   ├── session.py               # get_db session factory
│   │   └── engine.py                # SQLAlchemy engine + connection
│
│   ├── vectorstore/
│   │   ├── chroma_client.py         # Chroma client init via langchain-chroma (persist mode)
│   │   └── collections.py           # Collection management + CRUD
│
│   ├── prompts/
│   │   ├── system/
│   │   │   └── system_prompt.txt    # Main system prompt (Chinese)
│   │   ├── market/
│   │   │   ├── market_analysis.txt  # Market analysis prompt template (Chinese)
│   │   │   ├── market_structured.txt
│   │   │   ├── ticker_decision.txt  # Ticker extraction Phase 1: direct vs search
│   │   │   └── ticker_from_search.txt # Ticker extraction Phase 2: extract from Tavily
│   │   ├── rag/
│   │   │   ├── rag_generation.txt   # RAG-grounded generation prompt (Chinese)
│   │   ├── formatting/
│   │   │   └── structured_format.txt
│   │   ├── intent/
│   │   │   └── intent_classifier.txt # Intent classification prompt (Chinese)
│   │   ├── rejection/
│   │   │   └── unsupported_query.txt # Friendly rejection prompt (Chinese)
│   │   └── title/
│   │       └── title_generation.txt  # Session title generation prompt (Chinese)
│
│   ├── providers/
│   │   ├── base_provider.py         # BaseLLMProvider abstract class
│   │   ├── openai_provider.py       # OpenAI-compatible provider (ChatOpenAI with MiniMax base_url)
│   │   └── mock_provider.py         # Mock provider for testing without real API keys
│
│   ├── utils/
│   │   ├── logger.py                # Structured logging setup
│   │   ├── markdown.py              # Markdown utilities (if needed server-side)
│   │   ├── token_counter.py         # Token counting utilities
│   │   ├── time.py                  # UTC timestamp helpers
│   │   └── errors.py                # Custom exception classes
│
│   ├── config/
│   │   ├── settings.py              # Pydantic Settings (reads .env from project root)
│   │   └── constants.py             # Non-configurable constants
│
│   └── main.py                      # FastAPI app creation, router registration, startup
│
├── requirements.txt
└── data/                            # SQLite DB created here at runtime
```

---

# 27. Frontend File Structure

## 27.1 Frontend Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx               # Root layout (providers: QueryClient, ThemeProvider, Zustand)
│   │   ├── page.tsx                 # Main page: 3-panel layout
│   │   └── globals.css              # Tailwind directives + custom scrollbar styles

│   ├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx    # Chat area wrapper
│   │   ├── ChatMessage.tsx      # Single message (markdown rendered)
│   │   ├── ChatInput.tsx        # Text input + send button
│   │   ├── StreamingMessage.tsx # In-progress streaming message (incremental render)
│   │   └── CitationList.tsx     # Clickable citation links
│   │
│   ├── market/
│   │   ├── MarketPanel.tsx      # Right panel container
│   │   ├── PriceCard.tsx        # Current price + daily change
│   │   ├── TrendChart.tsx       # Recharts line chart (7d/30d toggle)
│   │   └── MetricsCard.tsx      # PE ratio, market cap, volume
│   │
│   ├── sidebar/
│   │   ├── Sidebar.tsx          # Left panel container
│   │   ├── SessionList.tsx      # Scrollable session list
│   │   ├── SessionItem.tsx      # Single session row (title, date, active indicator)
│   │   └── NewChatButton.tsx    # Create new session button
│   │
│   ├── markdown/
│   │   └── MarkdownRenderer.tsx # react-markdown wrapper with plugins
│   │
│   ├── ui/                      # shadcn/ui components (generated)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── toast.tsx
│   │   ├── sonner.tsx           # Toast notification system
│   │   └── ...
│   │
│   └── common/
│       ├── ErrorToast.tsx       # Toast error display + retry button
│       └── ThemeToggle.tsx      # Dark/light/system theme switcher

│   ├── features/
│   │   ├── chat/
│   │   │   └── useChatFeature.ts    # Composes useStreaming + useChat hook + chatStore
│   │   ├── sessions/
│   │   │   └── useSessionFeature.ts # Session CRUD operations
│   │   ├── market/
│   │   │   └── useMarketPanel.ts    # Derives market panel state from structured_data
│   │   └── rag/
│   │       └── useRagUpload.ts      # Document upload mutation
│   │
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts            # Base fetch wrapper (base URL, error handling)
│   │   │   ├── chat.ts              # POST /api/chat (streaming + non-streaming)
│   │   │   ├── sessions.ts          # Session CRUD API calls
│   │   │   ├── rag.ts               # POST /api/rag/upload
│   │   │   └── health.ts            # GET /api/health
│   │   │
│   │   ├── sse/
│   │   │   └── sseClient.ts         # fetch + ReadableStream SSE parser
│   │   │
│   │   └── session/
│   │       └── sessionManager.ts    # Session lifecycle helpers
│   │
│   ├── hooks/
│   │   ├── useChat.ts               # Chat message sending + response handling
│   │   ├── useStreaming.ts          # SSE stream consumption + state updates
│   │   ├── useSessions.ts           # TanStack Query hooks for sessions
│   │   └── useMarketPanel.ts        # Market panel data derivation
│   │
│   ├── stores/
│   │   ├── sessionStore.ts          # Zustand: activeSessionId, sidebarOpen
│   │   ├── chatStore.ts             # Zustand: streamingTokens, isStreaming, messages cache
│   │   └── uiStore.ts               # Zustand: theme preference, toasts
│   │
│   ├── types/
│   │   ├── api.ts                   # API request/response types
│   │   ├── session.ts               # Session, SessionDetail types
│   │   ├── chat.ts                  # ChatMessage, StreamingEvent types
│   │   └── market.ts                # MarketData, AssetData, ChartData types
│   │
│   └── lib/
│       ├── markdown.ts              # Markdown components customization
│       ├── utils.ts                 # General utilities
│       └── constants.ts             # API base URL, config constants
│
├── public/
├── tests/
│   └── e2e/
│       ├── chat.spec.ts
│       ├── session.spec.ts
│       ├── rag.spec.ts
│       ├── streaming.spec.ts
│       └── market_panel.spec.ts
│
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.ts                    # Includes rewrites() for API proxy
```

### 27.2 Next.js API Proxy

The frontend uses Next.js `rewrites()` to proxy `/api/*` to the backend at `http://localhost:8000`:

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
```

This allows frontend code to call `/api/chat` (relative path) without CORS issues
or hardcoded backend URLs. The proxy is transparent to the browser.

---

# 28. API Contract Design

## 28.1 API Standards

All APIs must:

- use JSON for request/response bodies
- use typed Pydantic v2 schemas
- return deterministic structures
- use UTC ISO 8601 timestamps
- support async execution (`async def`)

---

# 29. Chat API

## 29.1 Endpoint

```http
POST /api/chat
Accept: text/event-stream (for streaming)
Content-Type: application/json
```

---

## 29.2 Request Schema

```python
class ChatRequest(BaseModel):
    session_id: str          # UUID4
    query: str               # user's natural language query
    stream: bool = True      # True = SSE, False = JSON response
```

---

## 29.3 Non-Streaming Response

```python
class ChatResponse(BaseModel):
    answer_markdown: str
    structured_data: dict
    citations: list[Citation]
    metadata: dict            # session_id, intent, processing_time_ms
```

---

## 29.4 Streaming Response

Streaming uses `text/event-stream` with event-based payloads.

SSE event types: `token`, `structured_data`, `citations`, `done`, `error`

---

# 30. Session APIs

## 30.1 Create Session

```http
POST /api/sessions
```

Response:

```python
class SessionResponse(BaseModel):
    id: str              # UUID4
    title: str           # default "新对话" until first query
    created_at: str      # UTC ISO 8601
    updated_at: str      # UTC ISO 8601
```

---

## 30.2 List Sessions

```http
GET /api/sessions
```

Returns `list[SessionResponse]`, ordered by `updated_at` descending.

---

## 30.3 Load Session

```http
GET /api/sessions/{session_id}
```

Response:

```python
class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: list[ChatMessageSchema]
```

---

## 30.4 Update Session Title

```http
PATCH /api/sessions/{session_id}/title
Content-Type: application/json
```

Request body:

```json
{"title": "特斯拉股价分析"}
```

Used by the backend after async LLM title generation completes. The title is updated
in SQLite, and the frontend observes the change via TanStack Query cache invalidation.

---

## 30.5 Delete Session

```http
DELETE /api/sessions/{session_id}
```

Returns `204 No Content` on success. **Hard delete** — permanently removes the session
and all its messages from SQLite (CASCADE). No soft delete, no recovery.

---

# 31. RAG Upload API

## 31.1 Endpoint

```http
POST /api/rag/upload
Content-Type: multipart/form-data
```

Request body: file field named `file` (`.pdf`, `.md`, or `.txt`).

---

## 31.2 Upload Processing

```text
1. Receive file via multipart upload
2. Validate file type (.pdf, .md, .txt only)
3. Save to knowledge_base/{uuid}_{original_filename}
4. Create IngestionJob record (status: "pending")
5. Process: parse → chunk → embed → store in Chroma
6. Create KnowledgeDocument record
7. Update IngestionJob (status: "completed")
8. Return UploadResponse
```

Processing happens synchronously in the request (for simplicity). Large files may cause longer response times — acceptable for academic scope.

---

## 31.3 Upload Response

```python
class UploadResponse(BaseModel):
    document_id: str       # UUID4
    file_name: str         # original file name
    chunk_count: int       # number of chunks created
    status: str            # "completed"
```

---

## 31.4 File Validation

- Enforce file extensions: `.pdf`, `.md`, `.txt`
- Reject with 400 if type not supported
- Max file size: not enforced (academic scope)

---

# 32. Health API

## 32.1 Endpoint

```http
GET /api/health
```

## 32.2 Response

```python
class HealthResponse(BaseModel):
    status: str              # "healthy" | "degraded" | "unhealthy"
    database: str            # "connected" | "disconnected"
    vectorstore: str         # "connected" | "disconnected"
    llm_provider: str        # "miniMax" | "openai" | "mock" | "unavailable"
```

---

# 33. SQLAlchemy Model Design

## 33.1 Session Model

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)            # UUID4
    title = Column(String, nullable=False, default="新对话")
    created_at = Column(String, nullable=False)      # UTC ISO 8601
    updated_at = Column(String, nullable=False)      # UTC ISO 8601
```

---

## 33.2 Message Model

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)            # UUID4
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)            # "user" | "assistant"
    content = Column(Text, nullable=False)
    metadata_json = Column(Text)                     # JSON string: structured_data + citations
    created_at = Column(String, nullable=False)      # UTC ISO 8601
```

---

## 33.3 Knowledge Document Model

```python
class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(String, nullable=False)
```

---

## 33.4 Ingestion Job Model

```python
class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String, primary_key=True)
    file_name = Column(String, nullable=False)
    status = Column(String, nullable=False)          # "pending" | "processing" | "completed" | "failed"
    error_message = Column(String)
    created_at = Column(String, nullable=False)
```

---

# 34. LangGraph Builder Design

## 34.1 Graph Builder

File: `graph/builder.py`

Responsible for:
- creating StateGraph
- registering all nodes
- registering conditional edges
- compiling graph with `checkpointer=False` (session persistence is handled by SQLite,
  not by LangGraph checkpointing)

```python
compiled_graph = workflow.compile(checkpointer=False)
```

---

## 34.2 Node Registration

```python
workflow = StateGraph(GraphState)

# Nodes
workflow.add_node("intent", intent_node)
workflow.add_node("market_data", market_node)        # Yahoo Finance + normalize
workflow.add_node("news", news_node)                  # Tavily search
workflow.add_node("extract", extract_node)            # Tavily Extract full article text
workflow.add_node("retrieval", retrieval_node)        # Chroma similarity search
workflow.add_node("rerank", rerank_node)              # Local CrossEncoder rerank
workflow.add_node("generation", generation_node)      # LLM response generation
workflow.add_node("formatter", formatter_node)        # Normalize structured_data + citations
workflow.add_node("rejection", rejection_node)        # Friendly rejection for unsupported

# Entry
workflow.set_entry_point("intent")

# After intent: route to first node based on intent
workflow.add_conditional_edges(
    "intent",
    route_by_intent,
    {
        "market": "market_data",            # market flow
        "query_rewriter": "query_rewriter",  # RAG flow
        "hybrid": "market_data",            # hybrid starts with market data, then RAG
        "unsupported": "rejection",
    }
)

# market_data → news (shared by market and hybrid flows)
workflow.add_edge("market_data", "news")

# news → extract (shared by market and hybrid flows)
workflow.add_edge("news", "extract")

# After extract: market → generation, hybrid → retrieval (RAG phase)
workflow.add_conditional_edges(
    "extract",
    route_after_extract,
    {
        "market": "generation",
        "hybrid": "retrieval",
    }
)

# retrieval → rerank (shared by rag and hybrid flows)
workflow.add_edge("retrieval", "rerank")

# rerank → generation (both rag and hybrid paths converge here)
workflow.add_edge("rerank", "generation")

# generation → formatter → END (all flows)
workflow.add_edge("generation", "formatter")
workflow.add_edge("formatter", END)

# rejection → END
workflow.add_edge("rejection", END)
```

---

## 34.3 Conditional Routing

```python
# graph/edges/router.py

def route_by_intent(state: GraphState) -> str:
    """Route from intent node to first processing node."""
    intent = state["intent"]
    if state.get("error"):
        return "unsupported"
    if intent == "market":
        return "market"
    elif intent == "rag":
        return "rag"
    elif intent == "hybrid":
        return "hybrid"
    return "unsupported"


def route_after_extract(state: GraphState) -> str:
    """After extract node: market goes to generation, hybrid continues to RAG phase."""
    if state.get("error"):
        return "market"  # will go to generation which skips on error
    intent = state["intent"]
    if intent == "hybrid":
        return "hybrid"
    return "market"  # market flow → generation


```

**Fail-fast in nodes**: Each node checks `if state.get("error"): return state` at the start and skips all work if an error is already present. This ensures errors propagate through the graph without further processing.

---

# 35. Intent Router Logic

## 35.1 Router Categories

Supported intents (LLM-classified):

```text
market       — queries about stock prices, market data, asset metrics
rag          — queries about financial concepts, definitions, knowledge
hybrid       — queries combining market data + financial concepts
unsupported  — out-of-scope queries
```

---

## 35.2 Intent Classification Implementation

```python
# graph/intent_classifier.py

from pydantic import BaseModel
from typing import Literal

class IntentResult(BaseModel):
    intent: Literal["market", "rag", "hybrid", "unsupported"]

async def classify_intent(
    query: str,
    llm_provider,
    intent_prompt: str,
) -> IntentResult:
    structured_llm = llm_provider.get_model().with_structured_output(
        IntentResult,
        method="function_calling",
    )
    return await structured_llm.ainvoke(intent_prompt + "\n\nUser query: " + query)
```

---

## 35.3 Intent Examples

| Intent | Example Query |
|---|---|
| market | "特斯拉当前股价是多少？" |
| market | "显示苹果的市值和市盈率" |
| rag | "什么是市盈率？" |
| rag | "解释现金流折现估值法" |
| hybrid | "为什么特斯拉股价下跌？市盈率能说明什么？" |
| hybrid | "英伟达估值似乎很高——根据其当前市盈率解释" |
| unsupported | "写一首关于股市的诗" |
| unsupported | "给我讲个笑话" |

---

# 36. Tool Layer Specification

## 36.1 Market Data Tool

File: `tools/market_data_tool.py`

Responsibilities:
- **Ticker extraction (two-phase LLM):** Mapping table (`_CN_NAME_TO_TICKER`) is fed as
  context, NOT used as a hard pre-filter. Two phases:
  1. *Phase 1 (LLM Decision):* `TickerDecision` schema — mapping context + query → LLM
     evaluates every company/product in the query. `action="direct"` (confident → output
     all tickers, skip unlisted) or `action="search"` (any uncertainty → output Chinese
     search query)
  2. *Phase 2 (Tavily Search + Extract):* only triggered by `action="search"` — backend
     runs single Tavily search with pure query (no "stock news" suffix), then LLM with
     `TickerList` schema extracts tickers. Phase 2 schema has no `action` field → cannot loop
- fetch real-time stock price via `yfinance.Ticker(symbol).info`
- fetch historical data via `yfinance.Ticker(symbol).history(period="30d")`
- normalize output to standard dict format
- cache results with `TTLCache(maxsize=128, ttl=60)`
- for multi-asset queries: fetch all tickers in **parallel** via `asyncio.gather`

Typed interfaces:

```python
class TickerList(BaseModel):
    tickers: list[str]

class TickerDecision(BaseModel):
    action: Literal["direct", "search"]
    tickers: list[str] = []
    search_query: str = ""

async def extract_tickers(query: str, model) -> list[str]:
    """Two-phase: regex → LLM TickerDecision → (optional) Tavily search → TickerList."""

async def fetch_market_data(symbol: str) -> dict:
    """Returns normalized market data or raises MarketDataError.
    Wraps sync yfinance calls with asyncio.to_thread()."""

async def fetch_all_market_data(tickers: list[str]) -> dict[str, dict]:
    """Fetch data for multiple tickers in parallel via asyncio.gather.
    Returns dict keyed by ticker symbol. Caches per-ticker results."""
```

Normalized output per ticker:
```python
{
    "symbol": "TSLA",
    "price": 221.13,
    "change": 5.20,
    "change_pct": 2.4,
    "trend": "bullish",         # derived from change sign
    "market_metrics": {
        "market_cap": "692.5B",
        "pe_ratio": 62.3,
        "volume": "58.2M"
    },
    "chart_data": {
        "7d": [{"date": "...", "close": ...}, ...],
        "30d": [{"date": "...", "close": ...}, ...]
    }
}
```

---

## 36.2 Tavily Search Tool

File: `tools/tavily_search_tool.py`

Uses the official `langchain-tavily` package (NOT the deprecated `langchain_community` version):

```python
from langchain_tavily import TavilySearch

def create_tavily_search_tool(api_key: str) -> TavilySearch:
    return TavilySearch(
        max_results=5,
        tavily_api_key=api_key,
    )
```

Install: `pip install langchain-tavily`

Responsibilities:
- search financial news: query = f"{ticker} stock news"
- return top 5 results with title, url, snippet, published date
- provide citation URLs

---

## 36.3 Tavily Extract Tool

File: `tools/tavily_extract_tool.py`

Uses the official `langchain-tavily` package (NOT the deprecated `langchain_community` version):

```python
from langchain_tavily import TavilyExtract

def create_tavily_extract_tool(api_key: str) -> TavilyExtract:
    return TavilyExtract(
        tavily_api_key=api_key,
        extract_depth="advanced",
        format="markdown",
    )
```

Install: `pip install langchain-tavily`

Corresponding graph node: `graph/nodes/extract_node.py`

Responsibilities:
- take top 2 URLs **per ticker** from `state["news_data"]`
- extract full article text from each URL via Tavily Extract
- merge all extracted content and store in `state["extracted_articles"]`
- all extracted articles are sent to the LLM as context

This is a dedicated LangGraph node (not embedded in the news node), placed after
the news node in market and hybrid flows.

---

## 36.4 Retrieval Tool

File: `tools/retrieval_tool.py`

Responsibilities:
- embed user query using BAAI/bge-small-zh-v1.5
- similarity search in Chroma (top-k=8)
- return chunks with metadata (document_id, document_name, chunk_index)

---

## 36.5 Rerank Tool

File: `tools/rerank_tool.py`

Responsibilities:
- take top-8 chunks + user query
- CrossEncoder scores each chunk against query
- select top-4 most relevant chunks by score
- return ordered list of chunks (most relevant first)

Implementation: uses `sentence_transformers.CrossEncoder` with `BAAI/bge-reranker-base`
(278M params, runs on local CPU). Scores are computed in batch via `model.predict()`,
wrapped in `asyncio.to_thread()` to avoid blocking the event loop.

---

## 36.6 Embedding Tool

File: `tools/embedding_tool.py`

Responsibilities:
- load BAAI/bge-small-zh-v1.5 model (lazy, once, 24M params, 512 dims)
- embed single text or batch
- return normalized embedding vectors

```python
from langchain_huggingface import HuggingFaceEmbeddings

_model: HuggingFaceEmbeddings | None = None

def get_embedding_model() -> HuggingFaceEmbeddings:
    global _model
    if _model is None:
        _model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _model
```

---

## 36.7 LLM Tool

File: `tools/llm_tool.py`

Responsibilities:
- read LLM configuration from `config/settings.py`
- instantiate provider (OpenAI-compatible client with MiniMax base_url)
- wrap `model.with_structured_output(schema, method="function_calling")` for structured extraction
- provide streaming and non-streaming chat methods

---

# 37. LLM Provider Abstraction

## 37.1 Design Goal

The project must support any OpenAI-compatible API.

---

## 37.2 Base Provider Interface

```python
from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):

    @abstractmethod
    def get_model(self):
        """Return underlying model (e.g. ChatOpenAI instance)."""
        pass

    @abstractmethod
    async def chat(self, messages: list[dict], stream: bool = False):
        """Chat completion. Returns string or async iterator of tokens."""
        pass

    @abstractmethod
    def with_structured_output(self, schema, method: str = "function_calling"):
        """Return a runnable that outputs structured data via function_calling."""
        pass
```

---

## 37.3 Supported Providers

Initial implementations:
- **OpenAICompatibleProvider** (covers OpenAI, MiniMax, DeepSeek, OpenRouter — any `/v1/chat/completions` endpoint)
- **MockProvider** (for automated testing without real API keys)

The choice of provider is driven entirely by `.env`:

```
# For MiniMax (default):
MINIMAX_API_KEY=sk-cp-...
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7

# For OpenAI (just change env vars):
MINIMAX_API_KEY=sk-...
MINIMAX_BASE_URL=https://api.openai.com/v1
MINIMAX_MODEL=gpt-4o
```

---

# 38. Prompt Engineering Architecture

## 38.1 Prompt Directory

```text
prompts/
├── system/          # Main system prompt
├── market/          # Market analysis + ticker extraction prompts
├── rag/             # RAG generation prompt
├── formatting/      # Structured output formatting prompts
├── intent/          # Intent classification prompt
├── rejection/       # Unsupported query rejection prompt
└── title/           # Session title generation prompt
```

---

## 38.2 Prompt File Format

All prompts stored as `.txt` files with `{placeholder}` template variables.
**All prompts are written in Chinese** for optimal LLM performance with
Chinese-language user interactions and knowledge base content.

Example `prompts/intent/intent_classifier.txt`:

```text
你是一个金融问答系统的意图分类器。
请将用户的查询精确分类到以下四个类别之一：

- market：关于股票价格、市场数据、具体资产指标的查询
- rag：关于金融概念、定义、术语、理论的查询
- hybrid：同时涉及市场数据和金融概念的复合查询
- unsupported：与金融或投资完全无关的查询

示例：
- "特斯拉当前股价是多少？" → market
- "什么是市盈率？" → rag
- "为什么特斯拉股价下跌？市盈率能说明什么？" → hybrid
- "写一首关于股票的诗" → unsupported

特殊规则：如果用户只输入了一个股票代码（如"TSLA"、"AAPL"），应归类为 market。
如果用户只输入了一个简短术语（如"PE"、"市盈率"），应归类为 rag。

用户查询：{user_query}
```

Prompt files are loaded at startup/import time via a simple `load_prompt(path)` utility that reads the file contents.

---

## 38.3 Prompt Separation Strategy

Different prompts are isolated by responsibility.

Reasoning:
- maintainability (change one prompt without touching others)
- testability (test prompts independently)
- prompt iteration (rapid improvement cycle)
- debugging (isolate which prompt caused an issue)

---

# 39. System Prompt Specification

## 39.1 System Prompt Goals

The system prompt is written in **Chinese**. The assistant must:
- separate facts from analysis (事实 ≠ 分析)
- avoid hallucination (cite sources or acknowledge uncertainty)
- cite sources for all data claims (所有数据声明必须引用来源)
- avoid price prediction (no "will go up/down", 禁止预测涨跌)
- acknowledge uncertainty when data is incomplete
- respond in Chinese, matching the user's language

---

## 39.2 Required Behaviors

The system prompt must explicitly enforce:

```text
客观市场数据 ≠ 分析解读
```

Market data is presented as-is. Any interpretation must be clearly labeled as analysis
（分析仅代表基于数据的推断，不构成投资建议）.

---

## 39.3 Forbidden Behaviors

The assistant must NOT:
- fabricate market prices (编造市场数据)
- predict future stock movements (预测未来股价走势)
- invent citations or sources (伪造引用来源)
- claim unsupported financial conclusions (做出无数据支持的结论)
- give investment advice (提供投资建议)

---

# 40. Market Analysis Prompt Rules

## 40.1 Required Structure

Market responses should contain:

1. **Current Market Data** — price, change, key metrics (from actual data)
2. **Trend Summary** — 7-day and 30-day trend description (from historical data)
3. **Potential Influencing Factors** — related news (from Tavily, cited)
4. **Risk / Uncertainty** — acknowledge what the data cannot tell us

---

## 40.2 Analysis Constraints

Analysis must:

- remain probabilistic ("may suggest", "could indicate", NOT "will lead to")
- avoid certainty language
- distinguish news facts from AI inference
- always cite the source of news claims

---

# 41. RAG Prompt Rules

## 41.1 RAG Grounding

RAG responses must:

- prioritize retrieved context over model's own knowledge
- avoid unsupported expansion beyond retrieved documents
- cite retrieved documents by name

---

## 41.2 Citation Requirement

Every RAG response should include:

```text
Sources:
- [document_name], chunk [chunk_index]
```

---

# 42. Structured Output Rules

## 42.1 Structured Metadata Schema

The structured metadata uses an asset-list model. Single-asset queries produce a list of length 1.
Multi-asset queries produce a list with one entry per ticker.

```json
{
  "assets": [
    {
      "symbol": "TSLA",
      "price": 221.13,
      "change": 5.20,
      "change_pct": 2.4,
      "trend": "bullish",
      "market_metrics": {
        "market_cap": "692.5B",
        "pe_ratio": 62.3,
        "volume": "58.2M"
      },
      "chart_data": {
        "7d": [
          {"date": "2026-05-05", "close": 218.50},
          {"date": "2026-05-06", "close": 220.10}
        ],
        "30d": [
          {"date": "2026-04-12", "close": 205.30}
        ]
      }
    },
    {
      "symbol": "AAPL",
      "price": 198.45,
      "change": -1.30,
      "change_pct": -0.65,
      "trend": "bearish",
      "market_metrics": {
        "market_cap": "3.08T",
        "pe_ratio": 32.1,
        "volume": "45.1M"
      },
      "chart_data": {
        "7d": [...],
        "30d": [...]
      }
    }
  ]
}
```

---

## 42.2 Structured Data Implementation

Structured data is built by the **formatter_node** from real Yahoo Finance data — NOT extracted from LLM output.
The LLM only extracts citations.

```python
class AssetData(BaseModel):
    symbol: str
    price: float | None = None
    change: float | None = None
    change_pct: float | None = None
    trend: str | None = None
    market_metrics: dict | None = None
    chart_data: dict | None = None

class StructuredData(BaseModel):
    assets: list[AssetData]
```

The formatter_node populates every field of `AssetData` from `state["market_data"]`:
- `symbol` → from ticker
- `price` → yfinance `info["currentPrice"]` or `history["Close"][-1]`
- `change` → `info["regularMarketChange"]`
- `change_pct` → `info["regularMarketChangePercent"]`
- `trend` → derived: "bullish" if change > 0, "bearish" if < 0, "neutral" if 0
- `market_metrics` → `{"market_cap": ..., "pe_ratio": ..., "volume": ...}` from yfinance info
- `chart_data` → built from yfinance `history(period="30d")` (7d and 30d arrays)

For multi-asset queries, `assets` contains one entry per ticker.

---

## 42.3 Structured Data Rules

Structured data must:

- remain deterministic (same input → same structure)
- use normalized keys (snake_case in backend, camelCase in frontend)
- avoid markdown formatting (pure JSON values)
- be JSON serializable (no dates, sets, or complex objects)

---

## 42.4 Citations Schema

```python
class Citation(BaseModel):
    title: str
    url: str = ""
    source_type: Literal["web", "rag", "yahoo_finance"]
```

Citations are extracted via `with_structured_output` during the generation phase (included in the same structured output call).

---

# 43. Streaming Service Design

## 43.1 Streaming Responsibilities

Streaming service manages:

- SSE lifecycle (open → events → close)
- event formatting (`event: ...\ndata: ...\n\n`)
- connection cleanup (on disconnect or error)
- stream termination (send `done` or `error`, then close)

---

## 43.2 Streaming Flow

```text
Graph execution starts
    ↓
SSE connection opened (text/event-stream)
    ↓
LLM generates tokens
    ↓ Each token
SSE "token" event sent
    ↓
Frontend incrementally renders markdown
    ↓
LLM generation complete
    ↓
Structured data extracted
    ↓
SSE "structured_data" event sent
    ↓
SSE "citations" event sent
    ↓
SSE "done" event sent
    ↓
SSE connection closed
```

---

# 44. Frontend Streaming Strategy

## 44.1 Streaming Method

Frontend uses: `fetch` + `ReadableStream`

NOT: `EventSource`

Reasoning:

- `fetch` supports POST requests (required for /api/chat)
- supports custom headers (future auth expansion)
- supports cancellation via `AbortController`
- more flexible than `EventSource` (which only supports GET)

---

## 44.2 SSE Client Implementation

```typescript
// services/sse/sseClient.ts
async function* streamChat(body: ChatRequest): AsyncGenerator<SSEEvent> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
    body: JSON.stringify(body),
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    // Parse complete SSE events from buffer
    const events = parseSSEBuffer(buffer);
    for (const event of events) yield event;
  }
}
```

---

# 45. Frontend Component Design

## 45.1 Chat Components

```text
components/chat/
├── ChatContainer.tsx       # Scrollable message list + input
├── ChatMessage.tsx          # Rendered message (markdown)
├── ChatInput.tsx            # Textarea + send button, handles Enter
├── StreamingMessage.tsx     # Real-time token accumulation display
└── CitationList.tsx         # Clickable citation links at end of message
```

---

## 45.2 Market Components

```text
components/market/
├── MarketPanel.tsx          # Right panel container, handles empty vs active state
├── AssetTabs.tsx            # Tab bar for multi-asset switching (hidden when single asset)
├── PriceCard.tsx            # Large price display + change badge (green/red)
├── TrendChart.tsx           # Recharts <LineChart>, toggle 7d/30d
└── MetricsCard.tsx          # Grid of PE ratio, market cap, volume
```

---

## 45.3 Sidebar Components

```text
components/sidebar/
├── Sidebar.tsx              # Left panel wrapper
├── SessionList.tsx          # Scrollable list
├── SessionItem.tsx          # Title + date + active highlight
└── NewChatButton.tsx        # "+" button, creates session, navigates
```

---

## 45.4 Component Hierarchy

```text
layout.tsx
├── ThemeProvider (next-themes)
├── QueryClientProvider (TanStack Query)
└── page.tsx
    ├── Sidebar
    │   ├── NewChatButton
    │   └── SessionList
    │       └── SessionItem[]
    ├── ChatContainer
    │   ├── ChatMessage[] / StreamingMessage
    │   ├── CitationList
    │   └── ChatInput
    └── MarketPanel
        ├── AssetTabs (shown only when assets.length > 1)
        ├── PriceCard
        ├── TrendChart
        └── MetricsCard
```

---

# 46. State Management Rules

## 46.1 Zustand Rules

Zustand stores ONLY UI state. Never server cache.

Examples:
- `activeSessionId: string | null`
- `sidebarOpen: boolean`
- `isStreaming: boolean`
- `streamingTokens: string`
- `theme: "light" | "dark" | "system"`

---

## 46.2 TanStack Query Rules

TanStack Query manages ONLY server state. Never UI state.

Examples:
- `useQuery({ queryKey: ["sessions"], queryFn: fetchSessions })`
- `useMutation({ mutationFn: createSession, onSuccess: invalidateQueries })`
- `useQuery({ queryKey: ["session", id], queryFn: () => fetchSession(id) })`

---

# 47. Markdown Rendering Rules

## 47.1 Markdown Features

The renderer must support:

- GitHub Flavored Markdown (tables, task lists, strikethrough)
- headings (H1-H6)
- inline code and code blocks with syntax highlighting
- links (open in new tab)
- blockquotes

---

## 47.2 Security Rules

- Sanitize HTML: no raw HTML passthrough
- Use `rehype-sanitize` or equivalent
- All links: `target="_blank" rel="noopener noreferrer"`

---

# 48. Market Panel Behavior

## 48.1 Panel Update Trigger

The market panel updates when a SSE `structured_data` event contains `assets` with one or more entries.

---

## 48.2 Default Empty State

```text
"No active asset"
"Ask a market question to see data here"
```

For RAG-only or unsupported queries, the panel remains in the empty state.

---

## 48.3 Multi-Asset Tab Switching

When `assets` contains multiple entries:

- A Tab bar appears at the top: `TSLA | AAPL | BABA`
- The first asset is selected by default
- Clicking a tab switches the displayed PriceCard, TrendChart, and MetricsCard
- Tab switching is purely client-side (no API call)

---

## 48.4 Price Color Coding

- Positive change: green
- Negative change: red
- No change: neutral gray

---

# 49. Chart Design

## 49.1 Chart Types

- 7-day line chart (default view)
- 30-day line chart (toggle button)

---

## 49.2 Chart Source

Charts use `structured_data.chart_data` from backend (Yahoo Finance historical data, normalized).

---

# 50. Error Handling Specification

## 50.1 Fail-Fast Policy

No graceful fallback logic. Errors propagate explicitly.

---

## 50.2 Error Categories

| Error Type | Behavior |
|---|---|
| LLM Failure | SSE error event, terminate stream |
| Market API Failure | SSE error event, terminate stream |
| Retrieval Failure | SSE error event, terminate stream |
| Upload Failure | JSON error response (400/500) |
| SSE Failure | terminate stream, frontend shows error |

---

## 50.3 Error Format (Unified)

All errors use the same structure:

```json
{
  "error": {
    "type": "MarketAPIError",
    "message": "Failed to retrieve market data for TSLA"
  }
}
```

GraphState stores error as `Optional[dict]`:

```python
{
    "type": "MarketAPIError",
    "message": "Failed to retrieve market data for TSLA"
}
```

---

## 50.4 Frontend Error UX

Frontend displays errors via:
- Toast notification (using `sonner`)
- Failed message state (inline error in chat)
- Retry button (re-sends last user query)

---

# 51. Logging Architecture

## 51.1 Required Logs

The system must log:

- incoming requests (method, path, session_id)
- graph routing (intent: {intent})
- node execution (node: {name}, duration_ms)
- retrieval latency (k: {k}, duration_ms)
- market API latency (symbol: {symbol}, duration_ms)
- SSE lifecycle (events_sent, duration_ms)
- API failures (error_type, error_message, traceback)

---

## 51.2 Log Format

```text
[2026-05-12T10:30:00] [INFO] [graph.router] Intent classified: market
[2026-05-12T10:30:02] [INFO] [tools.market] Fetched market data for TSLA in 1200ms
[2026-05-12T10:30:05] [ERROR] [api.chat] SSE stream terminated: MarketAPIError - ...
```

---

# 52. Configuration Management

## 52.1 Environment Variables

Two `.env` files serve different purposes:

| File | Purpose |
|---|---|
| `docs/.env` | Development configuration with **real API keys** (used during implementation) |
| `.env` (project root) | Template/symlink for runtime — loaded by Pydantic `BaseSettings` |
| `.env.example` (project root) | Safe-to-commit template without secrets |

The backend reads from project root `.env` at runtime via:
```python
class Settings(BaseSettings):
    ...
    class Config:
        env_file = ".env"  # relative to CWD (project root)
```

For local development, the developer copies `docs/.env` to project root or uses a symlink.

```
# .env file at project root

# LLM Provider (MiniMax by default)
MINIMAX_API_KEY=sk-cp-...
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7

# Tavily Search
TAVILY_API_KEY=tvly-dev-...

# Database paths (optional, defaults below)
SQLITE_PATH=./backend/data/sqlite.db
CHROMA_PATH=./backend/chroma_db/

# Embedding model (optional)
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

---

## 52.2 Settings Management

Centralized under: `config/settings.py` using Pydantic `BaseSettings`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    minimax_api_key: str
    minimax_base_url: str = "https://api.minimaxi.com/v1"
    minimax_model: str = "MiniMax-M2.7"
    tavily_api_key: str
    sqlite_path: str = "./backend/data/sqlite.db"
    chroma_path: str = "./backend/chroma_db/"
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Startup Validation

On FastAPI startup, the system validates that required API keys are present:

- If `MINIMAX_API_KEY` is missing or empty → **fail with clear error message** (no mock fallback)
- If `TAVILY_API_KEY` is missing or empty → **fail with clear error message**
- The error tells the user exactly which env var is missing

This matches the fail-fast philosophy: no silent degradation, no MockProvider auto-switch.
The MockProvider is only used explicitly in unit tests.

---

# 53. Local Development Workflow

## 53.1 Startup Command

Single startup entry: `start_project.bat`

---

## 53.2 Batch Script Responsibilities

The script should:

1. Check Python venv exists, create if not → `python -m venv venv`
2. Install backend deps → `pip install -r backend/requirements.txt`
3. Install frontend deps → `cd frontend && npm install`
4. Start FastAPI server on port 8000 in a new terminal
5. Start Next.js dev server on port 3000 in a new terminal

---

# 54. AI Coding Agent Rules

## 54.1 Mandatory Constraints

AI coding agents MUST:

- follow file structure exactly
- avoid architectural changes
- maintain strict typing
- preserve repository pattern (graph nodes → tools, NOT graph nodes → API directly)
- preserve tool isolation (tools are stateless, typed, independently testable)
- use `with_structured_output(schema, method="function_calling")` for all structured output

---

## 54.2 Forbidden Behaviors

AI coding agents must NOT:

- merge layers (e.g., business logic inside API routes)
- place business logic in routes
- bypass repositories (graph nodes accessing DB directly)
- directly call external APIs inside graph nodes (must go through tools)
- use untyped state or raw dicts
- hardcode model names or API keys

---

# 55. Engineering Priorities

## 55.1 Priority Order

1. correctness
2. architecture clarity
3. maintainability
4. testability
5. UI polish

---

# TSD.md — Financial Asset QA System
# Part 3 — Testing, Implementation Roadmap, Coding Standards, Acceptance Criteria, and AI-Agent Execution Instructions

---

# 56. Testing Architecture

## 56.1 Testing Philosophy

The testing strategy prioritizes:

- backend correctness
- orchestration correctness
- API reliability
- end-to-end workflow validation

The project does NOT prioritize:

- frontend unit testing
- visual snapshot testing
- performance benchmarking

---

## 56.2 Testing Goals

The testing system must validate:

| Area | Goal |
|---|---|
| LangGraph routing | correct intent flow for all 4 intents |
| Tool execution | correct API integration + normalization |
| Database operations | correct CRUD + transaction behavior |
| SSE streaming | stable incremental delivery + correct events |
| RAG pipeline | correct retrieval + rerank behavior |
| Session persistence | correct history reconstruction |
| Frontend integration | correct end-to-end behavior via Playwright |

---

## 56.3 Coverage Targets

| Layer | Target |
|---|---|
| Backend overall | 70% - 80% |
| Critical services | 80%+ |
| Frontend unit testing | not required |
| E2E critical flows | mandatory (10 flows) |

---

## 56.4 Testing Order

```text
Full implementation completed
    ↓
Write and run all tests
    ↓
Fix failures
    ↓
Re-run all tests
    ↓
All green (passing)
```

---

# 57. Backend Test Structure

## 57.1 Test Directory Structure

```text
tests/
├── unit/
│   ├── graph/
│   │   ├── test_intent_node.py
│   │   ├── test_market_node.py
│   │   ├── test_retrieval_node.py
│   │   ├── test_rerank_node.py
│   │   ├── test_generation_node.py
│   │   └── test_formatter_node.py
│   ├── tools/
│   │   ├── test_market_data_tool.py
│   │   ├── test_tavily_search_tool.py
│   │   ├── test_retrieval_tool.py
│   │   └── test_embedding_tool.py
│   ├── repositories/
│   │   ├── test_session_repository.py
│   │   ├── test_message_repository.py
│   │   └── test_document_repository.py
│   └── services/
│       ├── test_session_service.py
│       └── test_rag_service.py
│
├── integration/
│   ├── rag/
│   │   └── test_rag_pipeline.py
│   ├── market/
│   │   └── test_market_integration.py
│   └── graph/
│       ├── test_market_flow.py
│       ├── test_rag_flow.py
│       ├── test_hybrid_flow.py
│       └── test_unsupported_flow.py
│
├── api/
│   ├── test_chat_api.py
│   ├── test_session_api.py
│   ├── test_rag_api.py
│   └── test_health_api.py
│
├── e2e/
│   └── playwright/
│
├── fixtures/
│   ├── documents/                 # test .md, .txt, .pdf files
│   ├── market_data/               # mock Yahoo Finance responses
│   ├── sessions/                  # pre-built session states
│   └── graph_states/              # sample GraphState dicts
│
├── conftest.py                    # shared fixtures, test DB setup, mock provider
└── pytest.ini                     # pytest config
```

---

# 58. Unit Testing Specification

## 58.1 Unit Testing Scope

Unit tests cover:

- repositories (with in-memory SQLite)
- graph nodes (with mock tools)
- tools (with mock API responses)
- services (with mock repositories)
- utility functions

---

## 58.2 Repository Testing

Repositories must test:

- CRUD correctness (create, read, update, delete)
- invalid query handling (missing session, duplicate ID)
- transaction isolation

Use in-memory SQLite for repository tests.

---

## 58.3 Tool Testing

Tools must test:

- API normalization (raw response → standardized dict)
- invalid symbol handling (e.g., "ZZZZZZ")
- response parsing correctness

Use mock API responses (httpx mock or manual fixture).

---

## 58.4 Graph Node Testing

Graph node tests validate:

- state transition correctness (input state → output state)
- expected output fields present
- failure propagation (error set in state)

---

# 59. Integration Testing

## 59.1 Integration Scope

Integration tests validate:

- full graph orchestration (nodes + edges working together)
- RAG pipeline (ingestion → retrieval → rerank)
- database integration (real SQLite, real Chroma)
- streaming pipeline (SSE event correctness)

---

## 59.2 Market Integration Tests

Validate:

- Yahoo Finance data retrieval (real API)
- normalization logic (data format correctness)
- market metric extraction (PE ratio, market cap, volume)

---

## 59.3 RAG Integration Tests

Validate:

- embedding creation (correct dimensions)
- Chroma insertion (data persists)
- retrieval quality (relevant chunks returned)
- rerank execution (correct chunk selection)

---

# 60. API Testing

## 60.1 API Testing Stack

```text
pytest
pytest-asyncio
httpx (AsyncClient against FastAPI test client)
```

---

## 60.2 API Testing Rules

Every endpoint must validate:

- success response (200/201)
- response schema correctness (Pydantic validation)
- invalid request handling (400)
- not found handling (404)
- error response format

---

## 60.3 Chat API Tests

Required tests:

- send normal query (non-streaming)
- send market query (streaming, verify events)
- send RAG query (streaming, verify events)
- send hybrid query
- send unsupported query (verify rejection)
- invalid payload (missing session_id)
- verify SSE events order: token* → structured_data → citations → done

---

## 60.4 Session API Tests

Required tests:

- create session (verify default title, UUID4)
- load session (verify messages included)
- list sessions (verify ordered by updated_at desc)
- delete session (verify 204, verify cascade deletes messages)
- load non-existent session (verify 404)

---

# 61. Playwright E2E Testing

## 61.1 E2E Goals

Playwright validates real user workflows in a real browser.

---

## 61.2 Playwright Coverage (10 Mandatory Flows)

1. Open application → 3-panel layout renders
2. Create new session → appears in sidebar
3. Ask market question → streaming response renders
4. Verify market panel updates → price, chart, metrics appear
5. Ask RAG question (after uploading doc) → citation appears
6. Ask hybrid question → both market data and citations
7. Switch session → conversation history restores
8. Verify history restoration → old messages render correctly
9. Upload RAG document → success toast appears
10. Ask unsupported question → friendly rejection message

---

## 61.3 Playwright Structure

```text
frontend/tests/e2e/
├── chat.spec.ts
├── session.spec.ts
├── rag.spec.ts
├── streaming.spec.ts
└── market_panel.spec.ts
```

---

# 62. Mocking Strategy

## 62.1 Mocking Philosophy

The project uses:

```text
minimal mocking
```

Reasoning:

- academic projects benefit from real integration (more convincing demo)
- easier demonstration (real data is more compelling)
- better architecture validation

---

## 62.2 Allowed Mocking

Allowed:
- Mock LLM provider (for unit tests — avoid real API calls in CI)
- Mock Tavily responses (for reproducibility)
- Mock Yahoo Finance failures (for error path testing)

---

## 62.3 Forbidden Mocking

Avoid mocking (use real implementations):
- repositories (use in-memory SQLite instead)
- graph routing (test the actual compiled graph)
- SSE protocol (test real streaming)
- retrieval pipeline (use real Chroma with test data)

---

# 63. Fixture Design

## 63.1 Fixture Categories

```text
fixtures/
├── documents/           # Test documents for RAG
│   ├── financial_glossary.md
│   ├── earnings_summary.txt
│   └── sample_report.pdf
├── market_data/         # Cached Yahoo Finance responses
│   ├── tsla_info.json
│   └── aapl_history.json
├── sessions/            # Pre-built session data
└── graph_states/        # Sample GraphState for node tests
```

---

## 63.2 Test Documents

The repository should include:

- financial glossary markdown (key terms and definitions)
- earnings summary txt (mock earnings report)
- example financial PDF (short academic finance paper or mock document)

---

# 64. Streaming Test Strategy

## 64.1 SSE Validation

Streaming tests must validate:

- ordered token delivery (tokens arrive in sequence)
- stream completion (done event received)
- structured event correctness (valid JSON in structured_data event)
- stream termination behavior (error event closes stream)
- event order: token* → structured_data → citations → done

---

## 64.2 Streaming Event Validation

Required events verified:

```text
token              — at least one received
structured_data    — exactly one, valid JSON
citations          — exactly one, valid array
done               — exactly one, stream closes after
error              — stream terminates immediately
```

---

# 65. LangGraph Testing Specification

## 65.1 Graph Testing Priorities

Critical graph behaviors:

- routing correctness (intent → correct flow)
- state mutation correctness (nodes modify state correctly)
- node execution order (correct for each flow)
- error propagation (fail-fast: error in state stops further processing)

---

## 65.2 Required Graph Tests

```text
- market route: intent="market" → market_node → news_node → extract_node → generation_node → formatter_node
- rag route: intent="rag" → retrieval_node → rerank_node → generation_node → formatter_node
- hybrid route: intent="hybrid" → market_node → news_node → extract_node → query_rewriter_node → retrieval_node → rerank_node → generation_node → formatter_node
- unsupported route: intent="unsupported" → rejection_node → END
- rerank execution: 8 chunks in → 4 chunks out
- formatter execution: structured_data normalized, citations assembled
```

---

# 66. RAG Evaluation Rules

## 66.1 Retrieval Validation

RAG tests validate:

- retrieved chunk relevance (chunks contain query-related terms)
- chunk count (top-8 returned)
- chunk metadata completeness (document_id, document_name, chunk_index)

---

## 66.2 Citation Validation

Responses must reference:

- retrieved source document name
- meaningful chunk reference

---

# 67. Frontend Engineering Rules

## 67.1 Frontend Philosophy

Frontend must prioritize:

- clarity
- responsiveness
- maintainability
- streaming UX

NOT:

- animation-heavy design
- excessive visual complexity

---

## 67.2 Frontend Styling Rules

Mandatory:

- Tailwind utility classes (no inline CSS)
- shadcn/ui components (consistent design system)
- responsive layout (sidebar collapses on narrow screens)
- dark mode via `next-themes` + Tailwind `dark:` classes

---

## 67.3 Forbidden Frontend Behaviors

Avoid:

- inline CSS (`style={{}}` attributes)
- untyped props (no `any`)
- oversized global state (keep Zustand stores minimal)
- direct `fetch` calls inside components (use service layer)

---

# 68. Backend Engineering Rules

## 68.1 Backend Philosophy

Backend must remain:

- layered (api → graph → tools/services → repositories → database)
- typed (Python type hints everywhere)
- modular (each layer importable independently)
- deterministic (same input → same output)

---

## 68.2 Mandatory Backend Rules

Required:

- `async def` for all endpoints and graph nodes
- Pydantic v2 schemas for all API contracts
- repository isolation (graph never touches DB directly)
- tool isolation (graph never calls external APIs directly)
- structured logging (Python `logging` module)
- all structured output via `model.with_structured_output(schema, method="function_calling")`

---

## 68.3 Forbidden Backend Behaviors

Forbidden:

- business logic inside API routes (routes are thin: validate → call service → return)
- direct DB access inside graph nodes (must go through repositories)
- raw SQL inside services (must go through repositories)
- untyped responses (must use Pydantic schemas)
- hardcoded API keys or model names

---

# 69. Prompt Engineering Rules

## 69.1 Prompt Design Philosophy

Prompts must:

- be modular (one file per concern)
- be explicit (no ambiguity in instructions)
- minimize hallucination (instruct grounding, citation, uncertainty acknowledgment)
- enforce structured behavior

---

## 69.2 Prompt Constraints

Prompts must explicitly instruct:

- distinguish facts from analysis
- avoid unsupported claims
- avoid future prediction
- cite uncertainty when data is incomplete
- cite sources for all data claims

---

## 69.3 Output Formatting Rules

Responses should:

- use concise markdown
- avoid excessive verbosity
- maintain financial professionalism (objective tone, no hype)

---

# 70. LLM Integration Rules

## 70.1 Provider Compatibility

The system supports any OpenAI-compatible API by changing `.env`:

- MiniMax (default for dev/test — free tier)
- OpenAI
- OpenRouter
- DeepSeek-compatible endpoints

---

## 70.2 Model Configuration

Configuration externalized to `.env`. No hardcoded values.

---

## 70.3 Streaming Rules

Streaming providers must support:

- incremental tokens (not batch-only)
- async iteration
- cancellation (respect `AbortController`)

---

## 70.4 Structured Output Rules

All structured output uses:

```python
model.with_structured_output(
    SchemaClass,
    method="function_calling",
)
```

This applies to:
- Intent classification → `IntentResult`
- Structured data extraction → `StructuredData`
- Citations extraction → `list[Citation]`

---

# 71. RAG Document Processing

## 71.1 Ingestion Pipeline

```text
POST /api/rag/upload (multipart file)
    ↓
Save file to knowledge_base/{uuid}_{filename}
    ↓
Parse file:
  - .pdf → PyPDFLoader / pdfplumber
  - .md → raw text
  - .txt → raw text
    ↓
Chunk: RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    ↓
Embed: BAAI/bge-small-zh-v1.5 (HuggingFaceEmbeddings)
    ↓
Store in Chroma (persist mode)
    ↓
Create KnowledgeDocument record in SQLite
    ↓
Return UploadResponse
```

---

## 71.2 Chunk Metadata

Every chunk stored in Chroma must include:

```json
{
  "document_id": "550e8400-...",
  "document_name": "financial_glossary.md",
  "chunk_index": 0
}
```

---

# 72. Financial Analysis Rules

## 72.1 Financial Data Requirements

All market analysis must:

- use actual retrieved data (no fabrication)
- separate facts from interpretation
- avoid invented statistics

---

## 72.2 News Analysis Rules

News-based reasoning must:

- cite article source (URL + title)
- distinguish article facts from AI inference (label analysis clearly)

---

# 73. Session Management Rules

## 73.1 Session Lifecycle

```text
Create (POST /api/sessions, title="新对话")
    → First user query triggers title generation (async)
    → All messages persisted (user + assistant)
    → Reload (GET /api/sessions/{id} returns messages)
    → Delete (DELETE /api/sessions/{id}, cascade deletes messages)
```

---

## 73.2 Session Persistence Rules

Every completed interaction must persist:

- user message (role="user", content=query)
- assistant response (role="assistant", content=markdown, metadata_json=structured_data+citations)

---

# 74. Structured Metadata Rules

## 74.1 Metadata Usage

Structured metadata is used for:

- frontend market panel rendering
- chart rendering (Recharts data)
- testing assertions (verifiable JSON output)
- session history display

---

## 74.2 Metadata Constraints

Metadata must remain:

- JSON serializable
- deterministic (same input → same structure)
- normalized keys (snake_case in Python, camelCase in TypeScript)

---

# 75. Error Handling UX

## 75.1 Frontend Error Display

Frontend displays:
- Toast notification (sonner)
- Inline error message (in chat)
- Retry button (re-sends query)

---

## 75.2 Backend Error Format (Unified)

All errors use:

```json
{
  "error": {
    "type": "MarketAPIError",
    "message": "Failed to retrieve market data for TSLA"
  }
}
```

GraphState.error stores: `{"type": "...", "message": "..."}` (dict, not string).

Error types: `LLMError`, `MarketAPIError`, `TavilyError`, `RetrievalError`, `ValidationError`, `InternalError`.

**Streaming mode**: errors are sent as SSE `error` events, which immediately terminate the stream.
Frontend displays a toast + inline error with retry button.

**Non-streaming mode**: errors are returned as JSON `{"error": {"type": "...", "message": "..."}}`
with appropriate HTTP status codes (400/500).

---

# 76. Local File Storage

## 76.1 Knowledge Base Directory

`knowledge_base/` (project root) stores:

- uploaded documents (raw files)
- parsed intermediate files (if any)

---

## 76.2 Storage Constraints

No cloud storage integration required. Everything local.

---

# 77. Environment Setup

## 77.1 Backend Setup

```bash
python -m venv venv
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 77.2 Frontend Setup

```bash
npm install
npm run dev    # Next.js on port 3000
```

---

# 78. Startup Script Specification

## 78.1 Required File

`start_project.bat` at project root.

---

## 78.2 Script Responsibilities

The script:

1. Activates Python virtual environment
2. Installs backend dependencies (`pip install -r backend/requirements.txt`)
3. Installs frontend dependencies (`cd frontend && npm install`)
4. Starts FastAPI server on port 8000 (new terminal)
5. Starts Next.js dev server on port 3000 (new terminal)
6. Opens browser at `http://localhost:3000`

---

## 78.3 Expected Ports

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs (Swagger) |

---

# 79. README Requirements

## 79.1 Mandatory Sections

README must contain:

- project overview
- architecture diagram (ASCII or image)
- tech stack summary
- setup instructions (prerequisites, .env, startup)
- API overview (endpoints table)
- LangGraph workflow diagram
- RAG pipeline diagram
- prompt engineering strategy
- testing strategy
- limitations
- future improvement ideas

---

## 79.2 Architecture Diagram Requirement

README must include:

- system architecture diagram (frontend → backend → LangGraph → tools/DB)
- graph workflow diagram (intent routing → flows)

---

# 80. Demo Requirements

## 80.1 Mandatory Demonstrations

The demo should show:

1. project overview (architecture walkthrough)
2. market question → streaming response → market panel update
3. RAG upload → RAG question → citation display
4. hybrid question → combined market + knowledge response
5. session switching → history restoration
6. architecture explanation

---

# 81. Suggested Implementation Order

## 81.1 Recommended Development Sequence

### Phase 1: Backend Foundation
Build:

- FastAPI app skeleton (main.py, settings.py, CORS)
- SQLite database (engine, models, session factory)
- Repository layer (SessionRepository, MessageRepository)
- Session API routes (CRUD)
- Health API

### Phase 2: LangGraph Integration
Build:

- GraphState (TypedDict)
- Graph builder (nodes + edges)
- Intent classifier (LLM-based, function_calling)
- All graph nodes (market, retrieval, rerank, generation, formatter, rejection)
- Conditional routing

### Phase 3: Market Data Integration
Build:

- Yahoo Finance tool (yfinance wrapper with TTLCache)
- Tavily Search + Extract tools
- Market analysis prompts
- Structured data extraction via function_calling

### Phase 4: Frontend Chat UI
Build:

- Next.js + Tailwind + shadcn/ui setup
- next-themes dark mode
- Zustand stores
- TanStack Query hooks
- 3-panel layout (sidebar + chat + market)
- SSE streaming renderer (fetch + ReadableStream)
- Markdown rendering
- Session CRUD UI

### Phase 5: Market Panel
Build:

- PriceCard (current price + daily change)
- TrendChart (7d/30d Recharts line)
- MetricsCard (PE ratio, market cap, volume)
- Panel state: empty → active

### Phase 6: RAG Pipeline
Build:

- Document upload (multipart form)
- File parsing (.pdf, .md, .txt)
- Chunking + embedding
- Chroma storage (persist mode)
- Retrieval + rerank tools
- RAG prompts
- Citation display in frontend

### Phase 7: Testing
Build:

- All unit tests
- Integration tests
- API tests
- Playwright E2E tests
- Debug and fix all failures

---

# 82. Acceptance Criteria

## 82.1 Functional Acceptance

The system is considered complete when it supports:

- market QA (asks a stock question → gets price, metrics, chart data)
- RAG QA (uploads a doc → asks a question → gets grounded answer with citations)
- hybrid QA (asks combined question → gets market data + knowledge)
- streaming responses (tokens appear incrementally)
- session persistence (reload page → old conversations preserved)
- session switching (sidebar → click session → history restored)
- market panel updates (structured_data drives right panel)
- document ingestion (upload file → chunks stored in Chroma)

---

## 82.2 Engineering Acceptance

The system must demonstrate:

- clean layered architecture
- typed schemas (Pydantic v2 for every API)
- modular layering (api → graph → tools/services → repositories → database)
- test coverage (70%+ backend)
- repository pattern (no direct DB access outside repositories)
- tool abstraction (no external API calls outside tools)

---

## 82.3 UI Acceptance

Frontend must demonstrate:

- responsive 3-panel layout
- streaming UX (tokens appear in real-time)
- markdown rendering (tables, code blocks, headings)
- market visualization (price, chart, metrics)
- dark mode support

### 82.3.1 Initial Load State

On first page load (no active session):
- Sidebar: visible, shows session list (may be empty). "新对话" button at top.
- Chat area: empty state — no messages, no input box. Display a hint:
  "选择一个对话或创建新对话开始"
- Market panel: empty state — "暂无活跃资产" / "提出市场相关问题以查看数据"

After user clicks "新对话" or selects an existing session:
- Sidebar: selected session highlighted
- Chat area: shows all messages for the session (empty if new), input box appears
- Market panel: empty (updates when SSE `structured_data` event arrives)

### 82.3.2 Session Switching

When user clicks a different session in the sidebar:
- Chat area transitions to new session's messages
- Market panel clears (resets to empty state)
- No additional API call to backend (messages already loaded via TanStack Query)

---

# 83. Non-Goals

## 83.1 Explicit Non-Goals

The project intentionally excludes:

- authentication / authorization
- multi-user architecture
- Redis or any distributed cache
- Docker containerization
- Kubernetes deployment
- distributed systems
- production deployment
- advanced observability (metrics, tracing)
- enterprise security hardening

---

# 84. Future Improvement Ideas

## 84.1 Potential Extensions

- Redis caching (replace TTLCache)
- auth system (user login, personal sessions)
- portfolio tracking (watchlist, holdings)
- multi-agent architecture (specialist agents)
- WebSocket streaming (bidirectional)
- advanced rerank evaluation framework (RAGAS metrics)
- deployment pipeline (CI/CD, Docker)

---

# 85. Final Architecture Summary

## 85.1 Core Stack Summary

```text
Frontend:
Next.js 15 + TypeScript + TailwindCSS + shadcn/ui + next-themes
API Proxy: Next.js rewrites (localhost:8000)

Backend:
FastAPI + LangGraph (LangChain) + SQLAlchemy + Pydantic v2
Package: backend/app/ (app package for clean imports)

Databases:
SQLite (relational, via SQLAlchemy) + Chroma (vector, via langchain-chroma, persist mode)

RAG:
langchain-huggingface (BAAI/bge-small-zh-v1.5) + langchain-chroma retrieval
+ langchain-text-splitters (RecursiveCharacterTextSplitter) + local CrossEncoder rerank
Document loading: langchain-community PyPDFLoader (PDF) + raw text (.md, .txt)

Web Search:
langchain-tavily (TavilySearch + TavilyExtract)

LLM:
MiniMax-M2.7 (all tasks) — OpenAI-compatible via ChatOpenAI with MiniMax base_url

Streaming:
Dual-track SSE (text/event-stream): tokens streamed in real-time via asyncio.Queue
while graph retains complete markdown for post-processing (formatter + structured extraction)
Frontend: fetch + ReadableStream (NOT EventSource)

Language:
All UI, prompts, and generated responses in Simplified Chinese

Testing:
pytest + pytest-asyncio + httpx + Playwright
```

---

# 86. Final Engineering Philosophy

The project prioritizes:

- clarity
- modularity
- AI-native orchestration (LangGraph)
- testability
- data-driven responses

over:

- infrastructure complexity
- premature optimization
- enterprise-scale concerns

---

# 87. AI-Agent Execution Directive

## 87.1 Primary Instruction

AI coding agents implementing this project MUST:

- follow this TSD strictly (file structure, layer boundaries, naming)
- preserve architecture boundaries (no crossing layers)
- avoid unnecessary abstraction (don't over-engineer)
- prioritize correctness over creativity
- use `with_structured_output(schema, method="function_calling")` for ALL structured output
- place ALL prompts in `.txt` files under `prompts/`
- generate UUID4 for all IDs
- use async/await throughout the backend
- use UTC ISO 8601 for all timestamps

## 87.2 Final Constraint

If implementation conflicts arise:

```text
architecture consistency > feature expansion
```

When the TSD is silent on a detail, choose the simplest reasonable approach and
maintain consistency with the rest of the codebase.

---

# Appendix A: Key Implementation Details Summary

| Decision | Choice |
|---|---|
| ID format | UUID4 |
| Python version | 3.11+ |
| Node.js version | 20 LTS+ |
| Backend port | 8000 |
| Frontend port | 3000 |
| CORS origin (dev) | `http://localhost:3000` |
| Frontend API proxy | Next.js rewrites: `/api/*` → `http://localhost:8000/api/*` |
| SQLite path | `./backend/data/sqlite.db` (created at runtime) |
| Chroma path | `./backend/chroma_db/` |
| Chroma library | langchain-chroma (not raw chromadb) |
| Chroma collection | `financial_knowledge` |
| Embedding library | langchain-huggingface (HuggingFaceEmbeddings) |
| Reranker model | BAAI/bge-reranker-base (sentence_transformers CrossEncoder) |
| Knowledge base | `./knowledge_base/` (pre-loaded with 3 Chinese docs) |
| Documents pre-loaded | `pe_ratio.md`, `dcf_valuation.md`, `ebitda.md` (all Chinese) |
| Chunk size | 800 chars |
| Chunk overlap | 150 chars |
| Retrieval top-k | 8 |
| Rerank top-n | 4 |
| Market cache TTL | 60 seconds |
| Cache max size | 128 entries |
| Streaming method | SSE (text/event-stream) via dual-track architecture |
| Structured output | `with_structured_output(schema, method="function_calling")` |
| Prompt format | `.txt` files with `{placeholder}` templates (Chinese) |
| Default model | MiniMax-M2.7 (OpenAI-compatible at /v1/chat/completions) |
| LLM env vars | `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL` |
| LLM provider | ChatOpenAI with MiniMax base_url (configurable via .env) |
| Tavily Search | langchain-tavily TavilySearch |
| Tavily Extract | langchain-community TavilyExtract |
| Timestamp format | UTC ISO 8601 |
| Error format | SSE error event: `{"error": {"type": "...", "message": "..."}}` |
| yfinance integration | `asyncio.to_thread()` wrapper for sync calls |
| Title generation | FastAPI BackgroundTasks (fire-and-forget), LLM generates Chinese title ≤15 chars |
| Title update endpoint | PATCH /api/sessions/{id}/title |
| Default session title | "新对话" |
| Backend package root | `backend/app/` (with `app/` package) |
| Frontend source root | `frontend/src/` (Next.js 15 convention) |
| User language | Simplified Chinese (all UI, prompts, and generated responses) |
| LangGraph checkpointer | disabled (False) — session state in SQLite |
| Messages format | OpenAI: `[{"role": "user"|"assistant", "content": "..."}]` |
| System prompt | dynamically prepended to messages (not stored in DB) |
| Initial page state | no active session, chat area empty, input hidden |
| PDF parsing | PyPDFLoader (langchain_community) |
| Graph execution | `compile(checkpointer=False)` + dual-track SSE streaming |

---

# Appendix B: Graph Flow Summary

```text
Intent: market
━━━━━━━━━━━━━━━━━
intent → market_data → news → extract → generation → formatter → END

Intent: rag
━━━━━━━━━━━━━━━━━
intent → query_rewriter → retrieval → rerank → generation → formatter → END

Intent: hybrid (sequential: market first, then RAG)
━━━━━━━━━━━━━━━━━
intent → market_data → news → extract → query_rewriter → retrieval → rerank → generation → formatter → END

Note: Hybrid runs phases sequentially (not in parallel).
     - Phase 1: market_data + news + extract (sets state["market_data"], state["news_data"], state["extracted_articles"])
     - Phase 2: query_rewriter + retrieval + rerank (sets state["rewritten_query"], state["retrieved_docs"], state["reranked_docs"])
     - Generation: LLM generates final markdown answer from all raw context (market + news + articles + RAG docs)

Intent: unsupported
━━━━━━━━━━━━━━━━━
intent → rejection → END
```

---

# Appendix C: SSE Event Sequence

```text
event: token
data: {"content": "根据"}

event: token
data: {"content": "当前"}

event: token
data: {"content": "数据"}

... more tokens ...

event: structured_data
data: {"assets": [{"symbol": "TSLA", "price": 221.13, "change": 5.20, "change_pct": 2.4, "trend": "bullish", "market_metrics": {...}, "chart_data": {...}}]}

event: citations
data: [{"title": "特斯拉今日股价分析", "url": "https://...", "source_type": "web"}, ...]

event: done
data: {"session_id": "550e8400-..."}
```
