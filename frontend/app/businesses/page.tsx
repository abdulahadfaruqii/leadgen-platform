"use client";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { Select } from "@/components/ui/select";
import { DataTable } from "@/components/ui/data-table";
import { Business } from "@/types";
import { getCategoryColor, getStatusColor, getScoreClass } from "@/lib/utils";
import { useBusinesses } from "@/hooks/use-businesses";

export default function BusinessesPage() {
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const apiParams = useMemo(
    () => ({
      limit: 100,
      ...(search ? { search } : {}),
      ...(categoryFilter ? { category: categoryFilter } : {}),
      ...(statusFilter ? { status: statusFilter } : {}),
    }),
    [search, categoryFilter, statusFilter]
  );
  const { businesses, isLoading, error, refetch } = useBusinesses(apiParams);

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
      width: "130px",
      render: (row: Business) => <span className={`tag-pill ${getCategoryColor(row.category)}`}>{row.category}</span>,
    },
    {
      key: "location",
      header: "Location",
      width: "130px",
      render: (row: Business) => (
        <span className="text-sm text-slate-400">
          {row.city}, {row.state}
        </span>
      ),
    },
    {
      key: "rating",
      header: "Rating",
      width: "100px",
      render: (row: Business) => (
        <div className="text-sm">
          <span className="text-amber-400">★</span> {row.google_rating ?? "—"}{" "}
          <span className="text-slate-500">({row.google_review_count ?? 0})</span>
        </div>
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
      width: "70px",
      render: (row: Business) =>
        row.lead_score ? (
          <span className={`tag-pill ${getScoreClass(row.lead_score)}`}>{Math.round(row.lead_score)}</span>
        ) : (
          <span className="text-slate-600">-</span>
        ),
    },
  ];

  return (
    <AppShell>
      <PageHeader
        title="Businesses"
        subtitle="Browse discovered businesses"
        actions={
          <>
            <SearchInput value={search} onChange={setSearch} placeholder="Search businesses..." className="w-64" />
            <Button onClick={() => refetch()}>Refresh</Button>
          </>
        }
      />

      <div className="flex flex-wrap gap-3 mb-5">
        <Select
          value={categoryFilter}
          onChange={setCategoryFilter}
          placeholder="All Categories"
          options={[
            { value: "Dentists", label: "Dentists" },
            { value: "Restaurants", label: "Restaurants" },
            { value: "Gyms", label: "Gyms" },
            { value: "Law Firms", label: "Law Firms" },
            { value: "Real Estate", label: "Real Estate" },
            { value: "Beauty Salons", label: "Beauty Salons" },
            { value: "Medical Clinics", label: "Medical Clinics" },
          ]}
        />
        <Select
          value={statusFilter}
          onChange={setStatusFilter}
          placeholder="All Status"
          options={[
            { value: "discovered", label: "Discovered" },
            { value: "qualified", label: "Qualified" },
            { value: "contacted", label: "Contacted" },
          ]}
        />
      </div>

      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}
      {isLoading ? (
        <p className="text-slate-500">Loading businesses…</p>
      ) : (
        <DataTable
          columns={columns}
          data={businesses}
          keyExtractor={(b) => b.id}
          emptyMessage="No businesses found matching your filters"
        />
      )}
    </AppShell>
  );
}
