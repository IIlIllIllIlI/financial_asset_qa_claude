import { create } from "zustand";
import type { Citation, AssetData } from "@/types/api";

interface ChatStore {
  streamingTokens: string;
  isStreaming: boolean;
  useStreaming: boolean;
  statusMessage: string | null;
  structuredData: { assets: AssetData[] } | null;
  citations: Citation[] | null;
  error: { type: string; message: string } | null;

  setStreamingTokens: (tokens: string) => void;
  appendToken: (token: string) => void;
  setIsStreaming: (v: boolean) => void;
  setUseStreaming: (v: boolean) => void;
  setStatusMessage: (msg: string | null) => void;
  setStructuredData: (data: { assets: AssetData[] } | null) => void;
  setCitations: (citations: Citation[] | null) => void;
  setError: (error: { type: string; message: string } | null) => void;
  resetStreamingState: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  streamingTokens: "",
  isStreaming: false,
  useStreaming: true,
  statusMessage: null,
  structuredData: null,
  citations: null,
  error: null,

  setStreamingTokens: (tokens) => set({ streamingTokens: tokens }),
  appendToken: (token) =>
    set((s) => ({ streamingTokens: s.streamingTokens + token })),
  setIsStreaming: (v) => set({ isStreaming: v }),
  setUseStreaming: (v) => set({ useStreaming: v }),
  setStatusMessage: (msg) => set({ statusMessage: msg }),
  setStructuredData: (data) => set({ structuredData: data }),
  setCitations: (citations) => set({ citations }),
  setError: (error) => set({ error }),
  resetStreamingState: () =>
    set({
      streamingTokens: "",
      isStreaming: false,
      statusMessage: null,
      structuredData: null,
      citations: null,
      error: null,
    }),
}));
