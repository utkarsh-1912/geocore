/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from './features/dashboard/Sidebar';
import { SchemaForm } from './features/calculations/SchemaForm';
import { ResultsRenderer } from './features/results/ResultsRenderer';
import { HistoryPanel } from './features/history/HistoryPanel';
import { DashboardGrid } from './features/dashboard/DashboardGrid';
import { HomeView } from './features/dashboard/HomeView';
import { HistoryProvider, useHistory } from './context/HistoryContext';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { FavoritesProvider, useFavorites } from './context/FavoritesContext';
import { Menu, History as HistoryIcon, Search, Sun, Moon, HelpCircle, ArrowLeft, Home, Download, FileText, FileJson, ChevronRight, ChevronDown, Sheet } from 'lucide-react';
import { GeoAILogo } from './components/common/GeoAILogo';
import { motion, AnimatePresence } from 'framer-motion';
import { GEOTECHNICAL_MODULES } from './config/geotechnicalModules';
import { getSchema } from './features/calculations/schemas';
import { api } from './api/client';
import { generatePDF, downloadCSV, downloadJSON } from './utils/exportUtils';
import { Toaster, toast } from 'sonner';
import html2canvas from 'html2canvas';
import { HelpModal } from './components/HelpModal';
import { StatusModal } from './components/StatusModal';
import { Preloader } from './components/Preloader';
import { GeoAICopilot } from './features/copilot/GeoAICopilot';
import { GeoAIFullWindow } from './features/copilot/GeoAIFullWindow';
import { CommandPalette } from './features/command/CommandPalette';

const ICON_BUTTON = 'h-8 w-8 shrink-0 flex items-center justify-center rounded-lg text-text-muted hover:text-text-main hover:bg-surface-muted transition-colors';

