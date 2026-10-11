"use client";
import { useCallback, useEffect, useState } from "react";
import { analyticsApi } from "@/lib/api";
import { DashboardMetrics } from "@/types";

type AnalyticsPayload = DashboardMetrics & {
  outreach_funnel?: {
    sent: number;
    opened: number;
    clicked: number;
    replied: number;
  };
};

export function useAnalytics() {
  const [metrics, setMetrics] = useState<AnalyticsPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await analyticsApi.dashboard();
      setMetrics(res.data);
    } catch {
      setError("Failed to load analytics");
      setMetrics(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return { metrics, isLoading, error, refetch: fetchMetrics };
}
