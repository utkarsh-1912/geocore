/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 * 
 * GeoAI Copilot (Slide-out Drawer Assistant).
 * Minimal border-radius, strict theme colors, and deterministic Groundhog calculations.
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Bot, Send, X, Terminal, ArrowRight, CheckCircle, 
    RefreshCw, Zap
} from 'lucide-react';
import { GeoAILogo } from '../../components/common/GeoAILogo';
import { Button } from '../../components/ui/Button';
import { api } from '../../api/client';

export const GeoAICopilot = ({ isOpen, onClose, onSelectFunction, currentContext }) => {
    const [messages, setMessages] = useState([
        {
            id: 'init-1',
            sender: 'ai',
            text: "Hello! I am your GeoCore AI Assistant.\n\nI run 100% offline with direct access to 213 Groundhog engineering calculation tools.",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            suggestedPrompts: [
                "Calculate Rankine earth pressure for phi = 32 deg",
                "Calculate Gmax for Vs = 240 m/s and gamma = 19 kN/m3",
                "Find void ratio for porosity = 0.38"
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
            const streamResponse = await api.geoaiChatStream(text, currentContext);
            const reader = streamResponse.body.getReader();
            const decoder = new TextDecoder();
            
            let aiMessageId = Date.now() + 1;
            let accumulatedText = '';
            let executedTool = null;
            let toolParameters = null;
            let toolResults = null;
            
            setMessages(prev => [...prev, {
                id: aiMessageId,
                sender: 'ai',
                text: '',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }]);
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    try {
                        const eventData = JSON.parse(line.slice(6));
                        
                        if (eventData.type === 'token' && eventData.content) {
                            accumulatedText += eventData.content;
                            setMessages(prev => prev.map(msg =>
                                msg.id === aiMessageId ? { ...msg, text: accumulatedText } : msg
                            ));
                        } else if (eventData.type === 'tool_start') {
                            executedTool = eventData.tool_name;
                            toolParameters = eventData.tool_args;
                            setMessages(prev => prev.map(msg =>
                                msg.id === aiMessageId 
                                    ? { ...msg, text: `Calculating with **${eventData.tool_name}**...` }
                                    : msg
                            ));
                        } else if (eventData.type === 'tool_result') {
                            toolResults = eventData.tool_result;
                            accumulatedText = '';
                        } else if (eventData.type === 'done') {
                            setMessages(prev => prev.map(msg =>
                                msg.id === aiMessageId 
                                    ? { 
                                        ...msg, 
                                        text: accumulatedText || msg.text,
                                        executedTool,
                                        parameters: toolParameters,
                                        results: toolResults
                                    } 
                                    : msg
                            ));
                        }
                    } catch (parseErr) { }
                }
            }
        } catch (streamErr) {
            try {
                const res = await api.geoaiChat(text, currentContext);
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    sender: 'ai',
                    text: res.response || 'Calculation completed.',
                    executedTool: res.executed_tool,
                    parameters: res.parameters_extracted,
                    results: res.results,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }]);
            } catch (err) {
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    sender: 'ai',
                    isError: true,
                    text: `Error: ${err.message || 'Execution failed.'}`,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }]);
            }
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
                onClick={onClose}
                className="fixed inset-0 bg-black/40 backdrop-blur-xs z-40"
            />

            <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="fixed top-0 right-0 bottom-0 w-[420px] bg-surface border-l border-border z-50 flex flex-col shadow-xl"
            >
                {/* Header */}
                <div className="p-3.5 border-b border-border flex items-center justify-between bg-surface">
                    <div className="flex items-center gap-2.5">
                        <GeoAILogo size={30} variant="badge" />
                        <div>
                            <h3 className="font-bold text-xs text-text-main">GeoAI Copilot</h3>
                            <p className="text-[10px] text-text-muted">213 Groundhog Routines</p>
                        </div>
                    </div>

                    <button
                        onClick={onClose}
                        className="p-1.5 rounded hover:bg-background text-text-muted hover:text-text-main transition-colors"
                        title="Close (Esc)"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* Messages Feed */}
                <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5 text-xs">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                        >
                            <div
                                className={`max-w-[90%] p-3 rounded shadow-sm ${
                                    msg.sender === 'user'
                                        ? 'bg-primary text-white'
                                        : msg.isError
                                        ? 'bg-red-500/10 border border-red-500/20 text-text-main'
                                        : 'bg-background border border-border text-text-main'
                                }`}
                            >
                                <div className="text-xs whitespace-pre-wrap leading-relaxed">
                                    {msg.text}
                                </div>

                                {/* Tool Result Card */}
                                {msg.executedTool && msg.results && (
                                    <div className="mt-2.5 p-2 bg-surface border border-border rounded text-[11px] space-y-2">
                                        <div className="text-primary font-semibold truncate">
                                            Routine: `{msg.executedTool}`
                                        </div>

                                        {onSelectFunction && (
                                            <button
                                                onClick={() => {
                                                    onSelectFunction(msg.executedTool, msg.parameters);
                                                    onClose();
                                                }}
                                                className="w-full py-1 px-2 rounded bg-primary/10 hover:bg-primary/20 text-primary font-medium flex items-center justify-center gap-1 transition-colors text-[11px]"
                                            >
                                                <span>Open in Form</span>
                                                <ArrowRight size={11} />
                                            </button>
                                        )}
                                    </div>
                                )}

                                {/* Suggested Prompts */}
                                {msg.suggestedPrompts && (
                                    <div className="mt-2.5 pt-2 border-t border-border/40 space-y-1">
                                        {msg.suggestedPrompts.map((p, idx) => (
                                            <button
                                                key={idx}
                                                onClick={() => handleSendMessage(p)}
                                                className="text-left text-[11px] p-1.5 rounded bg-surface hover:bg-primary/10 hover:text-primary transition-colors border border-border text-text-muted truncate w-full flex items-center gap-1.5"
                                            >
                                                <Zap size={10} className="shrink-0 text-primary" />
                                                <span className="truncate">{p}</span>
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                            <span className="text-[9px] text-text-muted mt-1 px-1">{msg.timestamp}</span>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex items-center gap-2 p-2 rounded bg-background border border-border w-fit text-[11px] text-text-muted">
                            <RefreshCw size={12} className="animate-spin text-primary" />
                            <span>Calculating...</span>
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
                            className="flex-1 resize-none bg-surface border border-border rounded px-2.5 py-1.5 text-xs text-text-main focus:outline-none focus:border-primary max-h-20"
                        />
                        <button
                            onClick={() => handleSendMessage()}
                            disabled={!inputValue.trim() || isLoading}
                            className="p-2 bg-primary text-white rounded hover:bg-primary/90 disabled:opacity-30 disabled:cursor-not-allowed transition-colors shrink-0"
                        >
                            <Send size={13} />
                        </button>
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
};
