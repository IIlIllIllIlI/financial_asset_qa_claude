# SPD.md — Financial Asset QA System
# Part 1 — Core System Architecture & Engineering Specification

---

# 1. Project Overview

## 1.1 Project Name

Financial Asset QA System

---

## 1.2 Project Goal

Design and implement an AI-native fullstack financial question-answering system powered by LLMs, external market APIs, RAG pipelines, and LangGraph orchestration.

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
| Vector Database | Chroma |
| Embedding Model | BAAI/bge-small-en-v1.5 |
| Streaming | SSE |
| Testing | pytest |
| Async Testing | pytest-asyncio |
| HTTP Testing | httpx |

---

## 2.3 External Services

| Service | Usage |
|---|---|
| Yahoo Finance | Market data |
| Tavily Search | Web search |
| Tavily Extract | Web content extraction |
| OpenAI-compatible APIs | LLM inference |

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
| Intent Router                                    |
|   ├── Market Data Flow                           |
|   ├── RAG Flow                                   |
|   ├── Hybrid Flow                                |
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
| Tavily Extract     |        | Lightweight LLM Rerank   |
+--------------------+        +--------------------------+
         |                                   |
         +-----------------+-----------------+
                           |
                           v
+--------------------------------------------------+
|                 Persistence Layer                |
|--------------------------------------------------|
| SQLite | ChromaDB | Local File Storage           |
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
- auto-generated titles

---

## 5.3 Chat Area Responsibilities

The center chat area manages:

- markdown rendering
- streaming response rendering
- user input
- loading states
- citations
- tool execution status

---

## 5.4 Market Panel Responsibilities

The right market panel displays:

- current asset price
- daily change
- 7-day trend chart
- PE ratio
- market cap
- trading volume
- detected active asset

This panel updates dynamically based on:

```text
structured_data.active_asset
```

returned by backend responses.

---

# 6. Backend Architecture

## 6.1 Backend Layers

```text
api/
↓
graph/
↓
tools/
↓
repositories/
↓
database
```

---

## 6.2 Layer Responsibilities

| Layer | Responsibility |
|---|---|
| api | transport + SSE |
| graph | orchestration |
| tools | external integrations |
| repositories | DB access |
| database | persistence |

---

## 6.3 Backend Design Principles

The backend enforces:

- strict typing
- repository abstraction
- isolated tool layer
- graph-based orchestration
- Pydantic validation
- async-first design

---

# 7. LangGraph Workflow Design

## 7.1 Graph Overview

```text
User Query
    ↓
Intent Router
    ├── Market Query
    ├── RAG Query
    ├── Hybrid Query
    └── Unsupported Query
```

---

## 7.2 Market Query Flow

```text
Market Query
    ↓
Market Tool Node
    ↓
News Search Node
    ↓
Response Generation Node
    ↓
Structured Formatter Node
```

---

## 7.3 RAG Query Flow

```text
RAG Query
    ↓
Retriever Node
    ↓
Lightweight Rerank Node
    ↓
Context Builder
    ↓
Response Generation Node
```

---

## 7.4 Hybrid Query Flow

Hybrid queries combine:

- market data
- financial concepts
- news explanations
- RAG retrieval

Example:

```text
Why did Tesla stock fall recently and what does its PE ratio imply?
```

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
class GraphState(TypedDict):
    session_id: str

    user_query: str

    messages: list

    intent: str

    retrieved_docs: list

    reranked_docs: list

    market_data: dict

    citations: list

    structured_data: dict

    final_response: str

    error: str | None
```

---

## 8.3 State Design Principles

State objects must remain:

- serializable
- deterministic
- debuggable
- minimal
- explicit

---

# 9. Persistence Architecture

## 9.1 Databases

| Database | Usage |
|---|---|
| SQLite | relational persistence |
| Chroma | vector retrieval |

---

## 9.2 SQLite Responsibilities

SQLite stores:

- sessions
- messages
- document metadata
- ingestion jobs

SQLite does NOT store:

- embeddings
- market cache
- raw vector data

---

## 9.3 Chroma Responsibilities

Chroma stores:

- document chunks
- embeddings
- vector metadata

---

# 10. Database Schema

## 10.1 chat_sessions

```sql
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

---

## 10.2 chat_messages

