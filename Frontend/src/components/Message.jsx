import React, { useEffect, useState, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';

/* ====================================================================
 * Message bubble v2 — Moonlit Palace (چاندنی محل)
 *
 *   Bot:   glass-morphism lavender-silver panel, crescent-moon avatar
 *   User:  warm amber glass panel, gold-star avatar
 *   Error: red-tinted glass variant
 *
 * Features:
 *   • Directional entrance animations (slide-in-bot / slide-in-user)
 *   • Typing indicator (3 bouncing gold dots) while waiting for first token
 *   • Completion celebration glow when streaming finishes
 *   • Inline 5-star rating for completed bot stories
 *   • Hover glow & corner ornaments
 * ==================================================================== */

/* ---------- Mini star-rating component ---------- */
const StarRating = () => {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [hasRated, setHasRated] = useState(false);
  const { isDark } = useTheme();

  const handleRate = (star) => {
    setRating(star);
    setHasRated(true);
  };

  return (
    <div className="flex items-center gap-0.5 mt-3 pt-2 border-t border-gold/8" dir="ltr">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => handleRate(star)}
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(0)}
          className="p-0.5 transition-all duration-200 hover:scale-125 active:scale-90 focus:outline-none"
          aria-label={`Rate ${star} stars`}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            className={`transition-all duration-300 ${star <= (hover || rating)
              ? 'fill-gold drop-shadow-golden'
              : isDark ? 'fill-cream/15' : 'fill-[#1A1B2E]/15'
              } ${star <= rating && hasRated ? 'animate-star-pop' : ''}`}
            style={{ animationDelay: `${star * 0.06}s` }}
          >
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </button>
      ))}
      {hasRated && (
        <span className="text-[10px] text-gold/50 ml-2 animate-fade-in font-sans select-none">
          شکریہ ✦
        </span>
      )}
    </div>
  );
};

/* ---------- Typing indicator (three bouncing dots) ---------- */
const TypingIndicator = () => {
  const { isDark } = useTheme();
  return (
    <div className="flex items-center gap-2 py-3 px-1" dir="rtl">
      <div className="flex gap-1.5 items-end">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 rounded-full bg-gradient-to-t from-gold/70 to-gold-light/70 animate-typing-dot"
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
      </div>
      <span className={`urdu-text text-sm mr-2 select-none ${isDark ? 'text-cream/30' : 'text-[#1A1B2E]/30'}`}>
        جادوئی قلم لکھ رہا ہے
      </span>
    </div>
  );
};

/* ---------- Main Message component ---------- */
const Message = ({ text, sender, isStreaming = false, isError = false }) => {
  const { isDark } = useTheme();
  const isBot = sender === 'bot';
  const [visible, setVisible] = useState(false);
  const [justCompleted, setJustCompleted] = useState(false);
  const prevStreaming = useRef(isStreaming);

  // Entrance delay
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 50);
    return () => clearTimeout(t);
  }, []);

  // Completion celebration — brief golden glow when streaming ends
  useEffect(() => {
    if (prevStreaming.current && !isStreaming && text) {
      setJustCompleted(true);
      const timer = setTimeout(() => setJustCompleted(false), 1800);
      return () => clearTimeout(timer);
    }
    prevStreaming.current = isStreaming;
  }, [isStreaming, text]);

  // Show typing dots when streaming just started (no text yet)
  const showTyping = isBot && isStreaming && !text;

  return (
    <div
      dir="ltr"
      className={`
        w-full flex mb-6
        ${visible
          ? isBot ? 'animate-slide-in-bot' : 'animate-slide-in-user'
          : 'opacity-0'}
        ${isBot ? 'justify-start' : 'justify-end'}
      `}
    >
      {/* Bot avatar — crescent moon */}
      {isBot && (
        <div className="flex-shrink-0 mt-1 mr-3">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500/50 to-indigo-700/60
            flex items-center justify-center border border-lavender/25 shadow-[0_0_14px_rgba(139,130,220,0.15)]
            transition-all duration-300 hover:border-lavender/40 hover:scale-105 hover:shadow-[0_0_20px_rgba(139,130,220,0.25)]">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path d="M13 3a9 9 0 1 1 0 18 7 7 0 1 0 0-18z" fill="#F0EEF8" opacity="1" />
              <circle cx="17" cy="7" r="1.2" fill="#FFFAE6" opacity="0.9" />
            </svg>
          </div>
        </div>
      )}

      {/* Bubble */}
      <div
        className={`
          relative max-w-[85%] sm:max-w-[75%] rounded-2xl px-5 py-4
          transition-all duration-500
          ${isBot
            ? isError
              ? 'glass-error text-red-200/90'
              : `glass-bot ${isDark ? 'text-moonbeam/90' : 'text-[#2A2A3E]'}`
            : `glass-user ${isDark ? 'text-cream/95' : 'text-[#1A1B2E]'}`
          }
          ${justCompleted ? 'animate-completion-glow' : ''}
        `}
      >
        {/* Corner ornaments — bot */}
        {isBot && !isError && (
          <>
            <div className="absolute top-2 left-2 w-4 h-4 border-t border-l border-lavender/12 rounded-tl-md
              transition-colors duration-500 group-hover:border-lavender/25" />
            <div className="absolute bottom-2 right-2 w-4 h-4 border-b border-r border-lavender/12 rounded-br-md
              transition-colors duration-500 group-hover:border-lavender/25" />
          </>
        )}

        {/* Corner ornaments — user */}
        {!isBot && (
          <>
            <div className="absolute top-2 right-2 w-4 h-4 border-t border-r border-gold/15 rounded-tr-md" />
            <div className="absolute bottom-2 left-2 w-4 h-4 border-b border-l border-gold/15 rounded-bl-md" />
          </>
        )}

        {/* Typing indicator */}
        {showTyping && <TypingIndicator />}

        {/* Message text */}
        {text && (
          <p
            className="urdu-text text-[1.1rem] leading-[3.5] whitespace-pre-wrap break-words"
            dir="rtl"
          >
            {text}
            {/* Streaming quill cursor */}
            {isStreaming && (
              <span className="inline-block w-0.5 h-5 bg-gold/80 ml-1 align-middle animate-quill-blink rounded-full" />
            )}
          </p>
        )}

        {/* Star rating — appears after bot finishes streaming */}
        {isBot && !isStreaming && text && !isError && <StarRating />}
      </div>

      {/* User avatar — glowing star */}
      {!isBot && (
        <div className="flex-shrink-0 mt-1 ml-3">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-amber-600/55 to-amber-800/55
            flex items-center justify-center border border-gold/30 shadow-[0_0_14px_rgba(212,175,55,0.15)]
            transition-all duration-300 hover:border-gold/50 hover:scale-105 hover:shadow-[0_0_20px_rgba(212,175,55,0.25)]">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2l2.4 4.8 5.3.8-3.85 3.75.9 5.25L12 14.1l-4.75 2.5.9-5.25L4.3 7.6l5.3-.8L12 2z"
                fill="#D4AF37" opacity="0.95" />
            </svg>
          </div>
        </div>
      )}
    </div>
  );
};

export default Message;
