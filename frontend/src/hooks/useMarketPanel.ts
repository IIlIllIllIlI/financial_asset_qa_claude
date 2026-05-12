import { useChatStore } from "@/stores/chatStore";
import { useState, useMemo } from "react";
import type { AssetData } from "@/types/api";

export function useMarketPanel() {
  const structuredData = useChatStore((s) => s.structuredData);
  const [activeIndex, setActiveIndex] = useState(0);

  const assets = useMemo(() => {
    if (!structuredData?.assets) return [];
    return structuredData.assets.filter((a) => a.symbol);
  }, [structuredData]);

  const activeAsset = assets.length > 0 ? assets[activeIndex] : null;

  return {
    assets,
    activeAsset,
    activeIndex,
    setActiveIndex,
  };
}
