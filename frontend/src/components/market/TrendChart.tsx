"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { ChartPoint } from "@/types/api";

export function TrendChart({
  chartData,
}: {
  chartData: { "7d": ChartPoint[]; "30d": ChartPoint[] } | null;
}) {
  const [period, setPeriod] = useState<"7d" | "30d">("7d");

  if (!chartData) return null;

  const data = chartData[period] || [];
  if (data.length === 0) return null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          价格走势
        </h4>
        <div className="flex gap-1">
          <button
            onClick={() => setPeriod("7d")}
            className={`px-2 py-1 text-xs rounded ${
              period === "7d"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
            }`}
          >
            7天
          </button>
          <button
            onClick={() => setPeriod("30d")}
            className={`px-2 py-1 text-xs rounded ${
              period === "30d"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
            }`}
          >
            30天
          </button>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10 }}
            tickFormatter={(v) => v.slice(5)}
          />
          <YAxis tick={{ fontSize: 10 }} domain={["auto", "auto"]} />
          <Tooltip
            labelFormatter={(v) => `日期: ${v}`}
            formatter={(value) => [`$${Number(value).toFixed(2)}`, "收盘价"]}
          />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
