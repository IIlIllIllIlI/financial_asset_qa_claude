# 金融资产问答系统 (Financial Asset QA System)

## 项目目标

一个智能金融问答助手，支持三类查询：
- **市场数据**：股票价格查询、市场指标分析（通过 yfinance）
- **金融知识**：RAG 检索增强生成的金融概念解释（基于本地知识库）
- **混合分析**：市场数据 + 知识库 + 新闻融合分析

## 技术栈

| 层 | 技术 | 备注 |
|---|---|---|
| 后端框架 | FastAPI + Uvicorn | Python 3.12+, port 8000 |
| AI 编排 | LangGraph (StateGraph) | 10 节点状态图，条件路由 |
| LLM | MiniMax M2.7 | OpenAI 兼容 API，reasoning 模型（输出 `<think>` 标签） |
| 向量检索 | ChromaDB + BGE-small-zh-v1.5 | 本地 CPU 运行，笔记本级延迟 |
| 数据库 | SQLite + SQLAlchemy ORM | 文件存储：`backend/data/sqlite.db` |
| 前端框架 | Next.js 16 + React 19 | Turbopack 开发服务器，port 3000 |
| 状态管理 | TanStack Query + Zustand | 服务端状态 (RQ) + 客户端状态 (Zustand) |
| 样式 | Tailwind CSS v4 | 配合 Radix UI 无样式组件 |
| E2E 测试 | Playwright 1.60 | Chromium, 单 worker, 串行 |
| 后端测试 | pytest + pytest-asyncio | 36 个测试用例 |
| 外部 API | yfinance, Tavily Search | 市场数据 + 网页搜索 |

## 项目结构

```
.
├── backend/                   # Python FastAPI 后端
│   ├── app/
│   │   ├── api/routes/        # POST /api/chat (SSE), CRUD /api/sessions, /api/rag/upload
│   │   ├── graph/             # LangGraph: builder, state, nodes/, edges/, prompts/
│   │   ├── tools/             # 6 tools: market_data, retrieval, rerank, embedding, tavily_*
│   │   ├── services/          # rag_service, session_service, title_generation_service
│   │   ├── models/            # SQLAlchemy: ChatSession, ChatMessage, KnowledgeDocument, IngestionJob
│   │   ├── repositories/      # 4 CRUD repositories
│   │   ├── providers/         # LLM provider (MiniMax via OpenAI compat)
│   │   ├── vectorstore/       # ChromaDB 单例
│   │   ├── database/          # SQLAlchemy engine + session factory
│   │   ├── config/            # settings.py (Pydantic), constants.py
│   │   └── utils/             # strip_thinking, prompt_loader, logger, errors
│   ├── tests/                 # pytest: api/ + unit/
│   └── requirements.txt
├── frontend/                  # Next.js 前端
│   ├── src/
│   │   ├── app/               # layout, page, providers (App Router)
│   │   ├── components/        # chat/, market/, sidebar/, common/, markdown/
│   │   ├── hooks/             # useChat (SSE), useSessions (RQ), useMarketPanel
│   │   ├── stores/            # chatStore, sessionStore, uiStore (Zustand)
│   │   ├── services/          # sse/sseClient.ts, api/client.ts, api/sessions.ts
│   │   ├── types/             # api, chat, session, market
│   │   └── lib/               # constants
│   ├── tests/e2e/             # 26 个 Playwright E2E 测试
│   └── playwright.config.ts
├── knowledge_base/            # 3 篇金融知识文档 (.md)
├── docs/                      # TSD_v1.md, requirement.md
└── .env                       # 放在 docs/.env 或项目根目录
```

## 核心架构

### LangGraph 流程图（10 节点）

```
ENTRY → intent ──→ market_data → news → extract ──→ generation → formatter → END
              │                                                    ↑
              ├──→ retrieval → rerank ─────────────────────────────┤
              │                                                    ↑
              ├──→ (hybrid: 两条路径汇合) ──→ merge ───────────────┘
              │
              └──→ (unsupported) → rejection → END
```

