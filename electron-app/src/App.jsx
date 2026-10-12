/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Sidebar } from './features/dashboard/Sidebar';
import { SchemaForm } from './features/calculations/SchemaForm';
import { ResultsRenderer } from './features/results/ResultsRenderer';
import { HistoryPanel } from './features/history/HistoryPanel';
import { DashboardGrid } from './features/dashboard/DashboardGrid';
import { HomeView } from './features/dashboard/HomeView';
import { HistoryProvider, useHistory } from './context/HistoryContext';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { FavoritesProvider } from './context/FavoritesContext';
import { FavoriteStar } from './components/common/FavoriteStar';
import { Menu, History as HistoryIcon, Search, Sun, Moon, HelpCircle, ArrowLeft, Home, Download, FileText, FileJson, ChevronRight, ChevronDown, Sheet, Save } from 'lucide-react';
import { GeoAILogo } from './components/common/GeoAILogo';
import { motion, AnimatePresence } from 'framer-motion';
import { catalogueEntry, findFunction, folderKey, modulesFor, readNavMode, storeNavMode } from './config/navigation';
import { CalculationMenu, CalculationMeta, ToolModal, ToolPanel } from './features/calculations/CalculationToolbar';
import { CompareAllMethods } from './features/calculations/CompareAllMethods';
import { MethodCompare } from './features/calculations/MethodCompare';
import { PhaseSolver } from './features/calculations/PhaseSolver';
import { ProjectValues } from './features/calculations/ProjectValues';
import { ProjectRuns } from './features/calculations/ProjectRuns';
import { downloadHtml } from './utils/downloadHtml';
import { getSchema } from './features/calculations/schemas';
import { api } from './api/client';
import { generatePDF, downloadCSV, downloadJSON } from './utils/exportUtils';
import { renderPlotImages } from './utils/plotImages';
import { Toaster, toast } from 'sonner';
import html2canvas from 'html2canvas';
import { HelpModal } from './components/HelpModal';
import { StatusModal } from './components/StatusModal';
import { Preloader } from './components/Preloader';
import { GeoAICopilot } from './features/copilot/GeoAICopilot';
import { GeoAIFullWindow } from './features/copilot/GeoAIFullWindow';
import { useShared, unreadStore } from './features/copilot/geoaiSession';
import { CommandPalette } from './features/command/CommandPalette';
import { IS_MAC } from './utils/platform';

const ICON_BUTTON = 'h-8 w-8 shrink-0 flex items-center justify-center rounded-md text-text-muted hover:text-text-main hover:bg-surface-muted transition-colors';

