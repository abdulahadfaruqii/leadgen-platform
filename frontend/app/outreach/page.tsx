"use client";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { toast } from "@/components/ui/toast";
import { useOutreach } from "@/hooks/use-outreach";
import { cn } from "@/lib/utils";

const channelColors: Record<string, string> = {
  email: "bg-indigo-500/15 text-indigo-400",
  linkedin: "bg-cyan-500/15 text-cyan-400",
  facebook: "bg-blue-500/15 text-blue-400",
  instagram: "bg-pink-500/15 text-pink-400",
  contact_form: "bg-amber-500/15 text-amber-400",
};

export default function OutreachPage() {
  const [channelFilter, setChannelFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const apiParams = useMemo(
    () => ({
      limit: 100,
      ...(channelFilter ? { channel: channelFilter } : {}),
      ...(statusFilter ? { status: statusFilter } : {}),
    }),
    [channelFilter, statusFilter]
  );
  const { messages, isLoading, error, approve, refetch } = useOutreach(apiParams);

  const handleApprove = async (id: string, approved: boolean) => {
    try {
      await approve(id, approved);
      toast(approved ? "Message approved" : "Message rejected");
    } catch (err: any) {
      toast(err?.response?.data?.detail || "Action failed", "error");
    }
  };

  return (
    <AppShell>
      <PageHeader
        title="Outreach"
        subtitle="Manage and approve outreach messages"
        actions={
          <>
            <Select
              value={channelFilter}
              onChange={setChannelFilter}
              placeholder="All Channels"
              options={[
                { value: "email", label: "Email" },
                { value: "linkedin", label: "LinkedIn" },
                { value: "facebook", label: "Facebook" },
                { value: "contact_form", label: "Contact Form" },
              ]}
            />
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              placeholder="All Status"
              options={[
                { value: "draft", label: "Pending Approval" },
                { value: "approved", label: "Approved" },
                { value: "sent", label: "Sent" },
                { value: "opened", label: "Opened" },
                { value: "replied", label: "Replied" },
              ]}
            />
            <Button variant="ghost" onClick={() => refetch()}>
              Refresh
            </Button>
          </>
        }
      />

      {error && <p className="text-sm text-red-400 mb-4">{error}</p>}

      {isLoading ? (
        <p className="text-slate-500">Loading outreach…</p>
      ) : messages.length === 0 ? (
        <p className="text-slate-500">No outreach messages yet.</p>
      ) : (
        <div className="space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className={cn("px-3 py-1 rounded-md text-xs font-bold", channelColors[msg.channel] || "bg-slate-500/15 text-slate-400")}>
                    {msg.channel}
                  </span>
                  <span className="text-sm text-slate-500">Business: {msg.business_id.slice(0, 8)}…</span>
                  <span className="text-xs text-slate-600">#{msg.sequence_position}</span>
                </div>
                <span
                  className={cn(
                    "px-3 py-1 rounded-md text-xs font-bold",
                    msg.requires_approval ? "bg-amber-500/15 text-amber-400" : "bg-emerald-500/15 text-emerald-400"
                  )}
                >
                  {msg.requires_approval ? "Pending Approval" : msg.status}
                </span>
              </div>

              {msg.subject && <p className="font-semibold text-slate-200 mb-2">{msg.subject}</p>}
              <p className="text-sm text-slate-400 leading-relaxed">{msg.body}</p>

              <div className="flex items-center gap-3 mt-5">
                {msg.requires_approval ? (
                  <>
                    <Button size="sm" onClick={() => handleApprove(msg.id, true)}>
                      Approve & Send
                    </Button>
                    <Button variant="ghost" size="sm" className="text-red-400 hover:text-red-300" onClick={() => handleApprove(msg.id, false)}>
                      Reject
                    </Button>
                  </>
                ) : (
                  <span className="text-xs text-slate-500">
                    {msg.approved_at ? `Approved on ${new Date(msg.approved_at).toLocaleDateString()}` : `Status: ${msg.status}`}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