```sql
CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata_json TEXT,
    created_at DATETIME NOT NULL,

    FOREIGN KEY(session_id)
    REFERENCES chat_sessions(id)
);
```

---

## 10.3 knowledge_documents

```sql
CREATE TABLE knowledge_documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    chunk_count INTEGER NOT NULL,
    created_at DATETIME NOT NULL
);
```

---

## 10.4 ingestion_jobs

```sql
CREATE TABLE ingestion_jobs (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME NOT NULL
);
```

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
Load session messages from SQLite
    ↓
Reconstruct conversation history
    ↓
Inject into graph state
    ↓
Generate response
    ↓
Persist new messages
```

---

## 11.3 Session Switching

Frontend supports:

- switching sessions
- restoring previous conversations
- continuing old conversations

---

# 12. RAG Architecture

## 12.1 Supported File Types

Supported:

- pdf
- md
- txt

Not supported:

- docx
- pptx
- html

---

## 12.2 RAG Pipeline

```text
Documents
    ↓
Chunking
    ↓
Embedding
    ↓
Chroma Storage
    ↓
Similarity Retrieval
    ↓
Lightweight LLM Rerank
    ↓
Context Builder
    ↓
LLM Generation
```

---

## 12.3 Chunking Strategy

```text
chunk_size = 800
chunk_overlap = 150
```

---

## 12.4 Embedding Model

```text
BAAI/bge-small-en-v1.5
```

---

## 12.5 Lightweight Rerank Strategy

The rerank stage uses:

```text
LLM-based reranking
```

instead of:

- cross-encoder rerankers
- heavyweight rerank models

Workflow:

```text
Top-K Retrieval
    ↓
LLM selects best chunks
    ↓
Final context assembly
```

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
- daily change
- 7-day trend
- 30-day trend
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
TTL = 60 seconds
```

No Redis or distributed cache will be used.

---

# 14. API Architecture

## 14.1 API Design Principles

All APIs must:

- use Pydantic schemas
- be fully typed
- support async execution
- return deterministic structures

---

## 14.2 Main API Categories

| Category | Purpose |
|---|---|
| Chat APIs | conversation |
| Session APIs | session management |
| RAG APIs | document ingestion |
| Health APIs | diagnostics |

---

## 14.3 Main Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/chat | send message |
| GET | /api/sessions | list sessions |
| POST | /api/sessions | create session |
| GET | /api/sessions/{id} | load session |
| DELETE | /api/sessions/{id} | delete session |
| POST | /api/rag/upload | upload document |
| GET | /api/health | health check |

---

# 15. SSE Streaming Protocol

## 15.1 Streaming Strategy

The system uses:

```text
event-based SSE
```

instead of raw token streaming.

---

## 15.2 SSE Event Types

### Token Event

```json
{
  "event": "token",
  "data": "Tesla"
}
```

---

### Structured Data Event

```json
{
  "event": "structured_data",
  "data": {}
}
```

---

### Citation Event

```json
{
  "event": "citations",
  "data": []
}
```

---

### Completion Event

```json
{
  "event": "done"
}
```

---

### Error Event

```json
{
  "event": "error",
  "data": {
    "message": "..."
  }
}
```

---

# 16. Repository Pattern

## 16.1 Repository Structure

```text
repositories/
├── session_repository.py
├── message_repository.py
├── document_repository.py
└── ingestion_repository.py
```

---

## 16.2 Repository Responsibilities

Repositories ONLY manage:

- DB CRUD
- query abstraction
- transaction isolation

Repositories must NOT contain:

- LLM logic
- orchestration logic
- business workflows

---

# 17. Tool Layer Design

## 17.1 Tool Layer Purpose

All external services must be isolated under:

```text
tools/
```

This includes:

- market APIs
- web search
- rerank
- vector retrieval

---

## 17.2 Tool Structure

```text
tools/
├── market_data_tool.py
├── tavily_search_tool.py
├── tavily_extract_tool.py
├── retrieval_tool.py
├── rerank_tool.py
└── embedding_tool.py
```

---

## 17.3 Tool Design Rules

Tools must:

- be stateless
- be independently testable
- expose typed interfaces
- avoid side effects

---

# 18. Frontend State Management

## 18.1 State Strategy

Frontend state management uses:

| Tool | Responsibility |
|---|---|
| Zustand | UI state |
| TanStack Query | server state |

---

## 18.2 Zustand Responsibilities

