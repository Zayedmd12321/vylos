"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { DottedGlowBackground } from "@/components/ui/DottedGlowBackground";
import { Navbar } from "@/components/layout/Navbar";

export default function DashboardPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = Cookies.get("token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthenticated(true);
    }
  }, [router]);

  const handleLogout = () => {
      Cookies.remove("token");
      router.push("/");
  };

  if (!isAuthenticated) return null; // Or a loading spinner

  return (
    <div className="min-h-screen bg-black text-white relative">
      <DottedGlowBackground dotColor="rgba(100, 100, 100, 0.2)" glowColor="rgba(255, 255, 255, 1)" />
      
      {/* Reusing navbar but ideally you want a DashboardNavbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.08] bg-black/50 backdrop-blur-xl">
         <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
             <span className="font-bold text-xl">Vylos Dashboard</span>
             <button onClick={handleLogout} className="text-sm text-red-400 hover:text-red-300">Log Out</button>
         </div>
      </nav>

      <main className="relative z-10 pt-32 px-6 max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Welcome to your Dashboard</h1>
        <p className="text-zinc-400">You are successfully authenticated. Your projects will appear here.</p>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl border border-white/10 bg-zinc-900/30">
                <h2 className="font-bold mb-2">Create New Project</h2>
                <p className="text-sm text-zinc-500">Import from GitHub or start a template.</p>
            </div>
        </div>
      </main>
    </div>
  );
}