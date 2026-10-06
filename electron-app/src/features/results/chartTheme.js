/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Makes every Plotly figure the backend returns follow the app theme.
 *
 * Groundhog's figures ship with Plotly's default template (light-blue plot area, white grid lines), a
 * fixed pixel width/height and hard-coded black or white line colours. On a themed page that gives blue
 * panels, invisible white lines on light backgrounds, invisible black lines on dark ones, charts wider than
 * their card, and an empty `title: {}`. `themeFigure` replaces all of that with colours read from the live
 * CSS theme and leaves the data, axis titles, ranges and tick settings the calculation chose untouched.
 */

const cssVar = (css, name, fallback) => css.getPropertyValue(name).trim() || fallback;

/** Concrete colours for the current theme (Plotly cannot resolve CSS variables). */
export function readChartPalette() {
    const root = document.documentElement;
    const css = getComputedStyle(root);
    const isDark = root.classList.contains('dark');
    const text = cssVar(css, '--color-text-main', isDark ? '#e9f3ed' : '#13201a');
    const muted = cssVar(css, '--color-text-muted', isDark ? '#a3b5ab' : '#51605a');
    const border = cssVar(css, '--color-border', isDark ? '#1f3027' : '#d6e2d8');
    const borderStrong = cssVar(css, '--color-border-strong', isDark ? '#2e4538' : '#b9cdbd');
    const surface = cssVar(css, '--color-surface', isDark ? '#0d1814' : '#ffffff');
    const primary = cssVar(css, '--color-primary', isDark ? '#a9cb7a' : '#5f8445');
    return {
        isDark, text, muted, border, borderStrong, surface, primary,
        grid: isDark ? 'rgba(163, 181, 171, 0.14)' : 'rgba(81, 96, 90, 0.14)',
        zero: isDark ? 'rgba(163, 181, 171, 0.35)' : 'rgba(81, 96, 90, 0.35)',
        // Categorical series: the logo green first, then warm and teal accents that stay distinct from each other.
        series: isDark
            ? [primary, '#e3b45c', '#6fb3a3', '#d98a5a', '#c9dc8e', '#b7a8d9', '#e0a0b8']
            : [primary, '#b7791f', '#2c6e63', '#9a4d1e', '#7a9a3a', '#6d5fa5', '#a3294f'],
        // Sequential scale for heatmaps / contours: from the surface colour up to the primary green.
        sequential: [[0, isDark ? '#16211b' : '#f0f5ea'], [0.5, isDark ? '#6a8e4e' : '#accc7c'], [1, primary]],
    };
}

// ---- colour helpers -------------------------------------------------------------------------------

const NAMED = { black: [0, 0, 0], white: [255, 255, 255] };
const DEFAULT_PLOTLY_COLORS = new Set([
    '#636efa', '#ef553b', '#00cc96', '#ab63fa', '#ffa15a', '#19d3f3', '#ff6692', '#b6e880', '#ff97ff', '#fecb52',
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#3b82f6', 'blue',
]);

function parseColor(value) {
    if (typeof value !== 'string') return null;
    const v = value.trim().toLowerCase();
    if (NAMED[v]) return NAMED[v];
    let m = /^#([0-9a-f]{3})$/.exec(v);
    if (m) return [...m[1]].map((c) => parseInt(c + c, 16));
    m = /^#([0-9a-f]{6})/.exec(v);
    if (m) return [0, 2, 4].map((i) => parseInt(m[1].slice(i, i + 2), 16));
    m = /^rgba?\(([^)]+)\)/.exec(v);
    if (m) {
        const parts = m[1].split(',').map((s) => parseFloat(s));
        return parts.length >= 3 && parts.slice(0, 3).every(Number.isFinite) ? parts.slice(0, 3) : null;
    }
    return null;
}

const isNeutralInk = (rgb) => rgb && Math.max(...rgb) - Math.min(...rgb) < 14 && (Math.max(...rgb) < 40 || Math.min(...rgb) > 225);

/** A line / text colour that is visible on the themed background (black and white become the theme ink). */
const inkFor = (color, palette) => (isNeutralInk(parseColor(color)) ? palette.text : color);

/** Series colours: Plotly's stock palette is replaced by the theme palette, explicit custom colours are kept. */
const seriesColor = (color, palette, index = 0) => {
    if (typeof color !== 'string') return color;
    const key = color.trim().toLowerCase();
    if (DEFAULT_PLOTLY_COLORS.has(key)) return palette.series[index % palette.series.length];
    return inkFor(color, palette);
};

// ---- figure theming -------------------------------------------------------------------------------

const AXIS_KEY = /^[xyz]axis\d*$/;
const COLORSCALE_DEFAULT_TYPES = new Set(['heatmap', 'contour', 'histogram2d', 'heatmapgl', 'surface']);
const BLUE_SCALES = new Set(['blues', 'plotly3', 'ice', 'viridis', 'bluered', 'electric', 'portland']);

