"use client";

import { useEffect, useState } from "react";
import { ChartBar, Pulse, GitBranch, Users, Database } from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import RepoTable from "@/components/tables/RepoTable";
import EngineerTable from "@/components/tables/EngineerTable";
import SecurityHeatmap from "@/components/charts/SecurityHeatmap";
import { fetchAPI } from "@/lib/utils";
import type { RepoAnalyticsResponse, EngineerAnalyticsResponse, MetricsResponse } from "@/types";

export default function AnalyticsPage() {
  const [data, setData] = useState<{
    repos: RepoAnalyticsResponse | null, 
    eng: EngineerAnalyticsResponse | null, 
    met: MetricsResponse | null
  }>({ repos: null, eng: null, met: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [r, e, m] = await Promise.all([
          fetchAPI<RepoAnalyticsResponse>("/api/analytics/repos?limit=50"),
          fetchAPI<EngineerAnalyticsResponse>("/api/analytics/engineers?limit=50"),
          fetchAPI<MetricsResponse>("/api/metrics?days=90"),
        ]);
        setData({ repos: r, eng: e, met: m });
      } catch (err) {
        console.error("Analytics Load Error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="font-mono text-accent-cyan animate-pulse text-center uppercase tracking-widest">
        Syncing_Intelligence_Nodes...
      </div>
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="border-b border-white/5 pb-6">
        <h1 className="text-3xl font-light text-white flex items-center gap-3 uppercase tracking-tighter">
          <ChartBar className="text-accent-cyan" weight="light" size={32} /> Intelligence Grid
        </h1>
        <p className="text-white/30 font-mono text-[10px] tracking-[0.3em] mt-1 uppercase">
          Cross-Sector Analytical Surveillance
        </p>
      </div>

      <Card className="bg-black/40 border-white/5 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-[10px] font-mono text-white/40 uppercase tracking-[0.2em] flex items-center gap-2">
            <Pulse className="text-accent-cyan" size={16} /> Temporal Threat Frequency
          </CardTitle>
        </CardHeader>
        <CardContent>
          <SecurityHeatmap data={data.met?.data || []} />
        </CardContent>
      </Card>

      <Tabs defaultValue="repos" className="space-y-6">
        <TabsList className="bg-white/5 border border-white/10 p-1 rounded-lg">
          <TabsTrigger value="repos" className="font-mono text-[10px] data-[state=active]:bg-accent-cyan data-[state=active]:text-black transition-all">
            <GitBranch size={14} className="mr-2" /> REPOSITORIES
          </TabsTrigger>
          <TabsTrigger value="engineers" className="font-mono text-[10px] data-[state=active]:bg-accent-cyan data-[state=active]:text-black transition-all">
            <Users size={14} className="mr-2" /> OPERATIVES
          </TabsTrigger>
        </TabsList>

        <TabsContent value="repos" className="animate-in slide-in-from-bottom-2 duration-500">
          <RepoTable data={data.repos?.data || []} />
        </TabsContent>

        <TabsContent value="engineers" className="animate-in slide-in-from-bottom-2 duration-500">
          <EngineerTable data={data.eng?.data || []} />
        </TabsContent>
      </Tabs>
    </div>
  );
}