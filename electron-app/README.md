# GeoCore desktop app

Electron shell and React 19 UI for GeoCore. The UI talks to the Python backend (`../python-backend`) over HTTP on `127.0.0.1:8000`; all calculations and GeoAI inference run there.

## Commands

Run from this directory.

| Command | What it does |
| :--- | :--- |
| `npm install` | Install dependencies (`npm ci` in CI) |
| `npm start` | Vite dev server plus Electron, once port 5173 is up |
| `npm run dev` | Vite dev server only (browser at `http://localhost:5173`) |
| `npm run build` | Production bundle into `dist/` |
| `npm run lint` | ESLint |
| `npm run dist:win` / `dist:mac` / `dist:linux` | Build the bundle and package an installer into `release/` |
| `npm run pack` | Unpacked app directory, no installer |

Start the backend first (`python main.py` in `python-backend/`), or the UI reports that the engine is unreachable. Packaged builds start the frozen backend themselves. The full release process is in [../RELEASE_GUIDE.md](../RELEASE_GUIDE.md).

## Layout

| Path | Contents |
| :--- | :--- |
| `electron/main.cjs`, `preload.js` | Main process: window, backend lifecycle, auto-update |
| `src/api/client.js` | The only place that calls the backend (REST and the GeoAI SSE stream) |
| `src/App.jsx` | Routing between home, calculation forms, history and GeoAI |
| `src/features/calculations/` | Schema-driven forms. One schema file per Groundhog domain in `schemas/`, field renderers, soil-profile editor, formula and derivation card, user guide (`guide/functionDocs.json` is generated from the Groundhog docstrings) |
| `src/features/copilot/` | GeoAI chat: `GeoAICopilot.jsx` (drawer), `GeoAIFullWindow.jsx` (full window), `geoaiStream.js` (one streamed turn), `chatHistory.js` |
| `src/features/results/` | Result tables, Plotly charts, PDF report export |
| `src/features/dashboard/`, `command/`, `history/` | Home, sidebar, command palette, calculation history |
| `src/components/ui/` | Shared UI components |
| `installer/` | NSIS installer assets and script |
| `public/` | Icons, bundled fonts, Plotly (the app works offline) |

## GeoAI chat in the UI

`geoaiStream.js` reads the SSE stream from `POST /api/geoai/chat?stream=true` and reports progress as stages: *Checking for tools*, *Loading the local model* (cold start only), *Interpreting input*, *Calling tool `<name>`*, *Generating output*. The backend sends a keepalive comment every 5 s while the model works; if nothing arrives for 45 s the client cancels the request and shows an error instead of spinning. The model is warmed in the background when the chat opens (`POST /api/geoai/warmup`).

## Conventions

- The UI never calculates. Inputs go to the backend; results are rendered as returned.
- Units are always shown next to the input and the result.
- Everything must work offline: no CDN assets, fonts or scripts.
