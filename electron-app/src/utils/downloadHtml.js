/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * Save an HTML string (e.g. a calculation report) as a file through the browser download flow.
 */
export const downloadHtml = (html, filename) => {
    const url = URL.createObjectURL(new Blob([html], { type: 'text/html' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
};

/**
 * Save a report (self-contained HTML) as a PDF. In the desktop app the main process renders and saves it
 * (resolves to the saved path, or null when the user cancels); in a plain browser the print dialog opens, where
 * "Save as PDF" is one of the printers (resolves to 'print').
 */
export const saveReportPdf = async (html, filename) => {
    if (window.electronAPI?.reportToPdf) return window.electronAPI.reportToPdf(html, filename);
    const win = window.open('', '_blank');
    if (!win) throw new Error('The browser blocked the print window.');
    win.document.write(html);
    win.document.close();
    win.focus();
    win.print();
    return 'print';
};
