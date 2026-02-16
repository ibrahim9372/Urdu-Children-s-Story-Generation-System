
import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import InputArea from './InputArea';
import { generateText } from '../utils/api';
import { Sparkles } from 'lucide-react';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]); // Start empty to show Welcome Screen
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const handleSendMessage = async (text) => {
        const userMsg = {
            id: Date.now(),
            text: text,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const responseText = await generateText(text);
            const botMsg = {
                id: Date.now() + 1,
                text: responseText,
                sender: 'bot',
                timestamp: new Date()
            };

            setIsTyping(false);
            setMessages(prev => [...prev, botMsg]);
        } catch (error) {
            console.error("Error generating text:", error);
            setIsTyping(false);
        }
    };

    const examplePrompts = [
        "ایک دفعہ کا ذکر ہے کہ ایک بادشاہ...",
        "جنگل میں ایک شیر اور چوہا...",
        "صبح کی سیر کے فائدے...",
        "لاہور ایک تاریخی شہر ہے..."
    ];

    return (
        <div className="flex flex-col h-full w-full max-w-4xl mx-auto relative bg-[#000000]">
            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto w-full custom-scrollbar pb-40 pt-10 px-4">

                {/* Welcome Screen */}
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-10 animate-fade-in">
                        <div className="bg-white/5 p-4 rounded-full mb-4 ring-1 ring-[#FF0033]/50 shadow-[0_0_15px_rgba(255,0,51,0.3)]">
                            <Sparkles size={48} className="text-[#FF0033]" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold font-sans text-white mb-2 tracking-tight">Urdu Trigram Model</h1>
                            <p className="text-gray-500">Next Generation Urdu Text Completion</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl px-4">
                            {examplePrompts.map((prompt, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleSendMessage(prompt)}
                                    className="group flex flex-col items-start p-4 bg-[#111111] hover:bg-[#1a1a1a] border border-[#333333] hover:border-[#FF0033] rounded-xl transition-all duration-300 text-right w-full hover:shadow-[0_0_10px_rgba(255,0,51,0.1)]"
                                >
                                    <span className="text-gray-200 urdu-text text-lg w-full group-hover:text-white transition-colors">{prompt}</span>
                                    <span className="text-xs text-[#FF0033] mt-2 font-sans opacity-0 group-hover:opacity-100 transition-opacity translate-y-2 group-hover:translate-y-0">Generate continuation &rarr;</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {messages.map((msg) => (
                    <Message
                        key={msg.id}
                        text={msg.text}
                        sender={msg.sender}
                        isTyping={false}
                    />
                ))}

                {isTyping && (
                    <Message
                        text=""
                        sender="bot"
                        isTyping={true}
                    />
                )}

                <div ref={messagesEndRef} className="h-0" />
            </div>

            {/* Input Area (Fixed) */}
            <div className="w-full max-w-4xl mx-auto">
                <InputArea onSendMessage={handleSendMessage} disabled={isTyping} />
            </div>
        </div>
    );
};

export default ChatInterface;
