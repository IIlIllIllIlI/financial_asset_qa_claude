"use client";

import type { AssetData } from "@/types/api";

export function PriceCard({ asset }: { asset: AssetData }) {
  const { symbol, price, change, change_pct, trend } = asset;

  const changeColor =
    trend === "bullish"
      ? "text-green-600 dark:text-green-400"
      : trend === "bearish"
      ? "text-red-600 dark:text-red-400"
      : "text-gray-500";

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white">{symbol}</h3>
      <div className="mt-2">
        <span className="text-3xl font-bold text-gray-900 dark:text-white">
          ${price?.toLocaleString() ?? "--"}
        </span>
      </div>
      <div className={`mt-1 flex items-center gap-2 ${changeColor}`}>
        <span className="text-lg font-medium">
          {change != null ? (change >= 0 ? "+" : "") + change.toFixed(2) : "--"}
        </span>
        <span className="text-sm">
          ({change_pct != null ? (change_pct >= 0 ? "+" : "") + change_pct.toFixed(2) + "%" : "--"})
        </span>
      </div>
    </div>
  );
}
