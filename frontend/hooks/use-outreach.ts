"use client";
import { useCallback, useEffect, useState } from "react";
import { outreachApi } from "@/lib/api";
import { OutreachMessage } from "@/types";

export function useOutreach(params?: Record<string, unknown>) {
  const [messages, setMessages] = useState<OutreachMessage[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMessages = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await outreachApi.list({ limit: 100, ...params });
      setMessages(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch {
      setError("Failed to load outreach");
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  }, [JSON.stringify(params || {})]);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  const approve = async (id: string, approved: boolean) => {
    await outreachApi.approve(id, approved);
    await fetchMessages();
  };

  return { messages, total, isLoading, error, approve, refetch: fetchMessages };
}
