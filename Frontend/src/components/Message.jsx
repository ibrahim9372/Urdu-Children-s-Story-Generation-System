
import React, { useEffect, useState } from 'react';
import { Bot, User } from 'lucide-react';

const Message = ({ text, sender, isTyping }) => {
    const isBot = sender === 'bot';
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setIsVisible(true), 50);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div className={`
      group w-full text-gray-100 border-b border-[#222]
      ${isBot ? 'bg-[#0a0a0a]' : 'bg-[#000000]'}
      transition-opacity duration-500 ease-out
      ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}
    `}>
            <div className="text-base gap-4 md:gap-6 md:max-w-2xl lg:max-w-[38rem] xl:max-w-3xl flex lg:px-0 m-auto w-full py-[1.5rem] px-4">

                {/* Avatar */}
                <div className={`
          flex-shrink-0 w-[30px] h-[30px] rounded-sm flex items-center justify-center
          ${isBot ? 'bg-[#FF0033]' : 'bg-[#222222]'}
          shadow-[0_0_10px_rgba(255,0,51,0.2)]
        `}>
                    {isBot ? <Bot size={20} className="text-black" /> : <User size={20} className="text-white" />}
                </div>

                {/* Content */}
                <div className="relative flex-1 overflow-hidden">
                    {isTyping ? (
                        <div className="flex gap-1 items-center h-6">
                            <span className="w-2 h-2 bg-[#FF0033] rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="w-2 h-2 bg-[#FF0033] rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="w-2 h-2 bg-[#FF0033] rounded-full animate-bounce"></span>
                        </div>
                    ) : (
                        <div className="prose prose-invert max-w-none">
                            <p className={`urdu-text text-[1.1rem] leading-[2.2] whitespace-pre-wrap ${!isBot ? 'text-gray-100' : 'text-gray-300'}`} dir="rtl">
                                {text}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Message;
