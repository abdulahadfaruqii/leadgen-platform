"use client";
import { Sidebar } from "./sidebar";
import { ToastContainer } from "@/components/ui/toast";
import { useAuth } from "@/hooks/use-auth";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth(true);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0f1117] text-slate-400">
        Loading…
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen bg-[#0f1117]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="p-8 max-w-7xl mx-auto">{children}</div>
      </main>
      <ToastContainer />
    </div>
  );
}
