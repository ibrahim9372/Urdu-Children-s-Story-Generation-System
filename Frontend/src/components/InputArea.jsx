import React, { useState, useRef, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';

/**
 * Input area v2 — "magical scrying pool" style.
 *
 * Features:
 *   • Glass-morphism input container
 *   • Pulsing golden glow when focused
 *   • Shimmer overlay on focus
 *   • Four decorative corner ornaments that brighten on focus
 *   • Gradient send button with hover scale & glow
 *   • RTL Urdu text, auto-resize, Enter-to-submit
 */
const InputArea = ({ onSendMessage, disabled }) => {
  const { isDark } = useTheme();
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 180) + 'px';
    }
  }, [input]);

  const canSend = input.trim() && !disabled;
  const isActive = isFocused || input;

  return (
    <div className={`absolute bottom-0 left-0 w-full bg-gradient-to-t from-transparent via-transparent to-transparent pt-6 pb-6 px-4 z-20 transition-colors duration-500
      ${isDark ? 'from-palace-night via-palace-night/95' : 'from-[#FFFDF5] via-[#FFFDF5]/95'}`}>
      <div className="md:max-w-2xl lg:max-w-[38rem] xl:max-w-3xl mx-auto w-full relative">
        <form
          onSubmit={handleSubmit}
          className={`
            relative flex items-end gap-2
            glass-input rounded-2xl overflow-hidden
            transition-all duration-500
            ${isActive
              ? 'border border-gold/30 shadow-[0_0_30px_rgba(212,175,55,0.1)] ring-1 ring-gold/15'
              : 'border border-indigo-700/20 shadow-[0_4px_20px_rgba(0,0,0,0.2)] hover:border-indigo-600/30'}
            ${isFocused ? 'animate-glow-pulse' : ''}
          `}
        >
          {/* Four decorative corner ornaments */}
          <div className={`absolute top-2 left-2 w-5 h-5 border-t border-l rounded-tl-md pointer-events-none transition-all duration-500
            ${isActive ? 'border-gold/25' : 'border-gold/8'}`} />
          <div className={`absolute bottom-2 right-2 w-5 h-5 border-b border-r rounded-br-md pointer-events-none transition-all duration-500
            ${isActive ? 'border-gold/25' : 'border-gold/8'}`} />
          <div className={`absolute top-2 right-2 w-5 h-5 border-t border-r rounded-tr-md pointer-events-none transition-all duration-500
            ${isActive ? 'border-gold/15' : 'border-gold/4'}`} />
          <div className={`absolute bottom-2 left-2 w-5 h-5 border-b border-l rounded-bl-md pointer-events-none transition-all duration-500
            ${isActive ? 'border-gold/15' : 'border-gold/4'}`} />

          {/* Shimmer overlay on focus */}
          {isFocused && (
            <div className="absolute inset-0 shimmer-gold rounded-2xl pointer-events-none" />
          )}

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="یہاں اپنی کہانی کا آغاز لکھیں ..."
            className={`
              w-full max-h-[180px] py-3 pl-14 pr-4 md:py-3 md:pl-16 md:pr-6
              bg-transparent border-0 outline-none
              urdu-text resize-none m-0 leading-[2.2]
              relative z-10
              ${isDark ? 'text-cream/90 placeholder-cream/20' : 'text-[#1A1B2E]/90 placeholder-[#1A1B2E]/20'}
            `}
            dir="rtl"
            rows={1}
            disabled={disabled}
            style={{ minHeight: '48px' }}
          />

          {/* Send button — golden gradient with glow */}
          <button
            type="submit"
            disabled={!canSend}
            className={`
              absolute left-3 bottom-3 p-2.5 rounded-xl z-10
              transition-all duration-400 flex items-center justify-center
              ${canSend
                ? 'bg-gradient-to-br from-gold to-gold-dim text-palace-night hover:from-gold-light hover:to-gold shadow-[0_0_20px_rgba(212,175,55,0.25)] scale-100 hover:scale-110 active:scale-90 hover:shadow-[0_0_30px_rgba(212,175,55,0.4)]'
                : 'bg-indigo-800/25 text-cream/15 cursor-not-allowed scale-90'}
            `}
            aria-label="Send"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </form>

        <div className={`text-center text-[10px] mt-3 font-sans tracking-[0.25em] uppercase select-none transition-colors duration-500
          ${isDark ? 'text-cream/15' : 'text-[#1A1B2E]/15'}`}>
          چاندنی محل <span className="text-gold/25 mx-1">✦</span> Trigram Language Model
        </div>
      </div>
    </div>
  );
};

export default InputArea;
