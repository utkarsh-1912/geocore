/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X, RefreshCw, Copy, Check, Activity, Server, Gauge, MemoryStick, Info,
    CircleX, Loader2, PowerOff
} from 'lucide-react';
import { toast } from 'sonner';
import { api } from '../api/client';
import { GeoAILogo } from './common/GeoAILogo';

const POLL_INTERVAL_MS = 3000;
const LATENCY_SAMPLES = 30;

const TONES = {
    ok: { text: 'text-success', bg: 'bg-success/10', border: 'border-success/30', dot: 'bg-success' },
    warn: { text: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/30', dot: 'bg-warning' },
    error: { text: 'text-error', bg: 'bg-error/10', border: 'border-error/30', dot: 'bg-error' },
    idle: { text: 'text-text-muted', bg: 'bg-surface-muted', border: 'border-border', dot: 'bg-text-subtle' },
};

const formatUptime = (seconds) => {
    if (seconds == null) return '—';
    const s = Math.floor(seconds);
    const d = Math.floor(s / 86400);
    const h = Math.floor((s % 86400) / 3600);
    const m = Math.floor((s % 3600) / 60);
    if (d) return `${d}d ${h}h`;
    if (h) return `${h}h ${m}m`;
    if (m) return `${m}m ${s % 60}s`;
    return `${s}s`;
};

const formatMb = (mb) => {
    if (mb == null) return '—';
    return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${Math.round(mb)} MB`;
};

const latencyTone = (ms) => (ms == null ? 'idle' : ms < 150 ? 'ok' : ms < 600 ? 'warn' : 'error');

/** Overall state from the app's health poll plus the latest diagnostics snapshot. */
const summarize = (backendStatus, details, fetchError) => {
    if (backendStatus === 'connecting' && !details) {
        return { tone: 'warn', title: 'Engine starting', subtitle: 'The calculation engine is booting — usually a few seconds.' };
    }
    if (backendStatus === 'offline' || (fetchError && !details)) {
        return { tone: 'error', title: 'Engine unreachable', subtitle: 'Calculations and GeoAI are unavailable until the engine responds.' };
    }
    if (details && !details.engine?.ready) {
        return { tone: 'warn', title: 'Warming up', subtitle: 'Engine is online and loading calculation modules in the background.' };
    }
    if (details?.geoai?.model_file_found === false) {
        return { tone: 'warn', title: 'Running with warnings', subtitle: 'The configured GeoAI model file is missing. Calculations are unaffected.' };
    }
    return { tone: 'ok', title: 'All systems operational', subtitle: 'Calculation engine and GeoAI services are responding normally.' };
};

const Badge = ({ tone, children }) => {
    const t = TONES[tone];
    return (
        <span className={`inline-flex items-center gap-1.5 px-1.5 py-0.5 rounded border text-[10px] uppercase font-bold tracking-wider whitespace-nowrap ${t.bg} ${t.border} ${t.text}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${t.dot}`} />
            {children}
        </span>
    );
};

const Section = ({ icon, title, action, className = '', children }) => (
    <section className={`space-y-3 bg-surface/50 border border-border rounded-md p-4 ${className}`}>
        <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-primary font-bold text-sm">
                {icon}
                <h3>{title}</h3>
            </div>
            {action}
        </div>
        {children}
    </section>
);

const ServiceRow = ({ icon, name, detail, tone, status, action }) => (
    <div className="flex items-center gap-3 p-2.5 bg-background rounded border border-border/50">
        <div className="p-1.5 rounded bg-primary/10 text-primary shrink-0">{icon}</div>
        <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-text-main">{name}</div>
            <div className="text-[11px] text-text-muted truncate">{detail}</div>
        </div>
        {action}
        <Badge tone={tone}>{status}</Badge>
    </div>
);

const Sparkline = ({ samples }) => {
    const w = 240, h = 40, pad = 2;
    if (samples.length < 2) {
        return <div className="h-10 flex items-center text-[11px] text-text-subtle">Collecting samples…</div>;
    }
    const max = Math.max(...samples, 50);
    const step = (w - pad * 2) / (LATENCY_SAMPLES - 1);
    const offset = (LATENCY_SAMPLES - samples.length) * step;
    const pts = samples.map((v, i) => [pad + offset + i * step, h - pad - (v / max) * (h - pad * 2)]);
    const line = pts.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
    const area = `${line} L${pts[pts.length - 1][0].toFixed(1)},${h} L${pts[0][0].toFixed(1)},${h} Z`;
    const [lx, ly] = pts[pts.length - 1];
    return (
        <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" className="w-full h-10 text-primary" aria-hidden="true">
            <path d={area} fill="currentColor" opacity="0.1" />
            <path d={line} fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" vectorEffect="non-scaling-stroke" />
            <circle cx={lx} cy={ly} r="2.5" fill="currentColor" />
        </svg>
    );
};

const Meter = ({ label, percent, hint }) => {
    const color = percent == null ? 'bg-text-subtle' : percent > 90 ? 'bg-error' : percent > 75 ? 'bg-warning' : 'bg-primary';
    return (
        <div className="space-y-1.5">
            <div className="flex items-baseline justify-between gap-2 text-xs">
                <span className="font-semibold text-text-main">{label}</span>
                <span className="text-text-muted tabular-nums truncate">{hint}</span>
            </div>
            <div className="h-1.5 rounded-sm bg-background border border-border/50 overflow-hidden">
                <motion.div
                    className={`h-full ${color}`}
                    initial={false}
                    animate={{ width: `${Math.min(percent ?? 0, 100)}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                />
            </div>
        </div>
    );
};