Zustand stores:

- active session
- sidebar state
- streaming state
- UI preferences

---

## 18.3 TanStack Query Responsibilities

TanStack Query manages:

- API fetching
- cache
- refetching
- optimistic updates

---

# 19. Markdown Rendering

## 19.1 Markdown Stack

```text
react-markdown
remark-gfm
rehype-highlight
```

---

## 19.2 Supported Markdown Features

- headings
- tables
- bullet lists
- code blocks
- inline code
- links

---

# 20. Charting

## 20.1 Chart Library

```text
Recharts
```

---

## 20.2 Supported Charts

- 7-day line chart
- 30-day line chart
- price trend chart

---

# 21. Auto Session Title Generation

## 21.1 Title Generation Strategy

After first user query:

```text
LLM generates short session title
```

Example:

```text
Tesla Stock Analysis
```

---

# 22. Startup Strategy

## 22.1 Single Startup Script

Project root includes:

```text
start_project.bat
```

Responsibilities:

- start backend
- start frontend
- initialize environment
- launch both terminals

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
├── unit/
├── integration/
├── api/
├── e2e/
└── fixtures/
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

- incoming requests
- graph routing
- tool invocation
- retrieval results
- rerank decisions
- SSE lifecycle
- API failures

---

# SPD.md — Financial Asset QA System
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
├── knowledge_base/
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

```text
backend/
├── app/
│
├── api/
│   ├── routes/
│   │   ├── chat.py
│   │   ├── sessions.py
│   │   ├── rag.py
│   │   └── health.py
│   │
│   ├── schemas/
│   │   ├── chat.py
│   │   ├── session.py
│   │   ├── rag.py
│   │   └── common.py
│   │
│   └── dependencies/
│
├── graph/
│   ├── builder.py
│   ├── state.py
│   ├── intent_classifier.py
│   ├── nodes/
│   │   ├── intent_node.py
│   │   ├── market_node.py
│   │   ├── retrieval_node.py
│   │   ├── rerank_node.py
│   │   ├── generation_node.py
│   │   └── formatter_node.py
│   │
│   └── edges/
│
├── tools/
│   ├── market_data_tool.py
│   ├── tavily_search_tool.py
│   ├── tavily_extract_tool.py
│   ├── retrieval_tool.py
│   ├── rerank_tool.py
│   ├── embedding_tool.py
│   └── llm_tool.py
│
├── repositories/
│   ├── session_repository.py
│   ├── message_repository.py
│   ├── document_repository.py
│   └── ingestion_repository.py
│
├── services/
│   ├── session_service.py
│   ├── rag_service.py
│   ├── streaming_service.py
│   └── title_generation_service.py
│
├── database/
│   ├── base.py
│   ├── models/
│   ├── session.py
│   ├── engine.py
│   └── migrations/
│
├── vectorstore/
│   ├── chroma_client.py
│   └── collections.py
│
├── prompts/
│   ├── system/
│   ├── market/
│   ├── rag/
│   ├── rerank/
│   └── formatting/
│
├── providers/
│   ├── base_provider.py
│   ├── openai_provider.py
│   ├── openrouter_provider.py
│   └── mock_provider.py
│
├── utils/
│   ├── logger.py
│   ├── markdown.py
│   ├── token_counter.py
│   ├── time.py
│   └── errors.py
│
├── config/
│   ├── settings.py
│   └── constants.py
│
├── main.py
└── requirements.txt
```

---

# 27. Frontend File Structure

## 27.1 Frontend Structure

```text
frontend/
├── src/
│
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
│
├── components/
│   ├── chat/
│   ├── market/
│   ├── sidebar/
│   ├── markdown/
│   ├── ui/
│   └── common/
│
├── features/
│   ├── chat/
│   ├── sessions/
│   ├── market/
│   └── rag/
│
├── services/
│   ├── api/
│   ├── sse/
│   └── session/
│
├── hooks/
│   ├── useChat.ts
│   ├── useStreaming.ts
│   ├── useSessions.ts
│   └── useMarketPanel.ts
│
├── stores/
│   ├── sessionStore.ts
│   ├── chatStore.ts
│   └── uiStore.ts
│
├── types/
│   ├── api.ts
│   ├── session.ts
│   ├── chat.ts
│   └── market.ts
│
├── lib/
│   ├── markdown.ts
│   ├── utils.ts
│   └── constants.ts
│
├── tests/
│   └── e2e/
│
├── public/
│
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.ts
```

