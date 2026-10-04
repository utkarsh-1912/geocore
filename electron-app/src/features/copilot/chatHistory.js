/**
 * Builds the compact conversation history sent with each GeoAI chat request so the
 * model can answer follow-ups ("explain the calculation") about earlier turns.
 * The backend keeps only the last few turns and replays tool results as a
 * deterministic calculation record (see core/geoai/agent.py: history_to_messages).
 */
const MAX_HISTORY_MESSAGES = 6;

// Date.now() alone can repeat for messages/conversations created in the same millisecond
// (e.g. two quick sends that both hit an error fallback path), which React then rejects as
// a duplicate list key — a counter guarantees every generated id is unique.
let idCounter = 0;
export const nextMessageId = (prefix) => `${prefix}-${Date.now()}-${++idCounter}`;

export const buildChatHistory = (messages = []) =>
    messages
        .filter(m => (m.sender === 'user' || m.sender === 'ai') && !m.isError && m.text)
        .slice(-MAX_HISTORY_MESSAGES)
        .map(m => {
            const item = { role: m.sender === 'user' ? 'user' : 'assistant', content: m.text };
            if (m.sender === 'ai' && m.executedTool) {
                item.tool = { name: m.executedTool, arguments: m.parameters || {}, result: m.results ?? null };
            }
            return item;
        });
