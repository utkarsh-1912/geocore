/**
 * Answers stopped at the generation cap end with the backend's truncation note
 * (core/geoai/response_guard.py: TRUNCATION_NOTE). The chat offers a "Continue"
 * chip on such answers instead of making the user type the follow-up.
 */
export const TRUNCATION_NOTE = '\n\n*(Answer cut off at the output length limit. Ask GeoAI to continue.)*';

export const CONTINUE_PROMPT = 'continue';

export const isTruncatedAnswer = (text) => typeof text === 'string' && text.endsWith(TRUNCATION_NOTE);

// The note is UI guidance, not part of the answer: keep it out of the history sent to the model.
export const stripTruncationNote = (text) => (isTruncatedAnswer(text) ? text.slice(0, -TRUNCATION_NOTE.length) : text);
