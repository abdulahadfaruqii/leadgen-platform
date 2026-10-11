"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/toast";
import { useAuth } from "@/hooks/use-auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, register } = useAuth(false);
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
        toast("Welcome back!");
      } else {
        await register(email, password, fullName);
        toast("Account created successfully!");
      }
      router.push("/");
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      toast(typeof detail === "string" ? detail : "Authentication failed", "error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f1117] relative overflow-hidden">
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />

      <div className="relative z-10 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 mx-auto rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg shadow-indigo-500/30 mb-4">
            LG
          </div>
          <h1 className="text-2xl font-bold text-slate-100">{isLogin ? "Welcome back" : "Get started"}</h1>
          <p className="text-sm text-slate-500 mt-2">
            {isLogin ? "Sign in to your LeadGen AI account" : "Create your LeadGen AI account"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-slate-900/80 border border-slate-800 rounded-xl p-8 space-y-5">
          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Full Name</label>
              <Input value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="John Doe" required={!isLogin} />
            </div>
          )}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Email</label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" required />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Password</label>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required minLength={8} />
          </div>
          <Button type="submit" className="w-full justify-center" isLoading={isLoading}>
            {isLogin ? "Sign In" : "Create Account"}
          </Button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <button onClick={() => setIsLogin(!isLogin)} className="text-indigo-400 hover:text-indigo-300 font-semibold">
            {isLogin ? "Sign up" : "Sign in"}
          </button>
        </p>
        <p className="text-center text-xs text-slate-600 mt-3">Demo: admin@leadgen.ai / admin12345</p>
      </div>
    </div>
  );
}
