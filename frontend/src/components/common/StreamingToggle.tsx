"use client";

import { useChatStore } from "@/stores/chatStore";

export function StreamingToggle() {
  const useStreaming = useChatStore((s) => s.useStreaming);
  const setUseStreaming = useChatStore((s) => s.setUseStreaming);

  return (
    <button
      onClick={() => setUseStreaming(!useStreaming)}
      className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      title={useStreaming ? "切换到非流式输出" : "切换到流式输出"}
    >
      {useStreaming ? (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
        </svg>
      ) : (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM16 16H8M16 12H8M10 8H8" />
        </svg>
      )}
    </button>
  );
}
