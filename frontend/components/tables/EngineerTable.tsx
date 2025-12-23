"use client";

import { useState } from "react";
import Image from "next/image";
import { ChevronUp, ChevronDown, User, Shield, AlertTriangle } from "lucide-react";
import { formatNumber, formatPercent, formatRelativeTime } from "@/lib/utils";
import type { Engineer } from "@/types";

interface EngineerTableProps {
  data: Engineer[];
}

type SortKey = "display_name" | "security_score" | "total_prs" | "clean_prs" | "blocked_prs" | "last_activity_at";

export default function EngineerTable({ data }: EngineerTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("security_score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const sortedData = [...data].sort((a, b) => {
    let aVal = a[sortKey] ?? (sortOrder === "asc" ? Infinity : -Infinity);
    let bVal = b[sortKey] ?? (sortOrder === "asc" ? Infinity : -Infinity);

    if (sortKey === "last_activity_at") {
      aVal = aVal ? new Date(aVal as string).getTime() : 0;
      bVal = bVal ? new Date(bVal as string).getTime() : 0;
    }

    if (aVal < bVal) return sortOrder === "asc" ? -1 : 1;
    if (aVal > bVal) return sortOrder === "asc" ? 1 : -1;
    return 0;
  });

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    else { setSortKey(key); setSortOrder("desc"); }
  };

  const SortHeader = ({ label, keyName }: { label: string, keyName: SortKey }) => (
    <th 
      className="px-6 py-4 text-left text-xs font-mono text-white/40 uppercase tracking-widest cursor-pointer hover:text-accent-crimson transition-colors"
      onClick={() => handleSort(keyName)}
    >
      <div className="flex items-center gap-2">
        {label}
        {sortKey === keyName && (
          sortOrder === "asc" ? <ChevronUp size={12} /> : <ChevronDown size={12} />
        )}
      </div>
    </th>
  );

  if (!data || data.length === 0) {
    return (
      <div className="py-20 text-center text-white/20 font-mono text-sm border border-dashed border-white/10 rounded-lg">
        [NO OPERATIVE DATA]
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-white/5">
      <table className="w-full">
        <thead className="bg-white/5 border-b border-white/10">
          <tr>
            <SortHeader label="Operative" keyName="display_name" />
            <SortHeader label="Rating" keyName="security_score" />
            <SortHeader label="Commits" keyName="total_prs" />
            <SortHeader label="Clean" keyName="clean_prs" />
            <SortHeader label="Violations" keyName="blocked_prs" />
            <SortHeader label="Last Active" keyName="last_activity_at" />
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {sortedData.map((engineer) => (
            <tr key={engineer.id} className="hover:bg-white/5 transition-colors">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center overflow-hidden border border-white/10">
                    {engineer.avatar_url ? (
                      <Image src={engineer.avatar_url} alt={engineer.id} width={32} height={32} />
                    ) : (
                      <User size={16} className="text-white/50" />
                    )}
                  </div>
                  <div>
                    <div className="font-medium text-white">{engineer.display_name || engineer.id}</div>
                    <div className="text-[10px] text-white/30 font-mono">@{engineer.id}</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2 font-mono font-bold">
                  {engineer.security_score >= 80 ? (
                    <span className="text-green-400">{engineer.security_score.toFixed(1)}</span>
                  ) : (
                    <span className="text-accent-crimson">{engineer.security_score.toFixed(1)}</span>
                  )}
                </div>
              </td>
              <td className="px-6 py-4 font-mono text-sm text-white/60">{engineer.total_prs}</td>
              <td className="px-6 py-4 font-mono text-sm text-green-400">
                {formatPercent(engineer.total_prs > 0 ? (engineer.clean_prs / engineer.total_prs) * 100 : 100)}
              </td>
              <td className="px-6 py-4">
                {engineer.blocked_prs > 0 ? (
                  <span className="flex items-center gap-1 text-accent-crimson font-bold text-xs bg-accent-crimson/10 px-2 py-1 rounded border border-accent-crimson/20">
                    <AlertTriangle size={10} /> {engineer.blocked_prs}
                  </span>
                ) : <span className="text-white/20">-</span>}
              </td>
              <td className="px-6 py-4 text-xs font-mono text-white/40">
                {engineer.last_activity_at ? formatRelativeTime(engineer.last_activity_at) : "INACTIVE"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}