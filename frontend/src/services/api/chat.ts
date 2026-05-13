import type { ChatRequest, ChatResponse } from "@/types/api";

export async function postChatNonStreaming(
  body: ChatRequest
): Promise<ChatResponse> {
  const res = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, stream: false }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat request failed");
  }
  return res.json();
}
