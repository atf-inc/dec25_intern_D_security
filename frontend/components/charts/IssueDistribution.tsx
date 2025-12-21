"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import type { IssuePattern } from "@/types";

interface IssueDistributionProps {
  data: IssuePattern[];
}

const COLORS = [
  "#ef4444", // red
  "#f97316", // orange
  "#f59e0b", // amber
  "#eab308", // yellow
  "#84cc16", // lime
  "#22c55e", // green
  "#14b8a6", // teal
  "#06b6d4", // cyan
  "#3b82f6", // blue
  "#8b5cf6", // violet
];

export default function IssueDistribution({ data }: IssueDistributionProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400">
        No issues detected
      </div>
    );
  }

  // Transform data for the pie chart
  const chartData = data.map((item) => ({
    name: formatPatternName(item.pattern),
    value: item.count,
    fullName: item.pattern,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
          dataKey="value"
          label={({ name, percent }) =>
            percent > 0.05 ? `${name} (${(percent * 100).toFixed(0)}%)` : ""
          }
          labelLine={false}
        >
          {chartData.map((_, index) => (
            <Cell
              key={`cell-${index}`}
              fill={COLORS[index % COLORS.length]}
              stroke="none"
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#1e293b",
            border: "none",
            borderRadius: "8px",
            color: "#f8fafc",
          }}
          formatter={(value: number, name: string) => [
            value,
            formatPatternName(name),
          ]}
        />
        <Legend
          layout="vertical"
          verticalAlign="middle"
          align="right"
          iconType="circle"
          iconSize={8}
          formatter={(value) => (
            <span className="text-xs text-slate-600 dark:text-slate-400">
              {value}
            </span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

function formatPatternName(pattern: string): string {
  // Convert pattern names like "AWS_KEY" to "AWS Key"
  return pattern
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

