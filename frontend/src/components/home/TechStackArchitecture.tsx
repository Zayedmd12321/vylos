"use client";

import React from "react";
import { 
  Github, Database, Box, HardDrive, Network, Cpu 
} from "lucide-react";

export const TechStackArchitecture = () => {
  return (
    <section className="relative py-24 bg-[#020202] border-t border-white/5 overflow-hidden">
      
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-emerald-500/5 blur-[100px] rounded-full pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-6 z-10">
        
        {/* Section Header */}
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/10 backdrop-blur-md mb-6 border border-emerald-500/20">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span className="text-emerald-400 text-xs font-mono font-medium tracking-wide uppercase">
              System Internals
            </span>
          </div>
          <h2 className="text-3xl md:text-5xl font-bold mb-6 tracking-tight text-white">
            Engineered with <span className="text-emerald-400">Giants</span>
          </h2>
          <p className="text-zinc-400 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
            We orchestrate the best-in-class open source technologies into a seamless, vertically integrated deployment engine.
          </p>
        </div>

        {/* --- THE BLUEPRINT DIAGRAM --- */}
        <div className="relative w-full">
            
            {/* Desktop: Connection Line Layer */}
            <div className="hidden md:block absolute top-[60px] left-0 w-full h-[2px] z-0">
                {/* Static Line */}
                <div className="absolute inset-x-12 top-0 h-full bg-zinc-800/50" />
                {/* Animated Beam */}
                <div className="absolute inset-x-12 top-0 h-full bg-gradient-to-r from-transparent via-emerald-500 to-transparent w-1/3 animate-shimmer-fast opacity-100" />
            </div>

            {/* Nodes Container */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-8 md:gap-4 relative z-10">
                
                <StackNode 
                    step="01"
                    title="Source"
                    tech="GitHub"
                    desc="Webhooks trigger instant builds."
                    icon={<Github className="w-6 h-6" />}
                    color="white"
                />

                <StackNode 
                    step="02"
                    title="Queue"
                    tech="Redis"
                    desc="High-throughput task buffer."
                    icon={<Database className="w-6 h-6" />}
                    color="red"
                />

                <StackNode 
                    step="03"
                    title="Runtime"
                    tech="Docker"
                    desc="Ephemeral build containers."
                    icon={<Box className="w-6 h-6" />}
                    color="blue"
                    isActive // Highlight the core tech
                />

                <StackNode 
                    step="04"
                    title="Storage"
                    tech="AWS S3"
                    desc="Persistent asset hosting."
                    icon={<HardDrive className="w-6 h-6" />}
                    color="yellow"
                />

                <StackNode 
                    step="05"
                    title="Edge"
                    tech="Nginx"
                    desc="Reverse proxy & routing."
                    icon={<Network className="w-6 h-6" />}
                    color="green"
                />

            </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes shimmer-fast {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(400%); }
        }
        .animate-shimmer-fast {
          animation: shimmer-fast 4s linear infinite;
        }
      `}</style>
    </section>
  );
};

// --- Sub-Component for a Single Tech Node ---

interface StackNodeProps {
    step: string;
    title: string;
    tech: string;
    desc: string;
    icon: React.ReactNode;
    color: "white" | "red" | "blue" | "yellow" | "green";
    isActive?: boolean;
}

const StackNode = ({ step, title, tech, desc, icon, color, isActive }: StackNodeProps) => {
    
    // Color mapping
    const colorStyles = {
        white: "text-zinc-200 group-hover:text-white bg-zinc-900 border-zinc-800 group-hover:border-zinc-600",
        red: "text-red-400 group-hover:text-red-300 bg-red-950/10 border-red-900/50 group-hover:border-red-500/50",
        blue: "text-blue-400 group-hover:text-blue-300 bg-blue-950/10 border-blue-900/50 group-hover:border-blue-500/50",
        yellow: "text-amber-400 group-hover:text-amber-300 bg-amber-950/10 border-amber-900/50 group-hover:border-amber-500/50",
        green: "text-emerald-400 group-hover:text-emerald-300 bg-emerald-950/10 border-emerald-900/50 group-hover:border-emerald-500/50",
    };

    const selectedStyle = colorStyles[color];

    return (
        <div className={`relative group flex flex-col items-center text-center p-6 pt-10 rounded-2xl border transition-all duration-300 bg-[#050505] z-10 
          ${isActive ? 'shadow-[0_0_30px_-10px_rgba(16,185,129,0.2)] border-emerald-500/30' : 'border-white/5 hover:border-white/10 hover:bg-[#0A0A0A]'}
        `}>
            {/* Step Number Bubble */}
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[#020202] px-2">
                <div className={`w-8 h-8 rounded-full border flex items-center justify-center text-[10px] font-mono font-bold ${isActive ? 'border-emerald-500 text-emerald-500' : 'border-zinc-800 text-zinc-600'}`}>
                    {step}
                </div>
            </div>

            {/* Icon Circle */}
            <div className={`w-14 h-14 rounded-full border flex items-center justify-center mb-5 transition-colors duration-300 ${selectedStyle}`}>
                {icon}
            </div>

            <h3 className="text-lg font-bold text-white mb-1">{tech}</h3>
            <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider mb-3">{title}</div>
            <p className="text-xs text-zinc-400 leading-relaxed max-w-[140px] mx-auto">
                {desc}
            </p>
        </div>
    )
}