"use client";

import { useEffect, useState } from "react";
import { Scan, ShieldCheck, WarningOctagon, GitPullRequest, Pulse, Broadcast } from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import TrendChart from "@/components/charts/TrendChart";
import IssueDistribution from "@/components/charts/IssueDistribution";
import { fetchAPI, formatNumber, formatPercent, cn } from "@/lib/utils";
import type { DashboardStats, MetricsResponse, IssuePatternsResponse } from "@/types";

export default function DashboardPage() {
  const [data, setData] = useState<{
    stats: DashboardStats | null, 
    metrics: MetricsResponse | null, 
    patterns: IssuePatternsResponse | null
  }>({ stats: null, metrics: null, patterns: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, m, p] = await Promise.all([
          fetchAPI<DashboardStats>("/api/analytics/dashboard"),
          fetchAPI<MetricsResponse>("/api/metrics?days=30"),
          fetchAPI<IssuePatternsResponse>("/api/issues/patterns?days=30")
        ]);
        setData({ stats: s, metrics: m, patterns: p });
      } catch (err) {
        console.error("Dashboard Load Error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="font-mono text-accent-cyan animate-pulse tracking-[0.5em] text-center uppercase">
        Initializing_Command_Center...
      </div>
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-1000">
      <header className="flex justify-between items-end border-b border-white/5 pb-6">
        <div>
          <h1 className="text-4xl font-light tracking-tighter text-white uppercase">Command Center</h1>
          <p className="text-white/30 font-mono text-[10px] uppercase tracking-[0.4em] mt-2">
            Perimeter Status: <span className="text-accent-emerald">Active_Surveillance</span>
          </p>
        </div>
        <div className="font-mono text-[10px] text-white/20 text-right hidden md:block">
          SECURE_LINK_ESTABLISHED // NODE_01
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Total Scans" value={formatNumber(data.stats?.summary.total_scans || 0)} icon={<Scan size={32} />} color="cyan" />
        <StatCard title="Compliance" value={formatPercent(data.stats?.summary.pass_rate || 0)} icon={<ShieldCheck size={32} />} color="emerald" />
        <StatCard title="Threats Blocked" value={formatNumber(data.stats?.summary.total_blocked || 0)} icon={<WarningOctagon size={32} />} color="crimson" />
        <StatCard title="Active Nodes" value={formatNumber(data.stats?.summary.active_repos || 0)} icon={<GitPullRequest size={32} />} color="cyan" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 bg-black/40 border-white/5 h-[450px]">
          <CardHeader>
            <CardTitle className="text-[10px] font-mono text-white/30 uppercase tracking-[0.2em] flex items-center gap-2">
              <Pulse className="text-accent-cyan" size={16} /> Neural Signal Frequency
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <TrendChart data={data.metrics?.data || []} showLegend />
          </CardContent>
        </Card>
        <Card className="bg-black/40 border-white/5 h-[450px]">
          <CardHeader>
            <CardTitle className="text-[10px] font-mono text-white/30 uppercase tracking-[0.2em] flex items-center gap-2">
              <Broadcast className="text-accent-crimson" size={16} /> Threat Signatures
            </CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <IssueDistribution data={data.patterns?.patterns || []} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string, value: string, icon: any, color: string }) {
  const colors: any = { 
    cyan: "text-accent-cyan border-accent-cyan/20 shadow-[0_0_15px_rgba(0,240,255,0.05)]", 
    crimson: "text-accent-crimson border-accent-crimson/20 shadow-[0_0_15px_rgba(255,0,60,0.05)]", 
    emerald: "text-accent-emerald border-accent-emerald/20 shadow-[0_0_15px_rgba(0,255,148,0.05)]" 
  };
  return (
    <div className={cn("p-6 rounded-2xl bg-white/5 border backdrop-blur-xl relative overflow-hidden transition-all hover:bg-white/10", colors[color])}>
      <div className="absolute -right-4 -top-4 opacity-5 scale-[3]">{icon}</div>
      <div className="text-[10px] font-mono uppercase tracking-widest opacity-40 mb-2">{title}</div>
      <div className="text-3xl font-light text-white">{value}</div>
    </div>
  );
}