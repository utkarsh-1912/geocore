/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Renders a GeoAI answer with its images (charts) placed where the model marked them with {{image:ID}} and
 * the unmarked ones after the answer. Text is rendered exactly as before (MarkdownText). Placement rules:
 * ./answerVisuals.js. Block formats: python-backend/core/geoai/visuals.py.
 */
import React, { useMemo } from 'react';
import { MarkdownText } from './MarkdownText';
import { ThemedChart } from '../results/ThemedChart';
import { placeImages } from './answerVisuals';
import { depthProfileFigure, xyFigure } from './visualFigures';

export const ImageBlock = ({ block }) => {
    switch (block.type) {
        case 'figure': return <ThemedChart figure={block.figure} title={block.title} />;
        case 'xy': return <ThemedChart figure={xyFigure(block)} title={block.title} />;
        case 'depth_profile':
            return (
                <div>
                    <ThemedChart figure={depthProfileFigure(block)} title={block.title} />
                    {block.note && <p className="mt-1 text-[11px] text-text-muted">{block.note}</p>}
                </div>
            );
        default: return null;
    }
};

export const AnswerWithVisuals = ({ text, visuals }) => {
    const plan = useMemo(() => placeImages(text, visuals), [text, visuals]);
    return (
        <div className="space-y-3">
            {plan.segments.map((seg, i) => (seg.kind === 'text'
                ? <MarkdownText key={`t${i}`} text={seg.text} />
                : <div key={seg.block.id} data-image-id={seg.block.id} data-placed="true"><ImageBlock block={seg.block} /></div>))}
            {plan.after.map((b) => <div key={b.id} data-image-id={b.id}><ImageBlock block={b} /></div>)}
        </div>
    );
};

export default AnswerWithVisuals;
