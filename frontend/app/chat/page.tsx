"use client";

import { useState, useRef, useEffect } from "react";
import { ChatCircleText, PaperPlaneTilt, Robot, User } from "@phosphor-icons/react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/types";

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => { 
    endRef.current?.scrollIntoView({ behavior: "smooth" }); 
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        body: JSON.stringify({ 
          message: userMsg.content, 
          history: messages.map(m => ({ role: m.role, content: m.content })) 
        }),
      });
      const data = await res.json();
      const aiMsg: ChatMessage = { id: (Date.now()+1).toString(), role: "assistant", content: data.response, timestamp: new Date() };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
        console.error("Chat error:", err);
    } finally { setLoading(false); }
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-in fade-in duration-500">
      <div className="border-b border-white/5 pb-6 mb-6">
        <h1 className="text-3xl font-light text-white flex items-center gap-3">
          <ChatCircleText className="text-accent-cyan" /> Security Oracle
        </h1>
        <p className="text-white/30 font-mono text-[10px] tracking-widest mt-1 uppercase">Heuristic_AI_Assistant</p>
      </div>

      <Card className="flex-1 flex flex-col bg-black/40 border-white/5 overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center opacity-20 font-mono text-xs">
                <Robot size={48} className="mb-4" />
                AWAITING_QUERY_INPUT...
            </div>
          )}
          {messages.map((m) => (
            <div key={m.id} className={cn("flex gap-4", m.role === "user" ? "flex-row-reverse" : "")}>
              <div className={cn("w-8 h-8 rounded flex items-center justify-center border shrink-0", m.role === "user" ? "border-accent-cyan bg-accent-cyan/10" : "border-white/10 bg-white/5")}>
                {m.role === "user" ? <User size={16} className="text-accent-cyan" /> : <Robot size={16} />}
              </div>
              <div className={cn("max-w-[80%] p-4 rounded-2xl text-sm font-light leading-relaxed", m.role === "user" ? "bg-accent-cyan text-black font-medium" : "bg-white/5 text-white/80")}>
                {m.content}
              </div>
            </div>
          ))}
          <div ref={endRef} />
        </CardContent>

        <div className="p-4 bg-black/60 border-t border-white/5">
          <div className="flex gap-4">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSend()}
              placeholder="Query security protocols..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-6 py-3 font-mono text-xs text-accent-cyan outline-none focus:border-accent-cyan transition-colors"
            />
            <button onClick={handleSend} disabled={loading} className="bg-accent-cyan text-black px-6 rounded-xl hover:bg-white transition-all flex items-center justify-center">
              <PaperPlaneTilt size={20} weight="bold" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}