"use client";

import { MarkdownRenderer } from "@/components/markdown/MarkdownRenderer";

export function StreamingMessage({ content, status }: { content: string; status: string | null }) {
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%] rounded-lg px-4 py-3 bg-gray-100 dark:bg-gray-800">
        {status && (
          <p className="text-sm text-gray-500 dark:text-gray-400 italic mb-2">
            {status}
          </p>
        )}
        {content ? (
          <MarkdownRenderer content={content} />
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]" />
          </div>
        )}
      </div>
    </div>
  );
}
