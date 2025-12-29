"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

// --- Layout Components ---
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

// --- UI Components ---
import { DottedGlowBackground } from "@/components/ui/DottedGlowBackground";

// --- Feature Components ---
import { Hero } from "@/components/home/Hero";
import { TechStackArchitecture } from "@/components/home/TechStackArchitecture";
import { FeaturesGrid } from "@/components/home/FeaturesGrid";

export default function Home() {
  const router = useRouter();

  // ⚡ Automatic Redirect if Logged In
  useEffect(() => {
    const token = Cookies.get("token");
    if (token) {
      router.push("/dashboard");
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-emerald-500/30 overflow-x-hidden relative">

      {/* --- BACKGROUND LAYERS --- */}
      <DottedGlowBackground 
           dotColor="rgba(70, 70, 70, 0.5)"       
           glowColor="rgba(255, 255, 255, 0.9)"   
           gap={40}                               
      />

      <Navbar />

      <main className="relative z-10">
        <Hero />
        <TechStackArchitecture />
        <FeaturesGrid />
      </main>

      <Footer />
    </div>
  );
}