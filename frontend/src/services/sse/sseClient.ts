import type { SSEEvent } from "@/types/chat";
import type { AssetData, Citation, ChatRequest } from "@/types/api";

let tokenBuffer = "";
function resetThinkingBuffer() { tokenBuffer = ""; }
function stripThinking(content: string): string {
  tokenBuffer += content;
  // Remove complete <think>...</think> blocks
  const cleaned = tokenBuffer.replace(/<think>[\s\S]*?<\/think>/g, "");
  // If there's an unclosed <think>, only take content before it
  const openIdx = cleaned.indexOf("<think>");
  if (openIdx !== -1) {
    return ""; // wait for closing tag
  }
  const emitted = cleaned;
  tokenBuffer = "";
  return emitted;
}

type SSECallback = {
  onStatus?: (node: string, status: string) => void;
  onToken?: (content: string) => void;
  onStructuredData?: (data: { assets: AssetData[] }) => void;
  onCitations?: (citations: Citation[]) => void;
  onDone?: (sessionId: string) => void;
  onError?: (error: { type: string; message: string }) => void;
};

function parseSSEEvents(buffer: string): SSEEvent[] {
  const events: SSEEvent[] = [];
  const parts = buffer.split("\n\n");

  for (const part of parts) {
    if (!part.trim()) continue;
    const lines = part.split("\n");
    let eventType = "";
    let dataStr = "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        eventType = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        dataStr = line.slice(6);
      }
    }

    if (eventType && dataStr) {
      try {
        const data = JSON.parse(dataStr);
        const event: SSEEvent = { type: eventType as SSEEvent["type"], ...data };
        events.push(event);
      } catch {
        // skip unparseable
      }
    }
  }

  return events;
}

export async function streamChat(
  body: ChatRequest,
  callbacks: SSECallback,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({ ...body, stream: true }),
    signal,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat request failed");
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  resetThinkingBuffer();

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = parseSSEEvents(buffer);
      buffer = ""; // reset buffer after parsing

      for (const event of events) {
        switch (event.type) {
          case "status":
            callbacks.onStatus?.(event.node || "", event.status || "");
            break;
          case "token":
            callbacks.onToken?.(event.content || "");
            break;
          case "structured_data":
            callbacks.onStructuredData?.({ assets: (event as Record<string, unknown>).assets as AssetData[] || [] });
            break;
          case "citations":
            callbacks.onCitations?.((event as unknown as { citations: Citation[] }).citations || []);
            break;
          case "done":
            callbacks.onDone?.(event.session_id || "");
            break;
          case "error":
            callbacks.onError?.(event.error || { type: "Unknown", message: "Stream error" });
            break;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
