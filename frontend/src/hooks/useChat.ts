import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { streamChat } from "@/services/sse/sseClient";
import { useSessionStore } from "@/stores/sessionStore";
import { useChatStore } from "@/stores/chatStore";
import type { SessionDetail, ChatMessageItem } from "@/types/session";

function makeOptimisticMessage(content: string): ChatMessageItem {
  return {
    id: `optimistic-${Date.now()}`,
    role: "user",
    content,
    created_at: new Date().toISOString(),
  };
}

export function useChat() {
  const queryClient = useQueryClient();
  const activeSessionId = useSessionStore((s) => s.activeSessionId);
  const store = useChatStore();

  const sendMessage = useCallback(
    async (query: string) => {
      if (!activeSessionId || !query.trim()) return;

      const trimmed = query.trim();

      // 乐观写入用户消息，让用户即刻看到自己发送的内容
      const optimisticMsg = makeOptimisticMessage(trimmed);
      queryClient.setQueryData<SessionDetail>(
        ["session", activeSessionId],
        (old) => {
          if (!old) return old;
          return { ...old, messages: [...old.messages, optimisticMsg] };
        }
      );

      store.resetStreamingState();
      store.setIsStreaming(true);

      const abortController = new AbortController();

      try {
        await streamChat(
          { session_id: activeSessionId, query: trimmed, stream: true },
          {
            onStatus: (_node, _status) => {
              const statusMessages: Record<string, string> = {
                market_data: "正在获取市场数据...",
                news: "正在搜索最新新闻...",
                extract: "正在提取文章内容...",
                retrieval: "正在搜索知识库...",
                rerank: "正在筛选相关信息...",
                merge: "正在整合上下文...",
                generation: "正在生成回复...",
              };
              store.setStatusMessage(statusMessages[_node] || _node);
            },
            onToken: (content) => {
              store.setStatusMessage(null);
              store.appendToken(content);
            },
            onStructuredData: (data) => {
              store.setStructuredData(data);
            },
            onCitations: (citations) => {
              store.setCitations(citations);
            },
            onDone: () => {
              store.setIsStreaming(false);
              queryClient.invalidateQueries({
                queryKey: ["session", activeSessionId],
              });
              queryClient.invalidateQueries({ queryKey: ["sessions"] });
            },
            onError: (error) => {
              store.setError(error);
              store.setIsStreaming(false);
              // 移除乐观消息，触发重新拉取
              queryClient.invalidateQueries({
                queryKey: ["session", activeSessionId],
              });
            },
          },
          abortController.signal
        );
      } catch (err: unknown) {
        if (err instanceof Error && err.name !== "AbortError") {
          store.setError({
            type: "NetworkError",
            message: err.message || "请求失败，请重试",
          });
        }
        store.setIsStreaming(false);
        queryClient.invalidateQueries({
          queryKey: ["session", activeSessionId],
        });
      }
    },
    [activeSessionId, store, queryClient]
  );

  return {
    sendMessage,
    abortController: null as AbortController | null,
  };
}
