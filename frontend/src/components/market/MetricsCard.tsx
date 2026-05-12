"use client";

import type { AssetData } from "@/types/api";

export function MetricsCard({ asset }: { asset: AssetData }) {
  const metrics = asset.market_metrics;
  if (!metrics) return null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        关键指标
      </h4>
      <div className="space-y-2">
        <MetricRow label="市值" value={metrics.market_cap || "--"} />
        <MetricRow
          label="市盈率"
          value={metrics.pe_ratio != null ? String(metrics.pe_ratio) : "--"}
        />
        <MetricRow label="成交量" value={metrics.volume || "--"} />
      </div>
    </div>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500 dark:text-gray-400">{label}</span>
      <span className="font-medium text-gray-900 dark:text-gray-100">{value}</span>
    </div>
  );
}
