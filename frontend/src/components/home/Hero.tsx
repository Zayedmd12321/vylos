"use client";
import React, { useState, useEffect } from "react";
import { Github, Play, Terminal, Lock } from "lucide-react";

export const Hero = () => {
  const [activeTab, setActiveTab] = useState("terminal");

  return (
    <section className="relative z-10 pt-40 pb-20 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
        
        {/* Release Badge */}
        <div className="group relative rounded-full p-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent mb-8">
            <div className="relative rounded-full bg-black/80 backdrop-blur-sm px-4 py-1.5 flex items-center gap-2 border border-white/10 hover:border-white/20 transition-colors cursor-default">
                 <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-xs font-mono text-zinc-300">
                    System Status: Operational
                </span>
            </div>
        </div>

        {/* Headline */}
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-8 relative z-20 bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-white/40 leading-tight">
           The Infrastructure <br/>
           <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
             You Don't Manage.
           </span>
        </h1>
        
        <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto mb-12 leading-relaxed">
          A serverless runtime built to understand how code becomes infrastructure. 
          From localhost to global edge in milliseconds.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full max-w-md relative z-20">
           <button className="h-12 px-8 rounded-full bg-white text-black font-bold hover:bg-zinc-200 transition-colors flex items-center gap-2">
             <Github className="w-4 h-4" />
             View Source
           </button>
           <button className="h-12 px-8 rounded-full border border-white/10 text-white font-medium hover:bg-white/5 transition-colors flex items-center gap-2">
             <Play className="w-4 h-4 text-emerald-400" />
             See Architecture
           </button>
        </div>

        {/* Terminal / Monitor Preview */}
        <div className="mt-24 w-full max-w-4xl relative group perspective-1000">
          <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/20 via-cyan-500/20 to-blue-500/20 rounded-2xl blur-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-1000" />
          
          <div className="relative bg-[#050505] rounded-xl border border-white/10 shadow-2xl overflow-hidden ring-1 ring-white/5 text-left">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-white/[0.02]">
              <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                  <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
              </div>
              <div className="text-[10px] text-zinc-500 font-mono">vylos-kernel — zsh — 80x24</div>
            </div>
            
            {/* Code Content */}
            <div className="p-6 font-mono text-xs md:text-sm text-zinc-400 h-[300px] overflow-hidden flex flex-col justify-end">
                <div className="space-y-2">
                    <div className="flex gap-2"><span className="text-emerald-500">➜</span> <span>~ git push vylos main</span></div>
                    <div className="text-zinc-500">remote: Resolving deltas: 100% (12/12)...</div>
                    <div className="text-zinc-300">remote: [Build Service] Detected Next.js app</div>
                    <div>remote: <span className="text-blue-400">info</span>  Creating Docker container...</div>
                    <div>remote: <span className="text-blue-400">info</span>  Pushing to registry (us-east-1)</div>
                    <div>remote: <span className="text-blue-400">info</span>  Configuring Nginx reverse proxy...</div>
                    <div>remote: <span className="text-emerald-400">success</span> Deployment complete!</div>
                    <div className="pt-2 text-white">
                        <span className="text-emerald-500">➜</span> <a href="#" className="underline decoration-zinc-700 underline-offset-4 hover:text-emerald-400 hover:decoration-emerald-400 transition-all">https://project-alpha.vylos.app</a>
                    </div>
                    <div className="animate-pulse w-2 h-4 bg-zinc-500 inline-block align-middle" />
                </div>
            </div>
          </div>
        </div>
      </section>
  );
};