const MainLayout = () => {
  // Navigation State
  const [viewState, setViewState] = useState('home');
  const [activeCategory, setActiveCategory] = useState(null);
  const [activeSubModule, setActiveSubModule] = useState(null);
  const [activeFunction, setActiveFunction] = useState(null);

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
  const [helpOpen, setHelpOpen] = useState(false);
  const [statusOpen, setStatusOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [selectedSearchIndex, setSelectedSearchIndex] = useState(-1);
  const [copilotOpen, setCopilotOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  const { isDarkMode, toggleTheme } = useTheme();
  const { history, addToHistory, clearHistory } = useHistory();

  // Sync native window controls overlay background on Windows with active theme
  useEffect(() => {
    if (window.electronAPI?.setTitleBarTheme) {
      window.electronAPI.setTitleBarTheme(isDarkMode);
    }
  }, [isDarkMode]);
  const { favorites } = useFavorites();

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
  const findModuleFunction = (funcId) => {
    for (const cat of GEOTECHNICAL_MODULES) {
      for (const sub of cat.subModules || []) {
        for (const fn of sub.functions || []) {
          if (fn.id === funcId || fn.name === funcId) {
            return { fn, cat, sub };
          }
        }
      }
    }
    return null;
  };

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

    GEOTECHNICAL_MODULES.forEach(category => {
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
  }, [searchQuery]);

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

  const selectFunction = (func) => {
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
          console.log("PDF Export: Attempting visualization capture for Plotly...");
          const visualElement = document.getElementById('results-visualization');
          if (visualElement) {
            console.log("PDF Export: Visual element found, starting html2canvas...");
            // Wait a bit for Plotly to be fully stable and rendered
            await new Promise(r => setTimeout(r, 800));
            try {
              const canvas = await html2canvas(visualElement, {
                backgroundColor: isDarkMode ? '#1a1a1a' : '#ffffff',
                scale: 1.5,
                useCORS: true,
                logging: true
              });
              capturedImage = canvas.toDataURL('image/png');
              console.log("PDF Export: Capture successful, image data length:", capturedImage.length);
            } catch (captureErr) {
              console.error("PDF Export: html2canvas failed", captureErr);
            }
          } else {
            console.warn("PDF Export: Visual element #results-visualization not found in DOM for Plotly");
          }
        }

        console.log("PDF Export: Calling generatePDF...");
        await generatePDF(calculationResults, calculationInputs, activeFunction.title, filename, capturedImage, currentSchema);
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
  const handleHomeSelectFunction = (func, category, subModule) => {
    if (category) setActiveCategory(category);
    if (subModule) setActiveSubModule(subModule);
    selectFunction(func);
  };

  return (
    <div className="flex h-screen bg-background text-text-main font-sans overflow-hidden transition-colors duration-300">
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
            toast: '!bg-surface !border !border-border !text-text-main !shadow-pop !rounded-xl',
            title: '!font-semibold',
            description: '!text-text-muted',
            actionButton: '!bg-primary !text-white',
            cancelButton: '!bg-surface-muted !text-text-main',
          }
        }}
      />
      <Sidebar
        modules={GEOTECHNICAL_MODULES}
        onSelectCategory={(cat) => selectCategory(cat)}
        selectedCategory={activeCategory}
        collapsed={!sidebarOpen}
        backendStatus={backendStatus}
        onStatusClick={() => setStatusOpen(true)}
        onOpenGeoAI={() => {
          setViewState('geoai');
          setActiveCategory(null);
          setActiveSubModule(null);
          setActiveFunction(null);
        }}
        isGeoAIActive={viewState === 'geoai'}
      />

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-13 shrink-0 border-b border-border flex items-center justify-between gap-3 px-3 drag-region bg-surface transition-colors duration-300 relative z-20"
          style={{ paddingRight: '140px', WebkitAppRegion: 'drag' }}>

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
                className={`flex items-center gap-2 px-2.5 h-8 rounded-lg text-sm font-medium transition-colors shrink-0 ${viewState === 'home' ? 'bg-primary/10 text-primary' : 'text-text-muted hover:bg-surface-muted hover:text-text-main'}`}
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
              className="hidden md:flex items-center gap-2 h-8 w-56 lg:w-64 px-2.5 mr-1 rounded-lg border border-border bg-background text-text-subtle hover:text-text-muted hover:border-border-strong transition-colors text-sm"
              title="Search & Commands (Ctrl+K)"
            >
              <Search size={15} />
              <span className="flex-1 text-left truncate">Search calculations…</span>
              <kbd className="font-sans text-[10px] font-semibold px-1.5 py-0.5 rounded border border-border bg-surface text-text-muted">Ctrl K</kbd>
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
            <div className="h-5 w-px bg-border mx-2 shrink-0" />
          </div>
        </header>

        <main className={`flex-1 ${viewState === 'geoai' ? 'overflow-hidden p-0' : 'overflow-auto p-6 md:p-8'} relative`}>
          <AnimatePresence mode="wait">
            {viewState === 'geoai' && (
              <motion.div
                key="geoai"
                initial={{ opacity: 0, scale: 0.99 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.99 }}
                transition={{ duration: 0.2 }}
                className="h-full w-full"
              >
                <GeoAIFullWindow
                  onSelectFunction={handleSelectFromAI}
                  canOpenForm={(toolName) => !!resolveFormForTool(toolName)}
                  currentContext={{
                    activeFunction: activeFunction?.id || activeFunction?.name,
                    activeCategory: activeCategory?.id,
                    activeSubModule: activeSubModule?.id
                  }}
                  onBackToModules={goHome}
                />
              </motion.div>
            )}

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
                  modules={GEOTECHNICAL_MODULES}
                  onSelectCategory={selectCategory}
                  onSelectFunction={handleHomeSelectFunction}
                  history={history}
                  favorites={favorites}
                  onClearRecent={clearHistory}
                  onOpenCopilot={() => setCopilotOpen(true)}
                  onOpenCommands={() => setCommandPaletteOpen(true)}
                  onOpenHelp={() => setHelpOpen(true)}
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
                className="max-w-6xl mx-auto w-full space-y-6"
              >
                <SchemaForm
                  functionId={activeFunction.id}
                  functionName={activeFunction.title}
                  schema={currentSchema}
                  onCalculate={handleCalculate}
                  isLoading={isLoading}
                  initialValues={calculationInputs}
                />

                {calculationResults && (
                  <div className="w-full space-y-4 pt-2">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-bold text-text-main flex items-center gap-2">
                        <span className="w-1 h-5 rounded-full bg-primary" />
                        <span>Analysis Results</span>
                      </h3>

                      {/* Export Dropdown */}
                      <div ref={exportDropdownRef} className="relative">
                        <button
                          onClick={() => setShowExportMenu(!showExportMenu)}
                          className="flex items-center gap-2 h-8 px-3 bg-primary text-white dark:text-background text-xs font-semibold rounded-lg hover:bg-primary/90 transition-colors shadow-card"
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
                              className="absolute right-0 mt-2 w-52 p-1 bg-surface border border-border rounded-xl shadow-pop z-50 overflow-hidden text-xs font-medium"
                            >
                              <button
                                onClick={() => { handleExport('pdf'); setShowExportMenu(false); }}
                                role="menuitem" className="flex items-center gap-2.5 text-text-main w-full px-3 py-2 rounded-lg text-left hover:bg-surface-muted transition-colors"
                              >
                                <FileText size={14} className="text-primary" />
                                <span>Export PDF Report</span>
                              </button>
                              <button
                                onClick={() => { handleExport('csv'); setShowExportMenu(false); }}
                                role="menuitem" className="flex items-center gap-2.5 text-text-main w-full px-3 py-2 rounded-lg text-left hover:bg-surface-muted transition-colors"
                              >
                                <Sheet size={14} className="text-primary" />
                                <span>Export CSV Data</span>
                              </button>
                              <button
                                onClick={() => { handleExport('json'); setShowExportMenu(false); }}
                                role="menuitem" className="flex items-center gap-2.5 text-text-main w-full px-3 py-2 rounded-lg text-left hover:bg-surface-muted transition-colors"
                              >
                                <FileJson size={14} className="text-primary" />
                                <span>Export JSON Data</span>
                              </button>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>

                    <ResultsRenderer
                      results={calculationResults}
                      functionName={activeFunction?.title}
                      formData={calculationInputs}
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
        onSelect={(item) => {
          // Restore full context
          if (item.category) setActiveCategory(item.category);
          if (item.subModule) setActiveSubModule(item.subModule);

          const funcObj = {
            title: item.functionName,
            id: item.functionId || item.functionName // Fallback for old history
          };
          setActiveFunction(funcObj);

          // Restore Schema
          const schema = getSchema(funcObj.id);
          setCurrentSchema(schema);

          setViewState('function');
          setCalculationResults(item.results);
          setCalculationInputs(item.inputs); // Restore Inputs
          setHistoryOpen(false);
          if (window.innerWidth < 1024) setSidebarOpen(false);
        }}
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
        onSelectFunction={handleSelectFromAI}
        canOpenForm={(toolName) => !!resolveFormForTool(toolName)}
        currentContext={{
          activeFunction: activeFunction?.id,
          activeCategory: activeCategory?.id
        }}
      />

      <CommandPalette
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
