"""Non-configurable application constants."""

# Chroma collection name
CHROMA_COLLECTION_NAME = "financial_knowledge"

# RAG chunking parameters
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retrieval top-k
RETRIEVAL_K = 8
RERANK_N = 4

# Market data cache
MARKET_CACHE_MAXSIZE = 128
MARKET_CACHE_TTL = 60

# Tavily search max results
TAVILY_MAX_RESULTS = 5

# SSE event types
SSE_TOKEN_EVENT = "token"
SSE_STATUS_EVENT = "status"
SSE_STRUCTURED_DATA_EVENT = "structured_data"
SSE_CITATIONS_EVENT = "citations"
SSE_DONE_EVENT = "done"
SSE_ERROR_EVENT = "error"

# Default session title
DEFAULT_SESSION_TITLE = "新对话"

# Title max length in Chinese characters
TITLE_MAX_CHARS = 15

# Response summary length for title generation
TITLE_SUMMARY_LENGTH = 200

# Query instruction for BGE embedding model
BGE_QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："
