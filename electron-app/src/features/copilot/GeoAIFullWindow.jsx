/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 * 
 * GeoAI Full-Window Geotechnical Assistant Workspace.
 * Clean, modern SLM workspace with inline message editing,
 * wrapped Qwen & Gemma installer selection, download checks,
 * collapsible history sidebar, and Groundhog calculations.
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    Send, ArrowRight, RefreshCw, Plus, MessageSquare, 
    Trash2, Copy, Cpu, Check, X, PanelLeft,
    PanelLeftClose, Download, Pencil, RotateCcw,
    Shield, CheckCircle2, ChevronDown, AlertTriangle,
    HardDrive, Zap, BookOpen, Compass, Layers, User,
    FileCode, ExternalLink, Sparkles
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

    // Gateway / Modal Filter State
    const [gatewayTab, setGatewayTab] = useState('qwen'); // 'qwen' | 'gemma'
    const [modalTab, setModalTab] = useState('all'); // 'all' | 'qwen' | 'gemma'
    const [customGgufPath, setCustomGgufPath] = useState('');
    const [isLinkingCustom, setIsLinkingCustom] = useState(false);

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
        const interval = setInterval(fetchStatus, 5000);
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
                        toast.success("AI Model engine installed and configured successfully!");
                        fetchStatus();
                    } else if (status.status === 'error') {
                        toast.error(`Download failed: ${status.error || 'Please check internet connection'}`);
                    }
                } catch (e) { }
            }, 1500);
        }
        return () => clearInterval(timer);
    }, [downloadStatus?.status]);

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
                    text: `Calculation Error: ${fallbackErr.message || "Failed to execute calculation."}`,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                };
                updateCurrentMessages([...updated, errorMsg]);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const startEditing = (msg) => {
        setEditingMsgId(msg.id);
        setEditingText(msg.text);
        setTimeout(() => {
            if (editTextareaRef.current) {
                editTextareaRef.current.focus();
                editTextareaRef.current.selectionStart = editTextareaRef.current.value.length;
            }
        }, 50);
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
                toast.info(`Downloading ${model.display_name || model.id}...`);
                setDownloadStatus({
                    status: 'downloading',
                    model_id: model.id,
                    display_name: model.display_name,
                    size_mb: model.size_mb
                });
                await api.geoaiDownloadModel(model.id, true);
            } else {
                await api.geoaiSelectModel(model.local_path, "llama_cpp");
                toast.success(`Active Model: ${model.display_name || model.id}`);
                setShowModelModal(false);
            }
            fetchStatus();
        } catch (e) {
            toast.error("Failed to select model");
        }
    };

    const handleCustomGgufLink = async () => {
        if (!customGgufPath.trim()) return;
        setIsLinkingCustom(true);
        try {
            await api.geoaiSelectModel(customGgufPath.trim(), 'llama_cpp');
            toast.success("Custom GGUF model linked successfully!");
            setCustomGgufPath('');
            setShowModelModal(false);
            fetchStatus();
        } catch (e) {
            toast.error(`Failed to link custom model: ${e.message || 'Check file path'}`);
        } finally {
            setIsLinkingCustom(false);
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

    const hasAnyModelInstalled = availableModels.some(m => m.is_installed) || (modelInfo && modelInfo.loaded && modelInfo.provider === 'llama_cpp');
    const activeModelName = modelInfo?.name || availableModels.find(m => m.is_installed)?.display_name || (hasAnyModelInstalled ? "Qwen 2.5 (1.5B)" : null);

    const qwenModels = availableModels.filter(m => m.family === 'qwen');
    const gemmaModels = availableModels.filter(m => m.family === 'gemma');

    const modalFilteredModels = availableModels.filter(m => {
        if (modalTab === 'qwen') return m.family === 'qwen';
        if (modalTab === 'gemma') return m.family === 'gemma';
        return true;
    });

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
                            <span className="truncate">Connected</span>
                        </div>
                        {memoryInfo && memoryInfo.process_ram_mb > 0 && (
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

                    {/* Single Unified Model Selector Button in Header */}
                    <div className="flex items-center gap-2">
                        {downloadStatus?.status === 'downloading' && (
                            <span className="text-[11px] text-primary flex items-center gap-1.5 animate-pulse border border-primary/30 px-2 py-1 rounded bg-primary/5">
                                <RefreshCw size={11} className="animate-spin" />
                                <span>Downloading Model...</span>
                            </span>
                        )}

                        <button
                            onClick={() => setShowModelModal(true)}
                            className={`px-3 py-1.5 rounded text-xs transition-all flex items-center gap-2 border ${
                                hasAnyModelInstalled
                                    ? 'border-border bg-background hover:border-primary/40 text-text-main shadow-xs'
                                    : 'border-amber-500/40 bg-amber-500/10 text-amber-500 hover:bg-amber-500/20'
                            }`}
                            title="Click to switch or install local SLM models"
                        >
                            {hasAnyModelInstalled ? (
                                <>
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                                    <span className="font-semibold text-[11px] truncate max-w-[160px]">
                                        {activeModelName}
                                    </span>
                                    <ChevronDown size={12} className="text-text-muted" />
                                </>
                            ) : (
                                <>
                                    <AlertTriangle size={13} className="shrink-0" />
                                    <span className="font-semibold text-[11px]">Install / Select Model</span>
                                    <ChevronDown size={12} />
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Message Scroll Area */}
                <div className="flex-1 overflow-y-auto p-3 sm:p-5">
                    {messages.length === 0 ? (
                        /* Empty State: Either Model Installation Gateway or Welcome Prompt Cards */
                        <div className="max-w-4xl mx-auto my-auto py-6 space-y-6">
                            {!hasAnyModelInstalled ? (
                                /* In-Chat Wrapped SLM Installer Gateway Card */
                                <div className="p-5 md:p-6 rounded border border-border bg-surface shadow-xs space-y-5">
                                    <div className="text-center space-y-2">
                                        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-500 text-[11px] font-semibold">
                                            <AlertTriangle size={12} />
                                            <span>No Local SLM Engine Installed</span>
                                        </div>
                                        <h2 className="text-xl font-bold text-text-main">
                                            Install Wrapped Offline Engine
                                        </h2>
                                        <p className="text-xs text-text-muted max-w-lg mx-auto leading-relaxed">
                                            Choose an offline model to enable local geotechnical reasoning wrapped with Groundhog's 213 calculation tools.
                                        </p>
                                    </div>

                                    {/* Active Download Progress Bar */}
                                    {downloadStatus?.status === 'downloading' && (
                                        <div className="p-3.5 rounded border border-primary/40 bg-primary/5 space-y-2">
                                            <div className="flex items-center justify-between text-xs font-semibold text-text-main">
                                                <span className="flex items-center gap-2">
                                                    <RefreshCw size={13} className="animate-spin text-primary" />
                                                    <span>Downloading {downloadStatus.display_name || downloadStatus.model_id}...</span>
                                                </span>
                                                <span className="font-mono text-primary">{downloadStatus.size_mb ? `${downloadStatus.size_mb} MB` : 'Downloading'}</span>
                                            </div>
                                            <div className="w-full bg-border/60 rounded-full h-1.5 overflow-hidden">
                                                <div className="bg-primary h-full rounded-full w-full animate-pulse" />
                                            </div>
                                        </div>
                                    )}

                                    {/* Family Selector Tabs */}
                                    <div className="space-y-3">
                                        <div className="flex border-b border-border">
                                            <button
                                                onClick={() => setGatewayTab('qwen')}
                                                className={`flex-1 py-2 px-3 text-xs font-bold transition-all flex items-center justify-center gap-2 border-b-2 ${
                                                    gatewayTab === 'qwen'
                                                        ? 'border-primary text-primary bg-primary/5'
                                                        : 'border-transparent text-text-muted hover:text-text-main'
                                                }`}
                                            >
                                                <Zap size={13} />
                                                <span>Qwen 2.5 (Fast Tool Calling)</span>
                                            </button>
                                            <button
                                                onClick={() => setGatewayTab('gemma')}
                                                className={`flex-1 py-2 px-3 text-xs font-bold transition-all flex items-center justify-center gap-2 border-b-2 ${
                                                    gatewayTab === 'gemma'
                                                        ? 'border-primary text-primary bg-primary/5'
                                                        : 'border-transparent text-text-muted hover:text-text-main'
                                                }`}
                                            >
                                                <Sparkles size={13} />
                                                <span>Gemma 2 (Research & Synthesis)</span>
                                            </button>
                                        </div>

                                        {gatewayTab === 'qwen' ? (
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                                                {qwenModels.map((model) => (
                                                    <div
                                                        key={model.id}
                                                        className="p-3.5 rounded border border-border bg-background flex flex-col justify-between gap-3 hover:border-primary/40 transition-colors"
                                                    >
                                                        <div className="space-y-1">
                                                            <div className="flex items-center justify-between">
                                                                <span className="text-xs font-bold text-text-main">{model.display_name}</span>
                                                                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface border border-border text-text-muted">
                                                                    {model.size_mb} MB
                                                                </span>
                                                            </div>
                                                            <p className="text-[11px] text-text-muted">{model.description}</p>
                                                        </div>
                                                        <button
                                                            onClick={() => handleSelectModel(model)}
                                                            disabled={downloadStatus?.status === 'downloading'}
                                                            className="w-full py-1.5 px-3 bg-primary text-white rounded text-xs font-semibold hover:bg-primary/90 flex items-center justify-center gap-1.5 transition-all shadow-xs disabled:opacity-50"
                                                        >
                                                            <Download size={12} />
                                                            <span>Install ({model.size_mb} MB)</span>
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                                                {gemmaModels.map((model) => (
                                                    <div
                                                        key={model.id}
                                                        className="p-3.5 rounded border border-border bg-background flex flex-col justify-between gap-3 hover:border-primary/40 transition-colors"
                                                    >
                                                        <div className="space-y-1">
                                                            <div className="flex items-center justify-between">
                                                                <span className="text-xs font-bold text-text-main">{model.display_name}</span>
                                                                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface border border-border text-text-muted">
                                                                    {model.size_mb} MB
                                                                </span>
                                                            </div>
                                                            <p className="text-[11px] text-text-muted">{model.description}</p>
                                                        </div>
                                                        <button
                                                            onClick={() => handleSelectModel(model)}
                                                            disabled={downloadStatus?.status === 'downloading'}
                                                            className="w-full py-1.5 px-3 bg-primary text-white rounded text-xs font-semibold hover:bg-primary/90 flex items-center justify-center gap-1.5 transition-all shadow-xs disabled:opacity-50"
                                                        >
                                                            <Download size={12} />
                                                            <span>Install ({model.size_mb} MB)</span>
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        {/* Auto-detect and custom GGUF */}
                                        <div className="pt-2 flex flex-wrap items-center justify-between gap-2 text-[11px]">
                                            <button
                                                onClick={handleAutoLink}
                                                className="text-primary font-semibold hover:underline flex items-center gap-1"
                                            >
                                                <RefreshCw size={11} />
                                                <span>Auto-detect installed desktop bundle</span>
                                            </button>

                                            <button
                                                onClick={() => setShowModelModal(true)}
                                                className="text-text-muted hover:text-text-main underline"
                                            >
                                                Custom GGUF / advanced settings
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                /* Standard Welcome Banner When Model is Installed */
                                <div className="flex flex-col items-center justify-center text-center py-4">
                                    <GeoAILogo size={44} variant="badge" className="mb-2.5" />
                                    <h2 className="text-base font-bold text-text-main mb-1">
                                        Geotechnical Intelligence Assistant
                                    </h2>
                                    <p className="text-xs text-text-muted max-w-lg mb-4 leading-relaxed">
                                        Offline Small Language Model executing 213 deterministic Groundhog calculations with strict parameter validation and provenance tracking.
                                    </p>
                                </div>
                            )}

                            {/* Prompt Cards (Always available to test immediately) */}
                            <div className="space-y-2">
                                <div className="text-[11px] font-semibold text-text-muted uppercase tracking-wider px-1">
                                    Quick Geotechnical Analyses
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
                                    {promptCards.map((card, idx) => (
                                        <div
                                            key={idx}
                                            onClick={() => handleSendMessage(card.prompt)}
                                            className="p-3 rounded border border-border bg-surface hover:border-primary/50 hover:bg-background transition-colors cursor-pointer space-y-1 group"
                                        >
                                            <div className="text-xs font-bold text-text-main group-hover:text-primary transition-colors">
                                                {card.title}
                                            </div>
                                            <div className="text-[11px] text-text-muted line-clamp-2">
                                                {card.prompt}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        /* Message List */
                        <div className="max-w-4xl mx-auto space-y-4">
                            {messages.map((msg) => {
                                const isEditing = editingMsgId === msg.id;

                                return (
                                    <div
                                        key={msg.id}
                                        className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} group`}
                                    >
                                        {msg.sender === 'ai' && (
                                            <GeoAILogo size={26} variant="badge" className="mt-0.5 shrink-0" />
                                        )}

                                        <div className={`max-w-[88%] space-y-1.5 ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                                            {isEditing ? (
                                                /* Inline Edit Box */
                                                <div className="w-full bg-surface border border-primary rounded p-3 space-y-2 text-xs shadow-sm">
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
                                                    className={`p-3.5 rounded text-xs leading-relaxed relative ${
                                                        msg.sender === 'user'
                                                            ? 'bg-primary text-white shadow-xs'
                                                            : 'bg-surface border border-border text-text-main shadow-xs'
                                                    }`}
                                                >
                                                    <div className="whitespace-pre-wrap">
                                                        {msg.text}
                                                    </div>

                                                    {/* Message Actions & Timestamp */}
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
                                                <div className="p-3 rounded border border-border bg-surface text-xs space-y-2.5 shadow-xs">
                                                    <div className="flex items-center justify-between">
                                                        <span className="font-semibold text-primary flex items-center gap-1.5">
                                                            <Zap size={12} />
                                                            <span>Routine: <code>{msg.executedTool}</code></span>
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

                                                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5 bg-background p-2 rounded border border-border">
                                                        {Object.entries(msg.results.result || msg.results).map(([k, v]) => {
                                                            if (k.startsWith('_')) return null;
                                                            return (
                                                                <div key={k} className="p-1.5 rounded bg-surface border border-border/50">
                                                                    <div className="text-[9px] font-bold text-text-muted uppercase truncate">{k}</div>
                                                                    <div className="text-xs font-semibold text-text-main truncate">
                                                                        {typeof v === 'number' ? v.toFixed(3) : String(v)}
                                                                    </div>
                                                                </div>
                                                            );
                                                        })}
                                                    </div>

                                                    {msg.results._provenance && (
                                                        <div className="text-[10px] text-text-muted pt-1 border-t border-border/40 flex items-center justify-between">
                                                            <span>{msg.results._provenance.method}</span>
                                                            <span className="font-mono text-[9px]">{msg.results._provenance.standard}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}

                            {isLoading && (
                                <div className="flex items-center gap-2 text-xs text-text-muted pl-1">
                                    <RefreshCw size={12} className="animate-spin text-primary" />
                                    <span>Reasoning and executing Groundhog calculation...</span>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>
                    )}
                </div>

                {/* --- Bottom Input Box --- */}
                <div className="border-t border-border bg-surface px-4 py-3 shrink-0 flex items-center justify-center">
                    <div className="w-full max-w-4xl flex items-end gap-2 bg-background border border-border focus-within:border-primary rounded p-2 transition-colors shadow-xs">
                        <textarea
                            ref={textareaRef}
                            value={inputValue}
                            onChange={(e) => {
                                setInputValue(e.target.value);
                                adjustTextareaHeight();
                            }}
                            onKeyDown={handleKeyDown}
                            rows={1}
                            placeholder="Enter geotechnical query, soil parameters, or calculation request..."
                            className="flex-1 resize-none bg-transparent px-2 py-1 text-xs text-text-main placeholder:text-text-muted focus:outline-none max-h-40 leading-relaxed"
                        />

                        <button
                            onClick={() => handleSendMessage()}
                            disabled={!inputValue.trim() || isLoading}
                            className="p-2 bg-primary text-white rounded hover:bg-primary/90 disabled:opacity-30 disabled:cursor-not-allowed transition-colors shrink-0 flex items-center justify-center h-8 w-8"
                        >
                            <Send size={14} />
                        </button>
                    </div>
                </div>
            </div>

            {/* --- Unified Model Selector Modal --- */}
            <AnimatePresence>
                {showModelModal && (
                    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
                        <div className="w-full max-w-lg bg-surface border border-border rounded shadow-xl overflow-hidden flex flex-col max-h-[85vh]">
                            <div className="p-4 border-b border-border flex items-center justify-between shrink-0">
                                <div className="flex items-center gap-2">
                                    <Cpu size={16} className="text-primary" />
                                    <h3 className="text-xs font-bold text-text-main">Local AI Model Manager</h3>
                                </div>
                                <button
                                    onClick={() => setShowModelModal(false)}
                                    className="p-1 hover:bg-background rounded text-text-muted hover:text-text-main"
                                >
                                    <X size={14} />
                                </button>
                            </div>

                            {/* Filter Tabs */}
                            <div className="flex border-b border-border px-4 bg-background/50 shrink-0">
                                <button
                                    onClick={() => setModalTab('all')}
                                    className={`py-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
                                        modalTab === 'all'
                                            ? 'border-primary text-primary'
                                            : 'border-transparent text-text-muted hover:text-text-main'
                                    }`}
                                >
                                    All Models ({availableModels.length})
                                </button>
                                <button
                                    onClick={() => setModalTab('qwen')}
                                    className={`py-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
                                        modalTab === 'qwen'
                                            ? 'border-primary text-primary'
                                            : 'border-transparent text-text-muted hover:text-text-main'
                                    }`}
                                >
                                    Qwen Series
                                </button>
                                <button
                                    onClick={() => setModalTab('gemma')}
                                    className={`py-2 px-3 text-xs font-semibold border-b-2 transition-colors ${
                                        modalTab === 'gemma'
                                            ? 'border-primary text-primary'
                                            : 'border-transparent text-text-muted hover:text-text-main'
                                    }`}
                                >
                                    Gemma Series
                                </button>
                            </div>

                            {/* Model List */}
                            <div className="p-4 space-y-3 overflow-y-auto flex-1">
                                {modalFilteredModels.map((model) => (
                                    <div
                                        key={model.id}
                                        className="p-3.5 rounded border border-border bg-background flex items-center justify-between gap-3"
                                    >
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-bold text-text-main">{model.display_name || model.id}</span>
                                                <span className="text-[10px] text-text-muted font-mono bg-surface px-1.5 py-0.5 rounded border border-border">
                                                    {model.size_mb} MB
                                                </span>
                                                {model.is_installed && (
                                                    <span className="text-[9px] font-semibold text-emerald-500 bg-emerald-500/10 px-1.5 py-0.2 rounded">
                                                        Installed
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-[11px] text-text-muted">{model.description}</p>
                                        </div>

                                        <button
                                            onClick={() => handleSelectModel(model)}
                                            disabled={downloadStatus?.status === 'downloading'}
                                            className={`px-3 py-1.5 rounded text-xs font-semibold shrink-0 transition-colors flex items-center gap-1 ${
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

                                {/* Custom Local GGUF File Linker */}
                                <div className="p-3 rounded border border-border bg-surface space-y-2 mt-4">
                                    <div className="text-xs font-bold text-text-main flex items-center gap-1.5">
                                        <FileCode size={13} className="text-primary" />
                                        <span>Link Custom .GGUF File</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <input
                                            type="text"
                                            value={customGgufPath}
                                            onChange={(e) => setCustomGgufPath(e.target.value)}
                                            placeholder="C:\path\to\model.gguf"
                                            className="flex-1 bg-background border border-border rounded px-2 py-1 text-xs text-text-main placeholder:text-text-muted focus:outline-none focus:border-primary"
                                        />
                                        <button
                                            onClick={handleCustomGgufLink}
                                            disabled={!customGgufPath.trim() || isLinkingCustom}
                                            className="px-2.5 py-1 bg-primary text-white rounded text-xs font-semibold hover:bg-primary/90 transition-colors disabled:opacity-40 shrink-0"
                                        >
                                            Link
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Modal Footer */}
                            <div className="p-3 border-t border-border bg-surface/50 flex items-center justify-between text-[11px] text-text-muted shrink-0">
                                <button
                                    onClick={handleAutoLink}
                                    className="text-primary font-semibold hover:underline flex items-center gap-1"
                                >
                                    <RefreshCw size={11} />
                                    <span>Auto-detect installed desktop bundle</span>
                                </button>
                                {memoryInfo && (
                                    <span className="font-mono">{memoryInfo.process_ram_mb} MB RAM</span>
                                )}
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
