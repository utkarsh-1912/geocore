/**
 * Minimal Markdown renderer for GeoAI answers.
 *
 * Covers what the local model actually emits: headings, paragraphs, **bold**, *italic*,
 * `code`, fenced code blocks, bullet / numbered lists, GFM tables and LaTeX math ($...$, \(...\),
 * $$...$$, \[...\]). Output is built from React elements; the only HTML is KaTeX's rendering of a
 * formula (MathTex), so model text cannot inject markup.
 *
 * Author: Utkarsh Gupta
 * License: GPL v3
 */
import React from 'react';
import { MathTex } from './MathTex';

// Underscore emphasis is not supported: it would mangle identifiers such as phi_eff.
// Math: $$..$$ and \(..\) always; $..$ only when it looks like TeX (see isInlineMath), so "$5 and $10" stays text.
const INLINE = /(`[^`\n]+`|\$\$[^$\n]+?\$\$|\\\([^\n]+?\\\)|\$[^$\n]+?\$|\*\*[^*\n]+?\*\*|(?<![\w*])\*[^*\s](?:[^*\n]*?[^*\s])?\*(?![\w*]))/g;

/** A $..$ span is math when it holds TeX syntax or is a short symbol ("$ e $", "$\phi'$"); prices are not. */
const isInlineMath = (body) => {
    const tex = body.trim();
    return tex.length > 0 && (/[\\^_{}=]/.test(tex) || (tex.length <= 3 && !/^\d/.test(tex)));
};

const renderInline = (text, keyPrefix = '') => {
    const parts = [];
    let last = 0;
    // matchAll iterates a copy of INLINE: the recursive calls for **bold** / *italic* contents
    // must not reset the shared lastIndex, or this loop re-finds the same token forever.
    for (const match of text.matchAll(INLINE)) {
        if (match.index > last) parts.push(text.slice(last, match.index));
        const token = match[0];
        const key = `${keyPrefix}-${match.index}`;
        if (token.startsWith('$$')) {
            parts.push(<MathTex key={key} tex={token.slice(2, -2).trim()} />);
        } else if (token.startsWith('\\(')) {
            parts.push(<MathTex key={key} tex={token.slice(2, -2).trim()} />);
        } else if (token.startsWith('$')) {
            const body = token.slice(1, -1);
            parts.push(isInlineMath(body) ? <MathTex key={key} tex={body.trim()} /> : token);
        } else if (token.startsWith('`')) {
            parts.push(<code key={key} className="px-1 py-px rounded-md bg-background border border-border font-mono text-[0.95em]">{token.slice(1, -1)}</code>);
        } else if (token.startsWith('**')) {
            parts.push(<strong key={key} className="font-semibold">{renderInline(token.slice(2, -2), key)}</strong>);
        } else {
            parts.push(<em key={key}>{renderInline(token.slice(1, -1), key)}</em>);
        }
        last = match.index + token.length;
    }
    if (last < text.length) parts.push(text.slice(last));
    return parts;
};

