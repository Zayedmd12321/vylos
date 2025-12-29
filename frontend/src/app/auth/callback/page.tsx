"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Cookies from "js-cookie";

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      Cookies.set("token", token, { expires: 7 }); // Save for 7 days
      router.push("/dashboard");
    } else {
      router.push("/login?error=oauth_failed");
    }
  }, [router, searchParams]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center text-white">
      <div className="animate-pulse">Authenticating...</div>
    </div>
  );
}