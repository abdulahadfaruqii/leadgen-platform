"use client";
import { useCallback, useEffect, useState } from "react";
import { campaignsApi } from "@/lib/api";
import { Campaign } from "@/types";

export function useCampaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCampaigns = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await campaignsApi.list({ limit: 100 });
      setCampaigns(res.data.items || []);
    } catch {
      setError("Failed to load campaigns");
      setCampaigns([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCampaigns();
  }, [fetchCampaigns]);

  const createCampaign = async (data: unknown) => {
    const res = await campaignsApi.create(data);
    await fetchCampaigns();
    return res.data;
  };

  const startCampaign = async (id: string) => {
    await campaignsApi.start(id);
    await fetchCampaigns();
  };

  return { campaigns, isLoading, error, createCampaign, startCampaign, refetch: fetchCampaigns };
}
