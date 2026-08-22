/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Bot, Send, X, Sparkles, Terminal, ArrowRight, CheckCircle, 
    AlertCircle, Layers, RefreshCw, ChevronRight, HelpCircle, Zap
} from 'lucide-react';
import { Button } from '../../components/ui/Button';

export const GeoAICopilot = ({ isOpen, onClose, onSelectFunction, currentContext }) => {
    const [messages, setMessages] = useState([
        {
            id: 'init-1',
            sender: 'ai',
            text: "**Hello! I am your GeoCore Local AI Assistant.**\n\nI run **100% offline** on your machine with direct access to **213 whitelisted Groundhog geotechnical tools**.\n\nYou can ask me to perform calculations, extract soil parameters, or analyze site data in plain English.",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            suggestedPrompts: [
                "Calculate Rankine earth pressure for phi = 32 deg",
                "Calculate Gmax for Vs = 240 m/s and gamma = 19 kN/m3",
                "Find void ratio for porosity = 0.38",
                "Calculate pipeline contact width for diameter = 1.0 m, penetration = 0.35 m"
            ]
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) {
            scrollToBottom();
        }
    }, [messages, isOpen]);

    const handleSendMessage = async (textToSend) => {
        const text = textToSend || inputValue;
        if (!text.trim() || isLoading) return;

        const userMsg = {
            id: `user-${Date.now()}`,
            sender: 'user',
            text: text.trim(),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setMessages(prev => [...prev, userMsg]);
        if (!textToSend) setInputValue('');
        setIsLoading(true);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/geoai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: text.trim(),
                    context: currentContext || {}
                })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail?.error || errData.detail || 'Offline AI Agent failed to respond');
            }

            const data = await response.json();

            const aiMsg = {
                id: `ai-${Date.now()}`,
                sender: 'ai',
                text: data.response || "Calculation completed.",
                executedTool: data.executed_tool,
                parameters: data.parameters_extracted,
                results: data.results?.result,
                candidateTools: data.candidate_tools || [],
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };

            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            setMessages(prev => [
                ...prev,
                {
                    id: `ai-err-${Date.now()}`,
                    sender: 'ai',
                    isError: true,
                    text: `**Agent Error**: ${error.message}\n\nPlease check that the Python backend is running.`,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
                onClick={onClose}
            />

            <motion.div
                initial={{ x: 450, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 450, opacity: 0 }}
                transition={{ type: 'spring', damping: 28, stiffness: 300 }}
                className="fixed right-0 top-0 bottom-0 w-full sm:w-[460px] bg-surface border-l border-border z-50 flex flex-col shadow-2xl"
            >
                {/* Header */}
                <div className="p-4 border-b border-border bg-background flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                            <Bot size={20} />
                        </div>
                        <div>
                            <h3 className="font-bold text-sm text-text-main flex items-center gap-1.5">
                                GeoAI Copilot
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary text-white font-semibold border border-primary/20">
                                    Beta
                                </span>
                            </h3>
                            <p className="text-[11px] text-text-muted">213 Groundhog Calculation Tools</p>
                        </div>
                    </div>

                    <button
                        onClick={onClose}
                        className="p-1.5 rounded-lg hover:bg-surface text-text-muted hover:text-text-main transition-colors"
                        title="Close Copilot (Esc)"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Messages Feed */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                        >
                            <div
                                className={`max-w-[90%] p-3 rounded-xl shadow-sm ${
                                    msg.sender === 'user'
                                        ? 'bg-primary text-white rounded-br-none'
                                        : msg.isError
                                        ? 'bg-red-500/10 border border-red-500/20 text-text-main rounded-bl-none'
                                        : 'bg-background border border-border text-text-main rounded-bl-none'
                                }`}
                            >
                                <div className="text-xs whitespace-pre-wrap leading-relaxed">
                                    {msg.text}
                                </div>

                                {/* Tool Result Card */}
                                {msg.executedTool && msg.results && (
                                    <div className="mt-3 p-2.5 bg-surface border border-border/80 rounded-lg text-xs space-y-2">
                                        <div className="flex items-center justify-between text-primary font-semibold">
                                            <span className="flex items-center gap-1">
                                                <CheckCircle size={13} className="text-green-500" />
                                                Routine: {msg.executedTool}
                                            </span>
                                        </div>

                                        {onSelectFunction && (
                                            <button
                                                onClick={() => {
                                                    onSelectFunction(msg.executedTool, msg.parameters);
                                                    onClose();
                                                }}
                                                className="w-full py-1.5 px-2.5 rounded bg-primary/10 hover:bg-primary/20 text-primary font-medium flex items-center justify-center gap-1 transition-colors text-[11px]"
                                            >
                                                <span>Open in Interactive Form</span>
                                                <ArrowRight size={12} />
                                            </button>
                                        )}
                                    </div>
                                )}

                                {/* Suggested Prompts */}
                                {msg.suggestedPrompts && (
                                    <div className="mt-3 pt-2.5 border-t border-border/50 space-y-1.5">
                                        <span className="text-[10px] uppercase font-bold text-text-muted tracking-wider">
                                            Quick Prompts:
                                        </span>
                                        <div className="flex flex-col gap-1">
                                            {msg.suggestedPrompts.map((p, idx) => (
                                                <button
                                                    key={idx}
                                                    onClick={() => handleSendMessage(p)}
                                                    className="text-left text-[11px] p-1.5 rounded bg-surface hover:bg-primary/10 hover:text-primary transition-colors border border-border/40 text-text-muted truncate flex items-center gap-1.5"
                                                >
                                                    <Zap size={11} className="shrink-0 text-primary" />
                                                    <span className="truncate">{p}</span>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                            <span className="text-[10px] text-text-muted mt-1 px-1">{msg.timestamp}</span>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex items-center gap-2 p-3 rounded-lg bg-background border border-border w-fit text-xs text-text-muted">
                            <RefreshCw size={14} className="animate-spin text-primary" />
                            <span>GeoAI is calculating with Groundhog engine...</span>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Bar */}
                <div className="p-3 border-t border-border bg-background">
                    <div className="flex items-center gap-2">
                        <textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask GeoAI to calculate or analyze..."
                            rows={1}
                            className="flex-1 resize-none bg-surface border border-border rounded-lg px-3 py-2 text-xs text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary max-h-24"
                        />
                        <Button
                            onClick={() => handleSendMessage()}
                            disabled={!inputValue.trim() || isLoading}
                            variant="primary"
                            className="h-9 px-3 shrink-0"
                        >
                            <Send size={15} />
                        </Button>
                    </div>
                    <div className="mt-1.5 flex items-center justify-between text-[10px] text-text-muted px-1">
                        <span>Press Enter to send • 100% Offline Local Inference</span>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
};
