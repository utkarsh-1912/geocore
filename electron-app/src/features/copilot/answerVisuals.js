/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Where each image goes in a GeoAI answer.
 *
 * The backend gives every chart block (a Plotly figure, a line chart, a depth profile) an `id` ("img1", ...) and
 * tells the model, in place of the figure, `{"image_id", "details"}`. The model writes {{image:ID}} in its
 * answer where an image belongs. This module splits the answer at those markers:
 *
 *  - a marker for a known image puts that image there, once (an unknown id or a repeat is dropped silently);
 *  - images the model did not mark are shown after the answer, so a small model that forgets the marker cannot
 *    hide the chart;
 *  - an answer without markers is returned untouched as one text segment (markdown is not re-flowed).
 *
 * Other blocks (tables, metrics, notes) are not handled here: they are shown as before.
 */

const MARKER = /\{\{\s*image\s*:\s*([A-Za-z0-9_-]+)\s*\}\}/g;
const PARTIAL_TAIL = /\{\{[^}]*\}?$/; // a marker still being streamed: hidden rather than shown as text
export const CHART_TYPES = ['figure', 'xy', 'depth_profile'];

const isImage = (v) => v && v.id && CHART_TYPES.includes(v.type);

export const imagesOf = (visuals) => (visuals || []).filter(isImage);

export function placeImages(text = '', visuals = []) {
    const byId = new Map(imagesOf(visuals).map((v) => [v.id, v]));
    const source = String(text).replace(PARTIAL_TAIL, '');
    const matches = [...source.matchAll(MARKER)];
    if (!matches.length) {
        return { segments: source ? [{ kind: 'text', text: source }] : [], after: [...byId.values()] };
    }

    const placed = new Set();
    const segments = [];
    let last = 0;
    const pushText = (chunk) => {
        if (chunk.trim()) segments.push({ kind: 'text', text: chunk.trim() });
    };
    for (const match of matches) {
        pushText(source.slice(last, match.index));
        const block = byId.get(match[1]);
        if (block && !placed.has(block.id)) {
            placed.add(block.id);
            segments.push({ kind: 'image', block });
        }
        last = match.index + match[0].length;
    }
    pushText(source.slice(last));
    return { segments, after: [...byId.values()].filter((v) => !placed.has(v.id)) };
}

/** The answer text without markers (for copying the answer to the clipboard or exporting it). */
export const stripImageMarkers = (text = '') => String(text).replace(MARKER, '').replace(/\n{3,}/g, '\n\n').trim();
