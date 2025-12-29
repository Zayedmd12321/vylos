"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Github, Chrome, Terminal, ArrowLeft, Mail, User, Lock, Fingerprint } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Cookies from "js-cookie";
import { DottedGlowBackground } from "@/components/ui/DottedGlowBackground";
import api, { loginWithProvider } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [isEmailMode, setIsEmailMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [formData, setFormData] = useState({
    full_name: "", username: "", email: "", password: "", confirmPassword: ""
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    if (formData.password !== formData.confirmPassword) {
        setError("Passwords do not match");
        setLoading(false);
        return;
    }

    try {
        // Exclude confirmPassword before sending
        const { confirmPassword, ...payload } = formData;
        const { data } = await api.post("/signup", payload);
        
        Cookies.set("token", data.access_token, { expires: 7 });
        router.push("/dashboard");
    } catch (err: any) {
        // Handle validation errors from backend
        if (err.response?.status === 422) {
             setError("Password must be 6-60 chars or invalid email.");
        } else {
             setError(err.response?.data?.detail || "Signup failed");
        }
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center relative overflow-hidden font-sans selection:bg-emerald-500/30">
      <DottedGlowBackground dotColor="rgba(100, 100, 100, 0.2)" glowColor="rgba(255, 255, 255, 1)" />

      <div className="w-full max-w-md relative z-10">
        <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden">
          <div className="p-8">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-white/5 border border-white/10 mb-4">
                <Terminal className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight mb-2">Create your account</h1>
              <p className="text-zinc-400 text-sm">Deploy your first project in seconds.</p>
            </div>

            {error && <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-xs text-center">{error}</div>}

            <AnimatePresence mode="wait">
              {!isEmailMode ? (
                <motion.div key="socials" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-4">
                  <button onClick={() => loginWithProvider("github")} className="w-full flex items-center justify-center gap-2 bg-white text-black font-semibold rounded-lg py-2.5 text-sm hover:bg-zinc-200 transition-all"><Github className="w-4 h-4" /> Continue with GitHub</button>
                  <button onClick={() => loginWithProvider("google")} className="w-full flex items-center justify-center gap-2 bg-zinc-900 border border-white/10 rounded-lg py-2.5 text-sm font-medium hover:bg-zinc-800 transition-all"><Chrome className="w-4 h-4" /> Continue with Google</button>
                  <div className="relative py-2"><div className="absolute inset-0 flex items-center"><span className="w-full border-t border-white/10" /></div><div className="relative flex justify-center text-xs uppercase"><span className="bg-black px-2 text-zinc-500">Or</span></div></div>
                  <button onClick={() => setIsEmailMode(true)} className="w-full flex items-center justify-center gap-2 bg-transparent border border-white/10 hover:border-white/30 rounded-lg py-2.5 text-sm font-medium text-zinc-300 transition-all"><Mail className="w-4 h-4" /> Continue with Email</button>
                </motion.div>
              ) : (
                <motion.form key="email-form" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                      <InputGroup name="full_name" value={formData.full_name} onChange={handleChange} label="Full Name" icon={<User />} placeholder="John Doe" />
                      <InputGroup name="username" value={formData.username} onChange={handleChange} label="Username" icon={<Fingerprint />} placeholder="johnd" />
                  </div>
                  <InputGroup name="email" value={formData.email} onChange={handleChange} label="Email" icon={<Mail />} type="email" placeholder="name@example.com" />
                  <InputGroup name="password" value={formData.password} onChange={handleChange} label="Password" icon={<Lock />} type="password" placeholder="Create a password" />
                  <InputGroup name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} label="Confirm Password" icon={<Lock />} type="password" placeholder="Confirm password" />

                  <button type="submit" disabled={loading} className="w-full bg-white text-black font-semibold rounded-lg py-2.5 text-sm hover:bg-zinc-200 transition-all mt-4">
                    {loading ? "Creating Account..." : "Sign Up"}
                  </button>
                  <button type="button" onClick={() => setIsEmailMode(false)} className="w-full text-zinc-500 text-xs hover:text-white flex items-center justify-center gap-1 py-2 transition-colors"><ArrowLeft className="w-3 h-3" /> Back to options</button>
                </motion.form>
              )}
            </AnimatePresence>
          </div>
          <div className="bg-zinc-900/30 border-t border-white/5 p-4 text-center">
             <p className="text-xs text-zinc-500">Already have an account? <Link href="/login" className="text-emerald-400 hover:underline">Log in</Link></p>
          </div>
        </div>
      </div>
    </div>
  );
}

function InputGroup({ label, icon, type = "text", placeholder, name, value, onChange }: any) {
    return (
        <div className="space-y-1.5">
            <label className="text-xs font-medium text-zinc-400 ml-1">{label}</label>
            <div className="relative group">
                <div className="absolute left-3 top-2.5 w-4 h-4 text-zinc-500 group-focus-within:text-white transition-colors">{React.cloneElement(icon, { size: 16 })}</div>
                <input name={name} value={value} onChange={onChange} type={type} placeholder={placeholder} className="w-full bg-zinc-900/50 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-all" required />
            </div>
        </div>
    )
}