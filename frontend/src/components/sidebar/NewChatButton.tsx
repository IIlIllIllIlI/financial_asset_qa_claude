"use client";

import { useCreateSession } from "@/hooks/useSessions";
import { useSessionStore } from "@/stores/sessionStore";

export function NewChatButton() {
  const createSession = useCreateSession();
  const setActiveSession = useSessionStore((s) => s.setActiveSession);

  const handleCreate = async () => {
    const session = await createSession.mutateAsync();
    setActiveSession(session.id);
  };

  return (
    <button
      onClick={handleCreate}
      disabled={createSession.isPending}
      className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
    >
      + 新对话
    </button>
  );
}
