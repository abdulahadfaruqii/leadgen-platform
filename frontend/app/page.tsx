"use client";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { StatCard } from "@/components/dashboard/stat-card";
import { ChartBars } from "@/components/dashboard/chart-bars";
import { LeadPreview } from "@/components/dashboard/lead-preview";
import { RecentActivity } from "@/components/dashboard/recent-activity";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useAnalytics } from "@/hooks/use-analytics";
import { useLeads } from "@/hooks/use-leads";
import { useBusinesses } from "@/hooks/use-businesses";
import { formatNumber } from "@/lib/utils";

export default function DashboardPage() {
  const router = useRouter();
  const { metrics, isLoading: metricsLoading } = useAnalytics();
  const { leads, isLoading: leadsLoading } = useLeads({ limit: 5 });
  const { businesses, isLoading: businessesLoading } = useBusinesses({ limit: 5 });

  const scoreDistribution = (metrics?.score_distribution || []).map((item) => ({
    label: item.range,
    value: item.count,
  }));

  const responseRate =
    metrics && metrics.total_outreach_sent
      ? `${((metrics.total_responses / metrics.total_outreach_sent) * 100).toFixed(1)}%`
      : "0%";

  return (
    <AppShell>
      <PageHeader
        title="Dashboard"
        subtitle="Overview of your lead generation performance"
        actions={
          <>
            <Button variant="ghost" onClick={() => router.push("/campaigns")}>
              View Campaigns
            </Button>
            <Button onClick={() => router.push("/campaigns?create=true")}>
              + New Campaign
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <StatCard
          label="Businesses Found"
          value={metricsLoading ? "…" : formatNumber(metrics?.total_businesses_found || 0)}
          change="Live from API"
          changeType="up"
          gradient="blue"
        />
        <StatCard
          label="Qualified Leads"
          value={metricsLoading ? "…" : formatNumber(metrics?.total_leads_qualified || 0)}
          change="Live from API"
          changeType="up"
          gradient="green"
        />
        <StatCard
          label="Outreach Sent"
          value={metricsLoading ? "…" : formatNumber(metrics?.total_outreach_sent || 0)}
          change="Live from API"
          changeType="up"
          gradient="orange"
        />
        <StatCard
          label="Response Rate"
          value={metricsLoading ? "…" : responseRate}
          change={`Avg score ${metrics?.avg_lead_score ?? 0}`}
          changeType="up"
          gradient="purple"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Lead Score Distribution</CardTitle>
          </CardHeader>
          {scoreDistribution.length ? (
            <ChartBars data={scoreDistribution} />
          ) : (
            <p className="text-sm text-slate-500 py-8 text-center">
              {metricsLoading ? "Loading…" : "No lead score data yet"}
            </p>
          )}
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Opportunities</CardTitle>
          </CardHeader>
          {leadsLoading ? (
            <p className="text-sm text-slate-500 py-8 text-center">Loading…</p>
          ) : leads.length ? (
            <LeadPreview leads={leads.slice(0, 5)} />
          ) : (
            <p className="text-sm text-slate-500 py-8 text-center">No leads yet</p>
          )}
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        {businessesLoading ? (
          <p className="text-sm text-slate-500 py-8 text-center">Loading…</p>
        ) : (
          <RecentActivity businesses={businesses.slice(0, 8)} />
        )}
      </Card>
    </AppShell>
  );
}
