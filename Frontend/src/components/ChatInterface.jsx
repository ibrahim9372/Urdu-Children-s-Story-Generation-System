import React, { useState, useRef, useEffect, useCallback } from 'react';
import Message from './Message';
import InputArea from './InputArea';
import { generateTextStream } from '../utils/api';
import { useTheme } from '../context/ThemeContext';

// ---------------------------------------------------------------------------
// Monotonic ID generator (fixes 5A-03)
// ---------------------------------------------------------------------------
let _nextId = 1;
const uid = () => _nextId++;

// Card accent characters — culturally appropriate
const cardAccents = ['✦', '☽', '◆', '✧'];

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const { isDark, toggleTheme } = useTheme();
  const messagesEndRef = useRef(null);
  // track the id of the currently-streaming bot message
  const streamMsgId = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // -----------------------------------------------------------------------
  // Send & stream
  // -----------------------------------------------------------------------
  const handleSendMessage = async (text) => {
    // 1. Append user message
    const userMsg = {
      id: uid(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsGenerating(true);

    // 2. Create a placeholder bot message for streaming
    const botId = uid();
    streamMsgId.current = botId;
    const botMsg = {
      id: botId,
      text: '',
      sender: 'bot',
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages((prev) => [...prev, botMsg]);

    try {
      // 3. Stream tokens in via SSE (fixes 5A-04)
      await generateTextStream(text, (token) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === botId ? { ...m, text: m.text + token } : m
          )
        );
      });

      // 4. Mark streaming complete
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botId ? { ...m, isStreaming: false } : m
        )
      );
    } catch (error) {
      // 5A-02: show error to user in Urdu
      console.error('Generation error:', error);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botId
            ? {
              ...m,
              text: 'معذرت، کہانی بنانے میں دقت آگئی۔ براہ کرم دوبارہ کوشش کریں۔',
              isStreaming: false,
              isError: true,
            }
            : m
        )
      );
    } finally {
      setIsGenerating(false);
      streamMsgId.current = null;
    }
  };

  // -----------------------------------------------------------------------
  // Example prompts
  // -----------------------------------------------------------------------
  const examplePrompts = [
    { urdu: 'ایک دفعہ کا ذکر ہے کہ ایک بادشاہ', label: 'بادشاہ کی کہانی' },
    { urdu: 'جنگل میں ایک شیر اور چوہا', label: 'شیر اور چوہا' },
    { urdu: 'ایک چھوٹی سی بچی تھی جس کا نام', label: 'بچی کی کہانی' },
    { urdu: 'پرانے زمانے میں ایک دانا بوڑھا', label: 'بوڑھے کی حکمت' },
  ];

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------
  return (
    <div className="flex flex-col h-full w-full max-w-4xl mx-auto relative">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto w-full custom-scrollbar pb-36 pt-6 px-4">

        {/* Welcome screen */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 pt-0 animate-fade-in relative z-10">

            <div className="space-y-6">
              <h2 className={`urdu-text text-5xl md:text-6xl font-bold tracking-wide animate-slide-up select-none
                ${isDark ? 'text-gold text-glow-gold' : 'text-[#B8860B] drop-shadow-md'}`}>
                باغِ کہانیاں
              </h2>
              <p className={`urdu-text text-xl animate-slide-up-delay max-w-lg mx-auto font-medium
                ${isDark ? 'text-cream/60' : 'text-[#2D3748]/80'}`}>
                اپنی کہانی شروع کریں — جادوئی الفاظ لکھیں اور دیکھیں کہانی کیسے بنتی ہے
              </p>
            </div>

            {/* Example prompt cards — enhanced glass tiles */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full max-w-3xl px-6 animate-slide-up-delay-2">
              {examplePrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(p.urdu)}
                  className={`
                    group relative p-4 rounded-2xl glass-card text-right
                    transition-all duration-500 overflow-hidden
                    hover:shadow-[0_12px_40px_rgba(212,175,55,0.15)]
                    hover:-translate-y-1
                    active:scale-[0.98] active:translate-y-0
                    border border-transparent
                  `}
                  style={{ animationDelay: `${idx * 0.15}s` }}
                >
                  {/* Decorative corner accent */}
                  <div className={`absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-gold/10 to-transparent rounded-bl-3xl transition-opacity duration-500
                    ${isDark ? 'opacity-30 group-hover:opacity-50' : 'opacity-10 group-hover:opacity-20'}`} />

                  {/* Shimmer overlay on hover */}
                  <div className="absolute inset-0 shimmer-gold rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />

                  <span className={`urdu-text text-xl font-medium block mb-1 relative z-10 transition-colors duration-300
                    ${isDark ? 'text-cream/90 group-hover:text-gold' : 'text-[#2D3748] group-hover:text-[#B8860B]'}`}>
                    {p.urdu}
                  </span>

                  <div className="flex items-center justify-end gap-2 relative z-10">
                    <span className={`text-[10px] uppercase tracking-wider font-sans font-semibold transition-colors duration-300
                      ${isDark ? 'text-gold/60 group-hover:text-gold' : 'text-[#B8860B]/60 group-hover:text-[#B8860B]'}`}>
                      {p.label}
                    </span>
                    <span className={`text-xs transition-colors duration-300
                      ${isDark ? 'text-gold/60 group-hover:text-gold' : 'text-[#B8860B]/60 group-hover:text-[#B8860B]'}`}>
                      {cardAccents[idx]}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message list */}
        {messages.map((msg) => (
          <Message
            key={msg.id}
            text={msg.text}
            sender={msg.sender}
            isStreaming={msg.isStreaming}
            isError={msg.isError}
          />
        ))}

        <div ref={messagesEndRef} className="h-0" />
      </div>

      {/* Input area */}
      <div className="w-full max-w-4xl mx-auto">
        <InputArea onSendMessage={handleSendMessage} disabled={isGenerating} />
      </div>
    </div>
  );
};

export default ChatInterface;
