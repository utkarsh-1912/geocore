/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * One streamed GeoAI chat turn, shared by the Copilot drawer and the full window.
 * The local model can need minutes per answer on a laptop CPU, so a turn can be stopped
 * (AbortController + backend cancel) and reports how it ended instead of spinning forever.
 */
import { useEffect, useState } from 'react';
import { api } from '../../api/client';

/**
 * Stream a chat turn. `onText(text)` receives the text to show while streaming; `onStage(stage)`
 * receives the agent's current phase ('loading_model'|'thinking'|'writing_answer') so the UI can
 * show what it's actually waiting on instead of a generic spinner.
 * Resolves to { text, executedTool, parameters, results, outcome: 'done'|'cancelled'|'error', error }.
 * Throws only when the request could not be started (the caller may fall back).
 */
export async function streamGeoAIChat({ text, context, history, signal, onText = () => {}, onStage = () => {} }) {
    const response = await api.geoaiChatStream(text, context, history, signal);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const turn = { text: '', executedTool: null, parameters: null, results: null, outcome: 'done', error: null };
    let buffer = '';

    const handle = (event) => {
        if (event.type === 'token' && event.content) {
            turn.text += event.content;
            onText(turn.text);
        } else if (event.type === 'stage') {
            // A new phase starts with nothing shown yet: clear any stale "Calculating with X..."
            // text so the stage label (rendered while the bubble is empty) takes over.
            turn.text = '';
            onStage(event.content);
            onText('');
        } else if (event.type === 'tool_start') {
            turn.executedTool = event.tool_name;
            turn.parameters = event.tool_args;
            onText(`Calculating with **${event.tool_name}**...`);
        } else if (event.type === 'tool_result') {
            turn.results = event.tool_result;
            turn.text = '';
        } else if (event.type === 'cancelled') {
            turn.outcome = 'cancelled';
        } else if (event.type === 'error') {
            turn.outcome = 'error';
            turn.error = event.content || 'GeoAI failed to answer.';
        }
    };

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // an event split across chunks completes on the next read
            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                let event;
                try {
                    event = JSON.parse(line.slice(6));
                } catch {
                    continue;
                }
                handle(event);
            }
        }
    } catch (err) {
        if (signal?.aborted) {
            turn.outcome = 'cancelled';
        } else {
            turn.outcome = 'error';
            turn.error = err.message || 'Connection to GeoAI was lost.';
        }
    }
    return turn;
}

/** Stop the running turn: abort the backend model call, then close the stream. */
export function stopGeoAIChat(controller) {
    api.geoaiCancel().catch(() => {});
    controller?.abort();
}

/** Final message text for a finished turn. `shownText` is what the bubble displayed last. */
export function finalTurnText(turn, shownText) {
    const text = turn.text || shownText || '';
    if (turn.outcome === 'cancelled') {
        return text ? `${text}\n\n_Stopped._` : '_Stopped._';
    }
    if (turn.outcome === 'error') {
        return `${text ? `${text}\n\n` : ''}**GeoAI error:** ${turn.error}`;
    }
    return text;
}

/** Whole seconds since `active` became true (0 while inactive). */
export function useElapsedSeconds(active) {
    const [seconds, setSeconds] = useState(0);
    useEffect(() => {
        if (!active) return undefined;
        const started = Date.now();
        const timer = setInterval(() => setSeconds(Math.floor((Date.now() - started) / 1000)), 1000);
        return () => {
            clearInterval(timer);
            setSeconds(0);
        };
    }, [active]);
    return seconds;
}

const STAGE_LABELS = {
    loading_model: 'Loading the local model...',
    thinking: 'Thinking...',
    writing_answer: 'Writing the answer...',
};

/** Progress label for the current agent phase: the local model processes the prompt on the CPU before the first word. */
export function stageLabel(stage, seconds) {
    const base = STAGE_LABELS[stage] || 'Thinking...';
    if (seconds < 5) return base;
    const hint = seconds >= 20 ? ' (local model on CPU; long questions can take a few minutes)' : '';
    return `${base} ${seconds}s${hint}`;
}
