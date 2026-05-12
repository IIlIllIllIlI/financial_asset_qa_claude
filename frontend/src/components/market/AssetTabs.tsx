"use client";

import type { AssetData } from "@/types/api";

interface AssetTabsProps {
  assets: AssetData[];
  activeIndex: number;
  onSelect: (index: number) => void;
}

export function AssetTabs({ assets, activeIndex, onSelect }: AssetTabsProps) {
  if (assets.length <= 1) return null;

  return (
    <div className="flex gap-1 border-b border-gray-200 dark:border-gray-700 mb-3">
      {assets.map((asset, i) => (
        <button
          key={asset.symbol}
          onClick={() => onSelect(i)}
          className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
            i === activeIndex
              ? "border-blue-600 text-blue-600 dark:text-blue-400"
              : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          {asset.symbol}
        </button>
      ))}
    </div>
  );
}
