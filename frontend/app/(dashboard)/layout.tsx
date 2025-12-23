import Navbar from "@/components/Navbar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Navbar />
      <main className="flex-1 ml-64 p-8 cyber-grid min-h-screen">
        {children}
      </main>
    </div>
  );
}