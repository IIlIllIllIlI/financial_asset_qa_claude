"use client";

import { useMarketPanel } from "@/hooks/useMarketPanel";
import { AssetTabs } from "./AssetTabs";
import { PriceCard } from "./PriceCard";
import { TrendChart } from "./TrendChart";
import { MetricsCard } from "./MetricsCard";

export function MarketPanel() {
  const { assets, activeAsset, activeIndex, setActiveIndex } = useMarketPanel();

  return (
    <div className="h-full overflow-y-auto p-4">
      <h2 className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-4">
        市场数据
      </h2>

      {!activeAsset ? (
        <div className="flex flex-col items-center justify-center h-64 text-gray-400">
          <svg className="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          <p className="text-sm">暂无活跃资产</p>
          <p className="text-xs mt-1">提出市场相关问题以查看数据</p>
        </div>
      ) : (
        <div className="space-y-4">
          <AssetTabs
            assets={assets}
            activeIndex={activeIndex}
            onSelect={setActiveIndex}
          />
          <PriceCard asset={activeAsset} />
          {activeAsset.chart_data && (
            <TrendChart chartData={activeAsset.chart_data} />
          )}
          {activeAsset.market_metrics && (
            <MetricsCard asset={activeAsset} />
          )}
        </div>
      )}
    </div>
  );
}
