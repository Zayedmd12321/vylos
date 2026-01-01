"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Cookies from "js-cookie";

function AuthCallbackContent() {
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

export default function AuthCallback() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black flex items-center justify-center text-white">
        <div className="animate-pulse">Loading...</div>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  );
}