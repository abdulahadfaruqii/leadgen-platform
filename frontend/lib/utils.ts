export function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}

export function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
  if (num >= 1000) return (num / 1000).toFixed(1) + "K";
  return num.toString();
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function getScoreClass(score: number): string {
  if (score >= 80) return "score-high";
  if (score >= 50) return "score-medium";
  return "score-low";
}

export function getScoreLabel(score: number): string {
  if (score >= 80) return "High";
  if (score >= 50) return "Medium";
  return "Low";
}

export function getStatusColor(status: string): string {
  const map: Record<string, string> = {
    discovered: "bg-indigo-500",
    qualified: "bg-emerald-500",
    contacted: "bg-amber-500",
    converted: "bg-purple-500",
    running: "bg-emerald-500",
    draft: "bg-slate-500",
    completed: "bg-indigo-500",
    pending: "bg-amber-500",
    approved: "bg-emerald-500",
    sent: "bg-indigo-500",
    opened: "bg-cyan-500",
    replied: "bg-emerald-500",
  };
  return map[status] || "bg-slate-500";
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function getCategoryColor(category: string): string {
  const map: Record<string, string> = {
    dentists: "bg-indigo-500/15 text-indigo-400",
    restaurants: "bg-amber-500/15 text-amber-400",
    gyms: "bg-cyan-500/15 text-cyan-400",
    "law firms": "bg-purple-500/15 text-purple-400",
    "real estate": "bg-pink-500/15 text-pink-400",
    hotels: "bg-rose-500/15 text-rose-400",
    "medical clinics": "bg-teal-500/15 text-teal-400",
    "beauty salons": "bg-fuchsia-500/15 text-fuchsia-400",
  };
  return map[category.toLowerCase()] || "bg-slate-500/15 text-slate-400";
}
