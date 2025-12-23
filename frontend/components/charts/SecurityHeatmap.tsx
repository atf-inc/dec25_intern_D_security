"use client";

import { useMemo } from "react";
import type { DailyMetric } from "@/types";

interface SecurityHeatmapProps {
  data: DailyMetric[];
}

export default function SecurityHeatmap({ data }: SecurityHeatmapProps) {
  const heatmapData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const weeks: { date: string; value: number; level: number }[][] = [];
    let currentWeek: { date: string; value: number; level: number }[] = [];

    const sortedData = [...data].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    sortedData.forEach((item, index) => {
      const date = new Date(item.date);
      const dayOfWeek = date.getDay();
      
      const totalActivity = item.total_scans;
      let level = 0;
      if (totalActivity > 0) level = 1;
      if (totalActivity > 5) level = 2;
      if (totalActivity > 10) level = 3;
      if (totalActivity > 20) level = 4;

      const cell = { date: item.date, value: totalActivity, level };

      if (dayOfWeek === 0 || index === 0) {
        if (currentWeek.length > 0) weeks.push(currentWeek);
        currentWeek = [];
        for (let i = 0; i < dayOfWeek; i++) currentWeek.push({ date: "", value: 0, level: -1 });
      }
      currentWeek.push(cell);
    });

    if (currentWeek.length > 0) weeks.push(currentWeek);
    return weeks;
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-[150px] flex items-center justify-center text-white/20 font-mono text-xs border border-dashed border-white/10 rounded-lg">
        NO ACTIVITY SIGNALS DETECTED
      </div>
    );
  }

  // Cyber Color Scale
  const levelColors = [
    "bg-white/5", // Level 0
    "bg-accent-cyan/20 shadow-[0_0_5px_rgba(0,240,255,0.1)]", // Level 1
    "bg-accent-cyan/40 shadow-[0_0_8px_rgba(0,240,255,0.2)]", // Level 2
    "bg-accent-cyan/70 shadow-[0_0_12px_rgba(0,240,255,0.4)]", // Level 3
    "bg-accent-cyan shadow-[0_0_15px_rgba(0,240,255,0.6)] animate-pulse", // Level 4
  ];

  return (
    <div className="overflow-x-auto pb-4">
      <div className="flex gap-1">
        <div className="flex gap-1">
          {heatmapData.map((week, weekIndex) => (
            <div key={weekIndex} className="flex flex-col gap-1">
              {week.map((day, dayIndex) => (
                <div
                  key={`${weekIndex}-${dayIndex}`}
                  className={`w-3 h-3 rounded-sm ${day.level === -1 ? "bg-transparent" : levelColors[day.level]} transition-all duration-300 hover:scale-125`}
                  title={day.date ? `${new Date(day.date).toLocaleDateString()}: ${day.value} scans` : ""}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}