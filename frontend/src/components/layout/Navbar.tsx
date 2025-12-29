"use client";

import React from "react";
import Link from "next/link";
import { Terminal } from "lucide-react";

export const Navbar = () => {
  return (
    <nav className="fixed top-0 w-full z-50 border-b border-white/[0.08] bg-black/50 backdrop-blur-xl transition-all duration-300">
      <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
        
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group cursor-pointer select-none">
          <div className="relative w-8 h-8 flex items-center justify-center bg-zinc-900 border border-white/10 rounded-lg group-hover:border-emerald-500/50 transition-colors duration-300">
            <Terminal className="w-4 h-4 text-white group-hover:text-emerald-400 transition-colors" />
          </div>
          <span className="font-bold text-xl tracking-tight text-white/90">Vylos</span>
        </Link>

        {/* Navigation Actions */}
        <div className="flex items-center gap-6">
          <Link 
            href="/docs" 
            className="hidden md:block text-sm text-zinc-400 hover:text-white transition-colors"
          >
            Documentation
          </Link>
          
          <div className="flex items-center gap-3">
             <Link 
                href="/login"
                className="text-sm font-medium text-white hover:text-emerald-400 transition-colors px-3 py-2"
             >
                Sign In
             </Link>
             <Link
                href="/signup"
                className="px-5 py-2 text-sm font-medium text-black bg-white rounded-full hover:bg-zinc-200 transition-all"
             >
                Get Started
             </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};