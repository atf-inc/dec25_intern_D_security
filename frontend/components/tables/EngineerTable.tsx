"use client";

import { useState } from "react";
import Image from "next/image";
import { 
  ChevronUp, 
  ChevronDown,
  TrendingUp,
  AlertTriangle,
  CheckCircle
} from "lucide-react";
import { formatNumber, formatPercent, formatRelativeTime, getBadgeColor } from "@/lib/utils";
import type { Engineer } from "@/types";

interface EngineerTableProps {
  data: Engineer[];
}

type SortKey = "display_name" | "security_score" | "total_prs" | "clean_prs" | "blocked_prs" | "last_activity_at";
type SortOrder = "asc" | "desc";

export default function EngineerTable({ data }: EngineerTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("security_score");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  const sortedData = [...data].sort((a, b) => {
    let aVal: string | number | null = sortKey === "display_name" 
      ? (a.display_name || a.id) 
      : a[sortKey];
    let bVal: string | number | null = sortKey === "display_name" 
      ? (b.display_name || b.id) 
      : b[sortKey];

    if (aVal === null) aVal = sortOrder === "asc" ? Infinity : -Infinity;
    if (bVal === null) bVal = sortOrder === "asc" ? Infinity : -Infinity;

    if (sortKey === "last_activity_at") {
      aVal = aVal ? new Date(aVal as string).getTime() : 0;
      bVal = bVal ? new Date(bVal as string).getTime() : 0;
    }

    if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
    if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortOrder("desc");
    }
  };

  const SortIcon = ({ columnKey }: { columnKey: SortKey }) => {
    if (sortKey !== columnKey) {
      return <ChevronUp className="w-4 h-4 opacity-0 group-hover:opacity-30" />;
    }
    return sortOrder === "asc" ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    );
  };

  const getBadge = (score: number): string => {
    if (score >= 95) return "platinum";
    if (score >= 85) return "gold";
    if (score >= 75) return "silver";
    if (score >= 60) return "bronze";
    return "none";
  };

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 text-slate-500">
        No engineers found
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            <th
              className="cursor-pointer group"
              onClick={() => handleSort("display_name")}
            >
              <div className="flex items-center gap-1">
                Engineer
                <SortIcon columnKey="display_name" />
              </div>
            </th>
            <th
              className="cursor-pointer group"
              onClick={() => handleSort("security_score")}
            >
              <div className="flex items-center gap-1">
                Score
                <SortIcon columnKey="security_score" />
              </div>
            </th>
            <th
              className="cursor-pointer group"
              onClick={() => handleSort("total_prs")}
            >
              <div className="flex items-center gap-1">
                Total PRs
                <SortIcon columnKey="total_prs" />
              </div>
            </th>
            <th
              className="cursor-pointer group"
              onClick={() => handleSort("clean_prs")}
            >
              <div className="flex items-center gap-1">
                Clean PRs
                <SortIcon columnKey="clean_prs" />
              </div>
            </th>
            <th
              className="cursor-pointer group"
              onClick={() => handleSort("blocked_prs")}
            >
              <div className="flex items-center gap-1">
                Blocked
                <SortIcon columnKey="blocked_prs" />
              </div>
            </th>
            <th>Issues</th>
            <th
              className="cursor-pointer group"
              onClick={() => handleSort("last_activity_at")}
            >
              <div className="flex items-center gap-1">
                Last Active
                <SortIcon columnKey="last_activity_at" />
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedData.map((engineer) => {
            const badge = getBadge(engineer.security_score);
            const cleanRate = engineer.total_prs > 0 
              ? (engineer.clean_prs / engineer.total_prs) * 100 
              : 100;

            return (
              <tr key={engineer.id}>
                <td>
                  <div className="flex items-center gap-3">
                    {engineer.avatar_url ? (
                      <Image
                        src={engineer.avatar_url}
                        alt={engineer.display_name || engineer.id}
                        width={32}
                        height={32}
                        className="rounded-full"
                      />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                        <span className="text-sm font-bold text-slate-500">
                          {(engineer.display_name || engineer.id).charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                    <div>
                      <p className="font-medium">{engineer.display_name || engineer.id}</p>
                      <p className="text-xs text-slate-500">@{engineer.id}</p>
                    </div>
                    {badge !== "none" && (
                      <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r ${getBadgeColor(badge)}`}>
                        {badge}
                      </span>
                    )}
                  </div>
                </td>
                <td>
                  <div className="flex items-center gap-2">
                    <TrendingUp className={`w-4 h-4 ${
                      engineer.security_score >= 80 ? "text-green-500" :
                      engineer.security_score >= 60 ? "text-yellow-500" :
                      "text-red-500"
                    }`} />
                    <span className="font-bold">{engineer.security_score.toFixed(1)}</span>
                  </div>
                </td>
                <td className="font-medium">{formatNumber(engineer.total_prs)}</td>
                <td>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span>{formatNumber(engineer.clean_prs)}</span>
                    <span className="text-xs text-slate-400">
                      ({formatPercent(cleanRate)})
                    </span>
                  </div>
                </td>
                <td>
                  {engineer.blocked_prs > 0 ? (
                    <span className="badge-danger">{engineer.blocked_prs}</span>
                  ) : (
                    <span className="text-slate-400">0</span>
                  )}
                </td>
                <td>
                  <div className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    <span>{formatNumber(engineer.total_issues_introduced)}</span>
                    {engineer.issues_fixed > 0 && (
                      <span className="text-green-600 text-xs">
                        ({engineer.issues_fixed} fixed)
                      </span>
                    )}
                  </div>
                </td>
                <td className="text-slate-500 text-sm">
                  {engineer.last_activity_at
                    ? formatRelativeTime(engineer.last_activity_at)
                    : "Never"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

