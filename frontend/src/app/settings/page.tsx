"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import api from "@/lib/api";
import { User, Mail, Github, Lock, Trash2, Save } from "lucide-react";
import { DottedGlowBackground } from "@/components/ui/DottedGlowBackground";
import { Navbar } from "@/components/layout/Navbar";

interface UserData {
  id: number;
  email: string;
  username?: string;
  full_name?: string;
  avatar_url?: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const token = Cookies.get("token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthenticated(true);
      fetchUserData();
      setIsLoading(false);
    }
  }, [router]);

  const fetchUserData = async () => {
    try {
      const { data } = await api.get("/me");
      setUserData(data);
    } catch (error) {
      console.error("Failed to fetch user data:", error);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Placeholder for save functionality
    setTimeout(() => {
      setIsSaving(false);
      alert("Settings saved!");
    }, 1000);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-black text-white">
      <DottedGlowBackground dotColor="rgba(100, 100, 100, 0.15)" glowColor="rgba(100, 100, 255, 0.4)" />
      
      <Navbar />

      <main className="relative z-10 pt-28 px-6 max-w-4xl mx-auto pb-20">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-400 mb-3">
            Settings
          </h1>
          <p className="text-zinc-500">Manage your account settings and preferences.</p>
        </div>

        <div className="space-y-6">
          {/* Profile Section */}
          <div className="p-6 rounded-xl border border-white/8 bg-zinc-900/50 backdrop-blur-sm">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <User size={20} className="text-indigo-400" />
              Profile Information
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">Full Name</label>
                <input
                  type="text"
                  value={userData?.full_name || ""}
                  onChange={(e) => setUserData(prev => prev ? {...prev, full_name: e.target.value} : null)}
                  className="w-full px-4 py-3 rounded-lg bg-black/50 border border-white/10 text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500 transition-colors"
                  placeholder="Enter your full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-300 mb-2">Username</label>
                <input
                  type="text"
                  value={userData?.username || ""}
                  onChange={(e) => setUserData(prev => prev ? {...prev, username: e.target.value} : null)}
                  className="w-full px-4 py-3 rounded-lg bg-black/50 border border-white/10 text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500 transition-colors"
                  placeholder="Enter your username"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                  <Mail size={16} />
                  Email Address
                </label>
                <input
                  type="email"
                  value={userData?.email || ""}
                  disabled
                  className="w-full px-4 py-3 rounded-lg bg-black/30 border border-white/10 text-zinc-500 cursor-not-allowed"
                />
                <p className="text-xs text-zinc-500 mt-1.5">Email cannot be changed</p>
              </div>
            </div>

            <button
              onClick={handleSave}
              disabled={isSaving}
              className="mt-6 flex items-center gap-2 px-5 py-2.5 rounded-lg bg-indigo-500 text-white font-medium hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save size={16} />
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
          </div>

          {/* Connected Accounts */}
          <div className="p-6 rounded-xl border border-white/8 bg-zinc-900/50 backdrop-blur-sm">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Github size={20} className="text-indigo-400" />
              Connected Accounts
            </h2>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center p-4 rounded-lg bg-black/30 border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center">
                    <Github size={20} />
                  </div>
                  <div>
                    <p className="font-medium">GitHub</p>
                    <p className="text-sm text-zinc-500">Connected</p>
                  </div>
                </div>
                <button className="text-sm text-red-400 hover:text-red-300">
                  Disconnect
                </button>
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="p-6 rounded-xl border border-red-500/30 bg-red-500/10 backdrop-blur-sm">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-red-400">
              <Trash2 size={20} />
              Danger Zone
            </h2>
            <p className="text-sm text-zinc-400 mb-4">
              Once you delete your account, there is no going back. Please be certain.
            </p>
            <button className="px-4 py-2 rounded-lg bg-red-500/20 border border-red-500/30 text-red-400 font-medium hover:bg-red-500/30 transition-colors">
              Delete Account
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
