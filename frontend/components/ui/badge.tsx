"use client";
import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "danger" | "info" | "purple";
  className?: string;
}

export function Badge({ children, variant = "default", className }: BadgeProps) {
  const variants = {
    default: "bg-slate-500/15 text-slate-400",
    success: "bg-emerald-500/15 text-emerald-400",
    warning: "bg-amber-500/15 text-amber-400",
    danger: "bg-red-500/15 text-red-400",
    info: "bg-cyan-500/15 text-cyan-400",
    purple: "bg-purple-500/15 text-purple-400",
  };
  return (
    <span className={cn("inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-semibold", variants[variant], className)}>
      {children}
    </span>
  );
}
