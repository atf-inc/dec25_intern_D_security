"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import type { IssuePattern } from "@/types";

interface IssueDistributionProps {
  data: IssuePattern[];
}

const COLORS = ["#FF003C", "#00F0FF", "#F0F0F0", "#333333"];

export default function IssueDistribution({ data }: IssueDistributionProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-white/20 text-xs font-mono">
        NO THREATS DETECTED
      </div>
    );
  }

  // Format data
  const chartData = data.slice(0, 4).map((item) => ({
    name: item.pattern.replace(/_/g, " "),
    value: item.count,
  }));

  return (
    <div className="w-full h-full relative">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#000",
              border: "1px solid #333",
              borderRadius: "4px",
              color: "#fff",
              fontSize: "12px"
            }}
            formatter={(value: number) => [value, "Detected"]}
          />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Center Label */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
        <div className="text-2xl font-bold text-white">{data.reduce((a, b) => a + b.count, 0)}</div>
        <div className="text-[10px] text-white/40 uppercase tracking-wider">Issues</div>
      </div>
    </div>
  );
}