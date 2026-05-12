"use client";

import type { Session } from "@/types/session";

interface SessionItemProps {
  session: Session;
  isActive: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

export function SessionItem({ session, isActive, onSelect, onDelete }: SessionItemProps) {
  const date = new Date(session.updated_at);
  const dateStr = date.toLocaleDateString("zh-CN", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      onClick={() => onSelect(session.id)}
      className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors ${
        isActive
          ? "bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
          : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
      }`}
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{session.title}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400">{dateStr}</p>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(session.id);
        }}
        className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all text-lg leading-none px-1"
        title="删除会话"
      >
        ×
      </button>
    </div>
  );
}
