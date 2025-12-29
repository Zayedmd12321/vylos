"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Github, Chrome, Terminal, ArrowRight, Mail, Lock } from "lucide-react";
import Cookies from "js-cookie";
import { DottedGlowBackground } from "@/components/ui/DottedGlowBackground";
import api, { loginWithProvider } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({ email: "", password: "" });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.type]: e.target.value });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const { data } = await api.post("/login", formData);
      // Save Token
      Cookies.set("token", data.access_token, { expires: 7 });
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center relative overflow-hidden font-sans selection:bg-emerald-500/30">
      <DottedGlowBackground dotColor="rgba(100, 100, 100, 0.2)" glowColor="rgba(255, 255, 255, 1)" />

      <div className="w-full max-w-md p-8 relative z-10 bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-white/5 border border-white/10 mb-4">
            <Terminal className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight mb-2">Welcome back</h1>
          <p className="text-zinc-400 text-sm">Enter your credentials to access your terminal.</p>
        </div>

        {/* OAuth Buttons */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <SocialButton onClick={() => loginWithProvider("github")} icon={<Github className="w-4 h-4" />} label="GitHub" />
          <SocialButton onClick={() => loginWithProvider("google")} icon={<Chrome className="w-4 h-4" />} label="Google" />
        </div>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-white/10" /></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-black px-2 text-zinc-500">Or continue with</span></div>
        </div>

        {/* Error Message */}
        {error && <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-xs text-center">{error}</div>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-zinc-300 ml-1">Email</label>
            <div className="relative group">
               <Mail className="absolute left-3 top-3 w-4 h-4 text-zinc-500 group-focus-within:text-white transition-colors" />
               <input type="email" value={formData.email} onChange={handleChange} placeholder="name@example.com" className="w-full bg-zinc-900/50 border border-white/10 rounded-lg px-10 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all" required />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center ml-1">
                <label className="text-xs font-medium text-zinc-300">Password</label>
                <Link href="#" className="text-xs text-emerald-400 hover:text-emerald-300">Forgot?</Link>
            </div>
            <div className="relative group">
               <Lock className="absolute left-3 top-3 w-4 h-4 text-zinc-500 group-focus-within:text-white transition-colors" />
               <input type="password" value={formData.password} onChange={handleChange} placeholder="••••••••" className="w-full bg-zinc-900/50 border border-white/10 rounded-lg px-10 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all" required />
            </div>
          </div>

          <button type="submit" disabled={loading} className="w-full bg-white text-black font-semibold rounded-lg py-2.5 text-sm hover:bg-zinc-200 transition-all flex items-center justify-center gap-2 disabled:opacity-70 mt-2">
            {loading ? <Spinner /> : <><span>Sign In</span><ArrowRight className="w-4 h-4" /></>}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-zinc-500">
          Don't have an account? <Link href="/signup" className="text-white hover:underline">Sign up</Link>
        </div>
      </div>
    </div>
  );
}

function SocialButton({ icon, label, onClick }: any) {
    return <button type="button" onClick={onClick} className="flex items-center justify-center gap-2 bg-zinc-900/50 hover:bg-zinc-800 border border-white/10 rounded-lg py-2.5 text-sm font-medium text-zinc-200 transition-all">{icon}{label}</button>
}
function Spinner() { return <div className="w-4 h-4 border-2 border-zinc-400 border-t-zinc-900 rounded-full animate-spin" /> }