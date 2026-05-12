"use client";

import { useEffect, useRef } from "react";
import { useSessionStore } from "@/stores/sessionStore";
import { useChatStore } from "@/stores/chatStore";
import { useSessionDetail } from "@/hooks/useSessions";
import { useChat } from "@/hooks/useChat";
import { ChatMessage } from "./ChatMessage";
import { StreamingMessage } from "./StreamingMessage";
import { CitationList } from "./CitationList";
import { ChatInput } from "./ChatInput";

export function ChatContainer() {
  const activeSessionId = useSessionStore((s) => s.activeSessionId);
  const { isStreaming, streamingTokens, statusMessage, citations, error } =
    useChatStore();
  const { sendMessage } = useChat();

  const { data: sessionDetail, isLoading } = useSessionDetail(activeSessionId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [sessionDetail?.messages, streamingTokens]);

  const messages = sessionDetail?.messages || [];
  const hasSession = !!activeSessionId;

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {!hasSession ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <p className="text-lg mb-2">选择一个对话或创建新对话开始</p>
              <p className="text-sm">点击左侧边栏的"新对话"按钮开始提问</p>
            </div>
          </div>
        ) : isLoading ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500">加载中...</p>
          </div>
        ) : messages.length === 0 && !isStreaming ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <p>输入问题开始对话</p>
          </div>
        ) : (
          <div>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isStreaming && (
              <>
                <StreamingMessage
                  content={streamingTokens}
                  status={statusMessage}
                />
                {citations && <CitationList citations={citations} />}
              </>
            )}
            {error && (
              <div className="flex justify-center my-4">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3 max-w-md">
                  <p className="text-red-700 dark:text-red-400 text-sm font-medium">错误：{error.message}</p>
                  <button
                    onClick={() => {
                      const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
                      if (lastUserMsg) sendMessage(lastUserMsg.content);
                    }}
                    className="mt-2 text-sm text-red-600 dark:text-red-400 underline"
                  >
                    重试
                  </button>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      {hasSession && (
        <ChatInput onSend={sendMessage} disabled={isStreaming} />
      )}
    </div>
  );
}
