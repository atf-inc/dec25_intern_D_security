"use client";

import { useEffect, useState } from "react";
import { 
  BarChart3, 
  GitBranch, 
  AlertTriangle,
  RefreshCw
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import RepoTable from "@/components/tables/RepoTable";
import EngineerTable from "@/components/tables/EngineerTable";
import SecurityHeatmap from "@/components/charts/SecurityHeatmap";
import { fetchAPI } from "@/lib/utils";
import type { RepoAnalyticsResponse, EngineerAnalyticsResponse, MetricsResponse } from "@/types";

export default function AnalyticsPage() {
  const [repos, setRepos] = useState<RepoAnalyticsResponse | null>(null);
  const [engineers, setEngineers] = useState<EngineerAnalyticsResponse | null>(null);
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function fetchData() {
    try {
      const [repoData, engineerData, metricsData] = await Promise.all([
        fetchAPI<RepoAnalyticsResponse>("/api/analytics/repos?limit=50"),
        fetchAPI<EngineerAnalyticsResponse>("/api/analytics/engineers?limit=50"),
        fetchAPI<MetricsResponse>("/api/metrics?days=90"),
      ]);
      
      setRepos(repoData);
      setEngineers(engineerData);
      setMetrics(metricsData);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return <AnalyticsSkeleton />;
  }

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Analytics
          </h1>
          <p className="text-slate-500 mt-1">
            Detailed security metrics and analysis
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-green-500" />
            Security Activity Heatmap
          </CardTitle>
        </CardHeader>
        <CardContent>
          <SecurityHeatmap data={metrics?.data || []} />
        </CardContent>
      </Card>

      {/* Tabs for Repos and Engineers */}
      <Tabs defaultValue="repos">
        <TabsList>
          <TabsTrigger value="repos" className="flex items-center gap-2">
            <GitBranch className="w-4 h-4" />
            Repositories
          </TabsTrigger>
          <TabsTrigger value="engineers" className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Engineers
          </TabsTrigger>
        </TabsList>

        <TabsContent value="repos" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Repository Security Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <RepoTable data={repos?.data || []} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="engineers" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Engineer Security Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <EngineerTable data={engineers?.data || []} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function AnalyticsSkeleton() {
  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <div className="h-8 w-48 skeleton rounded" />
        <div className="h-4 w-72 skeleton rounded" />
      </div>
      <div className="card p-6">
        <div className="h-[200px] skeleton rounded" />
      </div>
      <div className="card p-6">
        <div className="h-[400px] skeleton rounded" />
      </div>
    </div>
  );
}