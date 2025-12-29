"use client";

import React, { useEffect, useRef } from "react";

type DottedGlowBackgroundProps = {
  className?: string;
  dotColor?: string;
  glowColor?: string;
  gap?: number;
  radius?: number;
  fadeMask?: boolean;
};

export const DottedGlowBackground = ({
  className,
  dotColor = "rgba(120, 120, 120, 0.2)", 
  glowColor = "rgba(255, 255, 255, 1)", 
  gap = 30,
  radius = 1.5,
  fadeMask = true,
}: DottedGlowBackgroundProps) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  
  const mouseRef = useRef({ 
    x: -1000, y: -1000, 
    curX: -1000, curY: -1000 
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let rafId: number;
    let dots: { x: number; y: number }[] = [];

    const init = () => {
      const { width, height } = container.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.scale(dpr, dpr);

      dots = [];
      const cols = Math.ceil(width / gap) + 1;
      const rows = Math.ceil(height / gap) + 1;

      for (let i = 0; i <= cols; i++) {
        for (let j = 0; j <= rows; j++) {
          dots.push({ x: i * gap, y: j * gap });
        }
      }
    };

    const animate = () => {
      const { width, height } = container.getBoundingClientRect();
      ctx.clearRect(0, 0, width, height);

      // Smooth Mouse Movement (Lerp)
      mouseRef.current.curX += (mouseRef.current.x - mouseRef.current.curX) * 0.15;
      mouseRef.current.curY += (mouseRef.current.y - mouseRef.current.curY) * 0.15;

      const mx = mouseRef.current.curX;
      const my = mouseRef.current.curY;
      
      const interactionRadius = 250;
      const radiusSq = interactionRadius * interactionRadius;

      // --- PASS 1: Batch Render Static Dots (Performance) ---
      ctx.beginPath();
      ctx.fillStyle = dotColor;

      const activeDots: {x: number, y: number, alpha: number, scale: number}[] = [];

      dots.forEach(dot => {
        const dx = dot.x - mx;
        const dy = dot.y - my;
        const distSq = dx * dx + dy * dy;
        
        let intensity = 0;
        
        // Mouse Interaction
        if (distSq < radiusSq) {
           const dist = Math.sqrt(distSq);
           const t = 1 - (dist / interactionRadius);
           intensity = t * t * (3 - 2 * t); // Smooth cubic easing
        }

        if (intensity > 0.05) {
            // Defer drawing active dots to Pass 2
            activeDots.push({
                x: dot.x,
                y: dot.y,
                alpha: intensity,
                scale: 1 + (intensity * 0.8)
            });
        } else {
            // Add to static batch
            ctx.moveTo(dot.x + radius, dot.y);
            ctx.arc(dot.x, dot.y, radius, 0, Math.PI * 2);
        }
      });

      // Draw all static dots in one call
      ctx.fill();

      // --- PASS 2: Render Glowing Dots ---
      activeDots.forEach(ad => {
        ctx.beginPath();
        ctx.fillStyle = glowColor;
        
        // Performance: Only blur if bright enough
        if (ad.alpha > 0.3) {
            ctx.shadowBlur = 12 * ad.alpha;
            ctx.shadowColor = glowColor;
        } else {
            ctx.shadowBlur = 0;
        }
        
        ctx.globalAlpha = ad.alpha;
        ctx.arc(ad.x, ad.y, radius * ad.scale, 0, Math.PI * 2);
        ctx.fill();
        
        // Reset context
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;
      });

      rafId = requestAnimationFrame(animate);
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseRef.current.x = e.clientX - rect.left;
      mouseRef.current.y = e.clientY - rect.top;
    };

    const handleResize = () => init();

    window.addEventListener("resize", handleResize);
    window.addEventListener("mousemove", handleMouseMove);
    init();
    animate();

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("mousemove", handleMouseMove);
      cancelAnimationFrame(rafId);
    };
  }, [dotColor, glowColor, gap, radius]);

  return (
    <div ref={containerRef} className={className} style={{ position: "fixed", inset: 0, zIndex: 0, pointerEvents: "none" }}>
      <canvas ref={canvasRef} style={{ display: "block" }} />
      {fadeMask && (
        <div style={{
            position: "absolute",
            inset: 0,
            background: "radial-gradient(circle at center, transparent 30%, #000 100%)",
            opacity: 0.6
        }} />
      )}
    </div>
  );
};