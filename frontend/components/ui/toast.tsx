"use client";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface Toast {
  id: string;
  message: string;
  type: "success" | "error" | "warning" | "info";
}

let toastListeners: ((toasts: Toast[]) => void)[] = [];
let toasts: Toast[] = [];

function notify() {
  toastListeners.forEach((listener) => listener([...toasts]));
}

export function toast(message: string, type: Toast["type"] = "success") {
  const id = Math.random().toString(36).slice(2);
  toasts = [...toasts, { id, message, type }];
  notify();
  setTimeout(() => {
    toasts = toasts.filter((t) => t.id !== id);
    notify();
  }, 4000);
}

export function ToastContainer() {
  const [items, setItems] = useState<Toast[]>([]);

  useEffect(() => {
    const listener = (t: Toast[]) => setItems(t);
    toastListeners.push(listener);
    return () => {
      toastListeners = toastListeners.filter((l) => l !== listener);
    };
  }, []);

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3">
      {items.map((t) => (
        <div
          key={t.id}
          className={cn(
            "flex items-center gap-3 px-5 py-4 rounded-lg border shadow-2xl animate-slide-up min-w-[300px]",
            t.type === "success" && "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
            t.type === "error" && "bg-red-500/10 border-red-500/30 text-red-400",
            t.type === "warning" && "bg-amber-500/10 border-amber-500/30 text-amber-400",
            t.type === "info" && "bg-indigo-500/10 border-indigo-500/30 text-indigo-400"
          )}
        >
          <span className="text-lg">
            {t.type === "success" && "&#10003;"}
            {t.type === "error" && "&#10007;"}
            {t.type === "warning" && "&#9888;"}
            {t.type === "info" && "&#9432;"}
          </span>
          <span className="text-sm font-medium">{t.message}</span>
        </div>
      ))}
    </div>
  );
}
