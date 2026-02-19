import React from 'react';
import { useTheme } from '../context/ThemeContext';

/**
 * Decorative header v2 — breathing lanterns with staggered phase,
 * golden Urdu calligraphy title with text-glow, a shimmer divider,
 * and a persistent dark/light mode toggle.
 */
const Lantern = ({ size = 45, ropeHeight = 60, delay = 0, duration = 4, xOffset = 0, glowId = "lGlow" }) => (
  <div
    className="absolute top-0 flex flex-col items-center animate-float origin-top"
    style={{
      left: xOffset ? `${xOffset}px` : undefined,
      right: xOffset ? undefined : undefined,
      animationDuration: `${duration}s`,
      animationDelay: `${delay}s`,
      // Ensure the container is tall enough so the lantern doesn't get clipped if we changed overflow settings
      height: `${ropeHeight + size + 20}px`
    }}
  >
    {/* Rope - gradient line */}
    <div
      className="w-0.5 bg-gradient-to-b from-gold/10 via-gold/60 to-gold/80"
      style={{ height: `${ropeHeight}px` }}
    />

    {/* Lantern SVG */}
    <div className="relative animate-breathe" style={{ animationDelay: `${delay * 0.5}s` }}>
      <svg width={size} height={size} viewBox="0 0 64 64" fill="none" className="drop-shadow-lantern">
        <path d="M28 6 Q32 2 36 6" stroke="#D4AF37" strokeWidth="2" fill="none" />
        <path d="M24 14 L40 14 L38 10 L26 10 Z" fill="#D4AF37" opacity="0.85" />
        <path d="M24 14 Q20 32 24 48 L40 48 Q44 32 40 14 Z" fill={`url(#${glowId})`} stroke="#D4AF37" strokeWidth="1" />
        <rect x="22" y="48" width="20" height="4" rx="1" fill="#D4AF37" opacity="0.85" />
        <ellipse cx="32" cy="32" rx="4" ry="7" fill="#FFF3CD" opacity="0.8" />
        <ellipse cx="32" cy="30" rx="2" ry="4" fill="#FFE08A" opacity="0.85" />
        <defs>
          <radialGradient id={glowId} cx="0.5" cy="0.4" r="0.6">
            <stop offset="0%" stopColor="rgba(255,200,80,0.35)" />
            <stop offset="100%" stopColor="rgba(120,60,20,0.1)" />
          </radialGradient>
        </defs>
      </svg>
    </div>
  </div>
);

const Header = () => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="relative z-10 flex-shrink-0 py-4 px-6 w-full overflow-hidden" dir="ltr" style={{ minHeight: '130px' }}>

      {/* Left Lantern Group */}
      <div className="absolute top-0 left-4 md:left-12 h-full w-40 pointer-events-none z-20">
        {/* Big Main Lantern */}
        <div className="absolute left-0">
          <Lantern size={50} ropeHeight={60} delay={0} duration={6} glowId="lg1" />
        </div>
        {/* Small Companion Lantern */}
        <div className="absolute left-16">
          <Lantern size={35} ropeHeight={30} delay={2} duration={5} glowId="lg2" />
        </div>
      </div>

      {/* Right Lantern Group */}
      <div className="absolute top-0 right-4 md:right-12 h-full w-40 pointer-events-none z-20">
        {/* Big Main Lantern */}
        <div className="absolute right-0">
          <Lantern size={50} ropeHeight={60} delay={1} duration={6.5} glowId="rg1" />
        </div>
        {/* Small Companion Lantern */}
        <div className="absolute right-16">
          <Lantern size={35} ropeHeight={35} delay={3} duration={5.5} glowId="rg2" />
        </div>
      </div>

      {/* Center Text Container - Absolute centered to ignore lanterns */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pt-8 pointer-events-none">
        <h1 className="urdu-text text-3xl md:text-5xl text-gold tracking-wide text-glow-gold select-none drop-shadow-md pb-8 text-center">
          قلم و خیال
        </h1>
        <p className={`text-[10px] md:text-xs font-sans tracking-[0.2em] uppercase mt-0 transition-colors duration-500 font-medium text-center
          ${isDark ? 'text-cream/60' : 'text-[#2D3748]/70'}`}>
          Urdu Children's Story Generator
        </p>
      </div>

      {/* Theme toggle — persistent moon/sun icon (Top Right Absolute) */}
      <button
        onClick={toggleTheme}
        className={`absolute right-4 top-4 p-2 rounded-xl z-50
        transition-all duration-300 hover:scale-110 active:scale-90
        ${isDark
            ? 'text-cream/40 hover:text-gold hover:bg-white/5'
            : 'text-[#1A1B2E]/40 hover:text-gold hover:bg-black/5'
          }`}
        aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        title={isDark ? 'Light mode' : 'Dark mode'}
      >
        {isDark ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M13 3a9 9 0 1 1 0 18 7 7 0 1 0 0-18z" />
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <circle cx="12" cy="12" r="4.5" fill="currentColor" stroke="none" />
            <line x1="12" y1="1.5" x2="12" y2="4" />
            <line x1="12" y1="20" x2="12" y2="22.5" />
            <line x1="4.22" y1="4.22" x2="5.88" y2="5.88" />
            <line x1="18.12" y1="18.12" x2="19.78" y2="19.78" />
            <line x1="1.5" y1="12" x2="4" y2="12" />
            <line x1="20" y1="12" x2="22.5" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.88" y2="18.12" />
            <line x1="18.12" y1="5.88" x2="19.78" y2="4.22" />
          </svg>
        )}
      </button>

      {/* Bottom ornamental line with shimmer */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-64 h-px bg-gradient-to-r from-transparent via-gold/30 to-transparent shimmer-gold" />
    </header>
  );
};

export default Header;
