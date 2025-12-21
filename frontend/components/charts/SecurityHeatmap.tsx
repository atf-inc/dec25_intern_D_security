"use client";

import { useMemo } from "react";
import type { DailyMetric } from "@/types";

interface SecurityHeatmapProps {
  data: DailyMetric[];
}

export default function SecurityHeatmap({ data }: SecurityHeatmapProps) {
  const heatmapData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // Group by week and day
    const weeks: { date: string; value: number; level: number }[][] = [];
    let currentWeek: { date: string; value: number; level: number }[] = [];

    // Sort data by date
    const sortedData = [...data].sort(
      (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    sortedData.forEach((item, index) => {
      const date = new Date(item.date);
      const dayOfWeek = date.getDay();
      
      // Calculate activity level (0-4)
      const totalActivity = item.total_scans;
      let level = 0;
      if (totalActivity > 0) level = 1;
      if (totalActivity > 5) level = 2;
      if (totalActivity > 10) level = 3;
      if (totalActivity > 20) level = 4;

      const cell = {
        date: item.date,
        value: totalActivity,
        level,
      };

      // Start new week on Sunday or if it's the first item
      if (dayOfWeek === 0 || index === 0) {
        if (currentWeek.length > 0) {
          weeks.push(currentWeek);
        }
        currentWeek = [];
        // Pad beginning of week if needed
        for (let i = 0; i < dayOfWeek; i++) {
          currentWeek.push({ date: "", value: 0, level: -1 });
        }
      }

      currentWeek.push(cell);
    });

    // Push the last week
    if (currentWeek.length > 0) {
      weeks.push(currentWeek);
    }

    return weeks;
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="h-[150px] flex items-center justify-center text-slate-400">
        No activity data available
      </div>
    );
  }

  const levelColors = [
    "bg-slate-100 dark:bg-slate-800", // level 0 - no activity
    "bg-green-200 dark:bg-green-900", // level 1
    "bg-green-400 dark:bg-green-700", // level 2
    "bg-green-500 dark:bg-green-600", // level 3
    "bg-green-600 dark:bg-green-500", // level 4
  ];

  const dayLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-1">
        {/* Day labels */}
        <div className="flex flex-col gap-1 mr-2 text-xs text-slate-500">
          {dayLabels.map((day, i) => (
            <div
              key={day}
              className="h-4 flex items-center"
              style={{ visibility: i % 2 === 1 ? "visible" : "hidden" }}
            >
              {day}
            </div>
          ))}
        </div>

        {/* Heatmap grid */}
        <div className="flex gap-1">
          {heatmapData.map((week, weekIndex) => (
            <div key={weekIndex} className="flex flex-col gap-1">
              {week.map((day, dayIndex) => (
                <div
                  key={`${weekIndex}-${dayIndex}`}
                  className={`w-4 h-4 rounded-sm ${
                    day.level === -1
                      ? "bg-transparent"
                      : levelColors[day.level]
                  } transition-colors cursor-pointer hover:ring-2 hover:ring-slate-400`}
                  title={
                    day.date
                      ? `${formatDate(day.date)}: ${day.value} scans`
                      : ""
                  }
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-2 mt-4 text-xs text-slate-500">
        <span>Less</span>
        {levelColors.map((color, i) => (
          <div key={i} className={`w-4 h-4 rounded-sm ${color}`} />
        ))}
        <span>More</span>
      </div>
    </div>
  );
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

