"use client";
import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: "sm" | "md" | "lg";
  color?: string;
  className?: string;
  showLabel?: boolean;
}

export function ProgressBar({ value, max = 100, size = "md", color, className, showLabel }: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  const heights = { sm: "h-1.5", md: "h-2", lg: "h-3" };

  return (
    <div className={cn("w-full", className)}>
      {showLabel && (
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={cn("w-full bg-slate-800 rounded-full overflow-hidden", heights[size])}>
        <div
          className={cn("h-full rounded-full transition-all duration-500", color || "bg-gradient-to-r from-indigo-500 to-purple-500")}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
