"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { ProgressBar } from "@/components/ui/progress-bar";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { toast } from "@/components/ui/toast";
import { useCampaigns } from "@/hooks/use-campaigns";
import { cn } from "@/lib/utils";

const statusStyles: Record<string, string> = {
  running: "bg-emerald-500/15 text-emerald-400",
  draft: "bg-slate-500/15 text-slate-400",
  completed: "bg-indigo-500/15 text-indigo-400",
  paused: "bg-amber-500/15 text-amber-400",
};

export default function CampaignsPage() {
  return (
    <Suspense fallback={<AppShell><p className="text-slate-500">Loading…</p></AppShell>}>
      <CampaignsPageInner />
    </Suspense>
  );
}

function CampaignsPageInner() {
  const searchParams = useSearchParams();
  const { campaigns, isLoading, error, createCampaign, startCampaign, refetch } = useCampaigns();
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [form, setForm] = useState({
    name: "",
    target_country: "United States",
    target_state: "Texas",
    target_city: "",
    max_results_per_category: 100,
    categories: ["Dentists"] as string[],
    services: ["Website Redesign"] as string[],
  });

  useEffect(() => {
    if (searchParams.get("create") === "true") setIsModalOpen(true);
  }, [searchParams]);

  const filtered = campaigns.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = async () => {
    if (!form.name.trim() || !form.target_city.trim() || !form.categories.length || !form.services.length) {
      toast("Please fill all required fields", "warning");
      return;
    }
    setIsSaving(true);
    try {
      await createCampaign({
        name: form.name.trim(),
        target_country: form.target_country,
        target_state: form.target_state,
        target_city: form.target_city.trim(),
        target_categories: form.categories,
        services: form.services,
        max_results_per_category: Number(form.max_results_per_category) || 100,
      });
      setIsModalOpen(false);
      toast("Campaign created!");
    } catch (err: any) {
      toast(err?.response?.data?.detail || "Failed to create campaign", "error");
    } finally {
      setIsSaving(false);
    }
  };

  const handleStart = async (id: string) => {
    try {
      await startCampaign(id);
      toast("Campaign started");
    } catch (err: any) {
      toast(err?.response?.data?.detail || "Failed to start campaign", "error");
    }
  };

  return (
    <AppShell>
      <PageHeader
        title="Campaigns"
        subtitle="Manage your lead generation campaigns"
        actions={
          <>
            <SearchInput value={search} onChange={setSearch} placeholder="Search campaigns..." className="w-64" />
            <Button onClick={() => setIsModalOpen(true)}>+ New Campaign</Button>
          </>
        }
      />

      {error && (
        <div className="mb-4 text-sm text-red-400">
          {error}{" "}
          <button className="underline" onClick={() => refetch()}>Retry</button>
        </div>
      )}

      {isLoading ? (
        <p className="text-slate-500">Loading campaigns…</p>
      ) : filtered.length === 0 ? (
        <p className="text-slate-500">No campaigns yet. Create your first one.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((campaign) => (
            <div key={campaign.id} className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 hover:border-indigo-500/50 transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-bold text-slate-100">{campaign.name}</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    {campaign.target_city}, {campaign.target_state} • {(campaign.target_categories || []).join(", ")}
                  </p>
                </div>
                <span className={cn("px-3 py-1 rounded-full text-xs font-bold", statusStyles[campaign.status] || statusStyles.draft)}>
                  {campaign.status}
                </span>
              </div>
              <ProgressBar value={campaign.progress_percent || 0} showLabel className="mb-5" />
              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-800">
                <div className="text-center"><p className="text-xl font-extrabold text-slate-100">{campaign.businesses_found}</p><p className="text-[11px] text-slate-500 uppercase font-semibold mt-1">Found</p></div>
                <div className="text-center"><p className="text-xl font-extrabold text-slate-100">{campaign.leads_qualified}</p><p className="text-[11px] text-slate-500 uppercase font-semibold mt-1">Qualified</p></div>
                <div className="text-center"><p className="text-xl font-extrabold text-slate-100">{campaign.outreach_sent}</p><p className="text-[11px] text-slate-500 uppercase font-semibold mt-1">Outreach</p></div>
              </div>
              {campaign.status === "draft" && (
                <Button className="w-full mt-4 justify-center" size="sm" onClick={() => handleStart(campaign.id)}>Start Campaign</Button>
              )}
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Campaign"
        footer={
          <>
            <Button variant="ghost" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button onClick={handleCreate} isLoading={isSaving}>Create Campaign</Button>
          </>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Campaign Name</label>
            <Input placeholder="e.g. Texas Healthcare Blitz" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Country</label>
              <Select value={form.target_country} onChange={(value) => setForm({ ...form, target_country: value })} options={[{ value: "United States", label: "United States" }, { value: "Canada", label: "Canada" }]} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">State</label>
              <Select value={form.target_state} onChange={(value) => setForm({ ...form, target_state: value })} options={[{ value: "Texas", label: "Texas" }, { value: "California", label: "California" }]} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">City</label>
              <Input placeholder="e.g. Houston" value={form.target_city} onChange={(e) => setForm({ ...form, target_city: e.target.value })} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Max Results</label>
              <Input type="number" value={form.max_results_per_category} onChange={(e) => setForm({ ...form, max_results_per_category: Number(e.target.value) })} />
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Categories</label>
            <TagInput tags={form.categories} onChange={(categories) => setForm({ ...form, categories })} />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Services</label>
            <TagInput tags={form.services} onChange={(services) => setForm({ ...form, services })} />
          </div>
        </div>
      </Modal>
    </AppShell>
  );
}

function TagInput({ tags, onChange }: { tags: string[]; onChange: (tags: string[]) => void }) {
  const [input, setInput] = useState("");
  const addTag = () => {
    if (input.trim() && !tags.includes(input.trim())) {
      onChange([...tags, input.trim()]);
      setInput("");
    }
  };
  return (
    <div className="flex flex-wrap gap-2 p-2.5 bg-slate-900 border border-slate-700 rounded-lg min-h-[46px]">
      {tags.map((tag) => (
        <span key={tag} className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-400">
          {tag}
          <button onClick={() => onChange(tags.filter((t) => t !== tag))} className="hover:text-indigo-300">×</button>
        </span>
      ))}
      <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addTag())} placeholder={tags.length ? "" : "+ Add"} className="bg-transparent border-none outline-none text-slate-300 text-sm flex-1 min-w-[80px]" />
    </div>
  );
}
