"use client";
import { useCallback, useEffect, useState } from "react";
import { businessesApi } from "@/lib/api";
import { Business } from "@/types";

export function useBusinesses(params?: Record<string, unknown>) {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBusinesses = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await businessesApi.list({ limit: 100, ...params });
      setBusinesses(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch {
      setError("Failed to load businesses");
      setBusinesses([]);
    } finally {
      setIsLoading(false);
    }
  }, [JSON.stringify(params || {})]);

  useEffect(() => {
    fetchBusinesses();
  }, [fetchBusinesses]);

  return { businesses, total, isLoading, error, refetch: fetchBusinesses };
}
