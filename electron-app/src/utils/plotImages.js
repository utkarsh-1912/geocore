/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Report images of a result's Plotly figures. Rendered by Plotly itself from the figure data rather
 * than screenshotted from the page, so an exported plot has no modebar (toolbar), ignores whatever
 * zoom/pan the user left on screen (the calculation's own axis ranges and orientation are kept, e.g. a
 * downward depth axis), uses a print palette on white, and every plot of a multi-plot result is included.
 */
import { figureTitle, printChartPalette, themeFigure } from '../features/results/chartTheme';

// Pixel size of the rendered figure; the PDF scales it to the page width, so this sets the
// aspect ratio and how large text appears. Scale 2 keeps lines and labels sharp when printed.
const EXPORT_WIDTH = 800; // ~7.5 pt tick labels across an A4 text width
const EXPORT_SCALE = 2;

/** The Plotly figures in a result: one for 'plotly'/'plot', each of `plots` for 'multi_plot'. */
export const resultFigures = (displayData) => {
    if (!displayData) return [];
    if (displayData.type === 'multi_plot' && Array.isArray(displayData.plots)) return displayData.plots;
    if (displayData.type === 'plotly' || displayData.type === 'plot') return [displayData];
    return [];
};

/**
 * Render each figure of `displayData` to a PNG data URL.
 * Resolves to [{ dataUrl, width, height, title }] (pixel width/height of the figure, before scaling).
 */
export async function renderPlotImages(displayData, fallbackTitle = '') {
    const figures = resultFigures(displayData);
    if (figures.length === 0) return [];
    // The same bundle react-plotly.js loads, so this does not add a second copy of Plotly.
    const { default: Plotly } = await import('plotly.js/dist/plotly');
    const palette = printChartPalette();

    const images = [];
    for (const figure of figures) {
        const themed = themeFigure(figure, palette);
        const height = themed.layout.height;
        const layout = {
            ...themed.layout,
            autosize: false,
            width: EXPORT_WIDTH,
            height,
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#ffffff',
            margin: { ...themed.layout.margin, t: 16, r: 24, b: 16, l: 16 },
        };
        const dataUrl = await Plotly.toImage(
            { data: themed.data, layout, config: { staticPlot: true } },
            { format: 'png', width: EXPORT_WIDTH, height, scale: EXPORT_SCALE },
        );
        images.push({
            dataUrl,
            width: EXPORT_WIDTH,
            height,
            title: figureTitle(figure.title, figure.layout) || fallbackTitle,
        });
    }
    return images;
}