---

# 28. API Contract Design

## 28.1 API Standards

All APIs must:

- use JSON
- use typed Pydantic schemas
- return deterministic structures
- use UTC timestamps
- support async execution

---

# 29. Chat API

## 29.1 Endpoint

```http
POST /api/chat
```

---

## 29.2 Request Schema

````python
class ChatRequest(BaseModel):
    session_id: str
    query: str
    stream: bool = True
````
---

## 29.3 Non-Streaming Response
```` Python
class ChatResponse(BaseModel):
    answer_markdown: str
    structured_data: dict
    citations: list[str]
    metadata: dict
````
---

## 29.4 Streaming Response
Streaming uses:
``` 
text/event-stream
```
with event-based payloads.

---

# 30. Session APIs
## 30.1 Create Session
``` http
POST /api/sessions
```

---

## 30.2 Response
``` Python
class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
```

---

## 30.3 List Sessions
``` http
GET /api/sessions
```

---

## 30.4 Load Session
``` http
GET /api/sessions/{session_id}
```

---

## 30.5 Session Detail Response
``` Python
class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: list[ChatMessage]
```

---

# 31. RAG Upload API
## 31.1 Endpoint
``` http
POST /api/rag/upload
```
---

## 31.2 Supported Formats
- pdf
- md
- txt

---

## 31.3 Upload Response
``` Python
class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    chunk_count: int
    status: str
```

---

# 32. Health API
## 32.1 Endpoint
``` http
GET /api/health
```

## 32.2 Response
``` Python
class HealthResponse(BaseModel):
    status: str
    database: str
    vectorstore: str
    llm_provider: str
```

---

# 33. SQLAlchemy Model Design
## 33.1 Session Model
``` Python
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)

    title = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False)

    updated_at = Column(DateTime, nullable=False)
```

---

## 33.2 Message Model
``` Python
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)

    session_id = Column(
        String,
        ForeignKey("chat_sessions.id")
    )

    role = Column(String, nullable=False)

    content = Column(Text, nullable=False)

    metadata_json = Column(Text)

    created_at = Column(DateTime, nullable=False)
```


# 34. LangGraph Builder Design
## 34.1 Graph Builder
File:
`graph/builder.py`

Responsible for:
- creating graph
- registering nodes
- registering edges
- compiling graph

---

## 34.2 Node Registration
``` Python
graph.add_node("intent", intent_node)

graph.add_node("market", market_node)

graph.add_node("retrieval", retrieval_node)

graph.add_node("rerank", rerank_node)

graph.add_node("generation", generation_node)

graph.add_node("formatter", formatter_node)
```

---

# 35. Intent Router Logic
## 35.1 Router Categories
Supported intents:
``` 
market
rag
hybrid
unsupported
```

## 35.2 Intent Examples
Market Query: `What is Tesla's current stock price?`

RAG Query: `What is PE ratio?`

Hybrid Query: `Why did Tesla stock rise and what does PE ratio indicate?`

---

# 36. Tool Layer Specification
## 36.1 Market Data Tool
File: `tools/market_data_tool.py`

Responsibilities:
- fetch stock price
- fetch historical data
- fetch market metrics
- normalize market output

---

## 36.2 Tavily Search Tool
Responsibilities:
- search financial news
- retrieve related articles
- provide citation URLs

---

## 36.3 Retrieval Tool
Responsibilities:
- similarity search
- top-k retrieval
- metadata filtering

---

## 36.4 Rerank Tool
Responsibilities:
- lightweight reranking
- chunk selection
- context prioritization

---

# 37. LLM Provider Abstraction
## 37.1 Design Goal

The project must support: any OpenAI-compatible API

---

## 37.2 Base Provider Interface
``` Python
class BaseLLMProvider(ABC):

    @abstractmethod
    async def chat(
        self,
        messages: list,
        stream: bool = False
    ):
        pass
```

## 37.3 Supported Providers
Initial implementations:
- OpenAI
- OpenRouter
- Mock Provider

---

# 38. Prompt Engineering Architecture
## 38.1 Prompt Directory
```
prompts/
├── system/
├── market/
├── rag/
├── rerank/
└── formatting/
```

