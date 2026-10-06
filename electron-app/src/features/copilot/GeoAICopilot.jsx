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
    RefreshCw, Zap, Square, Maximize2
} from 'lucide-react';
import { GeoAILogo } from '../../components/common/GeoAILogo';
import { Button } from '../../components/ui/Button';
import { api } from '../../api/client';
import { buildChatHistory, nextMessageId } from './chatHistory';
import { MarkdownText } from './MarkdownText';
import { finalTurnText, stopGeoAIChat, streamGeoAIChat, stageLabel, useElapsedSeconds } from './geoaiStream';

export const GeoAICopilot = ({ isOpen, onClose, onExpand, onSelectFunction, canOpenForm, currentContext }) => {
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
    const [stage, setStage] = useState(null);
    const messagesEndRef = useRef(null);
    const abortRef = useRef(null);
    const elapsedSeconds = useElapsedSeconds(isLoading);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) {
            scrollToBottom();
        }
    }, [messages, isOpen]);

    // Load the local model in the background so the first question doesn't pay the load time.
    useEffect(() => {
        if (isOpen) {
            api.geoaiWarmup().catch(() => {});
        }
    }, [isOpen]);

    const handleSendMessage = async (textToSend) => {
        const text = textToSend || inputValue;
        if (!text.trim() || isLoading) return;

        const userMsg = {
            id: nextMessageId('user'),
            sender: 'user',
            text: text.trim(),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        const history = buildChatHistory(messages);
        setMessages(prev => [...prev, userMsg]);
        if (!textToSend) setInputValue('');
        setIsLoading(true);
        setStage(null);

        const aiMessageId = nextMessageId('ai');
        const setAiMessage = (fields) => setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId ? { ...msg, ...fields } : msg
        ));
        const controller = new AbortController();
        abortRef.current = controller;

        try {
            let shownText = '';
            const turnPromise = streamGeoAIChat({
                text,
                context: currentContext,
                history,
                signal: controller.signal,
                onText: (t) => {
                    shownText = t;
                    setAiMessage({ text: t });
                },
                onStage: setStage,
            });
            setMessages(prev => [...prev, {
                id: aiMessageId,
                sender: 'ai',
                text: '',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }]);
            const turn = await turnPromise;
            setAiMessage({
                text: finalTurnText(turn, shownText),
                executedTool: turn.executedTool,
                parameters: turn.parameters,
                results: turn.results
            });
        } catch {
            if (controller.signal.aborted) {
                setAiMessage({ text: '_Stopped._' });
                return;
            }
            // Drop the empty streaming placeholder so the fallback reply doesn't sit beside it.
            setMessages(prev => prev.filter(msg => msg.id !== aiMessageId));
            try {
                const res = await api.geoaiChat(text, currentContext, history);
                setMessages(prev => [...prev, {
                    id: nextMessageId('ai'),
                    sender: 'ai',
                    text: res.response || 'Calculation completed.',
                    executedTool: res.executed_tool,
                    parameters: res.parameters_extracted,
                    results: res.results,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }]);
            } catch (err) {
                setMessages(prev => [...prev, {
                    id: nextMessageId('ai'),
                    sender: 'ai',
                    isError: true,
                    text: `Error: ${err.message || 'Execution failed.'}`,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }]);
            }
        } finally {
            abortRef.current = null;
            setIsLoading(false);
        }
    };

    const handleStop = () => stopGeoAIChat(abortRef.current);

    // Stop a running answer when the drawer unmounts, so the model is not left computing.
    useEffect(() => () => abortRef.current?.abort(), []);

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

                    <div className="flex items-center gap-1">
                        {onExpand && (
                            <button
                                onClick={onExpand}
                                className="p-1.5 rounded hover:bg-background text-text-muted hover:text-text-main transition-colors"
                                title="Open in GeoAI tab"
                            >
                                <Maximize2 size={16} />
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="p-1.5 rounded hover:bg-background text-text-muted hover:text-text-main transition-colors"
                            title="Close (Esc)"
                        >
                            <X size={16} />
                        </button>
                    </div>
                </div>

                {/* Messages Feed */}
                <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5 text-xs">
                    {messages.map((msg) => (
                        <div
                            key={msg.id}
                            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                        >
                            <div
                                className={`max-w-[90%] px-3 py-2.5 rounded-md ${
                                    msg.sender === 'user'
                                        ? 'bg-primary/10 border border-primary/20 text-text-main rounded-br-sm'
                                        : msg.isError
                                        ? 'bg-error/10 border border-error/20 text-text-main rounded-bl-sm'
                                        : 'bg-background border border-border text-text-main rounded-bl-sm'
                                }`}
                            >
                                {msg.sender === 'ai' && !msg.text ? (
                                    <div className="flex items-center gap-2 text-[11px] text-text-muted">
                                        {isLoading ? (
                                            <>
                                                <RefreshCw size={12} className="animate-spin text-primary" />
                                                <span>{stageLabel(stage, elapsedSeconds)}</span>
                                            </>
                                        ) : (
                                            <span>No response received.</span>
                                        )}
                                    </div>
                                ) : (
                                    msg.sender === 'ai' ? (
                                        <MarkdownText text={msg.text} className="text-xs leading-relaxed" />
                                    ) : (
                                        <div className="text-xs whitespace-pre-wrap leading-relaxed">
                                            {msg.text}
                                        </div>
                                    )
                                )}

                                {/* Tool Result Card */}
                                {msg.executedTool && msg.results && (
                                    <div className="mt-2.5 p-2 bg-surface border border-border rounded text-[11px] space-y-2">
                                        <div className="text-primary font-semibold truncate">
                                            Routine: `{msg.executedTool}`
                                        </div>

                                        {onSelectFunction && canOpenForm?.(msg.executedTool) && (
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

                    {isLoading && messages[messages.length - 1]?.sender !== 'ai' && (
                        <div className="flex items-center gap-2 p-2 rounded bg-background border border-border w-fit text-[11px] text-text-muted">
                            <RefreshCw size={12} className="animate-spin text-primary" />
                            <span>{stageLabel(stage, elapsedSeconds)}</span>
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
                            className="flex-1 resize-none bg-surface border border-border rounded-md px-2.5 py-1.5 text-xs text-text-main placeholder:text-text-subtle focus:outline-none focus-visible:outline-none focus:border-primary/60 focus:ring-2 focus:ring-primary/15 transition-[border-color,box-shadow] duration-200 max-h-20"
                        />
                        {isLoading ? (
                            <button
                                onClick={handleStop}
                                title="Stop generating"
                                aria-label="Stop generating"
                                className="p-2 bg-surface border border-border text-text-main rounded hover:bg-background transition-colors shrink-0"
                            >
                                <Square size={11} className="fill-current" />
                            </button>
                        ) : (
                            <button
                                onClick={() => handleSendMessage()}
                                disabled={!inputValue.trim()}
                                title="Send"
                                aria-label="Send"
                                className="p-2 bg-primary text-on-primary rounded hover:bg-primary/90 disabled:opacity-30 disabled:cursor-not-allowed transition-colors shrink-0"
                            >
                                <Send size={13} />
                            </button>
                        )}
                    </div>
                </div>
            </motion.div>
        </AnimatePresence>
    );
};
