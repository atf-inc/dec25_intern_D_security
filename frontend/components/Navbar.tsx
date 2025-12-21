"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BarChart3,
  LineChart,
  Trophy,
  FlaskConical,
  MessageSquare,
  Shield,
  ExternalLink,
  Github,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Analytics",
    href: "/analytics",
    icon: BarChart3,
  },
  {
    title: "Metrics",
    href: "/metrics",
    icon: LineChart,
  },
  {
    title: "Champions",
    href: "/champions",
    icon: Trophy,
  },
  {
    title: "Test Generator",
    href: "/tests",
    icon: FlaskConical,
  },
  {
    title: "Security Chat",
    href: "/chat",
    icon: MessageSquare,
  },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-3 border-b border-slate-200 px-6 dark:border-slate-800">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-green-500 to-emerald-600">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-slate-900 dark:text-white">
              ATF Sentinel
            </h1>
            <p className="text-xs text-slate-500">Security Dashboard</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
                )}
              >
                <Icon className={cn(
                  "h-5 w-5",
                  isActive ? "text-green-600 dark:text-green-400" : ""
                )} />
                {item.title}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-slate-200 p-4 dark:border-slate-800">
          {/* API Status */}
          <div className="mb-4 rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">API Status</span>
              <div className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs text-green-600 dark:text-green-400">
                  Online
                </span>
              </div>
            </div>
          </div>

          {/* External Links */}
          <div className="space-y-2">
            <a
              href="/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            >
              <ExternalLink className="h-4 w-4" />
              API Docs
            </a>
            <a
              href="https://github.com/atf-inc/atf-sentinel"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            >
              <Github className="h-4 w-4" />
              GitHub
            </a>
          </div>

          {/* Version */}
          <div className="mt-4 text-center text-xs text-slate-400">
            v2.0.0 • © 2025 ATF Inc.
          </div>
        </div>
      </div>
    </aside>
  );
}