---
## 38.2 Prompt Separation Strategy
Different prompts are isolated by responsibility.

Reasoning:
- maintainability
- testability
- prompt iteration
- debugging

---

# 39. System Prompt Specification
## 39.1 System Prompt Goals

The assistant must:
- separate facts from analysis
- avoid hallucination
- cite sources
- avoid price prediction
- acknowledge uncertainty

---

## 39.2 Required Behaviors

The system prompt must explicitly enforce:
```
objective market data
≠
analytical interpretation
```

## 39.3 Forbidden Behaviors

The assistant must NOT:
- fabricate market prices
- predict future stock movements
- invent citations
- claim unsupported financial conclusions

---

# 40. Market Analysis Prompt Rules
## 40.1 Required Structure

Market responses should contain:
1. Current Market Data
2. Trend Summary
3. Potential Influencing Factors
4. Risk / Uncertainty

---

## 40.2 Analysis Constraints

Analysis must:

- remain probabilistic
- avoid certainty language
- distinguish news from inference

---

# 41. RAG Prompt Rules
## 41.1 RAG Grounding

RAG responses must:

- prioritize retrieved context
- avoid unsupported expansion
- cite retrieved documents

---

## 41.2 Citation Requirement

Every RAG response should include:

Sources:
- document name
- chunk reference

---

# 42. Structured Output Rules
## 42.1 Structured Metadata Schema
``` json
{
  "active_asset": "TSLA",

  "price": 221.13,

  "change_pct": 2.4,

  "trend": "bullish",

  "market_metrics": {
    "market_cap": "...",
    "pe_ratio": "...",
    "volume": "..."
  }
}
```

## 42.2 Structured Data Rules

Structured data must:

- remain deterministic
- use normalized keys
- avoid markdown formatting

---

# 43. Streaming Service Design
## 43.1 Streaming Responsibilities

Streaming service manages:

- SSE lifecycle
- event formatting
- connection cleanup
- stream termination

---

## 43.2 Streaming Flow
```
LLM token
    ↓
SSE event
    ↓
Frontend incremental rendering
```
---

# 44. Frontend Streaming Strategy
## 44.1 Streaming Method
Frontend uses: fetch + ReadableStream

NOT: EventSource

## 44.2 Reasoning

Advantages:

- supports POST requests
- supports auth expansion
- supports cancellation
- easier future extensibility

---

# 45. Frontend Component Design
## 45.1 Chat Components
```
components/chat/
├── ChatContainer.tsx
├── ChatMessage.tsx
├── ChatInput.tsx
├── StreamingMessage.tsx
└── CitationList.tsx
```

---

## 45.2 Market Components
```
components/market/
├── MarketPanel.tsx
├── PriceCard.tsx
├── TrendChart.tsx
├── MetricsCard.tsx
└── NewsPanel.tsx
```

---

## 45.3 Sidebar Components
```
components/sidebar/
├── SessionList.tsx
├── SessionItem.tsx
└── NewChatButton.tsx
```

---

# 46. State Management Rules
## 46.1 Zustand Rules

Zustand stores ONLY UI state.

Examples:

- selected session
- sidebar collapse
- loading state

---

## 46.2 TanStack Query Rules

TanStack Query manages ONLY server state.

Examples:

- sessions API
- chat history
- market data

---

# 47. Markdown Rendering Rules
## 47.1 Markdown Features

The renderer must support:

- GitHub markdown
- tables
- inline code
- syntax highlight

---

## 47.2 Security Rules

Markdown rendering must:

- sanitize HTML
- disable unsafe raw HTML

---

# 48. Market Panel Behavior
## 48.1 Panel Update Trigger

The market panel updates when: `structured_data.active_asset` changes.

---

## 48.2 Default Empty State

Default state: `No asset selected`

---

# 49. Chart Design
## 49.1 Chart Types

Charts include:

- 7-day line chart
- 30-day line chart

---

## 49.2 Chart Source

Charts use: Yahoo Finance historical data

---

# 50. Error Handling Specification
## 50.1 Fail-Fast Policy

No graceful fallback logic.

Errors must propagate explicitly.

---

## 50.2 Error Categories

| Error Type         | Behavior         |
| ------------------ | ---------------- |
| LLM Failure        | return error     |
| Market API Failure | return error     |
| Retrieval Failure  | return error     |
| SSE Failure        | terminate stream |