function themeAxis(axis = {}, palette) {
    const title = axis.title && typeof axis.title === 'object' ? axis.title : axis.title ? { text: axis.title } : undefined;
    return {
        ...axis,
        automargin: true,
        gridcolor: palette.grid,
        zerolinecolor: palette.zero,
        linecolor: palette.borderStrong,
        tickcolor: palette.borderStrong,
        showline: axis.showline ?? true,
        tickfont: { ...(axis.tickfont || {}), color: palette.muted, size: 11 },
        ...(title ? { title: { ...title, ...(typeof title.text === 'string' ? { text: title.text.replace(/\$/g, '') } : {}), font: { ...(title.font || {}), color: palette.text, size: 12 }, standoff: 10 } } : {}),
    };
}

function themeTrace(trace, palette, index) {
    if (!trace || typeof trace !== 'object') return trace;
    const next = { ...trace };
    if (next.line && typeof next.line === 'object') {
        next.line = { ...next.line, ...(next.line.color !== undefined ? { color: seriesColor(next.line.color, palette, index) } : {}) };
    }
    if (next.marker && typeof next.marker === 'object') {
        const marker = { ...next.marker };
        if (typeof marker.color === 'string') marker.color = seriesColor(marker.color, palette, index);
        // White marker outlines separate points on light backgrounds; keep them readable on dark ones too.
        if (marker.line && typeof marker.line === 'object') {
            marker.line = { ...marker.line, color: palette.surface, width: marker.line.width ?? 1 };
        }
        if (COLORSCALE_DEFAULT_TYPES.has(next.type) || Array.isArray(marker.color)) {
            if (!marker.colorscale || BLUE_SCALES.has(String(marker.colorscale).toLowerCase())) marker.colorscale = palette.sequential;
        }
        next.marker = marker;
    }
    if (typeof next.fillcolor === 'string') next.fillcolor = seriesColor(next.fillcolor, palette, index);
    if (typeof next.textfont?.color === 'string') next.textfont = { ...next.textfont, color: inkFor(next.textfont.color, palette) };
    if (COLORSCALE_DEFAULT_TYPES.has(next.type) && (!next.colorscale || BLUE_SCALES.has(String(next.colorscale).toLowerCase()))) {
        next.colorscale = palette.sequential;
    }
    if (next.type && ['heatmap', 'contour', 'surface'].includes(next.type) && next.colorbar) {
        next.colorbar = { ...next.colorbar, tickfont: { color: palette.muted }, outlinecolor: palette.border };
    }
    return next;
}

/** Plain-text chart heading: explicit title, Plotly title (string or {text}), else '' (never "undefined"/"no title"). */
export function figureTitle(explicit, layout) {
    const candidates = [explicit, layout?.title?.text, typeof layout?.title === 'string' ? layout.title : null];
    const found = candidates.find((t) => typeof t === 'string' && t.trim());
    return found ? found.replace(/<[^>]+>/g, '').replace(/\$/g, '').trim() : '';
}

/** "Depth [m] vs Cone resistance [MPa]" style subtitle from the axis titles, or ''. */
export function axisSubtitle(layout) {
    const text = (axis) => figureTitle(null, { title: axis?.title });
    const x = text(layout?.xaxis);
    const y = text(layout?.yaxis);
    if (x && y) return `${y} vs ${x}`;
    return y || x || '';
}

/**
 * Returns { data, layout, config } ready for react-plotly.js.
 * The figure's own title is dropped (the card heading shows it); width and height are removed so the
 * chart always fits its container, keeping a requested height within a sensible range.
 */
export function themeFigure(figure, palette) {
    const source = figure?.layout || {};
    const traceCount = (figure?.data || []).length;
    const layout = { ...source };

    delete layout.template; // the default template is what paints the plot area blue
    delete layout.width;
    delete layout.title;

    const requestedHeight = Number(source.height);
    const height = Number.isFinite(requestedHeight) ? Math.min(Math.max(requestedHeight, 320), 720) : 460;

    Object.keys(layout).filter((k) => AXIS_KEY.test(k)).forEach((k) => { layout[k] = themeAxis(layout[k], palette); });
    ['xaxis', 'yaxis'].forEach((k) => { layout[k] = themeAxis(layout[k], palette); });

    return {
        data: (figure?.data || []).map((trace, i) => themeTrace(trace, palette, i)),
        layout: {
            ...layout,
            autosize: true,
            height,
            colorway: palette.series,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { ...(source.font || {}), family: 'Inter, "Segoe UI", system-ui, sans-serif', color: palette.text, size: 12 },
            margin: { t: 24, r: 24, l: 24, b: 24, ...(source.margin || {}), pad: 4 },
            hovermode: source.hovermode || 'closest',
            hoverlabel: { bgcolor: palette.surface, bordercolor: palette.borderStrong, font: { color: palette.text, size: 12 } },
            legend: {
                ...(source.legend || {}),
                font: { color: palette.text, size: 11 },
                bgcolor: 'rgba(0,0,0,0)',
                ...(traceCount > 4 ? { orientation: 'h', y: -0.2, x: 0 } : {}),
            },
            modebar: { bgcolor: 'rgba(0,0,0,0)', color: palette.muted, activecolor: palette.primary },
            annotations: (source.annotations || []).map((a) => ({
                ...a, font: { ...(a.font || {}), color: inkFor(a.font?.color ?? palette.text, palette) },
            })),
            shapes: (source.shapes || []).map((s) => ({
                ...s, line: { ...(s.line || {}), ...(s.line?.color !== undefined ? { color: inkFor(s.line.color, palette) } : {}) },
            })),
        },
        config: { responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'] },
    };
}
