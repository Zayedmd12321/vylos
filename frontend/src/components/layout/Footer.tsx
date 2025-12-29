"use client";

import React from "react";
import { Terminal } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="py-12 border-t border-white/10 bg-black relative z-10">
      <div className="max-w-7xl mx-auto px-6 flex flex-col items-center">
        <div className="mb-8 flex items-center gap-2 opacity-80 hover:opacity-100 transition-opacity">
          <div className="w-6 h-6 bg-white rounded flex items-center justify-center">
            <Terminal className="w-3 h-3 text-black" />
          </div>
          <span className="font-bold text-lg text-white">Vylos</span>
        </div>
        <div className="flex flex-col items-center gap-4">
            <div className="flex gap-6 text-xs text-zinc-500">
                <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
                <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
                <a href="#" className="hover:text-white transition-colors">Status</a>
            </div>
            <p className="text-zinc-700 text-xs">
            © {new Date().getFullYear()} Vylos Inc. All systems operational.
            </p>
        </div>
      </div>
    </footer>
  );
};