---

## 50.3 Frontend Error UX
Frontend displays:

- toast notification
- failed message state
- retry button

---

# 51. Logging Architecture
## 51.1 Required Logs

The system must log:

- incoming requests
- graph routing
- node execution
- retrieval latency
- market API latency
- SSE lifecycle

---

## 51.2 Log Format

Preferred format: structured logs

---

# 52. Configuration Management
## 52.1 Environment Variables
```
OPENAI_API_KEY=
OPENAI_BASE_URL=
TAVILY_API_KEY=

SQLITE_PATH=
CHROMA_PATH=

EMBEDDING_MODEL=
```

---

## 52.2 Settings Management
Centralized under: `config/settings.py`

---

# 53. Local Development Workflow
## 53.1 Startup Command

Single startup entry: `start_project.bat`

---

## 53.2 Batch Script Responsibilities

The script should:

- activate environments
- start backend
- start frontend
- open separate terminals

---

# 54. AI Coding Agent Rules
## 54.1 Mandatory Constraints

AI coding agents MUST:

- follow file structure exactly
- avoid architectural changes
- maintain strict typing
- preserve repository pattern
- preserve tool isolation

---

## 54.2 Forbidden Behaviors

AI coding agents must NOT:

- merge layers
- place business logic in routes
- bypass repositories
- directly call APIs inside graph nodes

---

# 55. Engineering Priorities
## 55.1 Priority Order
1. correctness
2. architecture clarity
3. maintainability
4. testability
5. UI polish

---

# SPD.md — Financial Asset QA System
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
| LangGraph routing | correct intent flow |
| Tool execution | correct API integration |
| Database operations | correct persistence |
| SSE streaming | stable incremental delivery |
| RAG pipeline | correct retrieval behavior |
| Session persistence | correct history reconstruction |
| Frontend integration | correct end-to-end behavior |

---

## 56.3 Coverage Targets

| Layer | Target |
|---|---|
| Backend overall | 70% - 80% |
| Critical services | 80%+ |
| Frontend unit testing | not required |
| E2E critical flows | mandatory |

---

# 57. Backend Test Structure

## 57.1 Test Directory Structure

```text
tests/
├── unit/
│   ├── graph/
│   ├── tools/
│   ├── repositories/
│   └── services/
│
├── integration/
│   ├── rag/
│   ├── market/
│   └── graph/
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
│
├── conftest.py
└── pytest.ini
```

---

# 58. Unit Testing Specification

## 58.1 Unit Testing Scope

Unit tests should cover:

- repositories
- graph nodes
- tools
- utility functions
- services

---

## 58.2 Repository Testing

Repositories must test:

- CRUD correctness
- transaction correctness
- invalid query handling

---

## 58.3 Tool Testing

Tools must test:

- API normalization
- invalid symbol handling
- response parsing

---

## 58.4 Graph Node Testing

Graph node tests must validate:

- state transition correctness
- expected output fields
- failure propagation

---

# 59. Integration Testing

## 59.1 Integration Scope

Integration tests validate:

- graph orchestration
- retrieval pipeline
- database integration
- streaming pipeline

---

## 59.2 Market Integration Tests

Validate:

- Yahoo Finance retrieval
- normalization logic
- market metric extraction

---

## 59.3 RAG Integration Tests

Validate:

- embedding creation
- Chroma insertion
- retrieval quality
- rerank execution

---

# 60. API Testing

## 60.1 API Testing Stack

```text
pytest
pytest-asyncio
httpx
```

---

## 60.2 API Testing Rules

Every endpoint must validate:

- success response
- invalid request handling
- schema correctness
- status code correctness

---

## 60.3 Chat API Tests

Required tests:

```text
- send normal query
- send market query
- send rag query
- send hybrid query
- invalid payload
- streaming response
```

---

## 60.4 Session API Tests

Required tests:

```text
- create session
- load session
- list sessions
- delete session
```

---

# 61. Playwright E2E Testing

## 61.1 E2E Goals

Playwright validates:

```text
real user workflow
```

instead of isolated frontend logic.

---

## 61.2 Playwright Coverage

Mandatory flows:

```text
1. open application
2. create session
3. ask market question
4. receive streaming response
5. switch session
6. restore history
7. upload RAG document
8. ask RAG question
9. ask hybrid question
10. verify market panel updates
```

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

