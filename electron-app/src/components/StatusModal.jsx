/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X, RefreshCw, Copy, Check, Server, Gauge, CircleCheck, CircleAlert, CircleX, Loader2, PowerOff
} from 'lucide-react';
import { toast } from 'sonner';
import { api } from '../api/client';
import { GeoAILogo } from './common/GeoAILogo';

const POLL_INTERVAL_MS = 3000;
const LATENCY_SAMPLES = 24;

const TONES = {
    ok: { text: 'text-success', bg: 'bg-success/10', dot: 'bg-success', ring: 'ring-success/25', Icon: CircleCheck },
    warn: { text: 'text-warning', bg: 'bg-warning/10', dot: 'bg-warning', ring: 'ring-warning/25', Icon: CircleAlert },
    error: { text: 'text-error', bg: 'bg-error/10', dot: 'bg-error', ring: 'ring-error/25', Icon: CircleX },
    idle: { text: 'text-text-muted', bg: 'bg-surface-muted', dot: 'bg-text-subtle', ring: 'ring-border', Icon: CircleAlert },
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

/** Overall state derived from the app's health poll plus the latest diagnostics snapshot. */
const summarize = (backendStatus, details, fetchError) => {
    if (backendStatus === 'connecting' && !details) {
        return { tone: 'warn', title: 'Engine starting', subtitle: 'The calculation engine is booting. This usually takes a few seconds.' };
    }
    if (backendStatus === 'offline' || (fetchError && !details)) {
        return { tone: 'error', title: 'Engine unreachable', subtitle: 'Calculations and GeoAI are unavailable until the engine responds.' };
    }
    if (details && !details.engine?.ready) {
        return { tone: 'warn', title: 'Warming up', subtitle: 'Engine is online and loading calculation modules in the background.' };
    }
    return { tone: 'ok', title: 'All systems operational', subtitle: 'Calculation engine and GeoAI services are responding normally.' };
};

const Sparkline = ({ samples }) => {
    if (samples.length < 2) return <div className="h-7 w-24" />;
    const w = 96, h = 28, pad = 2;
    const max = Math.max(...samples, 50);
    const step = (w - pad * 2) / (LATENCY_SAMPLES - 1);
    const offset = (LATENCY_SAMPLES - samples.length) * step;
    const pts = samples.map((v, i) => [pad + offset + i * step, h - pad - (v / max) * (h - pad * 2)]);
    const line = pts.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
    const area = `${line} L${pts[pts.length - 1][0].toFixed(1)},${h} L${pts[0][0].toFixed(1)},${h} Z`;
    return (
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="text-primary" aria-hidden="true">
            <path d={area} fill="currentColor" opacity="0.12" />
            <path d={line} fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
        </svg>
    );
};

const Pill = ({ tone, children }) => {
    const t = TONES[tone];
    return (
        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold ${t.bg} ${t.text}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${t.dot}`} />
            {children}
        </span>
    );
};

const ServiceRow = ({ icon, name, detail, tone, status, aside }) => (
    <div className="flex items-center gap-3 px-4 py-3">
        <div className="w-9 h-9 shrink-0 rounded-lg bg-surface-muted text-text-muted flex items-center justify-center">
            {icon}
        </div>
        <div className="min-w-0 flex-1">
            <div className="text-sm font-semibold text-text-main">{name}</div>
            <div className="text-xs text-text-muted truncate" title={typeof detail === 'string' ? detail : undefined}>{detail}</div>
        </div>
        {aside}
        <Pill tone={tone}>{status}</Pill>
    </div>
);

const Meter = ({ label, value, total, percent, hint }) => {
    const pct = percent ?? (value != null && total ? (value / total) * 100 : null);
    const tone = pct == null ? 'bg-text-subtle' : pct > 90 ? 'bg-error' : pct > 75 ? 'bg-warning' : 'bg-primary';
    return (
        <div className="space-y-1.5">
            <div className="flex items-baseline justify-between text-xs">
                <span className="font-medium text-text-main">{label}</span>
                <span className="text-text-muted tabular-nums">{hint}</span>
            </div>
            <div className="h-1.5 rounded-full bg-surface-muted overflow-hidden">
                <motion.div
                    className={`h-full rounded-full ${tone}`}
                    initial={false}
                    animate={{ width: `${Math.min(pct ?? 0, 100)}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                />
            </div>
        </div>
    );
};

const Fact = ({ label, value, mono }) => (
    <div className="min-w-0">
        <dt className="text-[11px] uppercase tracking-wide font-semibold text-text-subtle">{label}</dt>
        <dd className={`mt-0.5 text-sm text-text-main truncate ${mono ? 'font-mono text-xs' : 'font-medium'}`} title={value ?? undefined}>{value ?? '—'}</dd>
    </div>
);

const Section = ({ title, children, className = '' }) => (
    <section>
        <h3 className="px-1 mb-2 text-[11px] uppercase tracking-wider font-semibold text-text-subtle">{title}</h3>
        <div className={`rounded-xl border border-border bg-surface ${className}`}>{children}</div>
    </section>
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

    useEffect(() => {
        if (!isOpen) return;
        refresh();
        const id = setInterval(refresh, POLL_INTERVAL_MS);
        return () => clearInterval(id);
    }, [isOpen, refresh]);

    const summary = summarize(backendStatus, details, fetchError);
    const tone = TONES[summary.tone];
    const engine = details?.engine || {};
    const geoai = details?.geoai || {};
    const memory = details?.memory || {};
    const runtime = details?.runtime || {};
    const latestLatency = latencies[latencies.length - 1];
    const reachable = !!details && !fetchError;

    const geoaiState = (() => {
        if (!reachable) return { tone: 'idle', status: 'Unavailable', detail: 'Waiting for engine' };
        if (!geoai.model_path) return { tone: 'idle', status: 'Heuristic', detail: 'No local model configured — using built-in routing' };
        if (geoai.model_file_found === false) return { tone: 'error', status: 'Missing', detail: `Model file not found: ${geoai.model_name}` };
        if (geoai.loaded) return { tone: 'ok', status: 'Loaded', detail: `${geoai.model_name} · in memory` };
        return { tone: 'idle', status: 'Standby', detail: `${geoai.model_name} · loads on first message` };
    })();

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
                        initial={{ opacity: 0, scale: 0.97, y: 12 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.97, y: 12 }}
                        transition={{ duration: 0.18, ease: 'easeOut' }}
                        className="relative w-full max-w-2xl max-h-[88vh] flex flex-col bg-background border border-border rounded-2xl shadow-pop overflow-hidden"
                    >
                        {/* Header / overall state */}
                        <div className="px-6 pt-5 pb-5 bg-surface border-b border-border">
                            <div className="flex items-start gap-4">
                                <div className={`relative w-12 h-12 shrink-0 rounded-xl flex items-center justify-center ring-4 ${tone.bg} ${tone.text} ${tone.ring}`}>
                                    {summary.tone === 'warn' && backendStatus === 'connecting'
                                        ? <Loader2 size={24} className="animate-spin" />
                                        : <tone.Icon size={24} />}
                                </div>
                                <div className="min-w-0 flex-1">
                                    <div className="text-[11px] uppercase tracking-wider font-semibold text-text-subtle">System health</div>
                                    <h2 id="status-title" className="text-lg font-bold text-text-main leading-tight">{summary.title}</h2>
                                    <p className="mt-0.5 text-sm text-text-muted">{summary.subtitle}</p>
                                </div>
                                <div className="flex items-center gap-1 -mr-2 -mt-1">
                                    <button
                                        onClick={refresh}
                                        className="p-2 rounded-lg text-text-muted hover:text-text-main hover:bg-surface-muted transition-colors"
                                        title="Refresh now"
                                        aria-label="Refresh diagnostics"
                                    >
                                        <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                                    </button>
                                    <button
                                        onClick={onClose}
                                        className="p-2 rounded-lg text-text-muted hover:text-text-main hover:bg-surface-muted transition-colors"
                                        aria-label="Close"
                                    >
                                        <X size={18} />
                                    </button>
                                </div>
                            </div>

                            <div className="mt-5 grid grid-cols-3 gap-3">
                                {[
                                    { label: 'Uptime', value: reachable ? formatUptime(details.uptime_seconds) : '—' },
                                    { label: 'Latency', value: latestLatency != null && reachable ? `${latestLatency} ms` : '—', tone: reachable ? latencyTone(latestLatency) : 'idle' },
                                    { label: 'Functions', value: engine.functions_registered ?? '—' },
                                ].map(stat => (
                                    <div key={stat.label} className="rounded-xl bg-surface-muted px-3.5 py-2.5">
                                        <div className="text-[11px] font-medium text-text-muted">{stat.label}</div>
                                        <div className={`text-lg font-bold tabular-nums leading-tight ${stat.tone ? TONES[stat.tone].text : 'text-text-main'}`}>{stat.value}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Body */}
                        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
                            {fetchError && (
                                <div className="flex items-start gap-3 rounded-xl border border-error/30 bg-error/5 px-4 py-3 text-sm">
                                    <CircleX size={18} className="text-error shrink-0 mt-0.5" />
                                    <div>
                                        <div className="font-semibold text-text-main">Diagnostics request failed</div>
                                        <div className="text-text-muted">{fetchError}. {details ? 'Showing the last successful snapshot.' : 'Retrying automatically.'}</div>
                                    </div>
                                </div>
                            )}

                            <Section title="Services" className="divide-y divide-border">
                                <ServiceRow
                                    icon={<Server size={18} />}
                                    name="Calculation engine"
                                    detail={engine.groundhog_version ? `Groundhog ${engine.groundhog_version}` : 'Groundhog'}
                                    tone={!reachable ? (backendStatus === 'connecting' ? 'warn' : 'error') : engine.ready ? 'ok' : 'warn'}
                                    status={!reachable ? (backendStatus === 'connecting' ? 'Starting' : 'Offline') : engine.ready ? 'Ready' : 'Warming up'}
                                />
                                <ServiceRow
                                    icon={<Gauge size={18} />}
                                    name="API response"
                                    detail={reachable ? `Local HTTP · polled every ${POLL_INTERVAL_MS / 1000}s` : 'No response'}
                                    tone={reachable ? latencyTone(latestLatency) : 'error'}
                                    status={reachable ? (latestLatency < 150 ? 'Fast' : latestLatency < 600 ? 'Slow' : 'Degraded') : 'Down'}
                                    aside={<div className="hidden sm:block"><Sparkline samples={latencies} /></div>}
                                />
                                <ServiceRow
                                    icon={<GeoAILogo size={18} />}
                                    name="GeoAI assistant"
                                    detail={
                                        <>
                                            {geoaiState.detail}
                                            {reachable && geoai.tools_registered != null && <span className="text-text-subtle"> · {geoai.tools_registered} tools</span>}
                                        </>
                                    }
                                    tone={geoaiState.tone}
                                    status={geoaiState.status}
                                    aside={geoai.loaded && (
                                        <button
                                            onClick={handleUnload}
                                            disabled={unloading}
                                            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium text-text-muted border border-border hover:text-text-main hover:border-border-strong transition-colors disabled:opacity-50"
                                            title="Release model weights from RAM"
                                        >
                                            {unloading ? <Loader2 size={12} className="animate-spin" /> : <PowerOff size={12} />}
                                            Unload
                                        </button>
                                    )}
                                />
                            </Section>

                            <Section title="Resources" className="p-4 space-y-4">
                                <Meter
                                    label="GeoCore engine"
                                    value={memory.process_ram_mb}
                                    total={memory.system_total_mb}
                                    hint={memory.process_ram_mb != null ? `${formatMb(memory.process_ram_mb)} of ${formatMb(memory.system_total_mb)}` : 'Unavailable'}
                                />
                                <Meter
                                    label="System memory"
                                    percent={memory.system_percent}
                                    hint={memory.system_percent != null ? `${memory.system_percent}% used · ${formatMb(memory.system_available_mb)} free` : 'Unavailable'}
                                />
                            </Section>

                            <Section title="Build" className="p-4">
                                <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-4">
                                    <Fact label="Version" value={details?.version ? `v${details.version}` : null} />
                                    <Fact label="Distribution" value={reachable ? (runtime.frozen ? 'Packaged release' : 'Development') : null} />
                                    <Fact label="Operating system" value={runtime.platform ? `${runtime.platform} ${runtime.platform_release || ''}`.trim() : null} />
                                    <Fact label="Architecture" value={runtime.architecture ? `${runtime.architecture}${memory.cpu_count ? ` · ${memory.cpu_count} threads` : ''}` : null} />
                                    <Fact label="Python" value={runtime.python} mono />
                                    <Fact label="GeoAI runtime" value={geoai.provider} mono />
                                </dl>
                            </Section>
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between gap-3 px-6 py-3 border-t border-border bg-surface text-xs text-text-muted">
                            <span className="flex items-center gap-2">
                                <span className={`w-1.5 h-1.5 rounded-full ${reachable ? 'bg-success animate-pulse' : 'bg-text-subtle'}`} />
                                {lastChecked ? `Live · checked ${lastChecked.toLocaleTimeString()}` : 'Checking…'}
                            </span>
                            <button
                                onClick={handleCopy}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium text-text-main border border-border hover:bg-surface-muted transition-colors"
                            >
                                {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                                {copied ? 'Copied' : 'Copy diagnostics'}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};
