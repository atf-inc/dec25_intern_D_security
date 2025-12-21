"use client";

import { useEffect, useState } from "react";
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  TrendingUp,
  Activity,
  GitPullRequest,
  Users
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import TrendChart from "@/components/charts/TrendChart";
import IssueDistribution from "@/components/charts/IssueDistribution";
import { fetchAPI, formatNumber, formatPercent } from "@/lib/utils";
import type { DashboardStats, MetricsResponse, IssuePatternsResponse } from "@/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [patterns, setPatterns] = useState<IssuePatternsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        const [dashboardStats, metricsData, patternsData] = await Promise.all([
          fetchAPI<DashboardStats>("/api/analytics/dashboard"),
          fetchAPI<MetricsResponse>("/api/metrics?days=30"),
          fetchAPI<IssuePatternsResponse>("/api/issues/patterns?days=30"),
        ]);
        
        setStats(dashboardStats);
        setMetrics(metricsData);
        setPatterns(patternsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }
    
    fetchDashboardData();
  }, []);

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 mx-auto text-yellow-500 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Unable to load dashboard</h2>
          <p className="text-slate-500">{error}</p>
        </div>
      </div>
    );
  }

  const summary = stats?.summary;

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Security Dashboard
          </h1>
          <p className="text-slate-500 mt-1">
            Real-time overview of your security scanning metrics
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Activity className="w-4 h-4 text-green-500 animate-pulse" />
          Live
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Scans"
          value={formatNumber(summary?.total_scans || 0)}
          subtitle={`${stats?.recent.scans_last_7_days || 0} this week`}
          icon={<GitPullRequest className="w-5 h-5" />}
          color="blue"
        />
        <StatCard
          title="Pass Rate"
          value={formatPercent(summary?.pass_rate || 100)}
          subtitle={`${formatNumber(summary?.total_passed || 0)} passed`}
          icon={<CheckCircle className="w-5 h-5" />}
          color="green"
        />
        <StatCard
          title="Issues Blocked"
          value={formatNumber(summary?.total_blocked || 0)}
          subtitle={`${formatNumber(summary?.critical_issues || 0)} critical`}
          icon={<XCircle className="w-5 h-5" />}
          color="red"
        />
        <StatCard
          title="Active Repos"
          value={formatNumber(summary?.active_repos || 0)}
          subtitle="Monitored repositories"
          icon={<Shield className="w-5 h-5" />}
          color="purple"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart - Takes 2 columns */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              Scan Trends (30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <TrendChart data={metrics?.data || []} />
            </div>
          </CardContent>
        </Card>

        {/* Issue Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              Top Issue Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <IssueDistribution data={patterns?.patterns || []} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Champions */}
      {stats?.top_champions && stats.top_champions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-500" />
              Security Champions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {stats.top_champions.map((champion, idx) => (
                <div
                  key={champion.id}
                  className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800"
                >
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
                    ${idx === 0 ? 'bg-yellow-100 text-yellow-700' : 
                      idx === 1 ? 'bg-slate-200 text-slate-700' :
                      idx === 2 ? 'bg-orange-100 text-orange-700' :
                      'bg-slate-100 text-slate-600'}
                  `}>
                    #{idx + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{champion.display_name}</p>
                    <p className="text-xs text-slate-500">
                      Score: {champion.security_score.toFixed(1)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  subtitle,
  icon,
  color,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  color: "blue" | "green" | "red" | "purple";
}) {
  const colorClasses = {
    blue: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
    green: "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
    red: "bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400",
    purple: "bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-500 dark:text-slate-400">{title}</p>
            <p className="text-3xl font-bold mt-1">{value}</p>
            <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
          </div>
          <div className={`p-3 rounded-full ${colorClasses[color]}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Loading Skeleton
function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <div className="h-8 w-64 skeleton rounded" />
        <div className="h-4 w-96 skeleton rounded" />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card p-6">
            <div className="h-4 w-20 skeleton rounded mb-2" />
            <div className="h-8 w-24 skeleton rounded mb-1" />
            <div className="h-3 w-32 skeleton rounded" />
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-6">
          <div className="h-[300px] skeleton rounded" />
        </div>
        <div className="card p-6">
          <div className="h-[300px] skeleton rounded" />
        </div>
      </div>
    </div>
  );
}

