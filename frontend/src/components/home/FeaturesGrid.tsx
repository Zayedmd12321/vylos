"use client";
import React, { useRef, useState } from "react";
import { Box, Zap, Shield, GitBranch, Globe, Lock } from "lucide-react";

export const FeaturesGrid = () => {
  return (
    <section className="py-32 relative z-10 max-w-7xl mx-auto px-6">
        <div className="mb-16">
           <h2 className="text-3xl md:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-600">
             Production Ready.<br />
             By Default.
           </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-6 lg:grid-cols-12 gap-4">
            <SpotlightCard className="md:col-span-3 lg:col-span-4 min-h-[250px]">
                <Box className="w-10 h-10 text-blue-400 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Auto-Dockerization</h3>
                <p className="text-zinc-400 text-sm">We analyze your package.json and generate an optimized Dockerfile instantly.</p>
            </SpotlightCard>

            <SpotlightCard className="md:col-span-3 lg:col-span-4 min-h-[250px]">
                <Zap className="w-10 h-10 text-amber-400 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Global Edge</h3>
                <p className="text-zinc-400 text-sm">Static assets cached at the edge. Dynamic compute routed via high-performance mesh.</p>
            </SpotlightCard>

            <SpotlightCard className="md:col-span-6 lg:col-span-4 min-h-[250px]">
                <Shield className="w-10 h-10 text-emerald-400 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Zero Trust & SSL</h3>
                <p className="text-zinc-400 text-sm">Automatic Let's Encrypt certificates provisioned for every domain and subdomain.</p>
            </SpotlightCard>

             <SpotlightCard className="md:col-span-6 lg:col-span-8 bg-zinc-900/50">
                <div className="flex flex-col md:flex-row items-center gap-8 h-full">
                    <div className="flex-1">
                        <GitBranch className="w-10 h-10 text-indigo-400 mb-4" />
                        <h3 className="text-xl font-bold text-white mb-2">Git Push to Deploy</h3>
                        <p className="text-zinc-400 text-sm max-w-md">
                           Connect your repository once. Every push to <code className="bg-zinc-800 px-1 py-0.5 rounded text-indigo-300">main</code> triggers a pipeline.
                        </p>
                    </div>
                </div>
            </SpotlightCard>

            <SpotlightCard className="md:col-span-6 lg:col-span-4 flex flex-col justify-center">
                 <Globe className="w-10 h-10 text-purple-400 mb-4" />
                 <h3 className="text-xl font-bold text-white mb-2">Custom Domains</h3>
                 <p className="text-zinc-400 text-sm">Map any domain instantly. CNAME verification handles the ownership check.</p>
            </SpotlightCard>
        </div>
    </section>
  );
};

// Utility for the card hover effect
function SpotlightCard({ children, className = "" }: { children: React.ReactNode, className?: string }) {
    const divRef = useRef<HTMLDivElement>(null);
    const [position, setPosition] = useState({ x: 0, y: 0 });
  
    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
      if (!divRef.current) return;
      const rect = divRef.current.getBoundingClientRect();
      setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    };
  
    return (
      <div
        ref={divRef}
        onMouseMove={handleMouseMove}
        className={`relative rounded-xl border border-white/10 bg-zinc-950 overflow-hidden group ${className}`}
      >
        <div
          className="pointer-events-none absolute -inset-px opacity-0 transition duration-300 group-hover:opacity-100"
          style={{ background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(255,255,255,0.06), transparent 40%)` }}
        />
        <div className="relative h-full p-8 z-10 flex flex-col">{children}</div>
      </div>
    );
}