"use client";

import { useSessions, useDeleteSession } from "@/hooks/useSessions";
import { useSessionStore } from "@/stores/sessionStore";
import { SessionItem } from "./SessionItem";

export function SessionList() {
  const { data: sessions, isLoading } = useSessions();
  const activeSessionId = useSessionStore((s) => s.activeSessionId);
  const setActiveSession = useSessionStore((s) => s.setActiveSession);
  const deleteSession = useDeleteSession();

  const handleDelete = (id: string) => {
    if (id === activeSessionId) {
      setActiveSession(null);
    }
    deleteSession.mutate(id);
  };

  if (isLoading) {
    return <p className="text-sm text-gray-500 px-3 py-2">加载中...</p>;
  }

  if (!sessions || sessions.length === 0) {
    return (
      <p className="text-sm text-gray-500 px-3 py-4 text-center">
        暂无对话
      </p>
    );
  }

  return (
    <div className="space-y-1">
      {sessions.map((session) => (
        <SessionItem
          key={session.id}
          session={session}
          isActive={session.id === activeSessionId}
          onSelect={setActiveSession}
          onDelete={handleDelete}
        />
      ))}
    </div>
  );
}
