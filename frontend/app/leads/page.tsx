"use client";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { DataTable } from "@/components/ui/data-table";
import { Lead } from "@/types";
import { getCategoryColor, getScoreClass } from "@/lib/utils";
import { useLeads } from "@/hooks/use-leads";

export default function LeadsPage() {
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const apiParams = useMemo(
    () => ({
      limit: 100,
      ...(priorityFilter ? { priority: priorityFilter } : {}),
      ...(statusFilter ? { outreach_status: statusFilter } : {}),
    }),
    [priorityFilter, statusFilter]
  );
  const { leads, isLoading, error, refetch } = useLeads(apiParams);

  const filtered = leads.filter((l) => {
    const name = l.business?.name?.toLowerCase() || "";
    return !search || name.includes(search.toLowerCase());
  });

  const columns = [
    {
      key: "business",
      header: "Business",
      render: (row: Lead) => (
        <div>
          <p className="font-semibold text-slate-200">{row.business?.name || row.business_id}</p>
          <p className="text-xs text-slate-500">{row.qualification_reasons?.[0] || "Qualified lead"}</p>
        </div>
      ),
    },
    {
      key: "category",
      header: "Category",
      width: "120px",
      render: (row: Lead) => (
        <span className={`tag-pill ${getCategoryColor(row.business?.category || "")}`}>
          {row.business?.category || "—"}
        </span>
      ),
    },
    {
      key: "location",
      header: "Location",
      width: "130px",
      render: (row: Lead) => (
        <span className="text-sm text-slate-400">
          {row.business?.city || "—"}
          {row.business?.state ? `, ${row.business.state}` : ""}
        </span>
      ),
    },
    {
      key: "priority",
      header: "Priority",
      width: "90px",
      render: (row: Lead) => (
        <span
          className={`text-xs font-bold uppercase ${
            row.priority === "high" ? "text-red-400" : row.priority === "medium" ? "text-amber-400" : "text-slate-400"
          }`}
        >
          {row.priority}
        </span>
      ),
    },
    {
      key: "score",
      header: "Score",
      width: "70px",
      render: (row: Lead) => (
        <span className={`tag-pill ${getScoreClass(row.overall_score)}`}>{Math.round(row.overall_score)}</span>
      ),
    },
    {
      key: "status",
      header: "Status",
      width: "110px",
      render: (row: Lead) => <span className="text-sm text-slate-300 capitalize">{row.outreach_status}</span>,
    },
  ];

  return (
    <AppShell>
      <PageHeader
        title="Qualified Leads"
        subtitle="High-potential businesses ready for outreach"
        actions={
          <>
            <SearchInput value={search} onChange={setSearch} placeholder="Search leads..." className="w-64" />
            <Button onClick={() => refetch()}>Refresh</Button>
          </>
        }
      />

      <div className="flex flex-wrap gap-3 mb-5">
        <Select
          value={priorityFilter}
          onChange={setPriorityFilter}
          placeholder="All Priorities"
          options={[
            { value: "high", label: "High" },
            { value: "medium", label: "Medium" },
            { value: "low", label: "Low" },
          ]}
        />
        <Select
          value={statusFilter}
          onChange={setStatusFilter}
          placeholder="All Status"
          options={[
            { value: "pending", label: "Pending" },
            { value: "contacted", label: "Contacted" },
            { value: "responded", label: "Responded" },
            { value: "converted", label: "Converted" },
          ]}
        />
      </div>

      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}
      {isLoading ? (
        <p className="text-slate-500">Loading leads…</p>
      ) : (
        <DataTable columns={columns} data={filtered} keyExtractor={(l) => l.id} emptyMessage="No leads found matching your filters" />
      )}
    </AppShell>
  );
}
