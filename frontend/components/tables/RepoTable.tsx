"use client";

import { useState } from "react";
import { 
  ChevronUp, ChevronDown, 
  GitBranch, ExternalLink, ShieldCheck, AlertOctagon
} from "lucide-react";
import { formatNumber, formatPercent, formatRelativeTime } from "@/lib/utils";
import type { Repository } from "@/types";

interface RepoTableProps {
  data: Repository[];
}

type SortKey = "name" | "total_scans" | "total_issues" | "blocked_prs" | "pass_rate" | "last_scan_at";

export default function RepoTable({ data }: RepoTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("total_scans");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const sortedData = [...data].sort((a, b) => {
    let aVal = a[sortKey] ?? (sortOrder === "asc" ? Infinity : -Infinity);
    let bVal = b[sortKey] ?? (sortOrder === "asc" ? Infinity : -Infinity);

    if (sortKey === "last_scan_at") {
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
      className="px-6 py-4 text-left text-xs font-mono text-white/40 uppercase tracking-widest cursor-pointer hover:text-accent-cyan transition-colors"
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
        [NO REPOSITORY DATA DETECTED]
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-white/5">
      <table className="w-full">
        <thead className="bg-white/5 border-b border-white/10">
          <tr>
            <SortHeader label="Target" keyName="name" />
            <SortHeader label="Scans" keyName="total_scans" />
            <SortHeader label="Health" keyName="pass_rate" />
            <SortHeader label="Threats" keyName="total_issues" />
            <SortHeader label="Blocks" keyName="blocked_prs" />
            <SortHeader label="Last Sync" keyName="last_scan_at" />
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {sortedData.map((repo) => (
            <tr key={repo.id} className="hover:bg-white/5 transition-colors group">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-white/5 text-white/60 group-hover:text-accent-cyan transition-colors">
                    <GitBranch size={16} />
                  </div>
                  <div>
                    <a href={`https://github.com/${repo.id}`} target="_blank" className="font-medium text-white hover:text-accent-cyan flex items-center gap-2">
                      {repo.name} <ExternalLink size={10} className="opacity-50" />
                    </a>
                    <div className="text-[10px] text-white/30 font-mono">{repo.organization}</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 font-mono text-sm text-white/80">{formatNumber(repo.total_scans)}</td>
              <td className="px-6 py-4">
                <div className="flex items-center gap-2">
                  {repo.pass_rate >= 90 ? <ShieldCheck size={14} className="text-green-500" /> : <AlertOctagon size={14} className="text-accent-crimson" />}
                  <span className={`font-mono text-sm ${repo.pass_rate >= 90 ? 'text-green-400' : 'text-accent-crimson'}`}>
                    {formatPercent(repo.pass_rate)}
                  </span>
                </div>
              </td>
              <td className="px-6 py-4 font-mono text-sm text-white/60">{formatNumber(repo.total_issues)}</td>
              <td className="px-6 py-4">
                {repo.blocked_prs > 0 ? (
                  <span className="px-2 py-1 rounded bg-accent-crimson/10 text-accent-crimson text-xs font-bold border border-accent-crimson/20">
                    {repo.blocked_prs}
                  </span>
                ) : <span className="text-white/20">-</span>}
              </td>
              <td className="px-6 py-4 text-xs font-mono text-white/40">
                {repo.last_scan_at ? formatRelativeTime(repo.last_scan_at) : "PENDING"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}