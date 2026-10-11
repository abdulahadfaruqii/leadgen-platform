"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { User } from "@/types";

export function useAuth(requireAuth = true) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem("user");
      }
    }

    if (!token) {
      setIsAuthenticated(false);
      setIsLoading(false);
      if (requireAuth) router.push("/login");
      return;
    }

    setIsAuthenticated(true);
    setIsLoading(false);
  }, [router, requireAuth]);

  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    localStorage.setItem("access_token", res.data.access_token);
    if (res.data.refresh_token) {
      localStorage.setItem("refresh_token", res.data.refresh_token);
    }
    const basicUser = {
      id: "me",
      email,
      full_name: email.split("@")[0],
      subscription_tier: "enterprise",
      monthly_lead_quota: 5000,
      monthly_leads_used: 0,
    } as User;
    localStorage.setItem("user", JSON.stringify(basicUser));
    setUser(basicUser);
    setIsAuthenticated(true);
    return res.data;
  };

  const register = async (email: string, password: string, full_name: string) => {
    await authApi.register({ email, password, full_name });
    return login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setUser(null);
    setIsAuthenticated(false);
    router.push("/login");
  };

  return { isAuthenticated, isLoading, user, login, register, logout };
}