const Stat = ({ label, value, tone }) => (
    <div className="p-2.5 bg-background rounded border border-border/50">
        <div className="text-[10px] uppercase font-bold tracking-wider text-text-muted">{label}</div>
        <div className={`mt-0.5 text-sm font-bold tabular-nums whitespace-nowrap ${tone ? TONES[tone].text : 'text-text-main'}`}>{value}</div>
    </div>
);

const Fact = ({ label, value, mono }) => (
    <div className="flex justify-between items-center gap-3 text-xs p-1.5 bg-background rounded border border-border/50 min-w-0">
        <span className="text-text-muted shrink-0">{label}</span>
        <span className={`truncate text-right text-text-main ${mono ? 'font-mono text-[11px]' : 'font-semibold'}`} title={value ?? undefined}>
            {value ?? '—'}
        </span>
    </div>
);

export const StatusModal = ({ isOpen, onClose, backendStatus }) => {
    const [details, setDetails] = useState(null);
    const [fetchError, setFetchError] = useState(null);
    const [latencies, setLatencies] = useState([]);
    const [refreshing, setRefreshing] = useState(false);
    const [lastChecked, setLastChecked] = useState(null);
    const [copied, setCopied] = useState(false);
    const [unloading, setUnloading] = useState(false);
    const inFlight = useRef(false);

    const refresh = useCallback(async () => {
        if (inFlight.current) return;
        inFlight.current = true;
        setRefreshing(true);
        try {
            const data = await api.healthDetails();
            setDetails(data);
            setFetchError(null);
            setLatencies(prev => [...prev, data.latencyMs].slice(-LATENCY_SAMPLES));
        } catch (err) {
            setFetchError(err.message || 'Request failed');
        } finally {
            setLastChecked(new Date());
            setRefreshing(false);
            inFlight.current = false;
        }
    }, []);

    // Poll only while the panel is open.
    useEffect(() => {
        if (!isOpen) return;
        refresh();
        const id = setInterval(refresh, POLL_INTERVAL_MS);
        return () => clearInterval(id);
    }, [isOpen, refresh]);

    const summary = summarize(backendStatus, details, fetchError);
    const tone = TONES[summary.tone];
    const reachable = !!details && !fetchError;
    const engine = details?.engine || {};
    const geoai = details?.geoai || {};
    const memory = details?.memory || {};
    const runtime = details?.runtime || {};
    const latest = latencies[latencies.length - 1];
    const avg = latencies.length ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length) : null;
    const peak = latencies.length ? Math.max(...latencies) : null;

    const engineState = !reachable
        ? (backendStatus === 'connecting' ? { tone: 'warn', status: 'Starting' } : { tone: 'error', status: 'Offline' })
        : engine.ready ? { tone: 'ok', status: 'Ready' } : { tone: 'warn', status: 'Warming up' };

    const geoaiState = (() => {
        if (!reachable) return { tone: 'idle', status: 'Unavailable', detail: 'Waiting for engine' };
        const tools = geoai.tools_registered != null ? ` · ${geoai.tools_registered} tools` : '';
        if (!geoai.model_path) return { tone: 'idle', status: 'Heuristic', detail: `No local model configured — built-in routing${tools}` };
        if (geoai.model_file_found === false) return { tone: 'error', status: 'Missing', detail: `Model file not found: ${geoai.model_name}` };
        if (geoai.loaded) return { tone: 'ok', status: 'Loaded', detail: `${geoai.model_name} · in memory${tools}` };
        return { tone: 'idle', status: 'Standby', detail: `${geoai.model_name} · loads on first message${tools}` };
    })();

    const processPct = memory.process_ram_mb != null && memory.system_total_mb
        ? (memory.process_ram_mb / memory.system_total_mb) * 100 : null;

    const handleUnload = async () => {
        setUnloading(true);
        try {
            await api.geoaiUnloadModel();
            toast.success('GeoAI model released from memory');
            refresh();
        } catch (err) {
            toast.error(`Could not unload model: ${err.message}`);
        } finally {
            setUnloading(false);
        }
    };

    const handleCopy = async () => {
        const report = {
            captured_at: new Date().toISOString(),
            app_status: backendStatus,
            latency_ms: { latest, avg, peak },
            user_agent: navigator.userAgent,
            error: fetchError,
            diagnostics: details,
        };
        try {
            await navigator.clipboard.writeText(JSON.stringify(report, null, 2));
            setCopied(true);
            setTimeout(() => setCopied(false), 1800);
        } catch {
            toast.error('Clipboard is not available');
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[60] flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="status-title">
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
                        className="relative w-full max-w-2xl bg-surface border border-border rounded-md shadow-2xl overflow-hidden"
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-border bg-background/50">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded ${tone.bg} ${tone.text}`}>
                                    <Activity size={22} />
                                </div>
                                <div>
                                    <h2 id="status-title" className="text-lg font-bold text-text-main font-display">System Health</h2>
                                    <p className="text-xs text-text-muted">Live engine, GeoAI and resource diagnostics</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={refresh}
                                    className="p-1.5 hover:bg-background rounded text-text-muted hover:text-text-main transition-colors"
                                    title="Refresh now"
                                    aria-label="Refresh diagnostics"
                                >
                                    <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                                </button>
                                <button
                                    onClick={onClose}
                                    className="p-1.5 hover:bg-background rounded text-text-muted hover:text-text-main transition-colors"
                                    aria-label="Close"
                                >
                                    <X size={18} />
                                </button>
                            </div>
                        </div>

                        {/* Overall status strip */}
                        <div className={`flex items-center justify-between gap-3 px-4 py-2.5 border-b ${tone.border} ${tone.bg}`}>
                            <div className="flex items-center gap-2.5 min-w-0">
                                {summary.tone === 'warn' && !reachable
                                    ? <Loader2 size={14} className={`${tone.text} animate-spin shrink-0`} />
                                    : <span className={`w-2 h-2 rounded-full shrink-0 ${tone.dot} ${summary.tone === 'ok' ? 'animate-pulse' : ''}`} />}
                                <span className={`text-sm font-bold whitespace-nowrap ${tone.text}`}>{summary.title}</span>
                                <span className="hidden sm:inline text-xs text-text-muted truncate">— {summary.subtitle}</span>
                            </div>
                            <span className="text-[11px] text-text-muted tabular-nums whitespace-nowrap">
                                {lastChecked ? `Checked ${lastChecked.toLocaleTimeString()}` : 'Checking…'}
                            </span>
                        </div>

                        {/* Content */}
                        <div className="p-6 max-h-[62vh] overflow-y-auto space-y-6">
                            {fetchError && details && (
                                <div className="flex items-start gap-2.5 p-3 rounded border border-error/30 bg-error/5 text-xs">
                                    <CircleX size={16} className="text-error shrink-0" />
                                    <span className="text-text-muted">
                                        <strong className="text-text-main">Last check failed:</strong> {fetchError}. Showing the previous snapshot.
                                    </span>
                                </div>
                            )}

                            <Section icon={<Server size={16} />} title="Services">
                                <div className="space-y-1.5">
                                    <ServiceRow
                                        icon={<Server size={14} />}
                                        name="Calculation engine"
                                        detail={[
                                            engine.groundhog_version ? `Groundhog ${engine.groundhog_version}` : 'Groundhog',
                                            engine.functions_registered != null ? `${engine.functions_registered} functions` : null,
                                        ].filter(Boolean).join(' · ')}
                                        tone={engineState.tone}
                                        status={engineState.status}
                                    />
                                    <ServiceRow
                                        icon={<GeoAILogo size={14} />}
                                        name="GeoAI assistant"
                                        detail={geoaiState.detail}
                                        tone={geoaiState.tone}
                                        status={geoaiState.status}
                                        action={geoai.loaded && (
                                            <button
                                                onClick={handleUnload}
                                                disabled={unloading}
                                                className="flex items-center gap-1 px-2 py-1 rounded border border-border text-[11px] font-semibold text-text-muted hover:text-text-main hover:bg-surface transition-colors disabled:opacity-50"
                                                title="Release model weights from RAM"
                                            >
                                                {unloading ? <Loader2 size={12} className="animate-spin" /> : <PowerOff size={12} />}
                                                Unload
                                            </button>
                                        )}
                                    />
                                </div>
                            </Section>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <Section
                                    icon={<Gauge size={16} />}
                                    title="Performance"
                                    action={reachable && <Badge tone={latencyTone(latest)}>{latest < 150 ? 'Fast' : latest < 600 ? 'Slow' : 'Degraded'}</Badge>}
                                >
                                    <div className="grid grid-cols-3 gap-1.5">
                                        <Stat label="Latency" value={reachable && latest != null ? `${latest} ms` : '—'} tone={reachable ? latencyTone(latest) : undefined} />
                                        <Stat label="Average" value={avg != null ? `${avg} ms` : '—'} />
                                        <Stat label="Uptime" value={reachable ? formatUptime(details.uptime_seconds) : '—'} />
                                    </div>
                                    <div className="p-2 bg-background rounded border border-border/50">
                                        <Sparkline samples={latencies} />
                                        <div className="flex justify-between text-[10px] text-text-subtle mt-1">
                                            <span>Last {LATENCY_SAMPLES} checks · every {POLL_INTERVAL_MS / 1000}s</span>
                                            <span className="tabular-nums">{peak != null ? `peak ${peak} ms` : ''}</span>
                                        </div>
                                    </div>
                                </Section>

                                <Section icon={<MemoryStick size={16} />} title="Resources">
                                    <div className="space-y-4 pt-1">
                                        <Meter
                                            label="GeoCore engine"
                                            percent={processPct}
                                            hint={memory.process_ram_mb != null ? `${formatMb(memory.process_ram_mb)} RAM` : 'Unavailable'}
                                        />
                                        <Meter
                                            label="System memory"
                                            percent={memory.system_percent}
                                            hint={memory.system_percent != null
                                                ? `${memory.system_percent}% · ${formatMb(memory.system_available_mb)} free of ${formatMb(memory.system_total_mb)}`
                                                : 'Unavailable'}
                                        />
                                        <p className="text-[11px] text-text-subtle leading-relaxed">
                                            A loaded GeoAI model is counted in engine memory. It unloads automatically after 15 minutes idle.
                                        </p>
                                    </div>
                                </Section>
                            </div>

                            <Section icon={<Info size={16} />} title="Build & Environment">
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                                    <Fact label="Version" value={details?.version ? `v${details.version}` : null} />
                                    <Fact label="Distribution" value={reachable ? (runtime.frozen ? 'Packaged release' : 'Development') : null} />
                                    <Fact label="Operating system" value={runtime.platform ? `${runtime.platform} ${runtime.platform_release || ''}`.trim() : null} />
                                    <Fact label="Architecture" value={runtime.architecture ? `${runtime.architecture}${memory.cpu_count ? ` · ${memory.cpu_count} threads` : ''}` : null} />
                                    <Fact label="Python" value={runtime.python} mono />
                                    <Fact label="GeoAI runtime" value={geoai.provider} mono />
                                </div>
                            </Section>
                        </div>

                        {/* Footer */}
                        <div className="p-3 bg-background/80 border-t border-border flex items-center justify-between">
                            <button
                                onClick={handleCopy}
                                className="flex items-center gap-1.5 px-3 py-1.5 border border-border text-text-main text-xs font-semibold rounded hover:bg-surface transition-colors"
                            >
                                {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                                {copied ? 'Copied' : 'Copy diagnostics'}
                            </button>
                            <button
                                onClick={onClose}
                                className="px-4 py-1.5 bg-primary text-on-primary text-xs font-semibold rounded hover:bg-primary/90 transition-all shadow-sm"
                            >
                                Done
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
