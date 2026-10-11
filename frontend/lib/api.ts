import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (
      err.response?.status === 401 &&
      typeof window !== "undefined" &&
      !window.location.pathname.startsWith("/login")
    ) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const campaignsApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get("/campaigns", { params }),
  get: (id: string) => api.get(`/campaigns/${id}`),
  create: (data: unknown) => api.post("/campaigns", data),
  update: (id: string, data: unknown) => api.patch(`/campaigns/${id}`, data),
  delete: (id: string) => api.delete(`/campaigns/${id}`),
  start: (id: string) => api.post(`/campaigns/${id}/start`),
};

export const businessesApi = {
  list: (params?: unknown) => api.get("/businesses", { params }),
  get: (id: string) => api.get(`/businesses/${id}`),
  update: (id: string, data: unknown) => api.patch(`/businesses/${id}`, data),
};

export const leadsApi = {
  list: (params?: unknown) => api.get("/leads", { params }),
  get: (id: string) => api.get(`/leads/${id}`),
  update: (id: string, data: unknown) => api.patch(`/leads/${id}`, data),
};

export const outreachApi = {
  list: (params?: unknown) => api.get("/outreach", { params }),
  get: (id: string) => api.get(`/outreach/${id}`),
  update: (id: string, data: unknown) => api.patch(`/outreach/${id}`, data),
  approve: (id: string, approved: boolean) =>
    api.post(`/outreach/${id}/approve`, { approved }),
};

export const analyticsApi = {
  dashboard: () => api.get("/analytics/dashboard"),
  campaign: (id: string) => api.get(`/analytics/campaigns/${id}`),
};

export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),
};
