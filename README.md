# 金融资产问答系统 (Financial Asset QA System)

基于大模型的全栈金融资产问答系统，支持**资产价格分析**、**金融知识 RAG 问答**和**混合深度分析**。

## 系统架构

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              Frontend (Next.js 16)                        │
│  ┌──────────┐  ┌───────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ Sidebar  │  │ Chat Area │  │ Market     │  │ StreamingMessage     │  │
│  │ (会话列表)│  │ (消息展示) │  │ Panel      │  │ (流式 Markdown 渲染) │  │
│  └──────────┘  └───────────┘  │ (图表/表格)│  └──────────────────────┘  │
│                               └────────────┘                            │
│  Stores: Zustand (chatStore, sessionStore, uiStore)                     │
│  Server State: TanStack Query (sessions, session detail)                │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ SSE / HTTP REST
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           Backend (FastAPI)                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    LangGraph StateGraph (10 Nodes)                 │   │
│  │                                                                    │   │
│  │   ENTRY → intent ──→ market_data → news → extract ──→ generation  │   │
│  │                 │                                   ↗             │   │
│  │                 ├──→ retrieval → rerank ────────────┘              │   │
│  │                 │                                   ↗             │   │
│  │                 └──→ (hybrid: 两条路径汇合) → ———————┘              │   │
│  │                                                                    │   │
│  │   Conditional Routing: intent → market | knowledge | hybrid        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Services: SessionService, RAGService, TitleGenerationService            │
│  Repositories: Session, Message, KnowledgeDocument, IngestionJob         │
└───┬──────────────┬────────────────────┬──────────────────────────────────┘
    │              │                    │
    ▼              ▼                    ▼
┌─────────┐  ┌──────────┐  ┌────────────────────┐
│ yfinance │  │  Tavily  │  │  ChromaDB (本地)    │
│ 市场数据  │  │ 网页搜索  │  │  BGE-small-zh-v1.5 │
└─────────┘  └──────────┘  └────────────────────┘
    │              │                    │
    ▼              ▼                    ▼
┌─────────────────────────────────────────────────┐
│              SQLite (会话/消息/知识库)             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                 LLM Provider                     │
│     MiniMax M2.7 (OpenAI 兼容 API)               │
│     Reasoning 模型，支持 function calling         │
└─────────────────────────────────────────────────┘
```

### 数据流（SSE 流式）

```
generation_node → asyncio.Queue.put(token)
  → chat.py event_stream() → SSE: "event: token\ndata: {...}"
  → sseClient.ts parseSSEEvents() → callbacks.onToken()
  → chatStore.appendToken() → StreamingMessage 实时渲染
```

### 三类意图路由

| 意图 | 路径 | 说明 |
|------|------|------|
| `market` | intent → market_data → news → extract → generation | 股票价格、涨跌幅分析 |
| `knowledge` | intent → retrieval → rerank → generation | 金融概念 RAG 问答 |
| `hybrid` | 两路并行 → merge → generation | 市场数据 + 知识库融合分析 |

## 技术选型

| 层 | 技术 | 选型理由 |
|---|---|---|
| **后端框架** | FastAPI + Uvicorn | 原生 async 支持，适配 LangGraph 异步编排；SSE 流式响应开箱即用 |
| **AI 编排** | LangGraph (StateGraph) | 10 节点条件路由，支持并行分支、故障快速传递；比 LangChain Agent 更可控 |
| **LLM** | MiniMax M2.7 | Reasoning 模型，复杂金融分析场景表现好；OpenAI 兼容 API，迁移成本低 |
| **向量检索** | ChromaDB | 轻量级本地运行，无需额外服务；Python 原生集成 |
| **Embedding** | BGE-small-zh-v1.5 | 中文金融文本嵌入效果好；24MB 极小体积，CPU 运行毫秒级延迟 |
| **Rerank** | BAAI/bge-reranker-base | 本地 CrossEncoder 重排序，替换 LLM rerank，延迟从 3-10s 降至 1-2s |
| **数据库** | SQLite + SQLAlchemy ORM | 零配置，适合单机部署；Repository 模式解耦数据访问 |
| **前端框架** | Next.js 16 + React 19 | App Router，Turbopack 开发服务器；SSR 可选，本项目以 CSR 为主 |
| **状态管理** | TanStack Query + Zustand | RQ 管理服务端缓存和自动失效；Zustand 管理客户端 UI 状态 |
| **样式** | Tailwind CSS v4 + Radix UI | 原子化 CSS，Radix 提供无样式可访问组件 |
| **图表** | Recharts | 声明式 API，React 生态集成好；支持 K 线图等金融图表 |
| **E2E 测试** | Playwright | 26 个测试用例，覆盖会话管理、聊天、市场面板全流程 |
| **后端测试** | pytest + pytest-asyncio | 36 个测试用例，覆盖 API 和工具函数 |

### 模型选型对比

| 环节 | 方案 | 延迟 | 成本 | 备注 |
|------|------|------|------|------|
| 对话生成 | MiniMax M2.7 | 15-120s | token plan | Reasoning 模型，输出带 `<think>` 标签 |
| Embedding | BGE-small-zh-v1.5 (本地) | <100ms | 免费 | CPU 运行，24MB |
| Rerank | BGE-reranker-base (本地) | 1-2s | 免费 | CPU 运行，278M 参数 |
| 意图分类 | MiniMax M2.7 | 3-5s | token plan | function_calling 模式 |
| 标题生成 | MiniMax M2.7 | 3-10s | token plan | 与主 Graph 并发执行，不阻塞流式输出 |

## Prompt 设计思路

### 设计原则

- **所有 Prompt 由 AI 辅助生成**：目前处于开发阶段，重点验证架构可行性，Prompt 不做频繁调优。每个 Prompt 保持简洁、职责单一。
- **结构约束优先**：股票代码提取、意图分类等关键决策节点，使用 `function_calling` + Pydantic Schema 约束 LLM 输出格式，避免自由文本解析的不确定性。
- **Few-shot 引导**：意图分类、股票代码提取等 Prompt 包含少量示例，帮助 LLM 理解边界情况

### Prompt 目录结构

```
backend/app/prompts/
├── system/
│   └── system_prompt.txt          # 全局 System Prompt
├── intent/
│   └── intent_classifier.txt      # 意图分类（market/knowledge/hybrid/unsupported）
├── market/
│   ├── ticker_decision.txt        # 股票代码提取 - 阶段1：判断 direct vs search
│   ├── ticker_from_search.txt     # 股票代码提取 - 阶段2：从搜索结果提取
│   └── market_analysis.txt        # 市场数据分析
├── rag/
│   ├── query_rewriter.txt         # 查询改写（知识库检索前）
│   └── rag_generation.txt         # RAG 增强生成
├── rejection/
│   └── unsupported_query.txt      # 不支持的查询回复
└── title/
    └── title_generation.txt       # 会话标题生成（仅用 user_query）
