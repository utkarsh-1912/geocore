/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * GeoAI chat state shared by every GeoAI view (the GeoAI tab and the Copilot drawer): the conversations, which
 * one is being answered, its live trace and its stop handle. Kept outside React so that
 *  - both views show and save the same conversations (two copies would overwrite each other's localStorage);
 *  - an answer keeps running when the view that asked moves out of sight, and lands in its conversation.
 * When an answer finishes and nobody is looking at that conversation, it is marked unread and a short chime
 * plays (sidebar dot + history dot).
 */
import { useSyncExternalStore } from 'react';

const STORAGE_KEY = 'geoai_conversations';

/** A value with React-style set (value or updater) and subscribe, for useSyncExternalStore. */
const createStore = (initial) => {
    let value = initial;
    const listeners = new Set();
    return {
        get: () => value,
        set: (next) => {
            const updated = typeof next === 'function' ? next(value) : next;
            if (updated === value) return;
            value = updated;
            listeners.forEach((l) => l());
        },
        subscribe: (listener) => {
            listeners.add(listener);
            return () => listeners.delete(listener);
        },
    };
};

/** [value, set] of a shared store, like useState. */
export const useShared = (store) => [useSyncExternalStore(store.subscribe, store.get), store.set];

const readConversations = () => {
    try {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        return Array.isArray(saved) ? saved : [];
    } catch {
        return [];
    }
};

export const conversationsStore = createStore(readConversations());
conversationsStore.subscribe(() => {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(conversationsStore.get()));
    } catch (e) {
        console.error('Failed to save GeoAI conversations', e);
    }
});

// Id of the conversation being answered (null when idle): one local model, so one answer at a time.
export const loadingConvStore = createStore(null);
export const liveStepsStore = createStore([]);
// The running answer's AbortController (a ref shared by all views: any of them can stop it).
export const abortHandle = { current: null };
// Ids of conversations with an answer nobody has seen yet.
export const unreadStore = createStore([]);

// ------------------------------------------------------------------------------------------- who is looking

// view id -> {visible, convId}: what each mounted GeoAI view shows right now.
const viewers = new Map();
let mounted = 0;

const isLookingAt = (convId) => !document.hidden
    && [...viewers.values()].some((v) => v.visible && v.convId === convId);

/** Register a GeoAI view; returns its unregister. The last view to go stops a running answer. */
export const registerView = (id) => {
    mounted += 1;
    return () => {
        viewers.delete(id);
        mounted -= 1;
        if (mounted === 0) abortHandle.current?.abort();
    };
};

/** A view's current state; clears the unread mark of a conversation it is now showing. */
export const reportView = (id, visible, convId) => {
    viewers.set(id, { visible, convId });
    if (visible && !document.hidden && unreadStore.get().includes(convId)) {
        unreadStore.set((ids) => ids.filter((x) => x !== convId));
    }
};

// Coming back to the app window counts as seeing what is on screen.
if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) return;
        const seen = [...viewers.values()].filter((v) => v.visible).map((v) => v.convId);
        if (seen.length) unreadStore.set((ids) => ids.filter((x) => !seen.includes(x)));
    });
}

/** A short two-note chime (Web Audio, no sound file). Silent if audio is unavailable. */
const playChime = () => {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const notes = [[880, 0], [1318.5, 0.12]];
        notes.forEach(([freq, at]) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.value = freq;
            const t = ctx.currentTime + at;
            gain.gain.setValueAtTime(0.0001, t);
            gain.gain.exponentialRampToValueAtTime(0.15, t + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
            osc.connect(gain).connect(ctx.destination);
            osc.start(t);
            osc.stop(t + 0.4);
        });
        setTimeout(() => ctx.close().catch(() => {}), 800);
    } catch {
        // no audio device or blocked: the dot is still shown
    }
};

/** An answer finished in `convId`: if nobody is looking at it, mark it unread and chime. */
export const answerFinished = (convId) => {
    if (!convId || isLookingAt(convId)) return;
    if (!unreadStore.get().includes(convId)) unreadStore.set((ids) => [...ids, convId]);
    playChime();
};

/** Forget a deleted conversation's unread mark. */
export const forgetUnread = (convId) => unreadStore.set((ids) => ids.filter((x) => x !== convId));
