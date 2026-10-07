/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Plotly figures for the GeoAI display blocks that are not already Plotly figures: `xy` (line chart of
 * series) and `depth_profile` (tracks against depth, with layer bands and markers). The block formats are
 * documented in python-backend/core/geoai/visuals.py. Colours are applied by `themeFigure`.
 */

const axisTitle = (label, unit) => (label ? { text: unit ? `${label} [${unit}]` : label } : undefined);

export function xyFigure(block) {
    return {
        data: (block.series || []).map((s) => ({ type: 'scatter', mode: 'lines', name: s.name, x: s.x, y: s.y })),
        layout: {
            xaxis: { title: axisTitle(block.x?.label, block.x?.unit) },
            yaxis: { title: axisTitle(block.y?.label, block.y?.unit) },
            height: 360,
        },
    };
}

/** Step values for an interval series: (value, top), (value, bottom) per interval. */
const stepTrace = (series) => {
    const x = [];
    const y = [];
    (series.value || []).forEach((v, i) => {
        x.push(v, v);
        y.push(series.top[i], series.bottom[i]);
    });
    return { x, y };
};

export function depthProfileFigure(block) {
    const tracks = block.tracks || [];
    const n = Math.max(tracks.length, 1);
    const gap = 0.025;
    const layout = {
        yaxis: { title: { text: 'Depth [m]' }, autorange: 'reversed' },
        showlegend: false,
        height: 420,
        shapes: [],
        annotations: [],
    };
    const data = [];

    tracks.forEach((track, i) => {
        const axis = i === 0 ? '' : String(i + 1);
        layout[`xaxis${axis}`] = {
            domain: [i / n + gap, (i + 1) / n - gap],
            title: axisTitle(track.title, track.unit),
            anchor: 'y',
            side: 'top',
        };
        (track.series || []).forEach((series) => {
            const points = series.kind === 'intervals' ? stepTrace(series) : { x: series.value, y: series.depth };
            data.push({ type: 'scatter', mode: 'lines', name: series.name, x: points.x, y: points.y, xaxis: `x${axis}`, yaxis: 'y' });
        });
    });

    (block.bands || []).forEach((band, i) => {
        layout.shapes.push({
            type: 'rect', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: band.top, y1: band.bottom,
            fillcolor: i % 2 ? 'rgba(169,203,122,0.10)' : 'rgba(120,150,170,0.10)', line: { width: 0 }, layer: 'below',
        });
        if (band.label) {
            layout.annotations.push({ xref: 'paper', yref: 'y', x: 1, xanchor: 'right', y: (band.top + band.bottom) / 2, text: band.label, showarrow: false, font: { size: 10 } });
        }
    });
    (block.markers || []).forEach((m) => {
        layout.shapes.push({ type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: m.depth, y1: m.depth, line: { dash: 'dash', width: 1.5 } });
        layout.annotations.push({ xref: 'paper', yref: 'y', x: 0, xanchor: 'left', y: m.depth, yanchor: 'bottom', text: m.label, showarrow: false, font: { size: 10 } });
    });
    return { data, layout };
}
