"use client";
import { Business } from "@/types";
import { DataTable } from "@/components/ui/data-table";
import { Badge } from "@/components/ui/badge";
import { getCategoryColor, getStatusColor, getScoreClass } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface RecentActivityProps {
  businesses: Business[];
}

export function RecentActivity({ businesses }: RecentActivityProps) {
  const columns = [
    {
      key: "name",
      header: "Business",
      render: (row: Business) => (
        <div>
          <p className="font-semibold text-slate-200">{row.name}</p>
          <p className="text-xs text-slate-500">{row.website || "No website"}</p>
        </div>
      ),
    },
    {
      key: "category",
      header: "Category",
      width: "120px",
      render: (row: Business) => (
        <span className={`tag-pill ${getCategoryColor(row.category)}`}>
          {row.category}
        </span>
      ),
    },
    {
      key: "location",
      header: "Location",
      width: "140px",
      render: (row: Business) => (
        <span className="text-sm text-slate-400">{row.city}, {row.state}</span>
      ),
    },
    {
      key: "status",
      header: "Status",
      width: "120px",
      render: (row: Business) => (
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${getStatusColor(row.status)}`} />
          <span className="text-sm text-slate-300 capitalize">{row.status}</span>
        </div>
      ),
    },
    {
      key: "score",
      header: "Score",
      width: "80px",
      render: (row: Business) => (
        row.lead_score ? (
          <span className={`tag-pill ${getScoreClass(row.lead_score)}`}>
            {Math.round(row.lead_score)}
          </span>
        ) : (
          <span className="text-slate-600 text-sm">-</span>
        )
      ),
    },
    {
      key: "action",
      header: "",
      width: "100px",
      render: () => (
        <Button variant="ghost" size="sm">View</Button>
      ),
    },
  ];

  return <DataTable columns={columns} data={businesses} keyExtractor={(b) => b.id} />;
}
