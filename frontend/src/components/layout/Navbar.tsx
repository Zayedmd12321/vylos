"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { Terminal, LogOut } from "lucide-react";

export const Navbar = () => {
  const pathname = usePathname();
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isMounting, setIsMounting] = useState(true);

  // Check authentication status whenever the route changes
  useEffect(() => {
    const token = Cookies.get("token");
    setIsAuthenticated(!!token);
    setIsMounting(false);
  }, [pathname]);

  const handleLogout = () => {
    Cookies.remove("token");
    setIsAuthenticated(false);
    router.push("/");
    router.refresh();
  };

  return (
    <nav className="fixed top-0 w-full z-50 border-b border-white/[0.08] bg-black/50 backdrop-blur-xl transition-all duration-300">
      <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
        
        {/* Logo - Always links to Home */}
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
          
          {!isMounting && (
            <div className="flex items-center gap-4">
              {isAuthenticated ? (
                <>
                   {/* Logged In View */}
                   <Link 
                      href="/dashboard"
                      className={`text-sm font-medium transition-colors ${pathname.includes('/dashboard') ? 'text-white' : 'text-zinc-400 hover:text-white'}`}
                   >
                      Dashboard
                   </Link>
                   
                   <div className="h-4 w-[1px] bg-zinc-800 hidden sm:block"></div>

                   <button
                      onClick={handleLogout}
                      className="group flex items-center gap-2 text-sm font-medium text-zinc-400 hover:text-red-400 transition-colors"
                   >
                      <LogOut size={15} />
                      <span className="hidden sm:inline">Sign Out</span>
                   </button>
                </>
              ) : (
                <>
                   {/* Guest View */}
                   <Link 
                      href="/login"
                      className="text-sm font-medium text-white hover:text-emerald-400 transition-colors px-2"
                   >
                      Sign In
                   </Link>
                   <Link
                      href="/signup"
                      className="px-5 py-2 text-sm font-medium text-black bg-white rounded-full hover:bg-zinc-200 transition-all"
                   >
                      Get Started
                   </Link>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};