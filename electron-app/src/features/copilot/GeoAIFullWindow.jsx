/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 * 
 * GeoAI Full-Window Geotechnical Assistant Workspace.
 * Clean, modern LLM workspace with inline message editing,
 * 1-click model setup, collapsible history sidebar, and Groundhog calculations.
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Send, ArrowRight, RefreshCw, Plus, MessageSquare, 
    Trash2, Copy, Cpu, Check, Sliders, X, PanelLeft,
    PanelLeftClose, Download, Pencil, RotateCcw,
    Shield, CheckCircle2, ChevronDown
} from 'lucide-react';
import { GeoAILogo } from '../../components/common/GeoAILogo';
import { ConfirmationModal } from '../../components/common/ConfirmationModal';
import { api } from '../../api/client';
import { toast } from 'sonner';

export const GeoAIFullWindow = ({ onSelectFunction, currentContext, onBackToModules }) => {
    // UI Layout State
    const [sidebarOpen, setSidebarOpen] = useState(true);

    // Default initial conversation generator
    const createDefaultConv = () => ({
        id: `conv-${Date.now()}`,
        title: 'New Analysis',
        createdAt: new Date().toISOString(),
        messages: []
    });

    // Conversations & Message State
    const [conversations, setConversations] = useState(() => {
        const saved = localStorage.getItem('geoai_conversations');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (Array.isArray(parsed) && parsed.length > 0) {
                    return parsed;
                }
            } catch (e) { }
        }
        return [createDefaultConv()];
    });

    const [activeConvId, setActiveConvId] = useState(() => {
        const saved = localStorage.getItem('geoai_conversations');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                if (Array.isArray(parsed) && parsed.length > 0) {
                    return parsed[0].id;
                }
            } catch (e) { }
        }
        return null;
    });

    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Inline Message Edit State
    const [editingMsgId, setEditingMsgId] = useState(null);
    const [editingText, setEditingText] = useState('');

    // Model & Download State
    const [modelInfo, setModelInfo] = useState(null);
    const [availableModels, setAvailableModels] = useState([]);
    const [downloadStatus, setDownloadStatus] = useState({ status: 'idle' });
    const [memoryInfo, setMemoryInfo] = useState(null);
    const [showModelModal, setShowModelModal] = useState(false);
    const [convToDelete, setConvToDelete] = useState(null);

    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);
    const editTextareaRef = useRef(null);

    // Keep activeConvId synchronized to a valid conversation at all times
    useEffect(() => {
        if (!activeConvId || !conversations.some(c => c.id === activeConvId)) {
            if (conversations.length > 0) {
                setActiveConvId(conversations[0].id);
            } else {
                const fresh = createDefaultConv();
                setConversations([fresh]);
                setActiveConvId(fresh.id);
            }
        }
    }, [conversations, activeConvId]);

    // Save conversations to localStorage
    useEffect(() => {
        localStorage.setItem('geoai_conversations', JSON.stringify(conversations));
    }, [conversations]);

    const activeConversation = conversations.find(c => c.id === activeConvId) || conversations[0] || createDefaultConv();
    const currentConvId = activeConversation?.id;
    const messages = activeConversation?.messages || [];

    // Scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    // Fetch model & memory status
    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 6000);
        return () => clearInterval(interval);
    }, []);

    // Poll download status if actively downloading
    useEffect(() => {
        let timer;
        if (downloadStatus?.status === 'downloading') {
            timer = setInterval(async () => {
                try {
                    const status = await api.geoaiGetDownloadStatus();
                    setDownloadStatus(status);
                    if (status.status === 'completed') {
                        toast.success("AI Model installed successfully!");
                        fetchStatus();
                    } else if (status.status === 'error') {
                        toast.error(`Download failed: ${status.error || 'Please check internet connection'}`);
                    }
                } catch (e) { }
            }, 2000);
        }
        return () => clearInterval(timer);
    }, [downloadStatus]);

    const fetchStatus = async () => {
        try {
            const statusRes = await api.geoaiStatus();
            setModelInfo(statusRes?.model_info);

            const memRes = await api.geoaiGetMemory();
            setMemoryInfo(memRes);

            const modelsRes = await api.geoaiListModels();
            setAvailableModels(modelsRes?.models || []);

            const dlRes = await api.geoaiGetDownloadStatus();
            setDownloadStatus(dlRes);
        } catch (e) { }
    };

    // Auto-resize main textarea
    const adjustTextareaHeight = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            const newHeight = Math.min(Math.max(textareaRef.current.scrollHeight, 38), 180);
            textareaRef.current.style.height = `${newHeight}px`;
        }
    };

    useEffect(() => {
        adjustTextareaHeight();
    }, [inputValue]);

    const createNewChat = () => {
        const newConv = createDefaultConv();
        setConversations(prev => [newConv, ...prev]);
        setActiveConvId(newConv.id);
        setEditingMsgId(null);
    };

    const confirmDeleteConversation = () => {
        if (!convToDelete) return;
        const id = convToDelete.id;
        const remaining = conversations.filter(c => c.id !== id);
        if (remaining.length === 0) {
            const fresh = createDefaultConv();
            setConversations([fresh]);
            setActiveConvId(fresh.id);
        } else {
            setConversations(remaining);
            if (activeConvId === id) {
                setActiveConvId(remaining[0].id);
            }
        }
        toast.success("Conversation deleted");
        setConvToDelete(null);
    };

    const updateCurrentMessages = (newMessages) => {
        const targetId = currentConvId || activeConvId;
        setConversations(prev => prev.map(conv => {
            if (conv.id === targetId) {
                let title = conv.title;
                if (conv.title === 'New Analysis' && newMessages.length > 0) {
                    const firstUser = newMessages.find(m => m.sender === 'user');
                    if (firstUser) {
                        title = firstUser.text.slice(0, 30) + (firstUser.text.length > 30 ? '...' : '');
                    }
                }
                return { ...conv, title, messages: newMessages };
            }
            return conv;
        }));
    };

    const handleSendMessage = async (textToSend, baseMessages = null) => {
        const text = textToSend || inputValue;
        if (!text.trim() || isLoading) return;

        const targetId = currentConvId || activeConvId;
        const msgsToUse = baseMessages || messages;

        const userMsg = {
            id: `user-${Date.now()}`,
            sender: 'user',
            text: text.trim(),
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        const updated = [...msgsToUse, userMsg];
        updateCurrentMessages(updated);
        if (!textToSend) setInputValue('');
        setEditingMsgId(null);
        setIsLoading(true);

        try {
            const streamResponse = await api.geoaiChatStream(text, currentContext);
            const reader = streamResponse.body.getReader();
            const decoder = new TextDecoder();

            const aiMessageId = Date.now() + 1;
            let accumulatedText = '';
            let executedTool = null;
            let toolParameters = null;
            let toolResults = null;

            const initialAiMsg = {
                id: aiMessageId,
                sender: 'ai',
                text: '',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
            updateCurrentMessages([...updated, initialAiMsg]);

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
                            setConversations(prev => prev.map(c => {
                                if (c.id === targetId) {
                                    return {
                                        ...c,
                                        messages: c.messages.map(m => m.id === aiMessageId ? { ...m, text: accumulatedText } : m)
                                    };
                                }
                                return c;
                            }));
                        } else if (eventData.type === 'tool_start') {
                            executedTool = eventData.tool_name;
                            toolParameters = eventData.tool_args;
                            setConversations(prev => prev.map(c => {
                                if (c.id === targetId) {
                                    return {
                                        ...c,
                                        messages: c.messages.map(m => m.id === aiMessageId ? {
                                            ...m,
                                            text: `Calculating with **${eventData.tool_name}**...`
                                        } : m)
                                    };
                                }
                                return c;
                            }));
                        } else if (eventData.type === 'tool_result') {
                            toolResults = eventData.tool_result;
                            accumulatedText = '';
                        } else if (eventData.type === 'done') {
                            setConversations(prev => prev.map(c => {
                                if (c.id === targetId) {
                                    return {
                                        ...c,
                                        messages: c.messages.map(m => m.id === aiMessageId ? {
                                            ...m,
                                            text: accumulatedText || m.text,
                                            executedTool,
                                            parameters: toolParameters,
                                            results: toolResults
                                        } : m)
                                    };
                                }
                                return c;
                            }));
                        }
                    } catch (err) { }
                }
            }
        } catch (err) {
            try {
                const res = await api.geoaiChat(text, currentContext);
                const aiMsg = {
                    id: Date.now() + 1,
                    sender: 'ai',
                    text: res.response || "Calculation complete.",
                    executedTool: res.executed_tool,
                    parameters: res.parameters_extracted,
                    results: res.results,
                    provenance: res.provenance,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                };
                updateCurrentMessages([...updated, aiMsg]);
            } catch (fallbackErr) {
                const errorMsg = {
                    id: Date.now() + 1,
                    sender: 'ai',
                    isError: true,
                    text: `Execution Error: ${fallbackErr.message || 'Could not complete calculation.'}`,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                };
                updateCurrentMessages([...updated, errorMsg]);
            }
        } finally {
            setIsLoading(false);
            fetchStatus();
        }
    };

    // Inline Message Edit Handlers
    const startEditing = (msg) => {
        setEditingMsgId(msg.id);
        setEditingText(msg.text);
    };

    const cancelEditing = () => {
        setEditingMsgId(null);
        setEditingText('');
    };

    const submitEdit = (msgId) => {
        if (!editingText.trim() || isLoading) return;
        const msgIndex = messages.findIndex(m => m.id === msgId);
        if (msgIndex === -1) return;

        // Truncate message history from this edit point
        const priorMessages = messages.slice(0, msgIndex);
        handleSendMessage(editingText.trim(), priorMessages);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleCopy = (text) => {
        navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard");
    };

    const handleAutoLink = async () => {
        try {
            const res = await api.geoaiAutoLinkModels();
            if (res?.status === 'linked') {
                toast.success("Discovered and auto-linked installed desktop model!");
                fetchStatus();
            } else {
                toast.info("No pre-installed models detected in application directories.");
            }
        } catch (e) {
            toast.error("Auto-link scan failed.");
        }
    };

    const handleSelectModel = async (model) => {
        try {
            if (!model.is_installed) {
                toast.info(`Downloading ${model.id}...`);
                setDownloadStatus({ status: 'downloading', model_id: model.id });
                await api.geoaiDownloadModel(model.id, true);
            } else {
                await api.geoaiSelectModel(model.local_path, "llama_cpp");
                toast.success(`Active Model: ${model.id}`);
                setShowModelModal(false);
            }
            fetchStatus();
        } catch (e) {
            toast.error("Failed to select model");
        }
    };

    const promptCards = [
        {
            title: "Soil Dynamics & Gmax",
            prompt: "Calculate Gmax for Vs = 260 m/s and gamma = 19.0 kN/m3"
        },
        {
            title: "Rankine Earth Pressure",
            prompt: "Calculate active and passive Rankine lateral earth pressure coefficients for phi = 34 deg"
        },
        {
            title: "CPT Soil Classification",
            prompt: "Classify CPT soil behavior type at depth 4.5m for qc = 14.2 MPa and fs = 65 kPa"
        },
        {
            title: "SPT Energy Normalization",
            prompt: "Normalize SPT test at depth 6m with raw blow count N = 20 with 60% hammer energy"
        }
    ];

    const hasAnyModelInstalled = availableModels.some(m => m.is_installed);
    const recommendedModel = availableModels.find(m => m.id.includes('1.5b')) || availableModels[0] || {
        id: "qwen2.5-1.5b-instruct",
        size_mb: 986
    };

    // --- GATEWAY VIEW: IF NO MODEL IS INSTALLED ON WORKSTATION ---
    if (!hasAnyModelInstalled && availableModels.length > 0) {
        return (
            <div className="flex h-full w-full bg-background text-text-main overflow-y-auto font-sans p-6 md:p-12">
                <div className="max-w-2xl mx-auto my-auto w-full text-center space-y-6">
                    <div className="inline-flex p-3.5 rounded bg-primary/10 border border-primary/20 text-primary shadow-sm">
                        <GeoAILogo size={44} />
                    </div>

                    <div className="space-y-2">
                        <h1 className="text-2xl font-bold tracking-tight text-text-main">
                            GeoAI Wrapped MCP / SLM Engine Gateway
                        </h1>
                        <p className="text-xs md:text-sm text-text-muted max-w-lg mx-auto leading-relaxed">
                            Offline Small Language Model (SLM) wrapped with the GeoCore Model Context Protocol (MCP) Tool Registry.
                            Executes 213 Groundhog engineering calculations with zero cloud dependencies.
                        </p>
                    </div>

                    {/* Architecture Visualizer */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-left bg-surface border border-border rounded p-3 text-xs">
                        <div className="p-2 rounded bg-background border border-border/60">
                            <div className="text-[10px] font-bold uppercase text-primary">1. Local SLM</div>
                            <div className="text-[11px] text-text-main font-medium mt-0.5">Qwen 2.5 GGUF</div>
                            <div className="text-[10px] text-text-muted">Parameter & intent reasoning</div>
                        </div>
                        <div className="p-2 rounded bg-background border border-border/60">
                            <div className="text-[10px] font-bold uppercase text-primary">2. Wrapped MCP</div>
                            <div className="text-[11px] text-text-main font-medium mt-0.5">Context Protocol</div>
                            <div className="text-[10px] text-text-muted">Typed schemas & validation</div>
                        </div>
                        <div className="p-2 rounded bg-background border border-border/60">
                            <div className="text-[10px] font-bold uppercase text-primary">3. Groundhog</div>
                            <div className="text-[11px] text-text-main font-medium mt-0.5">213 Deterministic Tools</div>
                            <div className="text-[10px] text-text-muted">Exact geotechnical results</div>
                        </div>
                    </div>

                    {/* 1-Click Install Card */}
                    <div className="p-5 rounded border border-border bg-surface text-left space-y-4 max-w-md mx-auto shadow-sm">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-sm font-bold text-text-main">Qwen 2.5 (1.5B Instruct)</h3>
                                <p className="text-[11px] text-text-muted">GGUF quantized for CPU inference & low RAM (&lt;2 GB)</p>
                            </div>
                            <span className="text-xs font-mono text-text-muted bg-background px-2 py-0.5 rounded border border-border">
                                {recommendedModel.size_mb} MB
                            </span>
                        </div>

                        <button
                            onClick={() => handleSelectModel(recommendedModel)}
                            disabled={downloadStatus?.status === 'downloading'}
                            className="w-full py-2.5 px-4 bg-primary text-white rounded text-xs font-semibold hover:bg-primary/90 flex items-center justify-center gap-2 transition-all shadow-sm disabled:opacity-50"
                        >
                            {downloadStatus?.status === 'downloading' ? (
                                <>
                                    <RefreshCw size={14} className="animate-spin" />
                                    <span>Downloading Wrapped Engine ({recommendedModel.size_mb} MB)...</span>
                                </>
                            ) : (
                                <>
                                    <Download size={14} />
                                    <span>Download & Install Engine ({recommendedModel.size_mb} MB)</span>
                                </>
                            )}
                        </button>

                        <div className="pt-2 border-t border-border/60 flex items-center justify-between text-[11px]">
                            <span className="text-text-muted">Installed with desktop app?</span>
                            <button
                                onClick={handleAutoLink}
                                className="text-primary font-semibold hover:underline flex items-center gap-1"
                            >
                                <RefreshCw size={11} />
                                <span>Auto-Detect & Link</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // --- MAIN WORKSPACE VIEW (WHEN MODEL IS READY) ---
    return (
        <div className="flex h-full w-full bg-background text-text-main overflow-hidden font-sans">
            {/* --- Collapsible Left Chat History Sidebar --- */}
            {sidebarOpen && (
                <div className="w-64 border-r border-border bg-surface flex flex-col h-full shrink-0">
                    {/* Aligned Top Bar */}
                    <div className="h-13 border-b border-border px-3 flex items-center justify-between gap-2 shrink-0 bg-surface">
                        <button
                            onClick={createNewChat}
                            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary text-white rounded text-xs font-semibold hover:bg-primary/90 transition-colors shadow-sm"
                        >
                            <Plus size={14} />
                            <span>New Chat</span>
                        </button>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            title="Collapse Sidebar"
                            className="p-2 border border-border rounded text-text-muted hover:text-text-main hover:bg-background transition-colors shrink-0"
                        >
                            <PanelLeftClose size={15} />
                        </button>
                    </div>

                    {/* Conversation List */}
                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                        <div className="px-2 py-1 text-[11px] font-semibold text-text-muted uppercase tracking-wider">
                            History
                        </div>
                        {conversations.map(conv => (
                            <div
                                key={conv.id}
                                onClick={() => {
                                    setActiveConvId(conv.id);
                                    setEditingMsgId(null);
                                }}
                                className={`group flex items-center justify-between px-3 py-2 rounded text-xs font-medium cursor-pointer transition-colors ${
                                    conv.id === activeConvId 
                                        ? 'bg-primary/10 text-primary border-l-2 border-primary font-semibold' 
                                        : 'text-text-muted hover:bg-background hover:text-text-main'
                                }`}
                            >
                                <div className="flex items-center gap-2 truncate">
                                    <MessageSquare size={13} className="shrink-0 opacity-70" />
                                    <span className="truncate">{conv.title}</span>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setConvToDelete(conv);
                                    }}
                                    title="Delete conversation"
                                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 rounded transition-opacity"
                                >
                                    <Trash2 size={12} />
                                </button>
                            </div>
                        ))}
                    </div>

                    {/* Clean Status Footer */}
                    <div className="border-t border-border bg-surface px-3 py-2 shrink-0 flex items-center justify-between text-[11px] text-text-muted">
                        <div className="flex items-center gap-1.5 truncate">
                            <span className="w-2 h-2 rounded-full bg-emerald-500" />
                            <span className="truncate">GeoAI Engine Ready</span>
                        </div>
                        {memoryInfo && (
                            <span className="font-mono text-[10px]">{memoryInfo.process_ram_mb} MB</span>
                        )}
                    </div>
                </div>
            )}

            {/* --- Main Chat Workspace --- */}
            <div className="flex-1 flex flex-col h-full overflow-hidden relative">
                {/* Top Header Bar */}
                <div className="h-13 border-b border-border bg-surface px-4 flex items-center justify-between shrink-0">
                    <div className="flex items-center gap-3">
                        {!sidebarOpen && (
                            <button
                                onClick={() => setSidebarOpen(true)}
                                title="Open Sidebar"
                                className="p-2 border border-border rounded text-text-muted hover:text-text-main hover:bg-background transition-colors"
                            >
                                <PanelLeft size={15} />
                            </button>
                        )}
                        <div className="flex items-center gap-2 text-xs font-semibold text-text-main">
                            <GeoAILogo size={18} className="text-primary" />
                            <span>GeoAI</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {downloadStatus?.status === 'downloading' && (
                            <span className="text-[11px] text-primary flex items-center gap-1.5 animate-pulse border border-primary/30 px-2 py-0.5 rounded">
                                <RefreshCw size={11} className="animate-spin" />
                                <span>Downloading Model...</span>
                            </span>
                        )}
                        <button
                            onClick={() => setShowModelModal(true)}
                            className="px-2.5 py-1.5 border border-border rounded text-xs text-text-muted hover:text-text-main hover:bg-background transition-colors flex items-center gap-1.5"
                        >
                            <Sliders size={13} />
                            <span>Models</span>
                        </button>
                    </div>
                </div>

                {/* Message Scroll Area */}
                <div className="flex-1 overflow-y-auto p-3 sm:p-4">
                    {messages.length === 0 ? (
                        /* Clean Initial Welcome */
                        <div className="max-w-5xl mx-auto my-auto flex flex-col items-center justify-center text-center py-6">
                            <GeoAILogo size={48} variant="badge" className="mb-2.5" />
                            <h2 className="text-base font-bold text-text-main mb-1">
                                Geotechnical Intelligence Assistant
                            </h2>
                            <p className="text-xs text-text-muted max-w-lg mb-5">
                                Local Small Language Model executing 213 deterministic Groundhog calculations with strict provenance tracking.
                            </p>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full text-left">
                                {promptCards.map((card, idx) => (
                                    <div
                                        key={idx}
                                        onClick={() => handleSendMessage(card.prompt)}
                                        className="p-2.5 rounded border border-border bg-surface hover:border-primary/50 hover:bg-background transition-colors cursor-pointer"
                                    >
                                        <div className="text-xs font-bold text-text-main mb-0.5">
                                            {card.title}
                                        </div>
                                        <div className="text-[11px] text-text-muted line-clamp-2">
                                            {card.prompt}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        /* Message List */
                        <div className="max-w-5xl mx-auto space-y-3.5">
                            {messages.map((msg) => {
                                const isEditing = editingMsgId === msg.id;

                                return (
                                    <div
                                        key={msg.id}
                                        className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} group`}
                                    >
                                        {msg.sender === 'ai' && (
                                            <GeoAILogo size={26} variant="badge" className="mt-0.5 shrink-0" />
                                        )}

                                        <div className={`max-w-[90%] space-y-1.5 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                                            {isEditing ? (
                                                /* Inline Edit Box */
                                                <div className="w-full bg-surface border border-primary rounded p-3 space-y-2 text-xs">
                                                    <textarea
                                                        ref={editTextareaRef}
                                                        value={editingText}
                                                        onChange={(e) => setEditingText(e.target.value)}
                                                        rows={2}
                                                        className="w-full resize-none bg-background border border-border rounded p-2 text-xs text-text-main focus:outline-none focus:border-primary"
                                                    />
                                                    <div className="flex items-center justify-end gap-2">
                                                        <button
                                                            onClick={cancelEditing}
                                                            className="px-2.5 py-1 text-xs text-text-muted hover:text-text-main rounded border border-border hover:bg-background"
                                                        >
                                                            Cancel
                                                        </button>
                                                        <button
                                                            onClick={() => submitEdit(msg.id)}
                                                            disabled={!editingText.trim()}
                                                            className="px-3 py-1 text-xs bg-primary text-white rounded hover:bg-primary/90 font-medium disabled:opacity-40"
                                                        >
                                                            Save & Resubmit
                                                        </button>
                                                    </div>
                                                </div>
                                            ) : (
                                                /* Standard Message Bubble */
                                                <div
                                                    className={`p-3 rounded text-xs leading-relaxed relative ${
                                                        msg.sender === 'user'
                                                            ? 'bg-primary text-white'
                                                            : 'bg-surface border border-border text-text-main'
                                                    }`}
                                                >
                                                    <div className="whitespace-pre-wrap">
                                                        {msg.text}
                                                    </div>

                                                    {/* Message Actions */}
                                                    <div className={`flex items-center justify-between pt-2 mt-2 border-t text-[10px] ${
                                                        msg.sender === 'user' 
                                                            ? 'border-white/20 text-white/80' 
                                                            : 'border-border/40 text-text-muted'
                                                    }`}>
                                                        <span>{msg.timestamp}</span>

                                                        <div className="flex items-center gap-2">
                                                            {msg.sender === 'user' && !isLoading && (
                                                                <button
                                                                    onClick={() => startEditing(msg)}
                                                                    title="Edit prompt"
                                                                    className="hover:underline flex items-center gap-1 opacity-80 hover:opacity-100"
                                                                >
                                                                    <Pencil size={10} />
                                                                    <span>Edit</span>
                                                                </button>
                                                            )}

                                                            {msg.sender === 'ai' && !isLoading && (
                                                                <button
                                                                    onClick={() => handleCopy(msg.text)}
                                                                    className="hover:text-text-main transition-colors flex items-center gap-1"
                                                                >
                                                                    <Copy size={11} />
                                                                    <span>Copy</span>
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Structured Calculation Output */}
                                            {msg.executedTool && msg.results && (
                                                <div className="p-2.5 rounded border border-border bg-surface text-xs space-y-2">
                                                    <div className="flex items-center justify-between">
                                                        <span className="font-semibold text-primary">
                                                            Routine: `{msg.executedTool}`
                                                        </span>
                                                        {onSelectFunction && (
                                                            <button
                                                                onClick={() => onSelectFunction(msg.executedTool, msg.parameters)}
                                                                className="flex items-center gap-1 text-[11px] text-primary hover:underline font-medium"
                                                            >
                                                                <span>Load in Form</span>
                                                                <ArrowRight size={11} />
                                                            </button>
                                                        )}
                                                    </div>

                                                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-1 bg-background p-1.5 rounded border border-border">
                                                        {Object.entries(msg.results.result || msg.results).map(([k, v]) => {
                                                            if (k.startsWith('_')) return null;
                                                            return (
                                                                <div key={k} className="p-1 rounded bg-surface border border-border/50">
                                                                    <div className="text-[9px] font-bold text-text-muted uppercase truncate">{k}</div>
                                                                    <div className="text-xs font-semibold text-text-main truncate">
                                                                        {typeof v === 'number' ? v.toFixed(3) : String(v)}
                                                                    </div>
                                                                </div>
                                                            );
                                                        })}
                                                    </div>

                                                    {msg.results._provenance && (
                                                        <div className="text-[10px] text-text-muted pt-1 border-t border-border/40">
                                                            {msg.results._provenance.method} • {msg.results._provenance.standard}
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}

                            {isLoading && (
                                <div className="flex items-center gap-2 text-xs text-text-muted">
                                    <RefreshCw size={12} className="animate-spin text-primary" />
                                    <span>Reasoning & calculating...</span>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>
                    )}
                </div>

                {/* --- Bottom Input Box --- */}
                <div className="border-t border-border bg-surface px-3 py-2 shrink-0 flex items-center justify-center">
                    <div className="w-full max-w-5xl flex items-end gap-1.5 bg-background border border-border focus-within:border-primary rounded p-1.5 transition-colors">
                        <textarea
                            ref={textareaRef}
                            value={inputValue}
                            onChange={(e) => {
                                setInputValue(e.target.value);
                                adjustTextareaHeight();
                            }}
                            onKeyDown={handleKeyDown}
                            rows={1}
                            placeholder="Enter geotechnical parameters or engineering calculation query..."
                            className="flex-1 resize-none bg-transparent px-2 py-1 text-xs text-text-main placeholder:text-text-muted focus:outline-none max-h-40 leading-relaxed"
                        />

                        <button
                            onClick={() => handleSendMessage()}
                            disabled={!inputValue.trim() || isLoading}
                            className="p-1.5 bg-primary text-white rounded hover:bg-primary/90 disabled:opacity-30 disabled:cursor-not-allowed transition-colors shrink-0 flex items-center justify-center h-7 w-7"
                        >
                            <Send size={13} />
                        </button>
                    </div>
                </div>
            </div>

            {/* --- Model Selector Modal --- */}
            <AnimatePresence>
                {showModelModal && (
                    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
                        <div className="w-full max-w-md bg-surface border border-border rounded shadow-lg overflow-hidden">
                            <div className="p-4 border-b border-border flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Cpu size={16} className="text-primary" />
                                    <h3 className="text-xs font-bold text-text-main">Local AI Models</h3>
                                </div>
                                <button
                                    onClick={() => setShowModelModal(false)}
                                    className="p-1 hover:bg-background rounded text-text-muted hover:text-text-main"
                                >
                                    <X size={14} />
                                </button>
                            </div>

                            <div className="p-4 space-y-2.5 max-h-80 overflow-y-auto">
                                {availableModels.map((model) => (
                                    <div
                                        key={model.id}
                                        className="p-3 rounded border border-border bg-background flex items-center justify-between gap-3"
                                    >
                                        <div className="space-y-0.5">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-semibold text-text-main">{model.id}</span>
                                                <span className="text-[10px] text-text-muted font-mono">({model.size_mb} MB)</span>
                                            </div>
                                            <p className="text-[11px] text-text-muted">{model.description}</p>
                                        </div>

                                        <button
                                            onClick={() => handleSelectModel(model)}
                                            disabled={downloadStatus?.status === 'downloading'}
                                            className={`px-3 py-1 rounded text-xs font-semibold shrink-0 transition-colors flex items-center gap-1 ${
                                                model.is_installed
                                                    ? 'bg-primary text-white hover:bg-primary/90'
                                                    : 'border border-primary text-primary hover:bg-primary/10'
                                            }`}
                                        >
                                            {model.is_installed ? (
                                                'Select'
                                            ) : downloadStatus?.status === 'downloading' && downloadStatus.model_id === model.id ? (
                                                <>
                                                    <RefreshCw size={11} className="animate-spin" />
                                                    <span>Downloading...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <Download size={11} />
                                                    <span>Download</span>
                                                </>
                                            )}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </AnimatePresence>

            {/* --- Custom Delete Confirmation Modal --- */}
            <ConfirmationModal
                isOpen={!!convToDelete}
                title="Delete Conversation?"
                message={`Are you sure you want to delete "${convToDelete?.title}"? This calculation history cannot be recovered.`}
                confirmText="Delete"
                cancelText="Cancel"
                variant="danger"
                onConfirm={confirmDeleteConversation}
                onCancel={() => setConvToDelete(null)}
            />
        </div>
    );
};
