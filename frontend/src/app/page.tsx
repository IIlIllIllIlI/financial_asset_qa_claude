"use client";

import { Sidebar } from "@/components/sidebar/Sidebar";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { MarketPanel } from "@/components/market/MarketPanel";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { ErrorToast } from "@/components/common/ErrorToast";

export default function Home() {
  return (
    <div className="flex h-full bg-gray-50 dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-end px-4 py-2 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <ThemeToggle />
        </header>
        <ChatContainer />
      </div>
      <div className="w-80 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 hidden lg:block">
        <MarketPanel />
      </div>
      <ErrorToast />
    </div>
  );
}
