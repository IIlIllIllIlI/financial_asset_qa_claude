import { useCallback } from "react";
import { flushSync } from "react-dom";
import { useQueryClient } from "@tanstack/react-query";
import { streamChat } from "@/services/sse/sseClient";
import { postChatNonStreaming } from "@/services/api/chat";
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

  const invalidateSession = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: ["session", activeSessionId],
    });
    queryClient.invalidateQueries({ queryKey: ["sessions"] });
  }, [activeSessionId, queryClient]);

  const sendMessage = useCallback(
    async (query: string) => {
      if (!activeSessionId || !query.trim()) return;

      const trimmed = query.trim();
      const useStreaming = useChatStore.getState().useStreaming;

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

      if (useStreaming) {
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
                flushSync(() => {
                  store.setStatusMessage(null);
                  store.appendToken(content);
                });
              },
              onStructuredData: (data) => {
                store.setStructuredData(data);
              },
              onCitations: (citations) => {
                store.setCitations(citations);
              },
              onDone: () => {
                store.setIsStreaming(false);
                invalidateSession();
                // Title generation is async fire-and-forget on the backend,
                // runs after the SSE stream closes. Schedule delayed refetches
                // to catch the updated title when it lands (typically 3-8s).
                [3000, 6000, 10000].forEach((delay) => {
                  setTimeout(
                    () => queryClient.invalidateQueries({ queryKey: ["sessions"] }),
                    delay
                  );
                });
              },
              onError: (error) => {
                store.setError(error);
                store.setIsStreaming(false);
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
      } else {
        // Non-streaming mode
        try {
          const response = await postChatNonStreaming({
            session_id: activeSessionId,
            query: trimmed,
            stream: false,
          });

          store.setStatusMessage(null);
          store.setStreamingTokens(response.answer_markdown);
          store.setStructuredData(response.structured_data);
          store.setCitations(response.citations);
          store.setIsStreaming(false);
          invalidateSession();
        } catch (err: unknown) {
          store.setError({
            type: "NetworkError",
            message:
              err instanceof Error ? err.message : "请求失败，请重试",
          });
          store.setIsStreaming(false);
          queryClient.invalidateQueries({
            queryKey: ["session", activeSessionId],
          });
        }
      }
    },
    [activeSessionId, store, queryClient, invalidateSession]
  );

  return {
    sendMessage,
    abortController: null as AbortController | null,
  };
}
