"use client";
import { useCallback, useEffect, useState } from "react";
import { leadsApi } from "@/lib/api";
import { Lead } from "@/types";

export function useLeads(params?: Record<string, unknown>) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLeads = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await leadsApi.list({ limit: 100, ...params });
      setLeads(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch {
      setError("Failed to load leads");
      setLeads([]);
    } finally {
      setIsLoading(false);
    }
  }, [JSON.stringify(params || {})]);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  return { leads, total, isLoading, error, refetch: fetchLeads };
}
