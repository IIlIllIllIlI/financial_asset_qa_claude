export interface SSEEvent {
  type: "token" | "status" | "structured_data" | "citations" | "done" | "error";
  content?: string;
  node?: string;
  status?: string;
  structured_data?: { assets: import("./api").AssetData[] };
  citations?: import("./api").Citation[];
  session_id?: string;
  error?: { type: string; message: string };
}
