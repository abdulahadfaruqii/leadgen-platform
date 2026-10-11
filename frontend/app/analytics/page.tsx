"use client";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/stat-card";
import { ChartBars } from "@/components/dashboard/chart-bars";
import { useAnalytics } from "@/hooks/use-analytics";
import { formatNumber } from "@/lib/utils";

export default function AnalyticsPage() {
  const { metrics, isLoading, error, refetch } = useAnalytics();

  const categoryData = (metrics?.top_categories || []).map((item) => ({
    label: item.name,
    value: item.count,
  }));

  const funnelData = [
    { label: "Sent", value: metrics?.outreach_funnel?.sent || metrics?.total_outreach_sent || 0 },
    { label: "Opened", value: metrics?.outreach_funnel?.opened || 0 },
    { label: "Clicked", value: metrics?.outreach_funnel?.clicked || 0 },
    { label: "Replied", value: metrics?.outreach_funnel?.replied || metrics?.total_responses || 0 },
  ];

  const scoreRows = metrics?.score_distribution || [];
  const scoreTotal = scoreRows.reduce((sum, row) => sum + row.count, 0) || 1;

  return (
    <AppShell>
      <PageHeader
        title="Analytics"
        subtitle="Deep insights into your lead generation performance"
        actions={<Button onClick={() => refetch()}>Refresh</Button>}
      />

      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <StatCard
          label="Avg Lead Score"
          value={isLoading ? "…" : String(metrics?.avg_lead_score ?? 0)}
          change="Live from API"
          changeType="up"
          gradient="blue"
        />
        <StatCard
          label="Conversion Rate"
          value={isLoading ? "…" : `${metrics?.conversion_rate ?? 0}%`}
          change="Live from API"
          changeType="up"
          gradient="green"
        />
        <StatCard
          label="Qualified Leads"
          value={isLoading ? "…" : formatNumber(metrics?.total_leads_qualified || 0)}
          change="Live from API"
          changeType="up"
          gradient="orange"
        />
        <StatCard
          label="Businesses Found"
          value={isLoading ? "…" : formatNumber(metrics?.total_businesses_found || 0)}
          change="Live from API"
          changeType="up"
          gradient="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Categories</CardTitle>
          </CardHeader>
          {categoryData.length ? (
            <ChartBars data={categoryData} />
          ) : (
            <p className="text-sm text-slate-500 py-8 text-center">{isLoading ? "Loading…" : "No category data"}</p>
          )}
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Outreach Funnel</CardTitle>
          </CardHeader>
          <div className="space-y-5 pt-4">
            {funnelData.map((item, i) => {
              const max = Math.max(funnelData[0].value, 1);
              const pct = (item.value / max) * 100;
              const colors = ["bg-indigo-500", "bg-cyan-500", "bg-amber-500", "bg-emerald-500"];
              return (
                <div key={item.label}>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-300">{item.label}</span>
                    <span className="font-bold text-slate-100">{item.value}</span>
                  </div>
                  <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div className={`h-full ${colors[i]} rounded-full transition-all`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Score Distribution</CardTitle>
        </CardHeader>
        <div className="space-y-3">
          {scoreRows.length === 0 ? (
            <p className="text-sm text-slate-500 py-6 text-center">{isLoading ? "Loading…" : "No score data"}</p>
          ) : (
            scoreRows.map((item) => (
              <div key={item.range} className="flex items-center gap-3">
                <span className="text-xs text-slate-500 w-12">{item.range}</span>
                <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                    style={{ width: `${(item.count / scoreTotal) * 100}%` }}
                  />
                </div>
                <span className="text-xs font-bold text-slate-300 w-8 text-right">{item.count}</span>
              </div>
            ))
          )}
        </div>
      </Card>
    </AppShell>
  );
}
