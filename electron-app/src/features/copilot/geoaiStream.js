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

// Longer than several backend keepalives (every 5 s), so only a dead backend trips it.
const STREAM_IDLE_TIMEOUT_MS = 45000;

/**
 * Stream a chat turn. `onText(text)` receives the text to show while streaming; `onStage(stage)`
 * receives the agent's current phase ('checking_tools'|'loading_model'|'thinking'|'calling_tool:<name>'|'writing_answer') so the UI can
 * show what it's actually waiting on instead of a generic spinner.
 * `onVisuals(blocks)` receives the display blocks (tables, charts) as soon as a tool returns, before the model
 * has written its interpretation; the answer places them with {{visual:ID}} markers (see answerVisuals.js).
 * Resolves to { text, executedTool, parameters, results, visuals, outcome: 'done'|'cancelled'|'error', error }.
 * Throws only when the request could not be started (the caller may fall back).
 */
export async function streamGeoAIChat({ text, context, history, signal, onText = () => {}, onStage = () => {}, onVisuals = () => {} }) {
    const response = await api.geoaiChatStream(text, context, history, signal);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const turn = { text: '', executedTool: null, parameters: null, results: null, visuals: [], outcome: 'done', error: null };
    let buffer = '';

    const handle = (event) => {
        if (event.type === 'token' && event.content) {
            turn.text += event.content;
            onText(turn.text);
        } else if (event.type === 'stage') {
            // A new phase starts with nothing shown yet: clear any stale text so the stage
            // label (rendered while the bubble is empty) takes over.
            turn.text = '';
            onStage(event.content);
            onText('');
        } else if (event.type === 'tool_start') {
            turn.executedTool = event.tool_name;
            turn.parameters = event.tool_args;
            // Shown as a stage (with the timer), not as fixed bubble text.
            onStage(`calling_tool:${event.tool_name}`);
            onText('');
        } else if (event.type === 'tool_result') {
            turn.results = event.tool_result;
            turn.text = '';
            if (event.visuals?.length) {
                turn.visuals = [...turn.visuals, ...event.visuals];
                onVisuals(turn.visuals);
            }
        } else if (event.type === 'cancelled') {
            turn.outcome = 'cancelled';
        } else if (event.type === 'error') {
            turn.outcome = 'error';
            turn.error = event.content || 'GeoAI failed to answer.';
        }
    };

    // The backend sends a keepalive every few seconds while the model works, so a silent stream
    // means the backend is dead or wedged, not just slow: stop waiting instead of spinning forever.
    let stalled = false;
    let idleTimer = null;
    const armIdleTimer = () => {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(() => {
            stalled = true;
            reader.cancel().catch(() => {});
        }, STREAM_IDLE_TIMEOUT_MS);
    };

    try {
        armIdleTimer();
        while (true) {
            const { done, value } = await reader.read();
            armIdleTimer();
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
    } finally {
        clearTimeout(idleTimer);
    }
    if (stalled && !signal?.aborted) {
        api.geoaiCancel().catch(() => {});  // free the model for the next question
        turn.outcome = 'error';
        turn.error = 'GeoAI stopped responding. The request was cancelled; please try again.';
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

/** Compact elapsed time: 45s, 1m 05s, 1h 02m. */
export function formatElapsed(totalSeconds) {
    const s = Math.max(0, Math.floor(totalSeconds || 0));
    if (s < 60) return `${s}s`;
    const m = Math.floor(s / 60);
    if (m < 60) return `${m}m ${String(s % 60).padStart(2, '0')}s`;
    return `${Math.floor(m / 60)}h ${String(m % 60).padStart(2, '0')}m`;
}

const STAGE_LABELS = {
    checking_tools: 'Checking for tools...',
    loading_model: 'Loading the local model...',
    thinking: 'Interpreting input...',
    writing_answer: 'Generating output...',
};

/** Progress label for the current agent phase: the local model processes the prompt on the CPU before the first word. */
export function stageLabel(stage, seconds) {
    const base = stage?.startsWith('calling_tool:')
        ? `Calling tool ${stage.slice('calling_tool:'.length)}...`
        : stage?.startsWith('agent:')
            ? `${stage.slice('agent:'.length)} specialist working...`
            : STAGE_LABELS[stage] || 'Interpreting input...';
    return seconds < 5 ? base : `${base} ${formatElapsed(seconds)}`;
}

const STEP_TITLES = {
    checking_tools: ['Checking available tools', 'Matching your question against the GeoCore tool registry'],
    loading_model: ['Loading the local model', 'Reading the model weights into memory'],
    thinking: ['Interpreting your request', 'Working out the intent, parameters and units'],
    writing_answer: ['Writing the answer', 'Explaining the result from the evidence gathered'],
};

/** Human title + one-line description of an agent stage, for the process trace. */
export function describeStage(stage) {
    if (stage?.startsWith('calling_tool:')) {
        const tool = stage.slice('calling_tool:'.length);
        return { title: `Running ${tool}`, hint: 'Deterministic Groundhog / GeoCore calculation', tool };
    }
    if (stage?.startsWith('agent:')) {
        return { title: `${stage.slice('agent:'.length)} specialist`, hint: 'Delegated to a specialist agent' };
    }
    const [title, hint] = STEP_TITLES[stage] || ['Working', ''];
    return { title, hint };
}

/**
 * Records the stages of one turn with timestamps, so the UI can show a live checklist while the
 * model works and keep it on the finished message. `onChange(steps)` gets a fresh array each time.
 */
export function createTraceRecorder(onChange = () => {}) {
    const startedAt = Date.now();
    const steps = [];
    const closeActive = () => {
        const last = steps[steps.length - 1];
        if (last && last.endedAt == null) last.endedAt = Date.now();
    };
    const emit = () => onChange(steps.map((step) => ({ ...step })));
    return {
        stage(stage) {
            if (!stage) return;
            const last = steps[steps.length - 1];
            if (last && last.stage === stage && last.endedAt == null) return;
            closeActive();
            steps.push({ stage, startedAt: Date.now(), endedAt: null });
            emit();
        },
        /** Close the trace for a finished turn; the result is stored on the message. */
        finish(turn) {
            closeActive();
            if (turn?.executedTool) {
                const toolStep = steps.find((step) => step.stage === `calling_tool:${turn.executedTool}`);
                if (toolStep) toolStep.parameters = turn.parameters || null;
            }
            const outcome = turn?.outcome || 'done';
            if (outcome !== 'done' && steps.length) steps[steps.length - 1].failed = outcome;
            emit();
            return { steps: steps.map((step) => ({ ...step })), totalMs: Date.now() - startedAt, outcome };
        },
    };
}
