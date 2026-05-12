import { create } from "zustand";

interface SessionStore {
  activeSessionId: string | null;
  sidebarOpen: boolean;
  setActiveSession: (id: string | null) => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  activeSessionId: null,
  sidebarOpen: true,
  setActiveSession: (id) => set({ activeSessionId: id }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
