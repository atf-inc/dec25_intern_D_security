"use client";

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from "recharts";
import type { DailyMetric } from "@/types";

interface TrendChartProps {
  data: DailyMetric[];
  showLegend?: boolean; // Added this back to fix the build error
}

export default function TrendChart({ data, showLegend = false }: TrendChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-white/20 font-mono text-xs">
        <div className="w-12 h-12 border border-white/10 rounded-full flex items-center justify-center mb-4">
          <div className="w-2 h-2 bg-accent-crimson rounded-full animate-ping" />
        </div>
        AWAITING SIGNAL DATA...
      </div>
    );
  }

  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString("en-US", { day: "numeric", month: "short" }),
    passed: item.passed,
    blocked: item.blocked,
    warned: item.warned,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <defs>
          <linearGradient id="colorPassed" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#00F0FF" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#FF003C" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#FF003C" stopOpacity={0} />
          </linearGradient>
        </defs>
        
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
        
        <XAxis 
          dataKey="date" 
          stroke="#333" 
          tick={{ fill: '#666', fontSize: 10, fontFamily: 'monospace' }} 
          tickLine={false}
          axisLine={false}
        />
        <YAxis 
          stroke="#333" 
          tick={{ fill: '#666', fontSize: 10, fontFamily: 'monospace' }} 
          tickLine={false}
          axisLine={false}
        />
        
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(5,5,5,0.9)",
            borderColor: "rgba(255,255,255,0.1)",
            borderRadius: "8px",
            boxShadow: "0 0 20px rgba(0,0,0,0.5)",
            fontSize: "12px",
            fontFamily: "monospace"
          }}
          itemStyle={{ color: "#fff" }}
        />

        {showLegend && (
          <Legend 
            verticalAlign="top" 
            height={36} 
            iconType="circle"
            formatter={(value) => <span className="text-white/60 text-xs font-mono uppercase ml-2">{value}</span>}
          />
        )}
        
        <Area 
          type="monotone" 
          dataKey="passed" 
          name="Passed"
          stroke="#00F0FF" 
          strokeWidth={2} 
          fill="url(#colorPassed)" 
          activeDot={{ r: 4, strokeWidth: 0, fill: "#fff" }}
        />
        <Area 
          type="monotone" 
          dataKey="blocked" 
          name="Blocked"
          stroke="#FF003C" 
          strokeWidth={2} 
          fill="url(#colorBlocked)" 
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}