const TABLE_SEP = /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/;
const BULLET = /^\s*[-*+]\s+(.*)$/;
const ORDERED = /^\s*\d+[.)]\s+(.*)$/;
const ORDERED_START = /^\s*(\d+)[.)]/;
const HEADING = /^(#{1,6})\s+(.*?)\s*#*\s*$/;

const splitRow = (line) => {
    let row = line.trim();
    if (row.startsWith('|')) row = row.slice(1);
    if (row.endsWith('|')) row = row.slice(0, -1);
    return row.split('|').map(c => c.trim());
};

const MATH_OPEN = /^\s*(\$\$|\\\[)/;
const MATH_CLOSE = { '$$': '$$', '\\[': '\\]' };

const isBlockStart = (line, next) =>
    /^\s*```/.test(line) || MATH_OPEN.test(line) || HEADING.test(line) || BULLET.test(line) || ORDERED.test(line)
    || /^\s*([-*_])(\s*\1){2,}\s*$/.test(line)
    || (line.includes('|') && next !== undefined && TABLE_SEP.test(next));

/** Parse Markdown into a list of blocks. Exported for tests. */
export const parseMarkdown = (source = '') => {
    const lines = String(source).replace(/\r\n?/g, '\n').split('\n');
    const blocks = [];
    let i = 0;
    while (i < lines.length) {
        const line = lines[i];
        if (!line.trim()) { i++; continue; }

        if (/^\s*```/.test(line)) {
            const body = [];
            i++;
            while (i < lines.length && !/^\s*```/.test(lines[i])) body.push(lines[i++]);
            i++; // closing fence (or end of a still-streaming block)
            blocks.push({ type: 'code', text: body.join('\n') });
            continue;
        }
        const math = line.match(MATH_OPEN);
        if (math) {
            // $$ ... $$ / \[ ... \]: on one line, or spread over several (closed or still streaming).
            const close = MATH_CLOSE[math[1]];
            const rest = line.trim().slice(math[1].length);
            const body = [];
            if (rest.includes(close)) {
                body.push(rest.slice(0, rest.indexOf(close)));
                i++;
            } else {
                if (rest.trim()) body.push(rest);
                i++;
                while (i < lines.length && !lines[i].includes(close)) body.push(lines[i++]);
                if (i < lines.length) {
                    body.push(lines[i].slice(0, lines[i].indexOf(close)));
                    i++;
                }
            }
            blocks.push({ type: 'math', text: body.join('\n').trim() });
            continue;
        }
        const heading = line.match(HEADING);
        if (heading) {
            blocks.push({ type: 'heading', level: heading[1].length, text: heading[2] });
            i++;
            continue;
        }
        if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) {
            blocks.push({ type: 'rule' });
            i++;
            continue;
        }
        if (line.includes('|') && i + 1 < lines.length && TABLE_SEP.test(lines[i + 1])) {
            const header = splitRow(line);
            const rows = [];
            i += 2;
            while (i < lines.length && lines[i].includes('|') && lines[i].trim()) rows.push(splitRow(lines[i++]));
            blocks.push({ type: 'table', header, rows });
            continue;
        }
        const listRe = BULLET.test(line) ? BULLET : ORDERED.test(line) ? ORDERED : null;
        if (listRe) {
            const items = [];
            while (i < lines.length && lines[i].trim()) {
                const item = lines[i].match(listRe);
                if (item) items.push(item[1]);
                else if (/^\s+\S/.test(lines[i]) && items.length) items[items.length - 1] += ' ' + lines[i].trim();
                else break;
                i++;
            }
            // Keep the source numbering: the model often separates items with blank lines, which
            // splits one list into several that would otherwise each restart at 1.
            const start = listRe === ORDERED ? Number(line.match(ORDERED_START)[1]) : undefined;
            blocks.push({ type: listRe === BULLET ? 'ul' : 'ol', items, start });
            continue;
        }
        const para = [line];
        i++;
        while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i], lines[i + 1])) para.push(lines[i++]);
        blocks.push({ type: 'p', lines: para });
    }
    return blocks;
};

const HEADING_CLASS = ['text-sm font-semibold', 'text-sm font-semibold', 'text-xs font-semibold', 'text-xs font-semibold'];

export const MarkdownText = ({ text, className = '' }) => {
    const blocks = parseMarkdown(text);
    return (
        <div className={`space-y-2 break-words ${className}`}>
            {blocks.map((b, bi) => {
                const k = `b${bi}`;
                switch (b.type) {
                    case 'heading':
                        return <div key={k} className={`${HEADING_CLASS[Math.min(b.level, 4) - 1]} text-text-main mt-1`}>{renderInline(b.text, k)}</div>;
                    case 'code':
                        return <pre key={k} className="p-2 rounded-md bg-background border border-border font-mono text-[11px] overflow-x-auto whitespace-pre">{b.text}</pre>;
                    case 'rule':
                        return <hr key={k} className="border-border" />;
                    case 'math':
                        return b.text ? <MathTex key={k} tex={b.text} display /> : null;
                    case 'ul':
                    case 'ol': {
                        const List = b.type;
                        return (
                            <List key={k} start={b.start} className={`${b.type === 'ul' ? 'list-disc' : 'list-decimal'} pl-5 space-y-0.5`}>
                                {b.items.map((item, ii) => <li key={ii}>{renderInline(item, `${k}-${ii}`)}</li>)}
                            </List>
                        );
                    }
                    case 'table':
                        return (
                            <div key={k} className="overflow-x-auto">
                                <table className="border-collapse text-[11px]">
                                    <thead>
                                        <tr>
                                            {b.header.map((h, hi) => (
                                                <th key={hi} className="border border-border bg-background px-2 py-1 text-left font-semibold">{renderInline(h, `${k}-h${hi}`)}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {b.rows.map((row, ri) => (
                                            <tr key={ri}>
                                                {b.header.map((_, ci) => (
                                                    <td key={ci} className="border border-border px-2 py-1 align-top">{renderInline(row[ci] ?? '', `${k}-${ri}-${ci}`)}</td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        );
                    default:
                        return (
                            <p key={k}>
                                {b.lines.map((l, li) => (
                                    <React.Fragment key={li}>
                                        {li > 0 && <br />}
                                        {renderInline(l, `${k}-${li}`)}
                                    </React.Fragment>
                                ))}
                            </p>
                        );
                }
            })}
        </div>
    );
};

export default MarkdownText;
