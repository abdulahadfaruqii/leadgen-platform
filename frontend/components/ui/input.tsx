"use client";
import { cn } from "@/lib/utils";
import { InputHTMLAttributes, forwardRef } from "react";

const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-sm outline-none transition-all placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20",
          className
        )}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";
export { Input };
