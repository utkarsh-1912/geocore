/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Cpu, Globe, Server, Code, ShieldCheck } from 'lucide-react';

// Helper to detect OS
const getOS = () => {
    const userAgent = window.navigator.userAgent;
    const platform = window.navigator.platform;
    const macosPlatforms = ['Macintosh', 'MacIntel', 'MacPPC', 'Mac68K'];
    const windowsPlatforms = ['Win32', 'Win64', 'Windows', 'WinCE'];
    const iosPlatforms = ['iPhone', 'iPad', 'iPod'];

    let os = 'Unknown OS';

    if (macosPlatforms.indexOf(platform) !== -1) {
        os = 'macOS';
    } else if (iosPlatforms.indexOf(platform) !== -1) {
        os = 'iOS';
    } else if (windowsPlatforms.indexOf(platform) !== -1) {
        os = 'Windows';
    } else if (/Android/.test(userAgent)) {
        os = 'Android';
    } else if (!os && /Linux/.test(platform)) {
        os = 'Linux';
    }

    return os;
};

export const StatusModal = ({ isOpen, onClose, backendStatus }) => {
    const osName = React.useMemo(() => getOS(), []);
    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
                    />

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="relative w-full max-w-lg bg-surface border border-border rounded-lg shadow-2xl overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-border bg-background/50">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${backendStatus === 'online' ? 'bg-primary/10 text-primary' : 'bg-red-500/10 text-red-500'}`}>
                                    <Cpu size={24} />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-text-main font-display">System Health</h2>
                                    <p className="text-sm text-text-muted">Diagnostic and version information</p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-background rounded-full text-text-muted hover:text-text-main transition-colors"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="p-6 space-y-6">
                            {/* Live Connection Status */}
                            <div className={`p-3 rounded-lg border flex items-center justify-between transition-colors ${backendStatus === 'online' ? 'bg-primary/5 border-primary/20' : 'bg-red-500/5 border-red-500/20'}`}>
                                <div className="flex items-center gap-3">
                                    <div className={`w-3 h-3 rounded-full ${backendStatus === 'online' ? 'bg-primary animate-pulse' : 'bg-red-500'}`} />
                                    <span className="font-bold text-text-main">Backend Engine</span>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-[10px] uppercase font-bold tracking-widest ${backendStatus === 'online' ? 'bg-primary/10 text-primary' : 'bg-red-500/10 text-red-500'}`}>
                                    {backendStatus === 'online' ? 'Connected' : 'Disconnected'}
                                </span>
                            </div>

                            {/* Details Grid */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-background/50 border border-border rounded-xl space-y-2">
                                    <div className="flex items-center gap-2 text-text-muted text-[10px] uppercase font-bold tracking-wider">
                                        <Code size={14} />
                                        <span>Version</span>
                                    </div>
                                    <p className="font-bold text-text-main">v1.0.1</p>
                                </div>
                                <div className="p-4 bg-background/50 border border-border rounded-xl space-y-2">
                                    <div className="flex items-center gap-2 text-text-muted text-[10px] uppercase font-bold tracking-wider">
                                        <Globe size={14} />
                                        <span>Environment</span>
                                    </div>
                                    <p className="font-bold text-text-main">{osName}</p>
                                </div>
                                <div className="p-4 bg-background/50 border border-border rounded-xl space-y-2">
                                    <div className="flex items-center gap-2 text-text-muted text-[10px] uppercase font-bold tracking-wider">
                                        <Server size={14} />
                                        <span>Engine</span>
                                    </div>
                                    <p className="font-bold text-primary">Groundhog v1.2</p>
                                </div>
                                <div className="p-4 bg-background/50 border border-border rounded-xl space-y-2">
                                    <div className="flex items-center gap-2 text-text-muted text-[10px] uppercase font-bold tracking-wider">
                                        <ShieldCheck size={14} />
                                        <span>Build Status</span>
                                    </div>
                                    <p className="font-bold text-primary">Release (Stable)</p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