const MainLayout = () => {
  // Navigation State
  const [viewState, setViewState] = useState('home');
  const [activeCategory, setActiveCategory] = useState(null);
  const [activeSubModule, setActiveSubModule] = useState(null);
  const [activeFunction, setActiveFunction] = useState(null);
  // Sidebar grouping: engineering tasks (calculation catalogue) or the classic library layout.
  const [navMode, setNavMode] = useState(readNavMode);
  const modules = useMemo(() => modulesFor(navMode), [navMode]);
  // Latest successful run of each method of a catalogue calculation in this session, for "Compare methods":
  // { [calculationId]: { [functionId]: { id, title, inputs, results } } }. Not persisted.
  const [methodRuns, setMethodRuns] = useState({});
  // The form tool whose panel is open inside the form card: 'project' | 'solver' | 'compare' | null.
  const [toolPanel, setToolPanel] = useState(null);
  // The open form's values as typed (kept in a ref: no re-render per keystroke), and the copy the method
  // comparison starts from, taken when it opens.
  const formValuesRef = useRef(null);
  const trackFormValues = useCallback((values) => { formValuesRef.current = values; }, []);
  const [compareSeed, setCompareSeed] = useState(null);
  const openToolPanel = useCallback((panel) => {
    if (panel === 'compare') setCompareSeed(formValuesRef.current ? { ...formValuesRef.current } : null);
    setToolPanel(panel);
  }, []);
  // Project ground model: values applied to the open form (merged by SchemaForm), where each came from, the
  // location they belong to, the run saved for the current result, and the project calculations panel.
  const [patchValues, setPatchValues] = useState(null);
  const [inputSources, setInputSources] = useState({});
  const [projectLocation, setProjectLocation] = useState(null);
  const [savedRunId, setSavedRunId] = useState(null);
  const [projectOpen, setProjectOpen] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [historyOpen, setHistoryOpen] = useState(false);

  // Data State
  const [currentSchema, setCurrentSchema] = useState(null);
  const [calculationResults, setCalculationResults] = useState(null);
  const [calculationInputs, setCalculationInputs] = useState(null); // Store inputs for export

  // Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);

  // UI State
  const [showExportMenu, setShowExportMenu] = useState(false);
  const exportDropdownRef = useRef(null);
  const mainRef = useRef(null);
  const [helpOpen, setHelpOpen] = useState(false);
  const [statusOpen, setStatusOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [selectedSearchIndex, setSelectedSearchIndex] = useState(-1);
  const [copilotOpen, setCopilotOpen] = useState(false);
  // GeoAI opened from the home "Select Model" button: show its model manager straight away.
  const [geoaiModelManager, setGeoaiModelManager] = useState(false);
  // Set on the first visit to the GeoAI tab; from then on it stays mounted (see <main>).
  const [geoaiMounted, setGeoaiMounted] = useState(false);
  useEffect(() => { if (viewState === 'geoai') setGeoaiMounted(true); }, [viewState]);
  const [geoaiUnread] = useShared(unreadStore);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  const { isDarkMode, toggleTheme } = useTheme();
  const { history, addToHistory, removeFromHistory, clearHistory } = useHistory();

  // Sync native window controls overlay background on Windows with active theme
  useEffect(() => {
    if (window.electronAPI?.setTitleBarTheme) {
      window.electronAPI.setTitleBarTheme(isDarkMode);
    }
  }, [isDarkMode]);

  // Each page opens at its top: the main pane is one scroll container shared by every view, so without this a
  // page opened from far down the home page would start scrolled past its content.
  useEffect(() => {
    mainRef.current?.scrollTo({ top: 0 });
  }, [viewState, activeCategory?.id, activeSubModule?.id, activeFunction?.id]);

  // Close export dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (exportDropdownRef.current && !exportDropdownRef.current.contains(event.target)) {
        setShowExportMenu(false);
      }
    };
    if (showExportMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showExportMenu]);

  // Navigation from AI Assistant
  const findModuleFunction = (funcId) => findFunction(modules, funcId);

  // GeoAI tool names (e.g. calculate_gmax_from_shear_wave_velocity) differ from
  // the calculation form ids; the tool registry records which form each tool uses.
  // Tools without a form (e.g. classify_cpt_soil_behavior) map to null.
  const [geoaiToolForms, setGeoaiToolForms] = useState({});

  useEffect(() => {
    if (backendStatus !== 'online') return;
    api.geoaiListTools()
      .then(({ tools = [] }) => {
        const forms = {};
        tools.forEach(t => { forms[t.name] = t.form_function || null; });
        setGeoaiToolForms(forms);
      })
      .catch(err => console.error('Failed to load GeoAI tool forms:', err));
  }, [backendStatus]);

  const resolveFormForTool = (toolName) => {
    const direct = findModuleFunction(toolName);
    if (direct) return direct;
    const formId = geoaiToolForms[toolName];
    return formId ? findModuleFunction(formId) : null;
  };

  const handleSelectFromAI = (funcId, params) => {
    const match = resolveFormForTool(funcId);

    if (!match) {
      toast.error(`No calculation form is available for '${funcId}'.`);
      return;
    }

    setActiveCategory(match.cat);
    setActiveSubModule(match.sub);
    selectFunction(match.fn);

    // Prefill the form with the arguments GeoAI used, keeping only fields the form knows.
    if (params && typeof params === 'object') {
      const inputs = getSchema(match.fn.id)?.inputs || [];
      const values = {};
      inputs.forEach(input => {
        if (params[input.name] !== undefined) values[input.name] = params[input.name];
        else if (input.default !== undefined) values[input.name] = input.default;
      });
      if (Object.keys(values).length > 0) setCalculationInputs(values);
    }
  };

  // App Ready State (Preloader)
  const [appReady, setAppReady] = useState(false);

  useEffect(() => {
    // Dismiss preloader smoothly after quick 300ms boot
    const timer = setTimeout(() => {
      setAppReady(true);
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  // Health Check Effect
  // The bundled engine takes a few seconds to boot after the window appears.
  // Until it has answered once (or the startup grace period expires) we stay in
  // 'connecting' ("Engine starting...") and poll with backoff; afterwards we
  // poll steadily and report 'offline' on failure.
  useEffect(() => {
    const STARTUP_GRACE_MS = 90000;
    const STEADY_INTERVAL_MS = 5000;
    const startedAt = Date.now();
    let everOnline = false;
    let delay = 500;
    let timer = null;
    let cancelled = false;

    const checkHealth = async () => {
      let healthy = false;
      try {
        healthy = await api.health();
      } catch {
        healthy = false;
      }
      if (cancelled) return;

      if (healthy) {
        everOnline = true;
        setBackendStatus('online');
      } else if (everOnline || Date.now() - startedAt > STARTUP_GRACE_MS) {
        setBackendStatus('offline');
      }

      if (everOnline) {
        delay = STEADY_INTERVAL_MS;
      } else {
        delay = Math.min(Math.round(delay * 1.5), STEADY_INTERVAL_MS);
      }
      timer = setTimeout(checkHealth, delay);
    };

    checkHealth();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);

  // Search Effect
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const query = searchQuery.toLowerCase();
    const results = [];

    modules.forEach(category => {
      // Check category
      if (category.title.toLowerCase().includes(query)) {
        results.push({ type: 'Category', item: category, category: category });
      }

      // Check Items (Sub-modules)
      if (category.items) {
        category.items.forEach(subModule => {
          if (subModule.title.toLowerCase().includes(query)) {
            results.push({ type: 'Module', item: subModule, category: category, subModule: subModule });
          }

          // Check Functions
          if (subModule.functions) {
            subModule.functions.forEach(func => {
              if (func.title.toLowerCase().includes(query)) {
                results.push({ type: 'Function', item: func, category: category, subModule: subModule, func: func });
              }
            });
          }
        });
      }
    });

    setSearchResults(results.slice(0, 10)); // Limit results
    setSelectedSearchIndex(-1);
  }, [searchQuery, modules]);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleGlobalKeyDown = (e) => {
      // Ctrl+H (or Cmd+H on Mac) to toggle history
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'h') {
        e.preventDefault();
        setHistoryOpen(prev => !prev);
      }

      // Ctrl+K to open Command Palette
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
      }

      // Ctrl+Shift+A (or Cmd+Shift+A on Mac) to toggle the GeoAI assistant panel
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'a') {
        e.preventDefault();
        setCopilotOpen(prev => !prev);
      }

      // '/' to focus search bar if not already in an input
      if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }


      // Escape to close all modals/panels
      if (e.key === 'Escape') {
        setHelpOpen(false);
        setStatusOpen(false);
        setHistoryOpen(false);
        setCopilotOpen(false);
        setCommandPaletteOpen(false);
        setSearchQuery('');
        setShowSearch(false);
      }
    };

    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);


  // Theme Effect
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Navigation Handlers
  const goHome = () => {
    setViewState('home');
    setActiveCategory(null);
    setActiveSubModule(null);
    setActiveFunction(null);
    setCalculationResults(null);
    setCalculationInputs(null);
    setSearchQuery('');
  };

  // Switching the grouping keeps the open calculation, re-filed under its group in the new navigation;
  // an open module or group page has no counterpart there, so that goes back home.
  const changeNavMode = (mode) => {
    if (mode === navMode) return;
    storeNavMode(mode);
    setNavMode(mode);
    const next = modulesFor(mode);
    if (viewState === 'function' && activeFunction) {
      const match = findFunction(next, activeFunction.id);
      if (match) {
        setActiveCategory(match.cat);
        setActiveSubModule(match.sub);
        return;
      }
    }
    if (viewState === 'category' || viewState === 'sub-module') goHome();
    else if (viewState === 'function') {
      setActiveCategory(null);
      setActiveSubModule(null);
    }
  };

  const selectCategory = (category) => {
    setActiveCategory(category);
    setViewState('category');
    setActiveSubModule(null);
    setActiveFunction(null);
    setSearchQuery('');
  };

  const selectSubModule = (subModule) => {
    setActiveSubModule(subModule);
    setViewState('sub-module');
    setActiveFunction(null);
    setSearchQuery('');
  };

  // Another method of the same catalogue calculation: open its own form, filed where it sits in this navigation.
  const selectMethod = (functionId) => {
    const match = findFunction(modules, functionId);
    if (match) {
      setActiveCategory(match.cat);
      setActiveSubModule(match.sub);
      selectFunction(match.fn);
    } else {
      const entry = catalogueEntry(functionId);
      selectFunction({ id: functionId, title: entry?.methods.find(m => m.id === functionId)?.title || functionId });
    }
  };

  // Form tools shown in a dialog over the form; the others (the phase solver) open inside the form card.
  const MODAL_TOOLS = ['project', 'compare'];
  const closeTool = useCallback(() => setToolPanel(null), []);

  // The open form tool's panel (inside the form card, with its name and a close button), or null.
  const formToolPanel = () => {
    if (MODAL_TOOLS.includes(toolPanel)) return null;
    const content = formToolContent();
    return content ? <ToolPanel tool={toolPanel} onClose={closeTool}>{content}</ToolPanel> : null;
  };

  // The open form tool's dialog, or null.
  const formToolModal = () => {
    if (!MODAL_TOOLS.includes(toolPanel) || viewState !== 'function') return null;
    if (!formToolContent(null)) return null;
    return <ToolModal tool={toolPanel} onClose={closeTool}>{(slot) => formToolContent(slot)}</ToolModal>;
  };

  const formToolContent = (actionsSlot = null) => {
    if (!activeFunction) return null;
    const entry = catalogueEntry(activeFunction.id);
    if (toolPanel === 'project') {
      return (
        <ProjectValues
          embedded
          actionsSlot={actionsSlot}
          functionId={activeFunction.id}
          onApply={(values, sources, locationId) => {
            setPatchValues({ values, at: Date.now() });
            setInputSources(prev => ({
              ...prev,
              ...Object.fromEntries(Object.entries(sources).map(([k, src]) => [k, { ...src, value: values[k] }])),
            }));
            setProjectLocation(locationId);
            setToolPanel(null);
            toast.success(`Applied ${Object.keys(values).length} project value(s) to the form.`);
          }}
        />
      );
    }
    if (toolPanel === 'solver' && entry?.calculation === 'phase_relations') {
      return <PhaseSolver embedded functionId={activeFunction.id} />;
    }
    if (toolPanel === 'compare' && entry) {
      const runs = entry.methods.map(m => methodRuns[entry.calculation]?.[m.id]).filter(Boolean);
      return (
        <div className="space-y-6">
          <CompareAllMethods key={entry.calculation} calculationId={entry.calculation} methods={entry.methods} inputs={compareSeed || calculationInputs} activeFunctionId={activeFunction.id} />
          {runs.length >= 2 && <MethodCompare embedded title={entry.title} runs={runs} onClose={() => setToolPanel(null)} />}
        </div>
      );
    }
    return null;
  };

  const selectFunction = (func) => {
    const sameCalculation = activeFunction && catalogueEntry(activeFunction.id)?.calculation === catalogueEntry(func.id)?.calculation;
    if (!sameCalculation) setToolPanel(null);
    setPatchValues(null);
    setInputSources({});
    setSavedRunId(null);
    setActiveFunction(func);
    setViewState('function');
    setCalculationResults(null);
    setCalculationInputs(null);
    const schema = getSchema(func.id);
    setCurrentSchema(schema);
    if (window.innerWidth < 1024) setSidebarOpen(false);
    setSearchQuery('');
    setSelectedSearchIndex(-1);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedSearchIndex(prev =>
        prev < searchResults.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedSearchIndex(prev => prev > 0 ? prev - 1 : 0);
    } else if (e.key === 'Enter') {
      if (selectedSearchIndex >= 0 && selectedSearchIndex < searchResults.length) {
        handleSearchSelect(searchResults[selectedSearchIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowSearch(false);
      setSearchQuery('');
    }
  };

  const handleSearchSelect = (result) => {
    if (result.type === 'Category') {
      selectCategory(result.category);
    } else if (result.type === 'Module') {
      setActiveCategory(result.category);
      selectSubModule(result.subModule);
    } else if (result.type === 'Function') {
      setActiveCategory(result.category);
      setActiveSubModule(result.subModule);
      selectFunction(result.func);
    }
    setSearchQuery('');
  };

  // Command Palette handlers
  const handleCommandNavigate = (type, item, category, subModule) => {
    if (type === 'Category') {
      selectCategory(category);
    } else if (type === 'Module') {
      if (category) setActiveCategory(category);
      selectSubModule(subModule);
    } else if (type === 'Function') {
      if (category) setActiveCategory(category);
      if (subModule) setActiveSubModule(subModule);
      selectFunction(item.func || item);
    }
  };

  const handleCommandAction = (action) => {
    switch (action) {
      case 'toggleTheme': toggleTheme(); break;
      case 'openHistory': setHistoryOpen(true); break;
      case 'openProject': setProjectOpen(true); break;
      case 'openCopilot': setCopilotOpen(true); break;
      case 'openHelp': setHelpOpen(true); break;
    }
  };

  // Loading State
  const [isLoading, setIsLoading] = useState(false);

  const handleCalculate = async (data) => {
    setIsLoading(true);
    setCalculationResults(null); // Clear previous results
    setCalculationInputs({ ...data }); // Save inputs

    try {
      const payloadArgs = { ...data };
      for (const key in payloadArgs) {
        if (payloadArgs[key] instanceof File) {
          const file = payloadArgs[key];
          console.log(`File check for ${key}:`, { name: file.name, hasPath: !!file.path, hasRawData: !!payloadArgs.raw_data });

          if (file.path) {
            payloadArgs[key] = file.path;
          } else if (payloadArgs.raw_data) {
            console.log(`Using raw_data for ${key} because file.path is missing.`);
            payloadArgs[key] = file.name; // Keep name for reference
          } else {
            console.warn(`File ${key} has no path and no raw_data!`);
            payloadArgs[key] = file.name;
          }
        }
      }
      console.log("handleCalculate final payload:", payloadArgs);

      const response = await fetch('http://127.0.0.1:8000/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          moduleId: activeSubModule ? activeSubModule.id : 'general',
          functionId: activeFunction.id,
          args: payloadArgs
        })
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        const err = await response.json();
        console.error("Backend error data:", err);
        let errorMsg = 'Calculation failed';
        let errorDetails = null;

        if (typeof err.detail === 'string') {
          errorMsg = err.detail;
        } else if (err.detail && typeof err.detail === 'object') {
          errorMsg = err.detail.error || err.detail.message || JSON.stringify(err.detail);
          errorDetails = err.detail.details;
        } else if (err.error) {
          errorMsg = typeof err.error === 'string' ? err.error : JSON.stringify(err.error);
          errorDetails = err.details;
        }

        const customError = new Error(errorMsg);
        if (errorDetails) customError.details = errorDetails;
        throw customError;
      }

      const results = await response.json();
      console.log("Success data:", results);

      if (results.error) {
        const customError = new Error(typeof results.error === 'string' ? results.error : JSON.stringify(results.error));
        if (results.details) customError.details = results.details;
        throw customError;
      }

      setCalculationResults(results);
      setSavedRunId(null);
      const methodEntry = catalogueEntry(activeFunction.id);
      if (methodEntry && methodEntry.methods.length > 1) {
        setMethodRuns(prev => ({
          ...prev,
          [methodEntry.calculation]: {
            ...prev[methodEntry.calculation],
            [activeFunction.id]: { id: activeFunction.id, title: activeFunction.title, inputs: { ...data }, results },
          },
        }));
      }
      console.log("App.jsx: Calling addToHistory with results");
      addToHistory({
        functionName: activeFunction.title,
        functionId: activeFunction.id, // Store ID for reliable lookup
        category: activeCategory,
        subModule: activeSubModule,
        inputs: data,
        results: results,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error("Calculation Error:", error);
      const engineStarting = backendStatus === 'connecting' && error instanceof TypeError;
      setCalculationResults({
        error: engineStarting
          ? 'The calculation engine is still starting. Please try again in a few seconds.'
          : (error.message || 'Calculation failed'),
        details: error.details || []
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Save the current result to the project; a value keeps its project source only if the form still holds it.
  const saveToProject = async () => {
    try {
      // A project value the user then edited is an override: the report names both values; the run no longer
      // depends on the project value (no staleness link).
      const sources = Object.fromEntries(Object.entries(inputSources).map(([k, src]) => (
        calculationInputs && String(calculationInputs[k]) === String(src.value)
          ? [k, src]
          : [k, { source: `entered by the user, overriding the project value ${src.value} (${src.source})`, inputs: [] }]
      )).filter(([k]) => calculationInputs && k in calculationInputs));
      const { id } = await api.projectSaveRun({
        function_id: activeFunction.id, inputs: calculationInputs || {}, results: calculationResults,
        input_sources: sources, location_id: projectLocation,
      });
      setSavedRunId(id);
      toast.success(`Saved to the project as run #${id}.`);
    } catch (e) {
      toast.error(`Could not save to the project: ${e.message}`);
    }
  };

  const downloadRunReport = async () => {
    try {
      downloadHtml(await api.projectRunReport(savedRunId), `geocore-run-${savedRunId}-report.html`);
    } catch (e) {
      toast.error(`Report failed: ${e.message}`);
    }
  };

  const handleExport = async (type) => {
    if (!calculationResults || !calculationInputs) return;

    const filename = `${activeFunction.title.replace(/\s+/g, '_')}_Results`;

    const toastId = toast.loading('Generating export...');

    try {
      if (type === 'pdf') {
        let capturedImage = null;

        // Flatten result if it was wrapped
        const displayData = calculationResults.result !== undefined ? calculationResults.result : calculationResults;

        // If results contain visualization, determine the best capture method
        if (displayData.type === 'image' && displayData.data) {
          console.log("PDF Export: Using direct base64 data for static image");
          capturedImage = `data:image/png;base64,${displayData.data}`;
        } else if (displayData.type === 'plotly' || displayData.type === 'plot' || displayData.type === 'multi_plot') {
          // Render every plot from its figure data (no toolbar, no on-screen zoom, print colours).
          try {
            capturedImage = await renderPlotImages(displayData, activeFunction.title);
          } catch (renderErr) {
            console.error("PDF Export: Plotly image render failed, falling back to a screenshot", renderErr);
          }
          const visualElement = !capturedImage?.length && document.getElementById('results-visualization');
          if (visualElement) {
            try {
              const canvas = await html2canvas(visualElement, {
                backgroundColor: isDarkMode ? '#1a1a1a' : '#ffffff',
                scale: 1.5,
                useCORS: true,
                ignoreElements: (el) => el.classList?.contains('modebar-container'),
              });
              capturedImage = canvas.toDataURL('image/png');
            } catch (captureErr) {
              console.error("PDF Export: html2canvas failed", captureErr);
            }
          }
        }

        // Method/standard/assumptions for the report header — grounded in groundhog's own
        // TOOL_METADATA and docstring, never fabricated. Never block the export if this fails.
        let explanation = null;
        try {
          explanation = await api.geoaiExplain(activeFunction.id, calculationInputs, displayData);
        } catch (explainErr) {
          console.warn("PDF Export: could not fetch method/standard explanation", explainErr);
        }

        console.log("PDF Export: Calling generatePDF...");
        await generatePDF(calculationResults, calculationInputs, activeFunction.title, filename, capturedImage, currentSchema, explanation);
        console.log("PDF Export: generatePDF completed");
        toast.success('PDF Report generated successfully', { id: toastId });
      } else if (type === 'csv') {
        downloadCSV(calculationResults.result || calculationResults, filename);
        toast.success('CSV Data generated successfully', { id: toastId });
      } else if (type === 'json') {
        downloadJSON(calculationResults, filename);
        toast.success('JSON Data generated successfully', { id: toastId });
      }
    } catch (error) {
      console.error("Export failed", error);
      toast.error('Export failed. Please try again.', { id: toastId });
    }
  };

  const getStatusMessage = () => {
    if (backendStatus === 'online') return "Engine Ready";
    if (backendStatus === 'offline') return "Engine Offline (Starting Offline Mode...)";
    return "Engine starting...";
  };

  // HomeView function selection handler
  // Reopen a past calculation (History panel, home "Recent") with its inputs and results.
  const openHistoryItem = (item) => {
    if (item.category) setActiveCategory(item.category);
    if (item.subModule) setActiveSubModule(item.subModule);
    const funcObj = {
      title: item.functionName,
      id: item.functionId || item.functionName // Fallback for old history
    };
    setActiveFunction(funcObj);
    setCurrentSchema(getSchema(funcObj.id));
    setViewState('function');
    setCalculationResults(item.results);
    setCalculationInputs(item.inputs);
    setHistoryOpen(false);
    if (window.innerWidth < 1024) setSidebarOpen(false);
  };

  // A starred folder: its module, then the folder's calculations.
  const openFolder = (category, subModule) => {
    setActiveCategory(category);
    selectSubModule(subModule);
  };

  const handleHomeSelectFunction = (func, category, subModule) => {
    if (category) setActiveCategory(category);
    if (subModule) setActiveSubModule(subModule);
    selectFunction(func);
  };

  return (
    <div className="app-ambient flex h-screen text-text-main font-sans overflow-hidden transition-colors duration-300">
      <AnimatePresence mode="wait">
        {!appReady && (
          <Preloader key="preloader" status={getStatusMessage()} />
        )}
      </AnimatePresence>

      <Toaster
        position="top-right"
        theme={isDarkMode ? 'dark' : 'light'}
        offset={64}
        toastOptions={{
          classNames: {
            toast: '!bg-surface !border !border-border !text-text-main !shadow-pop !rounded-md',
            title: '!font-semibold',
            description: '!text-text-muted',
            actionButton: '!bg-primary !text-on-primary',
            cancelButton: '!bg-surface-muted !text-text-main',
          }
        }}
      />
      <Sidebar
        modules={modules}
        navMode={navMode}
        onNavModeChange={changeNavMode}
        onSelectCategory={(cat) => selectCategory(cat)}
        selectedCategory={activeCategory}
        collapsed={!sidebarOpen}
        backendStatus={backendStatus}
        onStatusClick={() => setStatusOpen(true)}
        onOpenGeoAI={() => {
          setGeoaiModelManager(false);
          setViewState('geoai');
          setActiveCategory(null);
          setActiveSubModule(null);
          setActiveFunction(null);
        }}
        isGeoAIActive={viewState === 'geoai'}
        geoaiUnread={geoaiUnread.length}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <header className={`h-13 shrink-0 border-b border-border flex items-center justify-between gap-3 px-3 drag-region bg-surface/75 backdrop-blur-xl transition-colors duration-300 relative z-20 ${IS_MAC ? (sidebarOpen ? '' : 'pl-6') : 'pr-[146px]'}`}
          style={{ WebkitAppRegion: 'drag' }}>

          <div className="flex items-center gap-2 no-drag min-w-0 flex-1" style={{ WebkitAppRegion: 'no-drag' }}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className={ICON_BUTTON}
              title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
              aria-label="Toggle sidebar"
            >
              <Menu size={18} />
            </button>

            {/* Breadcrumbs */}
            <nav aria-label="Breadcrumb" className="flex items-center gap-1 overflow-hidden whitespace-nowrap min-w-0">
              {viewState !== 'home' && (
                <button onClick={() => {
                  if (viewState === 'function') selectSubModule(activeSubModule);
                  else if (viewState === 'sub-module') selectCategory(activeCategory);
                  else goHome();
                }} className={ICON_BUTTON} title="Back" aria-label="Back">
                  <ArrowLeft size={18} />
                </button>
              )}

              <button
                onClick={goHome}
                className={`flex items-center gap-2 px-2.5 h-8 rounded-md text-sm font-medium transition-colors shrink-0 ${viewState === 'home' ? 'bg-primary/12 text-primary' : 'text-text-muted hover:bg-surface-muted hover:text-text-main'}`}
              >
                <Home size={16} />
                <span className="hidden sm:inline">Home</span>
              </button>

              {viewState === 'geoai' && (
                <>
                  <ChevronRight size={14} className="text-text-subtle shrink-0" />
                  <span className="text-sm font-semibold text-text-main truncate flex items-center gap-1.5 px-1.5">
                    <GeoAILogo size={16} className="text-primary" />
                    <span>GeoAI</span>
                  </span>
                </>
              )}

              {activeCategory && (
                <>
                  <ChevronRight size={14} className="text-text-subtle shrink-0" />
                  <span className={`text-sm font-medium truncate max-w-[150px] sm:max-w-[250px] ${viewState === 'category' ? 'text-text-main font-semibold' : 'text-text-muted cursor-pointer hover:text-text-main'} px-1.5`}
                    onClick={() => selectCategory(activeCategory)}
                    title={activeCategory.title}>
                    {activeCategory.title}
                  </span>
                </>
              )}

              {activeSubModule && (
                <>
                  <ChevronRight size={14} className="text-text-subtle shrink-0" />
                  <span className={`text-sm font-medium truncate max-w-[150px] sm:max-w-[250px] ${viewState === 'sub-module' ? 'text-text-main font-semibold' : 'text-text-muted cursor-pointer hover:text-text-main'} px-1.5`}
                    onClick={() => selectSubModule(activeSubModule)}
                    title={activeSubModule.title}>
                    {activeSubModule.title}
                  </span>
                </>
              )}

              {activeFunction && (
                <>
                  <ChevronRight size={14} className="text-text-subtle shrink-0" />
                  <span className="text-sm font-semibold text-text-main truncate max-w-[180px] sm:max-w-[320px] px-1.5" title={activeFunction.title}>
                    {activeFunction.title}
                  </span>
                </>
              )}
            </nav>
          </div>

          <div className="flex items-center gap-1 no-drag h-full shrink-0" style={{ WebkitAppRegion: 'no-drag' }}>
            {/* Search / command palette trigger */}
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="hidden md:flex items-center gap-2 h-8 w-56 lg:w-64 px-3 mr-1 rounded-md border border-border bg-background/70 text-text-subtle hover:text-text-muted hover:border-primary/40 hover:shadow-[0_0_0_3px_color-mix(in_srgb,var(--color-primary)_12%,transparent)] transition-all text-sm"
              title="Search & Commands (Ctrl+K)"
            >
              <Search size={15} />
              <span className="flex-1 text-left truncate">Search calculations…</span>
              <kbd className="font-sans text-[10px] font-semibold px-1.5 py-0.5 rounded-md border border-border bg-surface text-text-muted">{IS_MAC ? '⌘K' : 'Ctrl K'}</kbd>
            </button>
            <button onClick={() => setCommandPaletteOpen(true)} className={`${ICON_BUTTON} md:hidden`} title="Search & Commands (Ctrl+K)" aria-label="Search">
              <Search size={18} />
            </button>

            <button onClick={toggleTheme} className={ICON_BUTTON} title={isDarkMode ? "Light Mode" : "Dark Mode"} aria-label="Toggle theme">
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button onClick={() => setHelpOpen(true)} className={ICON_BUTTON} title="Help & Shortcuts" aria-label="Help">
              <HelpCircle size={18} />
            </button>
            <button onClick={() => setHistoryOpen(true)} className={ICON_BUTTON} title="Calculation History (Ctrl+H)" aria-label="History">
              <HistoryIcon size={18} />
            </button>

            {/* Separator between app icons and native window controls (- [] x) */}
            {!IS_MAC && <div className="h-5 w-px bg-border ml-2 shrink-0" />}
          </div>
        </header>

        <main ref={mainRef} className={`flex-1 ${viewState === 'geoai' ? 'overflow-hidden p-0' : 'overflow-auto p-6 md:p-8'} relative`}>
          {/* The GeoAI tab stays mounted (hidden) once opened, so an answer keeps running while you work
              elsewhere; it is marked unread with a chime when it lands (features/copilot/geoaiSession.js). */}
          {geoaiMounted && (
            <div className={viewState === 'geoai' ? 'h-full w-full' : 'hidden'} aria-hidden={viewState !== 'geoai'}>
              <GeoAIFullWindow
                visible={viewState === 'geoai'}
                onSelectFunction={handleSelectFromAI}
                canOpenForm={(toolName) => !!resolveFormForTool(toolName)}
                currentContext={{
                  activeFunction: activeFunction?.id || activeFunction?.name,
                  activeCategory: activeCategory?.id,
                  activeSubModule: activeSubModule?.id
                }}
                onBackToModules={goHome}
                openModelManager={geoaiModelManager}
              />
            </div>
          )}
          <AnimatePresence mode="wait">
            {viewState === 'home' && (
              <motion.div
                key="home"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                <HomeView
                  modules={modules}
                  onSelectCategory={selectCategory}
                  onSelectFunction={handleHomeSelectFunction}
                  onSelectFolder={openFolder}
                  onOpenRecent={openHistoryItem}
                  onRemoveRecent={removeFromHistory}
                  onViewHistory={() => setHistoryOpen(true)}
                  history={history}
                  onClearRecent={clearHistory}
                  onOpenCopilot={() => setCopilotOpen(true)}
                  onOpenCommands={() => setCommandPaletteOpen(true)}
                  onOpenHelp={() => setHelpOpen(true)}
                  onOpenProject={() => setProjectOpen(true)}
                />
              </motion.div>
            )}

            {viewState === 'category' && activeCategory && (
              <motion.div
                key="category"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                <DashboardGrid
                  title={activeCategory.title}
                  description={activeCategory.description}
                  items={activeCategory.items}
                  isCategory
                  favoriteOf={(item) => ({ id: folderKey(activeCategory, item), type: 'folder' })}
                  onSelect={(item) => {
                    if (item.functions && item.functions.length > 0) {
                      selectSubModule(item);
                    } else {
                      selectSubModule(item);
                    }
                  }}
                />
              </motion.div>
            )}

            {viewState === 'sub-module' && activeSubModule && (
              <motion.div
                key="sub-module"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                <DashboardGrid
                  title={activeSubModule.title}
                  description={`Select a function from ${activeSubModule.title}`}
                  items={activeSubModule.functions || []}
                  favoriteOf={(item) => ({ id: item.id, type: 'method' })}
                  onSelect={selectFunction}
                />
              </motion.div>
            )}

            {viewState === 'function' && activeFunction && (
              <motion.div
                key="function"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 15 }}
                transition={{ duration: 0.2 }}
                className="max-w-6xl mx-auto w-full min-w-0 space-y-5"
              >
                <SchemaForm
                  toolbar={<CalculationMeta functionId={activeFunction.id} />}
                  actions={
                    <>
                      <FavoriteStar id={activeFunction.id} label={activeFunction.title} size={16} className="h-8 w-8 flex items-center justify-center" />
                      <CalculationMenu
                        functionId={activeFunction.id}
                        onSelectMethod={selectMethod}
                        runsCount={Object.keys(methodRuns[catalogueEntry(activeFunction.id)?.calculation] || {}).length}
                        panel={toolPanel}
                        onPanel={openToolPanel}
                      />
                    </>
                  }
                  panel={formToolPanel()}
                  patchValues={patchValues}
                  functionId={activeFunction.id}
                  functionName={activeFunction.title}
                  schema={currentSchema}
                  onCalculate={handleCalculate}
                  isLoading={isLoading}
                  initialValues={calculationInputs}
                  onValuesChange={trackFormValues}
                />

                {calculationResults && (
                  <div className="w-full min-w-0">
                    <ResultsRenderer
                      results={calculationResults}
                      functionName={activeFunction?.title}
                      functionId={activeFunction?.id}
                      formData={calculationInputs}
                      actions={
                      <div className="flex items-center gap-1.5">
                      {!calculationResults.error && (
                        <button onClick={savedRunId ? downloadRunReport : saveToProject}
                          className="inline-flex items-center gap-1.5 h-8 px-2.5 rounded-md border border-border bg-surface text-xs font-medium text-text-muted hover:border-primary/40 hover:text-text-main transition-colors"
                          title={savedRunId ? 'Download the calculation report of this run' : 'Save this result, its inputs and their sources to the project'}>
                          {savedRunId ? <FileText size={14} /> : <Save size={14} />}
                          <span>{savedRunId ? `Report (run #${savedRunId})` : 'Save to project'}</span>
                        </button>
                      )}
                      {/* Export Dropdown */}
                      <div ref={exportDropdownRef} className="relative">
                        <button
                          onClick={() => setShowExportMenu(!showExportMenu)}
                          className="inline-flex items-center gap-1.5 h-8 px-2.5 btn-brand text-xs font-medium rounded-md transition-colors"
                          aria-haspopup="menu"
                          aria-expanded={showExportMenu}
                        >
                          <Download size={14} />
                          <span>Export</span>
                          <ChevronDown size={14} className={`transition-transform ${showExportMenu ? 'rotate-180' : ''}`} />
                        </button>

                        <AnimatePresence>
                          {showExportMenu && (
                            <motion.div
                              initial={{ opacity: 0, y: -4 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -4 }}
                              transition={{ duration: 0.12 }}
                              role="menu"
                              className="absolute right-0 mt-2 w-52 p-1 bg-surface border border-border rounded-md shadow-pop z-50 overflow-hidden text-xs font-medium"
                            >
                              <button
                                onClick={() => { handleExport('pdf'); setShowExportMenu(false); }}
                                role="menuitem" className="flex items-center gap-2.5 text-text-main w-full px-3 py-2 rounded-md text-left hover:bg-surface-muted transition-colors"
                              >
                                <FileText size={14} className="text-primary" />
                                <span>Export PDF Report</span>
                              </button>
                              <button
                                onClick={() => { handleExport('csv'); setShowExportMenu(false); }}
                                role="menuitem" className="flex items-center gap-2.5 text-text-main w-full px-3 py-2 rounded-md text-left hover:bg-surface-muted transition-colors"
                              >
                                <Sheet size={14} className="text-primary" />
                                <span>Export CSV Data</span>
                              </button>
                              <button
                                onClick={() => { handleExport('json'); setShowExportMenu(false); }}
                                role="menuitem" className="flex items-center gap-2.5 text-text-main w-full px-3 py-2 rounded-md text-left hover:bg-surface-muted transition-colors"
                              >
                                <FileJson size={14} className="text-primary" />
                                <span>Export JSON Data</span>
                              </button>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                      </div>
                      }
                    />
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>

      <HistoryPanel
        isOpen={historyOpen}
        onClose={() => setHistoryOpen(false)}
        onSelect={openHistoryItem}
      />

      <HelpModal
        isOpen={helpOpen}
        onClose={() => setHelpOpen(false)}
      />

      <StatusModal
        isOpen={statusOpen}
        onClose={() => setStatusOpen(false)}
        backendStatus={backendStatus}
      />

      <GeoAICopilot
        isOpen={copilotOpen}
        onClose={() => setCopilotOpen(false)}
        onExpand={() => {
          setCopilotOpen(false);
          setGeoaiModelManager(false);
          setViewState('geoai');
          setActiveCategory(null);
          setActiveSubModule(null);
          setActiveFunction(null);
        }}
        onSelectFunction={handleSelectFromAI}
        canOpenForm={(toolName) => !!resolveFormForTool(toolName)}
        currentContext={{
          activeFunction: activeFunction?.id,
          activeCategory: activeCategory?.id
        }}
      />

      <ProjectRuns isOpen={projectOpen} onClose={() => setProjectOpen(false)} />
      {formToolModal()}

      <CommandPalette
        modules={modules}
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onNavigate={handleCommandNavigate}
        onAction={handleCommandAction}
      />
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <FavoritesProvider>
        <HistoryProvider>
          <MainLayout />
        </HistoryProvider>
      </FavoritesProvider>
    </ThemeProvider>
  );
}

export default App;
