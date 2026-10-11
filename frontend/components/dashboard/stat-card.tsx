"use client";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  changeType?: "up" | "down" | "neutral";
  gradient?: "blue" | "green" | "orange" | "purple";
  icon?: React.ReactNode;
}

export function StatCard({ label, value, change, changeType = "neutral", gradient = "blue", icon }: StatCardProps) {
  const gradients = {
    blue: "from-indigo-500 to-cyan-500",
    green: "from-emerald-500 to-teal-500",
    orange: "from-amber-500 to-orange-500",
    purple: "from-purple-500 to-pink-500",
  };

  return (
    <Card gradient className="relative overflow-hidden">
      <div className={cn("absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r", gradients[gradient])} />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</p>
          <p className="text-3xl font-extrabold text-slate-100 mt-2 tracking-tight">{value}</p>
          {change && (
            <p className={cn("text-xs font-semibold mt-2", 
              changeType === "up" && "text-emerald-400",
              changeType === "down" && "text-red-400",
              changeType === "neutral" && "text-slate-500"
            )}>
              {change}
            </p>
          )}
        </div>
        {icon && <div className="text-slate-600">{icon}</div>}
      </div>
    </Card>
  );
}