- **条件路由**：`edges/router.py` 三个路由函数根据 `intent` 决定路径
- **故障快速传递**：每个节点首行检查 `state.get("error")`，有错则跳过
- **SSE 流式**：`_token_queue`（asyncio.Queue）连接 LangGraph 节点和 SSE 响应

### SSE 流式数据流

```
generation_node → queue.put({type: "token", content: "..."})
        → chat.py event_stream() → yield "event: token\ndata: {...}\n\n"
        → sseClient.ts parseSSEEvents() → callbacks.onToken()
        → chatStore.setStreamingTokens() → StreamingMessage 组件重渲染
```

### 关键设计模式

- **单例模式**：LLM Provider、Embedding Model、Vector Store、Compiled Graph 均懒初始化
- **Repository 模式**：每个 SQLAlchemy Model 对应一个 Repository 类
- **Supplier Pattern**：`db_session_factory()()` 延迟获取 DB 会话（避免迭代器问题）

## 决策习惯与约定

### 编码风格
- **Python**：类型注解、async/await、单行 docstring、无冗余注释
- **TypeScript**：严格模式、接口先于 type、React 函数组件、无默认 export 外的命名导出
- **中文优先**：面向用户的文本（UI label、提示词、错误消息、session 标题）使用中文
- **后端路径**：`backend/` 目录是实际工作目录，uvicorn 从此启动；settings.py 中路径相对于 backend 目录

### E2E 测试注意事项
- **MiniMax M2.7 延迟不稳定**：15–120 秒，测试等待用户消息需 90s timeout
- **用户消息不本地添加**：仅在 SSE 流结束后由 React Query 从后端加载，`sendMessage` 不写本地
- **Turbopack HMR**：阻止 Playwright `page.goto` 的 `load` 事件，用 `waitUntil: "domcontentloaded"`
- **next-themes**：`ThemeProvider` 的 `setTheme` 在 Playwright 中不触发 React 重渲染，测试中用 `page.evaluate` 直接操作 class
- **Sidebar 污染**：`getByText("TSLA")` 会匹配侧边栏 session 标题，用 `.locator(".w-80").getByText(...)` 限定范围

### 已知陷阱
- **LangGraph `ainvoke` 不修改输入 state**：返回新的 result dict，不要从 `initial_state` 读取图执行后的结果
- **SSE 解析器扁平化**：`parseSSEEvents` 把 JSON data spread 到 event 对象，访问 `event.structured_data` 是 undefined，应访问 `event.assets`
- **MiniMax `<think>` 标签**：reasoning 模型输出 `<think>...</think>`，后端 `strip_thinking()` + 前端 `stripThinking()` 均需过滤
- **`sessionmaker` 不是迭代器**：`db_session_factory()` 返回 sessionmaker 对象，调用它获取 session → `db_session_factory()()`

## 环境变量

```bash
MINIMAX_API_KEY=xxx          # MiniMax API 密钥
TAVILY_API_KEY=xxx          # Tavily 搜索 API 密钥
MINIMAX_BASE_URL=https://api.minimaxi.com/v1   # 可选
MINIMAX_MODEL=MiniMax-M2.7  # 可选
```

`.env` 文件存放在项目根目录（settings.py 期望位置）或 `docs/.env`。

## 启动命令

```bash
# 后端
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端（开发）
cd frontend && npm run dev

# E2E 测试（先启动后端，再运行测试）
cd frontend && npx playwright test --reporter=line

# 后端单元测试
cd backend && python -m pytest tests/ -v

# 清理数据库
python -c "import sqlite3; c=sqlite3.connect('backend/data/sqlite.db'); c.execute('DELETE FROM chat_messages'); c.execute('DELETE FROM chat_sessions'); c.commit(); c.close()"
```

## 知识库

`knowledge_base/` 目录包含 3 篇中文金融知识文档，首次启动时自动导入 ChromaDB：
- `pe_ratio.md` — 市盈率（P/E Ratio）
- `dcf_valuation.md` — DCF 估值法
- `ebitda.md` — EBITDA 指标

自动导入的去重依据为 source filename，不会重复导入。
