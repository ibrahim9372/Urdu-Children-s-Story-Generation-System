import React, { useEffect, useRef } from 'react';

/**
 * Animated star field canvas v2 — renders:
 *   • Multi-layered twinkling stars (near / mid / far) with colour variety
 *   • Soft nebula colour patches for atmospheric depth
 *   • Shooting stars with glow trails
 *   • A softly glowing crescent moon
 *
 * Performance: debounced resize, mobile star-count reduction,
 * GPU-friendly compositing, requestAnimationFrame loop.
 */
const StarField = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let animId;
    let stars = [];
    let shootingStars = [];
    let nebulae = [];

    const isMobile = () => window.innerWidth < 768;

    /* ---- Initialisation ---- */
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initStars();
      initNebulae();
    };

    const initStars = () => {
      const density = isMobile() ? 5500 : 3000;
      const count = Math.floor((canvas.width * canvas.height) / density);
      stars = Array.from({ length: count }, () => {
        const layer = Math.random(); // 0→far, 1→near
        return {
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          r: (Math.random() * 1.2 + 0.2) * (layer < 0.3 ? 0.5 : layer < 0.7 ? 0.8 : 1.3),
          alpha: Math.random(),
          dAlpha: (Math.random() - 0.5) * (layer < 0.3 ? 0.004 : 0.01),
          layer,
          // Colour variety: white-blue (common), warm-gold, cool-lavender
          hue: Math.random() > 0.85 ? 45 : Math.random() > 0.7 ? 260 : 220,
        };
      });
    };

    const initNebulae = () => {
      nebulae = [
        { x: canvas.width * 0.78, y: canvas.height * 0.22, r: canvas.width * 0.18, color: [80, 50, 140] },
        { x: canvas.width * 0.18, y: canvas.height * 0.68, r: canvas.width * 0.14, color: [40, 60, 130] },
        { x: canvas.width * 0.52, y: canvas.height * 0.88, r: canvas.width * 0.22, color: [55, 35, 100] },
        { x: canvas.width * 0.38, y: canvas.height * 0.12, r: canvas.width * 0.10, color: [45, 50, 110] },
      ];
    };

    /* ---- Spawners ---- */
    const spawnShootingStar = () => {
      if (shootingStars.length > 2) return;
      shootingStars.push({
        x: Math.random() * canvas.width * 0.7 + canvas.width * 0.1,
        y: Math.random() * canvas.height * 0.35,
        len: Math.random() * 100 + 50,
        speed: Math.random() * 5 + 3,
        angle: Math.PI / 4 + (Math.random() - 0.5) * 0.4,
        alpha: 1,
        width: Math.random() * 1.5 + 0.8,
      });
    };

    /* ---- Draw helpers ---- */
    const drawNebulae = () => {
      for (const n of nebulae) {
        const grad = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r);
        const [r, g, b] = n.color;
        grad.addColorStop(0, `rgba(${r},${g},${b},0.04)`);
        grad.addColorStop(0.5, `rgba(${r},${g},${b},0.018)`);
        grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    const drawMoon = () => {
      const mx = canvas.width * 0.12;
      const my = canvas.height * 0.12;
      const mr = Math.min(canvas.width, canvas.height) * 0.04;

      // Multi-layered glow
      const outerGlow = ctx.createRadialGradient(mx, my, mr * 0.5, mx, my, mr * 6);
      outerGlow.addColorStop(0, 'rgba(255,223,130,0.1)');
      outerGlow.addColorStop(0.3, 'rgba(255,200,100,0.04)');
      outerGlow.addColorStop(0.6, 'rgba(200,180,150,0.015)');
      outerGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = outerGlow;
      ctx.beginPath();
      ctx.arc(mx, my, mr * 6, 0, Math.PI * 2);
      ctx.fill();

      // Crescent body
      ctx.save();
      ctx.beginPath();
      ctx.arc(mx, my, mr, 0, Math.PI * 2);
      ctx.fillStyle = '#FFF8DC';
      ctx.shadowColor = 'rgba(255,223,130,0.7)';
      ctx.shadowBlur = 25;
      ctx.fill();
      ctx.globalCompositeOperation = 'destination-out';
      ctx.beginPath();
      ctx.arc(mx + mr * 0.5, my - mr * 0.15, mr * 0.82, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalCompositeOperation = 'source-over';
      ctx.restore();
    };

    /* ---- Main draw loop ---- */
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Nebulae (deepest layer)
      drawNebulae();

      // 2. Stars — layered rendering
      for (const s of stars) {
        s.alpha += s.dAlpha;
        if (s.alpha > 1 || s.alpha < 0.08) s.dAlpha = -s.dAlpha;
        s.alpha = Math.max(0.06, Math.min(1, s.alpha));

        const brightness = s.layer < 0.3 ? 0.35 : s.layer < 0.7 ? 0.6 : 1;
        const alpha = s.alpha * brightness;

        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        if (s.hue === 45)       ctx.fillStyle = `rgba(255,215,100,${alpha * 0.85})`;
        else if (s.hue === 260) ctx.fillStyle = `rgba(180,170,230,${alpha * 0.7})`;
        else                    ctx.fillStyle = `rgba(210,220,255,${alpha * 0.7})`;
        ctx.fill();

        // Bright/near stars get a halo glow
        if (s.r > 1.3 && alpha > 0.55) {
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r * 3, 0, Math.PI * 2);
          ctx.fillStyle = s.hue === 45
            ? `rgba(255,215,100,${alpha * 0.06})`
            : `rgba(200,210,255,${alpha * 0.04})`;
          ctx.fill();
        }
      }

      // 3. Shooting stars with glow
      for (let i = shootingStars.length - 1; i >= 0; i--) {
        const ss = shootingStars[i];
        const ex = ss.x + Math.cos(ss.angle) * ss.len;
        const ey = ss.y + Math.sin(ss.angle) * ss.len;

        ctx.save();
        ctx.shadowColor = 'rgba(255,255,255,0.4)';
        ctx.shadowBlur = 6;
        const grad = ctx.createLinearGradient(ss.x, ss.y, ex, ey);
        grad.addColorStop(0, `rgba(255,250,230,${ss.alpha})`);
        grad.addColorStop(0.4, `rgba(255,255,255,${ss.alpha * 0.5})`);
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.strokeStyle = grad;
        ctx.lineWidth = ss.width;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(ss.x, ss.y);
        ctx.lineTo(ex, ey);
        ctx.stroke();
        ctx.restore();

        // Head glow
        ctx.beginPath();
        ctx.arc(ss.x, ss.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,250,230,${ss.alpha})`;
        ctx.fill();

        ss.x += Math.cos(ss.angle) * ss.speed;
        ss.y += Math.sin(ss.angle) * ss.speed;
        ss.alpha -= 0.01;
        if (ss.alpha <= 0 || ss.x > canvas.width || ss.y > canvas.height) {
          shootingStars.splice(i, 1);
        }
      }

      // 4. Moon (top layer)
      drawMoon();

      animId = requestAnimationFrame(draw);
    };

    /* ---- Bootstrap ---- */
    resize();
    let resizeTimer;
    const debouncedResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 150);
    };
    window.addEventListener('resize', debouncedResize);
    draw();

    const shootInterval = setInterval(() => {
      if (Math.random() > 0.35) spawnShootingStar();
    }, 4000);

    return () => {
      cancelAnimationFrame(animId);
      clearInterval(shootInterval);
      clearTimeout(resizeTimer);
      window.removeEventListener('resize', debouncedResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="starfield-canvas fixed inset-0 pointer-events-none z-0 transition-opacity duration-700"
      aria-hidden="true"
    />
  );
};

export default StarField;
