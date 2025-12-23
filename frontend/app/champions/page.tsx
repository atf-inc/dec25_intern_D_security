"use client";

import { useEffect, useState } from "react";
import { ShieldCheck, Crown, Medal, Trophy } from "@phosphor-icons/react";
import { Card } from "@/components/ui/card";
import { fetchAPI, cn } from "@/lib/utils";
import type { ChampionsResponse } from "@/types";

export default function ChampionsPage() {
  const [data, setData] = useState<ChampionsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAPI<ChampionsResponse>("/api/champions?limit=20")
      .then(setData)
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="font-mono text-accent-cyan animate-pulse text-center uppercase tracking-widest">
        Reconstructing_Leaderboard...
      </div>
    </div>
  );

  const champions = data?.champions || [];

  return (
    <div className="space-y-12 animate-in fade-in duration-700">
      <div className="text-center space-y-4">
        <h2 className="text-[10px] font-mono text-accent-cyan tracking-[0.5em] uppercase">Elite Operatives</h2>
        <h1 className="text-5xl font-light tracking-tighter uppercase">Security Champions</h1>
      </div>

      {champions.length === 0 ? (
        <div className="text-center py-20">
          <Trophy size={64} className="mx-auto text-white/10 mb-6" />
          <h3 className="text-xl font-light text-white/40 mb-2">No Champions Yet</h3>
          <p className="text-white/20 font-mono text-xs">Engineers need at least 1 PR scanned to appear here</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto items-end">
            {champions.slice(0, 3).map((c, i) => {
              const orderClass = i === 0 ? "md:order-2 scale-110 z-10" : i === 1 ? "md:order-1" : "md:order-3";
              const icon = i === 0 ? <Crown size={48} weight="fill" className="text-yellow-500" /> : 
                           i === 1 ? <Medal size={48} weight="fill" className="text-slate-400" /> : 
                                     <Trophy size={48} weight="fill" className="text-orange-600" />;
              
              return (
                <div key={c.id} className={cn("relative group w-full", orderClass)}>
                  <Card className={cn(
                    "bg-bg-surface border-white/10 overflow-hidden text-center p-8 transition-all duration-500 hover:border-white/20", 
                    i === 0 && "border-accent-cyan shadow-[0_0_40px_rgba(0,240,255,0.1)]"
                  )}>
                    <div className="flex justify-center mb-6">{icon}</div>
                    <h3 className="text-xl font-medium mb-1 text-white">{c.display_name}</h3>
                    <p className="text-accent-cyan font-mono text-[10px] mb-4 uppercase tracking-widest">
                      Rating: {c.security_score.toFixed(1)}
                    </p>
                    <div className="h-0.5 w-full bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-accent-cyan transition-all duration-1000" style={{ width: `${c.clean_rate}%` }} />
                    </div>
                  </Card>
                </div>
              );
            })}
          </div>

          {champions.length > 3 && (
            <div className="max-w-4xl mx-auto space-y-2">
              {champions.slice(3).map((c, i) => (
                <div key={c.id} className="flex items-center justify-between p-6 bg-white/5 rounded-xl border border-white/5 hover:border-white/20 transition-all group">
                  <div className="flex items-center gap-6">
                    <span className="font-mono text-white/20">#{i + 4}</span>
                    <span className="text-lg font-light text-white/80 group-hover:text-white transition-colors">
                      {c.display_name}
                    </span>
                  </div>
                  <div className="flex items-center gap-12">
                    <div className="text-right">
                      <div className="text-[9px] text-white/30 font-mono uppercase">Compliance</div>
                      <div className="text-accent-emerald font-mono text-sm">{c.clean_rate}%</div>
                    </div>
                    <ShieldCheck size={32} weight="thin" className="text-white/10 group-hover:text-accent-cyan transition-colors" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}