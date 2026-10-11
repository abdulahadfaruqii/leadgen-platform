"use client";
import { cn } from "@/lib/utils";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  gradient?: boolean;
}

export function Card({ children, className, gradient }: CardProps) {
  return (
    <div
      className={cn(
        "bg-slate-900/80 border border-slate-800 rounded-xl p-6 transition-all duration-200",
        gradient && "relative overflow-hidden",
        className
      )}
    >
      {gradient && (
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500" />
      )}
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("flex items-center justify-between mb-4", className)}>{children}</div>;
}

export function CardTitle({ children, className }: { children: React.ReactNode; className?: string }) {
  return <h3 className={cn("text-base font-bold text-slate-100", className)}>{children}</h3>;
}