```

## 数据来源

### 市场数据
- **Yahoo Finance** (`yfinance`)：实时股价、历史行情、涨跌幅、成交量等。覆盖全球主要交易所（美股、港股、A 股等）。免费，无需 API Key。

### 新闻与搜索
- **Tavily Search API**：用于两个场景——
  - 股票代码搜索（当 LLM 无法直接确定代码时）
  - 新闻搜索（市场分析时检索相关新闻和事件）

### 本地知识库
- `knowledge_base/` 下的文档，启动时自动导入 ChromaDB
- 文档分块：`RecursiveCharacterTextSplitter`，chunk_size=500，chunk_overlap=50
- 去重依据：source filename，不会重复导入

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 20+
- MiniMax API Key (或许也可以尝试其他兼容 OpenAI 格式的 API Key)
- Tavily API Key

### 安装与启动

**Windows** — 使用项目根目录的 `start_project.bat`，自动完成：
- 检测/复制 `.env` 文件
- 创建 Python venv + 安装依赖
- 安装前端 npm 依赖
- 分别在独立窗口启动后端 (port 8000) 和前端 (port 3000)

停止服务：双击 `stop_project.bat`。

访问 `http://localhost:3000` 即可使用。

### 运行测试

```bash
# 后端测试
cd backend && python -m pytest tests/ -v

# E2E 测试（先确保后端已启动）
cd frontend && npx playwright test --reporter=line

# 清理测试数据库
python -c "import sqlite3; c=sqlite3.connect('backend/data/sqlite.db'); c.execute('DELETE FROM chat_messages'); c.execute('DELETE FROM chat_sessions'); c.commit(); c.close()"
```

## 优化与扩展思考

### 多市场支持

- 目前查询只支持美股市场。针对多地上市公司的市场选择及默认权重问题，属于产品策略定义范畴。为避免过度设计，当前逻辑统一按美股执行。

### LLM 调用成本与速度优化

- **小模型分流**：意图分类、标题生成等轻量任务可切换至更便宜更快的小模型，减少模型开销和延迟。Query Rewriter 可以考虑使用大型的词汇表匹配而非LLM 生成。通过此类优化可以进一步降低响应时长。
- **缓存策略**：相同或相似的 query 可缓存中间结果（market_data、news），避免重复调用外部 API
- **流式优化**：当前 MiniMax M2.7 需完整 `<think>` 标签输出后才开始流式返回正文，后续可评估其他推理速度更快的模型

### 知识库扩展

- 当前仅 3 篇文档 + 1 篇杜撰文档用于测试，后续可批量导入研报、财报、金融教材等
- 引入文档管理、更新机制。
- RAG 检索需要基于真实业务场景做更完善的评估和优化

### 测试与评估体系
- 目前已初步具备 AI 生成的 API 端点与 E2E 测试覆盖。后续可以建立更完善的测试和评估体系，支撑系统的高频迭代与质量稳态。
- **端到端准确性评估**：构建标准测试集（query → expected answer），自动评估回答的事实准确性
- **股票代码提取准确率**：专项评估 LLM 对间接公司引用的代码提取能力
- **RAG 检索质量**：评估检索 recall@k、MRR 等指标
- **延迟监控**：记录各节点耗时，识别瓶颈