/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * One themed chart: a heading (title, else the function name, with the axis names as a subtitle) above a
 * Plotly figure that follows the light/dark theme and always fits its container.
 */
import React, { Suspense, useEffect, useMemo, useState } from 'react';
import { axisSubtitle, figureTitle, readChartPalette, themeFigure } from './chartTheme';

const Plot = React.lazy(() => import('react-plotly.js'));

/** Palette that follows the app theme (the root element's class / style changes on a theme switch). */
export const useChartPalette = () => {
    const [palette, setPalette] = useState(readChartPalette);
    useEffect(() => {
        const observer = new MutationObserver(() => setPalette(readChartPalette()));
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme', 'style'] });
        return () => observer.disconnect();
    }, []);
    return palette;
};

export const ThemedChart = ({ figure, title, fallbackTitle = '', index, total, bare = false }) => {
    const palette = useChartPalette();
    const themed = useMemo(() => themeFigure(figure, palette), [figure, palette]);

    const heading = figureTitle(title, figure?.layout) || fallbackTitle || 'Chart';
    const numbered = total > 1 ? `${heading} · ${index + 1} of ${total}` : heading;
    const subtitle = axisSubtitle(figure?.layout);

    return (
        <div className={`min-w-0 w-full ${bare ? '' : 'rounded-md border border-border bg-surface p-4 shadow-card'}`}>
            <div className="mb-3 min-w-0">
                <h3 className="truncate text-sm font-semibold text-text-main" title={numbered}>{numbered}</h3>
                {subtitle && <p className="truncate text-xs text-text-muted" title={subtitle}>{subtitle}</p>}
            </div>
            <div className="w-full min-w-0 overflow-hidden" style={{ height: themed.layout.height }}>
                <Suspense
                    fallback={
                        <div className="flex h-full w-full items-center justify-center gap-2 text-sm text-text-muted">
                            <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                            Loading chart…
                        </div>
                    }
                >
                    <Plot
                        data={themed.data}
                        layout={themed.layout}
                        config={themed.config}
                        useResizeHandler
                        style={{ width: '100%', height: '100%' }}
                    />
                </Suspense>
            </div>
        </div>
    );
};
