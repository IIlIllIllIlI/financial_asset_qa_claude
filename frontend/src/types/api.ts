export interface ChatRequest {
  session_id: string;
  query: string;
  stream?: boolean;
}

export interface ChatResponse {
  answer_markdown: string;
  structured_data: { assets: AssetData[] };
  citations: Citation[];
  metadata: { session_id: string; intent: string; processing_time_ms: number };
}

export interface AssetData {
  symbol: string;
  price: number | null;
  change: number | null;
  change_pct: number | null;
  trend: "bullish" | "bearish" | "neutral" | null;
  market_metrics: {
    market_cap?: string;
    pe_ratio?: number | null;
    volume?: string;
  } | null;
  chart_data: {
    "7d": ChartPoint[];
    "30d": ChartPoint[];
  } | null;
}

export interface ChartPoint {
  date: string;
  close: number;
}

export interface Citation {
  title: string;
  url: string;
  source_type: "web" | "rag" | "yahoo_finance";
}

export interface ErrorResponse {
  error: {
    type: string;
    message: string;
  };
}
