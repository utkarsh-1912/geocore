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
import { Menu, History as HistoryIcon, Search, Sun, Moon, HelpCircle, ArrowLeft, Home, Download, FileText, FileJson, Sparkles, Command } from 'lucide-react';
import { GeoAILogo } from './components/common/GeoAILogo';
import { motion, AnimatePresence } from 'framer-motion';
import { GEOTECHNICAL_MODULES } from './config/geotechnicalModules';
import { getSchema } from './features/calculations/schemas';
import { generatePDF, downloadCSV, downloadJSON } from './utils/exportUtils';
import { Toaster, toast } from 'sonner';
import html2canvas from 'html2canvas';
import { HelpModal } from './components/HelpModal';
import { StatusModal } from './components/StatusModal';
import { Preloader } from './components/Preloader';
import { GeoAICopilot } from './features/copilot/GeoAICopilot';
import { GeoAIFullWindow } from './features/copilot/GeoAIFullWindow';
import { CommandPalette } from './features/command/CommandPalette';

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
  const handleSelectFromAI = (funcId, params) => {
    let matchedFunc = null;
    let matchedCategory = null;
    let matchedSubModule = null;

    for (const cat of GEOTECHNICAL_MODULES) {
      for (const sub of cat.subModules || []) {
        for (const fn of sub.functions || []) {
          if (fn.id === funcId || fn.name === funcId) {
            matchedFunc = fn;
            matchedCategory = cat;
            matchedSubModule = sub;
            break;
          }
        }
      }
    }

    const funcObj = matchedFunc || { id: funcId, name: funcId, title: funcId };
    if (matchedCategory) setActiveCategory(matchedCategory);
    if (matchedSubModule) setActiveSubModule(matchedSubModule);
    selectFunction(funcObj);
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
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/health');
        if (response.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (err) {
        setBackendStatus('offline');
        console.log("Health Check Failed (Offline):", err);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000); // Check every 5s
    return () => clearInterval(interval);
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
      setCalculationResults({
        error: error.message || 'Calculation failed',
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
    return "Connecting to Engine...";
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
        style={{ marginTop: '50px' }}
        toastOptions={{
          className: 'bg-white border border-primary text-primary',
          style: {
            color: 'rgb(var(--color-primary))',
            borderColor: 'rgb(var(--color-primary))',
          },
          classNames: {
            toast: 'bg-white border-primary text-primary',
            title: 'text-primary',
            description: 'text-text-muted',
            actionButton: 'bg-primary text-white',
            cancelButton: 'bg-white text-primary border-primary',
            icon: 'text-primary'
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
        <header className="h-13 border-b border-border flex items-center justify-between px-4 drag-region bg-surface transition-colors duration-300 relative"
          style={{ paddingRight: '140px', WebkitAppRegion: 'drag' }}>

          <div className="flex items-center gap-4 no-drag min-w-0 flex-1" style={{ WebkitAppRegion: 'no-drag' }}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded hover:bg-background text-text-muted transition-colors shrink-0"
            >
              <Menu size={20} />
            </button>

            {/* Breadcrumbs */}
            <div className="flex items-center gap-2 overflow-hidden whitespace-nowrap mask-linear-fade">
              {viewState !== 'home' && (
                <button onClick={() => {
                  if (viewState === 'function') selectSubModule(activeSubModule);
                  else if (viewState === 'sub-module') selectCategory(activeCategory);
                  else goHome();
                }} className="p-2 rounded hover:bg-background text-text-muted transition-colors shrink-0">
                  <ArrowLeft size={18} />
                </button>
              )}

              <button
                onClick={goHome}
                className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm font-medium transition-colors shrink-0 ${viewState === 'home' ? 'bg-primary/10 text-primary' : 'text-text-muted hover:bg-background'}`}
              >
                <Home size={16} />
                <span className="hidden sm:inline">Home</span>
              </button>

              {viewState === 'geoai' && (
                <>
                  <span className="text-text-muted shrink-0">/</span>
                  <span className="text-sm font-semibold text-primary truncate flex items-center gap-1.5">
                    <GeoAILogo size={16} className="text-primary" />
                    <span>GeoAI</span>
                  </span>
                </>
              )}

              {activeCategory && (
                <>
                  <span className="text-text-muted shrink-0">/</span>
                  <span className={`text-sm font-medium truncate max-w-[150px] sm:max-w-[250px] ${viewState === 'category' ? 'text-primary' : 'text-text-muted cursor-pointer hover:text-text-main'}`}
                    onClick={() => selectCategory(activeCategory)}
                    title={activeCategory.title}>
                    {activeCategory.title}
                  </span>
                </>
              )}

              {activeSubModule && (
                <>
                  <span className="text-text-muted shrink-0">/</span>
                  <span className={`text-sm font-medium truncate max-w-[150px] sm:max-w-[250px] ${viewState === 'sub-module' ? 'text-primary' : 'text-text-muted cursor-pointer hover:text-text-main'}`}
                    onClick={() => selectSubModule(activeSubModule)}
                    title={activeSubModule.title}>
                    {activeSubModule.title}
                  </span>
                </>
              )}

              {activeFunction && (
                <>
                  <span className="text-text-muted shrink-0">/</span>
                  <span className="text-sm font-medium text-primary truncate max-w-[150px] sm:max-w-[250px]" title={activeFunction.title}>
                    {activeFunction.title}
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-1.5 no-drag h-full shrink-0" style={{ WebkitAppRegion: 'no-drag' }}>
            {/* Search Icon Button */}
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="p-2 rounded hover:bg-background text-text-muted hover:text-text-main transition-colors"
              title="Search & Commands (Ctrl+K)"
            >
              <Search size={18} />
            </button>

            <button onClick={toggleTheme} className="p-2 rounded hover:bg-background text-text-muted hover:text-text-main transition-colors" title={isDarkMode ? "Light Mode" : "Dark Mode"}>
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button
              onClick={() => setHelpOpen(true)}
              className="p-2 rounded hover:bg-background text-text-muted hover:text-text-main transition-colors"
              title="Help & Shortcuts"
            >
              <HelpCircle size={18} />
            </button>
            <button onClick={() => setHistoryOpen(true)} className="p-2 rounded hover:bg-background text-text-muted hover:text-text-main transition-colors" title="Calculation History">
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
                        <span>Analysis Results</span>
                      </h3>

                      {/* Export Dropdown */}
                      <div ref={exportDropdownRef} className="relative">
                        <button
                          onClick={() => setShowExportMenu(!showExportMenu)}
                          className="flex items-center gap-2 px-3.5 py-1.5 bg-primary text-white text-xs font-semibold rounded hover:bg-primary/90 transition-colors shadow-sm"
                        >
                          <Download size={14} />
                          <span>Export Results</span>
                        </button>

                        <AnimatePresence>
                          {showExportMenu && (
                            <motion.div
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: 10 }}
                              className="absolute right-0 mt-2 w-48 bg-background border border-border rounded shadow-lg z-50 overflow-hidden text-xs font-medium"
                            >
                              <button
                                onClick={() => { handleExport('pdf'); setShowExportMenu(false); }}
                                className="flex items-center gap-2.5 text-text-main hover:text-white w-full px-4 py-2.5 text-left hover:bg-primary transition-colors"
                              >
                                <FileText size={14} className="text-primary" />
                                <span>Export PDF Report</span>
                              </button>
                              <button
                                onClick={() => { handleExport('csv'); setShowExportMenu(false); }}
                                className="flex items-center gap-2.5 text-text-main hover:text-white w-full px-4 py-2.5 text-left hover:bg-primary transition-colors"
                              >
                                <FileText size={14} className="text-primary" />
                                <span>Export CSV Data</span>
                              </button>
                              <button
                                onClick={() => { handleExport('json'); setShowExportMenu(false); }}
                                className="flex items-center gap-2.5 text-text-main hover:text-white w-full px-4 py-2.5 text-left hover:bg-primary transition-colors"
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
