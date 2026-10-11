"use client";
import { Lead } from "@/types";
import { getInitials, getScoreClass, formatNumber } from "@/lib/utils";
import { ScoreRing } from "@/components/ui/score-ring";

interface LeadPreviewProps {
  leads: Lead[];
}

export function LeadPreview({ leads }: LeadPreviewProps) {
  const gradients = [
    "from-indigo-500 to-purple-600",
    "from-amber-500 to-red-500",
    "from-cyan-500 to-indigo-500",
    "from-emerald-500 to-cyan-500",
    "from-pink-500 to-rose-500",
  ];

  return (
    <div className="space-y-3">
      {leads.map((lead, i) => (
        <div
          key={lead.id}
          className="flex items-center gap-4 p-4 rounded-lg bg-slate-800/30 border border-transparent hover:border-slate-700 hover:bg-slate-800/50 transition-all cursor-pointer"
        >
          <div className={`w-11 h-11 rounded-full bg-gradient-to-br ${gradients[i % gradients.length]} flex items-center justify-center text-white font-bold text-sm shrink-0`}>
            {getInitials(lead.business?.name || "Unknown")}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-slate-200 truncate">
              {lead.business?.name || "Unknown Business"}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">
              {lead.business?.category} &bull; {lead.business?.city}, {lead.business?.state}
              {lead.business?.website ? "" : " &bull; No website"}
            </p>
          </div>
          <ScoreRing score={lead.overall_score} size={44} />
        </div>
      ))}
    </div>
  );
}