- academic projects benefit from real integration
- easier demonstration
- better architecture validation

---

## 62.2 Allowed Mocking

Allowed:

- mock LLM provider
- mock Tavily responses
- mock Yahoo Finance failures

---

## 62.3 Forbidden Mocking

Avoid mocking:

- repositories
- graph routing
- SSE protocol
- retrieval pipeline

---

# 63. Fixture Design

## 63.1 Fixture Categories

```text
fixtures/
├── documents/
├── market_data/
├── sessions/
└── graph_states/
```

---

## 63.2 Test Documents

The repository should include:

- financial glossary markdown
- earnings summary txt
- example financial PDF

---

# 64. Streaming Test Strategy

## 64.1 SSE Validation

Streaming tests must validate:

- ordered token delivery
- stream completion
- structured event correctness
- stream termination behavior

---

## 64.2 Streaming Event Validation

Required events:

```text
token
structured_data
citations
done
error
```

---

# 65. LangGraph Testing Specification

## 65.1 Graph Testing Priorities

Critical graph behaviors:

- routing correctness
- state mutation correctness
- node execution order
- error propagation

---

## 65.2 Required Graph Tests

```text
- market route
- rag route
- hybrid route
- unsupported route
- rerank execution
- formatter execution
```

---

# 66. RAG Evaluation Rules

## 66.1 Retrieval Validation

RAG tests should validate:

- retrieved chunk relevance
- chunk ordering
- rerank filtering

---

## 66.2 Citation Validation

Responses must reference:

- retrieved source
- document metadata

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

- Tailwind utility classes
- shadcn/ui components
- responsive layout
- dark mode compatibility

---

## 67.3 Forbidden Frontend Behaviors

Avoid:

- inline CSS
- untyped props
- oversized global state
- direct fetch calls inside components

---

# 68. Backend Engineering Rules

## 68.1 Backend Philosophy

Backend must remain:

- layered
- typed
- modular
- deterministic

---

## 68.2 Mandatory Backend Rules

Required:

- async endpoints
- typed schemas
- repository isolation
- tool isolation
- structured logging

---

## 68.3 Forbidden Backend Behaviors

Forbidden:

- business logic inside routes
- direct DB access inside graph nodes
- raw SQL inside services
- untyped responses

---

# 69. Prompt Engineering Rules

## 69.1 Prompt Design Philosophy

Prompts must:

- be modular
- be explicit
- minimize hallucination
- enforce structured behavior

---

## 69.2 Prompt Constraints

Prompts must explicitly instruct:

```text
- distinguish facts from analysis
- avoid unsupported claims
- avoid future prediction
- cite uncertainty
```

---

## 69.3 Output Formatting Rules

Responses should:

- use concise markdown
- avoid excessive verbosity
- maintain financial professionalism

---

# 70. LLM Integration Rules

## 70.1 Provider Compatibility

The system must support:

```text
OpenAI-compatible APIs
```

including:

- OpenAI
- OpenRouter
- DeepSeek-compatible endpoints

---

## 70.2 Model Configuration

Configuration must be externalized:

```text
.env
```

NOT hardcoded.

---

## 70.3 Streaming Rules

Streaming providers must support:

- incremental tokens
- async iteration
- cancellation

---

# 71. RAG Document Processing

## 71.1 Ingestion Pipeline

```text
upload
    ↓
parse
    ↓
chunk
    ↓
embed
    ↓
store
```

---

## 71.2 Chunk Metadata

Every chunk should contain:

```json
{
  "document_id": "...",
  "document_name": "...",
  "chunk_index": 0
}
```

---

# 72. Financial Analysis Rules

## 72.1 Financial Data Requirements

All market analysis must:

- use actual retrieved data
- separate facts from interpretation
- avoid invented statistics

---

## 72.2 News Analysis Rules

News-based reasoning must:

- cite article source
- distinguish article facts from AI inference

---

# 73. Session Management Rules

## 73.1 Session Lifecycle

```text
create
→ persist
→ update
→ reload
→ delete
```

---

## 73.2 Session Persistence Rules

Every completed interaction must persist:

- user message
- assistant response
- structured metadata

---

# 74. Structured Metadata Rules

## 74.1 Metadata Usage

Structured metadata is used for:

- frontend rendering
- market panel updates
- chart rendering
- testing assertions

---

