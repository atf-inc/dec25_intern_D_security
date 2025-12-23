"use client";

import { usePathname } from "next/navigation";
import Navbar from "@/components/Navbar";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLandingPage = pathname === "/";

  if (isLandingPage) {
    return <>{children}</>;
  }

  return (
    <div className="flex">
      <Navbar />
      <main className="flex-1 ml-64 p-8 cyber-grid min-h-screen">
        {children}
      </main>
    </div>
  );
}