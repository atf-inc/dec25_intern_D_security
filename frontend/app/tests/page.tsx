"use client";

import { useState } from "react";
import { Flask, Terminal, Code, Cpu } from "@phosphor-icons/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function TestsPage() {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  async function generate() {
    if (!code) return;
    setLoading(true);
    try {
      const res = await fetch("/api/tests/generate", {
        method: "POST",
        body: JSON.stringify({ code, language: "python" }),
      });
      const data = await res.json();
      setResult(data.tests);
    } catch (err) {
        console.error(err);
    } finally { setLoading(false); }
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="border-b border-white/5 pb-6">
        <h1 className="text-3xl font-light text-white flex items-center gap-3 uppercase tracking-tighter">
          <Flask className="text-accent-cyan" size={32} /> Security Lab
        </h1>
        <p className="text-white/40 font-mono text-[10px] tracking-widest mt-1 uppercase">AI_VULNERABILITY_SYNTHESIS_ENGINE</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-black/60 border-white/10 shadow-2xl">
          <CardHeader className="border-b border-white/5">
            <CardTitle className="text-[10px] font-mono flex items-center gap-2 text-white/40 uppercase tracking-widest">
              <Terminal size={14} /> SOURCE_BUFFER
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full h-[500px] bg-transparent p-6 font-mono text-sm text-accent-cyan outline-none resize-none placeholder:opacity-10"
              placeholder="// Input sensitive logic for deep-scan analysis..."
            />
            <div className="p-4 border-t border-white/5 bg-black/40">
                <Button onClick={generate} loading={loading} className="w-full bg-accent-cyan text-black hover:bg-white transition-all font-mono text-[10px] font-bold py-6 rounded-xl uppercase tracking-widest">
                   <Cpu size={18} className="mr-2" /> EXECUTE_VULN_SYNTHESIS
                </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-black/60 border-white/10 shadow-2xl">
          <CardHeader className="border-b border-white/5">
            <CardTitle className="text-[10px] font-mono flex items-center gap-2 text-white/40 uppercase tracking-widest">
              <Code size={14} /> ANALYSIS_REPORT
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            {result ? (
              <pre className="text-xs font-mono text-white/70 whitespace-pre-wrap leading-relaxed overflow-y-auto h-[480px] custom-scrollbar">
                {result}
              </pre>
            ) : (
              <div className="h-[480px] flex flex-col items-center justify-center text-white/10 font-mono text-[10px] italic">
                <div className="w-16 h-16 border border-white/5 rounded-full flex items-center justify-center mb-4">
                    <div className="w-3 h-3 bg-accent-cyan rounded-full animate-ping" />
                </div>
                AWAITING_SOURCE_SIGNAL...
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}