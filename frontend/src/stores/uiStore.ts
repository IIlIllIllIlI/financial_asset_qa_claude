import { create } from "zustand";

type Theme = "light" | "dark" | "system";

interface UIStore {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  theme: "system",
  setTheme: (theme) => {
    set({ theme });
    if (typeof window !== "undefined") {
      localStorage.setItem("theme-preference", theme);
    }
  },
}));
