"use client";

import { useSessionStore } from "@/stores/sessionStore";
import { NewChatButton } from "./NewChatButton";
import { SessionList } from "./SessionList";

export function Sidebar() {
  const sidebarOpen = useSessionStore((s) => s.sidebarOpen);

  if (!sidebarOpen) {
    return (
      <div className="w-0 overflow-hidden">
        <button
          onClick={() => useSessionStore.getState().setSidebarOpen(true)}
          className="fixed left-2 top-2 z-10 p-2 bg-white dark:bg-gray-800 rounded-lg shadow"
          title="展开侧边栏"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-200">金融问答助手</h2>
        <button
          onClick={() => useSessionStore.getState().setSidebarOpen(false)}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          title="收起侧边栏"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
      </div>
      <div className="p-3">
        <NewChatButton />
      </div>
      <div className="flex-1 overflow-y-auto px-3">
        <SessionList />
      </div>
    </div>
  );
}