## 74.2 Metadata Constraints

Metadata must remain:

- JSON serializable
- deterministic
- normalized

---

# 75. Error Handling UX

## 75.1 Frontend Error Display

Frontend should display:

- toast notification
- retry button
- failed state indicator

---

## 75.2 Backend Error Format

````json
{
  "error": {
    "type": "MarketAPIError",
    "message": "Failed to retrieve market data"
  }
}
````

---
# 76. Local File Storage
## 76.1 Knowledge Base Directory
`knowledge_base/`

stores:

- uploaded documents
- parsed intermediate files

---

## 76.2 Storage Constraints

No cloud storage integration required.

---

# 77. Environment Setup
## 77.1 Backend Setup
``` 
python -m venv venv
pip install -r requirements.txt
```

---

## 77.2 Frontend Setup
```
npm install
npm run dev
```

# 78. Startup Script Specification
## 78.1 Required File
`start_project.bat`

---

## 78.2 Script Responsibilities

The script should:

1. activate backend environment
2. start FastAPI server
3. start frontend server
4. open both terminals

---

# 79. README Requirements
## 79.1 Mandatory Sections

README must contain:

- project overview
- architecture diagram
- tech stack
- setup instructions
- API overview
- LangGraph workflow
- RAG pipeline
- prompt engineering strategy
- testing strategy
- limitations
- future improvements

---

## 79.2 Architecture Diagram Requirement

README must include:

- system architecture diagram
- graph workflow diagram

---

# 80. Demo Video Requirements
## 80.1 Mandatory Demonstrations

The demo video must show:
1. project overview
2. market question
3. streaming response
4. market panel update
5. RAG upload
6. RAG question
7. hybrid question
8. session switching
9. architecture explanation

---

# 81. Suggested Implementation Order
## 81.1 Recommended Development Sequence
### Phase 1: backend foundation
Build:

- FastAPI
- SQLite
- SQLAlchemy
- sessions
- message persistence

---

### Phase 2: LangGraph integration
Build:

- graph
- state
- router
- market flow

---

### Phase 3: market data integration

Build:

- Yahoo Finance tools
- market formatter
- structured response

---

### Phase 4: frontend chat UI
Build:

- sidebar
- chat area
- streaming rendering

---

### Phase 5: market panel

Build:

- price card
- chart
- metrics

---

### Phase 6: RAG pipeline

Build:

- ingestion
- Chroma
- retrieval
- rerank

---

### Phase 7: Playwright E2E

Build:

- critical user flow tests

---

# 82. Acceptance Criteria
## 82.1 Functional Acceptance

The system is considered complete when it supports:

- market QA
- RAG QA
- hybrid QA
- streaming responses
- session persistence
- session switching
- market panel updates
- document ingestion

---

## 82.2 Engineering Acceptance

The system must demonstrate:

- clean architecture
- typed schemas
- modular layering
- test coverage
- repository pattern
- tool abstraction

---

## 82.3 UI Acceptance

Frontend must demonstrate:

- responsive layout
- streaming UX
- markdown rendering
- market visualization

---

# 83. Non-Goals
## 83.1 Explicit Non-Goals

The project intentionally excludes:

- authentication
- multi-user architecture
- Redis
- Docker
- Kubernetes
- distributed systems
- production deployment
- advanced observability
- enterprise security

---

# 84. Future Improvement Ideas
## 84.1 Potential Extensions

Future improvements may include:

- Redis caching
- auth system
- portfolio tracking
- multi-agent architecture
- websocket streaming
- advanced rerank models
- evaluation framework
- deployment pipeline

---

# 85. Final Architecture Summary
## 85.1 Core Stack Summary

```
Frontend:
Next.js + TypeScript + Tailwind + shadcn/ui

Backend:
FastAPI + LangGraph + SQLAlchemy

Databases:
SQLite + Chroma

RAG:
Embedding + Retrieval + Lightweight LLM Rerank

Streaming:
Event-based SSE

Testing:
pytest + Playwright
```

---

# 86. Final Engineering Philosophy

The project prioritizes:

- clarity
- modularity
- AI-native orchestration
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

- follow this SPD strictly
- preserve architecture boundaries
- avoid unnecessary abstraction
- prioritize correctness over creativity

## 87.2 Final Constraint

If implementation conflicts arise:
```
architecture consistency
>
feature expansion
```

