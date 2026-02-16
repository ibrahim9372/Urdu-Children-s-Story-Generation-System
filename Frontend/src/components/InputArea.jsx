
import React, { useState, useRef, useEffect } from 'react';
import { SendHorizontal } from 'lucide-react';

const InputArea = ({ onSendMessage, disabled }) => {
    const [input, setInput] = useState('');
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

    // Auto-resize
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
        }
    }, [input]);

    return (
        <div className="
      absolute bottom-0 left-0 w-full 
      bg-gradient-to-t from-[#000000] via-[#000000] to-transparent
      pt-24 pb-8 px-4
    ">
            <div className="md:max-w-2xl lg:max-w-[38rem] xl:max-w-3xl mx-auto w-full relative">
                <form
                    onSubmit={handleSubmit}
                    className={`
            relative flex items-end gap-2 
            bg-[#111111] border border-[#333]
            rounded-xl overflow-hidden 
            transition-all duration-300
            ${input ? 'ring-1 ring-[#FF0033] shadow-[0_0_15px_rgba(255,0,51,0.15)] border-[#FF0033]' : 'shadow-lg hover:border-[#555]'}
          `}
                >
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="یہاں لکھیں ... (Type your Urdu prompt here)"
                        className="
              w-full max-h-[200px] py-[14px] pl-4 pr-12 md:py-[16px] md:pl-6 
              bg-transparent border-0 outline-none 
              text-white placeholder-gray-500 
              urdu-text resize-none m-0 leading-relaxed
            "
                        dir="rtl"
                        rows={1}
                        disabled={disabled}
                        style={{ minHeight: '56px' }}
                    />

                    <button
                        type="submit"
                        disabled={!input.trim() || disabled}
                        className={`
              absolute left-3 bottom-3 p-2 rounded-md transition-all duration-200
              ${input.trim() && !disabled
                                ? 'bg-[#FF0033] text-black hover:bg-[#d9002b] shadow-[0_0_10px_rgba(255,0,51,0.4)] scale-100'
                                : 'bg-transparent text-gray-600 cursor-not-allowed scale-90'}
            `}
                    >
                        <SendHorizontal size={18} />
                    </button>
                </form>
                <div className="text-center text-[10px] text-gray-600 mt-3 font-sans tracking-widest uppercase">
                    Urdu Trigram Model <span className="text-[#FF0033] mx-1">•</span> Powered by AI
                </div>
            </div>
        </div>
    );
};

export default InputArea;
