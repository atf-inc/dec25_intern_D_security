"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  SquaresFour, ChartBar, TrendUp, Trophy,
  Flask, ChatCircleText, ShieldCheck, SignOut
} from "@phosphor-icons/react";
import { cn } from "@/lib/utils";

const navItems = [
  { title: "Command Center", href: "/dashboard", icon: SquaresFour },
  { title: "Intelligence Grid", href: "/analytics", icon: ChartBar },
  { title: "Neural Trends", href: "/metrics", icon: TrendUp },
  { title: "Elite Champions", href: "/champions", icon: Trophy },
  { title: "Security Lab", href: "/tests", icon: Flask },
  { title: "Security Oracle", href: "/chat", icon: ChatCircleText },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-bg-surface border-r border-white/5 flex flex-col">
      <div className="h-24 flex items-center gap-3 px-6 border-b border-white/5">
        <div className="w-10 h-10 bg-white text-black rounded flex items-center justify-center shadow-[0_0_20px_rgba(255,255,255,0.2)]">
          <ShieldCheck weight="fill" size={24} />
        </div>
        <div>
          <h1 className="font-bold text-white text-xs tracking-[0.2em]">ATF SENTINEL</h1>
          <p className="text-[9px] text-accent-cyan font-mono animate-pulse">SYSTEM_ONLINE</p>
        </div>
      </div>

      <nav className="flex-1 py-6 px-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 group",
                isActive
                  ? "bg-white/10 text-white shadow-neumorph border border-white/10"
                  : "text-white/40 hover:text-white hover:bg-white/5"
              )}
            >
              <item.icon size={20} weight={isActive ? "fill" : "light"} className={isActive ? "text-accent-cyan" : ""} />
              <span>{item.title}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-white/5">
        <div className="text-[10px] font-mono text-white/20 mb-2 uppercase">System_Status</div>
        <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden mb-6">
          <div className="h-full bg-accent-emerald w-full" />
        </div>
        <Link href="/" className="flex items-center gap-3 w-full px-4 py-2 rounded-xl text-white/30 hover:text-accent-crimson transition-all text-xs font-mono">
          <SignOut size={18} />
          <span>EXIT_CONSOLE</span>
        </Link>
      </div>
    </aside>
  );
}