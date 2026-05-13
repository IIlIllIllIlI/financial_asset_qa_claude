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

function parseSSEEvents(buffer: string): { events: SSEEvent[]; remainder: string } {
  const events: SSEEvent[] = [];
  const parts = buffer.split("\n\n");

  // Last part may be incomplete — keep it for the next read
  const complete = parts.slice(0, -1);
  const remainder = parts[parts.length - 1];

  for (const part of complete) {
    if (!part.trim()) continue;
    const event = _parseSSEPart(part);
    if (event) events.push(event);
  }

  return { events, remainder };
}

function _parseSSEPart(part: string): SSEEvent | null {
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

  if (!eventType || !dataStr) return null;

  try {
    const data = JSON.parse(dataStr);
    return { type: eventType as SSEEvent["type"], ...data };
  } catch {
    return null;
  }
}

export async function streamChat(
  body: ChatRequest,
  callbacks: SSECallback,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch("http://localhost:8000/api/chat", {
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
      const { events, remainder } = parseSSEEvents(buffer);
      buffer = remainder; // preserve incomplete events for next read

      for (const event of events) {
        switch (event.type) {
          case "status":
            callbacks.onStatus?.(event.node || "", event.status || "");
            break;
          case "token":
            callbacks.onToken?.(event.content || "");
            // Yield to event loop so browser paints between tokens
            await new Promise((resolve) => setTimeout(resolve, 0));
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
