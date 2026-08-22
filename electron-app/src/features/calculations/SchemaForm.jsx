/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect } from 'react';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { HelpCircle, X, Book, Loader, Settings, ChevronDown, ChevronRight, Check, Sparkles, Edit2, Save, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import { SoilProfileModal } from './SoilProfileModal';
import { SavedProfilesList } from './SavedProfilesList';
import { ProfileViewModal } from './ProfileViewModal';
import SchemaEditor from './SchemaEditor';
import { UserGuideTemplate, generateDefaultDocumentation } from './UserGuideTemplate';


// Object Selector Component
const ObjectSelector = ({ objectType, value, onChange, required, refreshTrigger }) => {
    const [options, setOptions] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!objectType) return;
        fetchObjects();
    }, [objectType, refreshTrigger]);

    const fetchObjects = () => {
        setLoading(true);
        // Fetch available objects of this type from backend
        fetch(`http://127.0.0.1:8000/api/objects/${objectType}`)
            .then(res => res.json())
            .then(data => {
                setOptions(data.objects || []);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load objects", err);
                setLoading(false);
            });
    };

    return (
        <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full"
            required={required}
        >
            <option value="">Select {objectType}...</option>
            {/* If value exists but isn't in options (common after refresh/reload), show it */}
            {value && !options.find(o => o.id === value) && (
                <option value={value}>Profile {value.substring(0, 8)}</option>
            )}
            {options.map(opt => (
                <option key={opt.id} value={opt.id}>
                    {opt.name || `${objectType} (${opt.id.substring(0, 6)}...)`}
                </option>
            ))}
            {options.length === 0 && !loading && <option disabled>No {objectType}s created yet</option>}
        </select>
    );
};

// Simple Tabs Component
const Tabs = ({ tabs, activeTab, onChange }) => (
    <div className="flex border-b border-border bg-background">
        {tabs.map(tab => (
            <button
                key={tab.id}
                onClick={() => onChange(tab.id)}
                className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.id
                    ? 'border-primary text-primary bg-primary/5'
                    : 'border-transparent text-text-muted hover:text-text-main hover:bg-secondary/5'
                    }`}
            >
                {tab.label}
            </button>
        ))}
    </div>
);

// Interactive Multi-Parameter Tag / Chip Selector
const ParameterChipsSelector = ({ name, value, availableColumns, onChange, required, disabled, placeholder }) => {
    const [rawMode, setRawMode] = useState(false);

    // Parse current value into array of selected column names
    const selectedList = React.useMemo(() => {
        if (!value) return [];
        if (Array.isArray(value)) return value.map(v => String(v).trim()).filter(Boolean);
        return String(value)
            .split(/[,;\n]/)
            .map(s => s.trim())
            .filter(Boolean);
    }, [value]);

    const toggleColumn = (col) => {
        let newList;
        if (selectedList.includes(col)) {
            newList = selectedList.filter(c => c !== col);
        } else {
            newList = [...selectedList, col];
        }
        onChange(newList.join(', '));
    };

    const selectAll = () => {
        onChange(availableColumns.join(', '));
    };

    const selectNumeric = () => {
        const numeric = availableColumns.filter(c => {
            const lc = c.toLowerCase();
            return !lc.includes('soil type') && !lc.includes('description') && !lc.includes('layer') && !lc.includes('name') && !lc.includes('lithology') && !lc.includes('color');
        });
        onChange(numeric.join(', '));
    };

    const clearAll = () => {
        onChange('');
    };

    if (rawMode || availableColumns.length === 0) {
        return (
            <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                    <span className="text-[11px] text-text-muted">Comma-separated parameters:</span>
                    {availableColumns.length > 0 && (
                        <button
                            type="button"
                            onClick={() => setRawMode(false)}
                            className="text-[11px] text-primary hover:underline font-medium"
                        >
                            Switch to Tag Selection
                        </button>
                    )}
                </div>
                <Input
                    type="text"
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder || "e.g. qc [MPa], fs [kPa]"}
                    required={required}
                    disabled={disabled}
                />
            </div>
        );
    }

    return (
        <div className="space-y-2 p-3 bg-surface/50 border border-border rounded-md">
            <div className="flex flex-wrap items-center justify-between gap-1.5 text-xs">
                <span className="text-text-muted font-medium">
                    Select parameters from profile ({selectedList.length} selected):
                </span>
                <div className="flex items-center gap-1.5">
                    <button
                        type="button"
                        onClick={selectNumeric}
                        className="text-[11px] px-2 py-0.5 rounded bg-primary/10 hover:bg-primary/20 text-primary font-medium transition-colors flex items-center gap-1"
                        title="Select typical numeric columns"
                    >
                        <Zap size={11} className="stroke-[2.5]" />
                        <span>Numeric</span>
                    </button>
                    <button
                        type="button"
                        onClick={selectAll}
                        className="text-[11px] px-2 py-0.5 rounded bg-primary/10 hover:bg-primary/20 text-primary font-medium transition-colors"
                    >
                        All
                    </button>
                    <button
                        type="button"
                        onClick={clearAll}
                        className="text-[11px] px-2 py-0.5 rounded bg-background hover:bg-border text-text-muted transition-colors"
                    >
                        Clear
                    </button>
                    <button
                        type="button"
                        onClick={() => setRawMode(true)}
                        className="text-[11px] text-text-muted hover:text-primary transition-colors underline"
                    >
                        Custom Text
                    </button>
                </div>
            </div>

            {/* Chips Grid */}
            <div className="flex flex-wrap gap-1.5 max-h-48 overflow-y-auto p-1.5 bg-background/50 rounded border border-border/50">
                {availableColumns.map(col => {
                    const isSelected = selectedList.includes(col);
                    return (
                        <button
                            key={col}
                            type="button"
                            onClick={() => toggleColumn(col)}
                            disabled={disabled}
                            className={`px-2.5 py-1 rounded text-xs font-medium transition-all flex items-center gap-1.5 ${
                                isSelected
                                    ? 'bg-primary text-white shadow-sm ring-1 ring-primary'
                                    : 'bg-surface border border-border text-text-main hover:border-primary/50 hover:bg-primary/5'
                            }`}
                        >
                            {isSelected && <Check size={12} className="stroke-[2.5]" />}
                            <span>{col}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};

// Smart Single Column Dropdown Selector
const ColumnSelectDropdown = ({ name, value, availableColumns, onChange, required, disabled, placeholder }) => {
    const [isCustom, setIsCustom] = useState(false);

    return (
        <div className="space-y-1.5">
            {!isCustom ? (
                <div className="flex gap-2">
                    <select
                        value={value || ''}
                        onChange={(e) => {
                            if (e.target.value === '__custom__') {
                                setIsCustom(true);
                            } else {
                                onChange(e.target.value);
                            }
                        }}
                        className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full text-sm"
                        disabled={disabled}
                        required={required}
                    >
                        <option value="">-- Select column --</option>
                        {availableColumns.map(col => (
                            <option key={col} value={col}>{col}</option>
                        ))}
                        <option value="__custom__">Add column name...</option>
                    </select>
                </div>
            ) : (
                <div className="flex gap-2 items-center">
                    <Input
                        type="text"
                        value={value || ''}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder="Enter custom column name"
                        className="flex-1"
                        required={required}
                        disabled={disabled}
                    />
                    <button
                        type="button"
                        onClick={() => setIsCustom(false)}
                        className="text-xs text-primary hover:underline px-2 shrink-0"
                    >
                        Back to List
                    </button>
                </div>
            )}
        </div>
    );
};

export const SchemaForm = ({ functionName, schema, onCalculate, isLoading, initialValues }) => {
    const [formData, setFormData] = useState({});
    const [showDocs, setShowDocs] = useState(false);
    const [fileColumns, setFileColumns] = useState([]);

    const [uploadError, setUploadError] = useState(null);
    const [validationErrors, setValidationErrors] = useState({});

    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
    const [refreshProfiles, setRefreshProfiles] = useState(0);
    const [viewProfileId, setViewProfileIds] = useState(null);
    const [showSavedProfiles, setShowSavedProfiles] = useState(false);

    // Schema Customization State
    const [isEditMode, setIsEditMode] = useState(false);
    const [overrides, setOverrides] = useState({});
    const [editingField, setEditingField] = useState(null);

    // Page Documentation State
    const [pageDocs, setPageDocs] = useState('');
    const [isEditingDocs, setIsEditingDocs] = useState(false);
    const [editedDocs, setEditedDocs] = useState('');
    const [activeDocTab, setActiveDocTab] = useState('guide'); // 'guide' | 'fields'

    // AI Auto-Fill State
    const [showAutoFillModal, setShowAutoFillModal] = useState(false);
    const [autoFillText, setAutoFillText] = useState('');
    const [isAutoFilling, setIsAutoFilling] = useState(false);
    const [autoFillMsg, setAutoFillMsg] = useState(null);

    const handleAutoFill = async () => {
        if (!autoFillText.trim() || isAutoFilling) return;
        setIsAutoFilling(true);
        setAutoFillMsg(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/geoai/autofill', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    function_id: functionName,
                    raw_text: autoFillText
                })
            });
            if (!response.ok) throw new Error('Auto-fill extraction failed');
            const data = await response.json();
            const extracted = data.fields || {};
            const count = data.extracted_count || 0;
            if (count === 0) {
                setAutoFillMsg({ type: 'warn', text: 'No matching parameters found in text.' });
            } else {
                const newForm = { ...formData };
                Object.keys(extracted).forEach(k => {
                    newForm[k] = extracted[k].value;
                });
                setFormData(newForm);
                setAutoFillMsg({ type: 'success', text: `Successfully populated ${count} parameters!` });
                setTimeout(() => {
                    setShowAutoFillModal(false);
                    setAutoFillText('');
                    setAutoFillMsg(null);
                }, 1200);
            }
        } catch (e) {
            setAutoFillMsg({ type: 'error', text: e.message });
        } finally {
            setIsAutoFilling(false);
        }
    };

    // Helper for Schema Image Upload
    const handleSchemaImageUpload = async (file, fieldName) => {
        if (!file) return;
        const formDataUpload = new FormData();
        formDataUpload.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/assets/upload', {
                method: 'POST',
                body: formDataUpload
            });
            if (!response.ok) throw new Error('Upload failed');
            const data = await response.json();
            const fullUrl = `http://localhost:8000${data.url}`;

            // Save to override
            const currentOverride = overrides[functionName]?.[fieldName] || {};
            handleSaveOverride(functionName, fieldName, { ...currentOverride, imageUrl: fullUrl });
        } catch (error) {
            console.error("Schema Image Upload Error:", error);
            // Optionally show toast
        }
    };

    // Normalize schema inputs (support both 'inputs' array and JSON Schema 'properties')
    const normalizedInputs = React.useMemo(() => {
        if (!schema) return [];
        if (schema.inputs) return schema.inputs;
        if (schema.properties) {
            return Object.entries(schema.properties).map(([key, prop]) => ({
                name: key,
                label: prop.title || key,
                type: prop.type,
                description: prop.description,
                default: prop.default,
                required: schema.required?.includes(key),
                enum: prop.enum,
                minimum: prop.minimum,
                maximum: prop.maximum,
                unit: prop.unit,
                objectType: prop.objectType
            }));
        }
        return [];
    }, [schema]);

    // Fetch Overrides and Page Docs on Mount/Update
    useEffect(() => {
        const defaultDocs = schema?.documentation || generateDefaultDocumentation(functionName, schema, normalizedInputs);

        fetch('http://localhost:8000/api/schema/overrides')
            .then(res => res.json())
            .then(data => {
                console.log("Loaded schema overrides:", data);
                setOverrides(data);

                // Initialize Page Docs
                const customDocs = data[functionName]?._page_docs?.description;
                const initialDocs = (customDocs && customDocs.trim()) ? customDocs : defaultDocs;
                setPageDocs(initialDocs);
                setEditedDocs(initialDocs);
            })
            .catch(err => {
                console.error("Failed to load schema overrides:", err);
                setPageDocs(defaultDocs);
                setEditedDocs(defaultDocs);
            });
    }, [functionName, schema, normalizedInputs]);

    const handleSavePageDocs = () => {
        const metadata = { description: editedDocs }; // Store as description field in metadata object
        handleSaveOverride(functionName, '_page_docs', metadata);
        setPageDocs(editedDocs);
        setIsEditingDocs(false);
    };

    const handleSaveOverride = (funcId, fieldName, metadata) => {
        // Optimistic update
        setOverrides(prev => ({
            ...prev,
            [funcId]: {
                ...prev[funcId],
                [fieldName]: metadata
            }
        }));

        // Persist to backend
        fetch('http://localhost:8000/api/schema/override', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                functionId: funcId,
                fieldName: fieldName,
                metadata: metadata
            })
        }).catch(err => console.error("Failed to save override:", err));
    };

    useEffect(() => {
        console.log("SchemaForm useEffect - initialValues changed:", initialValues);
        // Initialize form with initialValues if available, otherwise defaults
        if (initialValues && Object.keys(initialValues).length > 0) {
            console.log("SchemaForm - Setting formData from initialValues:", initialValues);
            setFormData(initialValues);
        } else if (normalizedInputs.length > 0) {
            const defaults = {};
            normalizedInputs.forEach(input => {
                if (input.default !== undefined) {
                    defaults[input.name] = input.default;
                }
            });
            console.log("SchemaForm - Setting defaults:", defaults);
            setFormData(defaults);
        }
    }, [normalizedInputs, initialValues]);

    const validateField = (name, value, regexPattern) => {
        if (!regexPattern) return true;
        try {
            const regex = new RegExp(regexPattern);
            const isValid = regex.test(String(value));
            setValidationErrors(prev => ({
                ...prev,
                [name]: isValid ? null : 'Invalid format'
            }));
            return isValid;
        } catch (e) {
            console.error("Invalid regex:", regexPattern);
            return true;
        }
    };

    const fetchObjectDetails = (type, id) => {
        if (!type || !id) return;
        console.log(`Fetching details for ${type} ID: ${id}`);
        fetch(`http://127.0.0.1:8000/api/objects/${type}/${id}`)
            .then(res => res.json())
            .then(data => {
                if (data.columns && Array.isArray(data.columns)) {
                    console.log("Loaded columns from object:", data.columns);
                    setFileColumns(data.columns);
                }
            })
            .catch(err => console.error("Failed to fetch object details:", err));
    };

    // Effect to load columns if initial value exists
    useEffect(() => {
        if (!normalizedInputs || normalizedInputs.length === 0) return;

        // Find object_select fields
        const objectFields = normalizedInputs.filter(i => i.type === 'object_select');
        objectFields.forEach(field => {
            const val = formData[field.name];
            if (val) {
                fetchObjectDetails(field.objectType, val);
            }
        });
    }, [normalizedInputs, formData]); // Check dependencies carefully. formData triggers often.

    const handleChange = (name, value, regexPattern = null) => {
        console.log(`SchemaForm handleChange: ${name} =`, value);

        if (regexPattern) {
            validateField(name, value, regexPattern);
        }

        setFormData(prev => {
            const newState = { ...prev, [name]: value };
            console.log("SchemaForm State Update (handleChange):", newState);
            return newState;
        });

        // Check if this is an object selector
        const inputDef = normalizedInputs.find(i => i.name === name);
        if (inputDef && inputDef.type === 'object_select' && value) {
            fetchObjectDetails(inputDef.objectType, value);
        }
    };

    const handleFileUpload = async (name, file) => {
        setUploadError(null);
        if (!file) return;

        console.log(`SchemaForm handleFileUpload: ${name} =`, file.name);
        // Update form data with file object
        setFormData(prev => {
            const newState = { ...prev, [name]: file };
            console.log("SchemaForm State Update (handleFileUpload):", newState);
            return newState;
        });

        try {
            // Attempt to get file path via Electron API if available
            if (window.electronAPI && window.electronAPI.getPathForFile) {
                try {
                    const filePath = window.electronAPI.getPathForFile(file);
                    if (filePath) {
                        console.log("SchemaForm: Got file path:", filePath);
                        Object.defineProperty(file, 'path', {
                            value: filePath,
                            writable: false
                        });
                    }
                } catch (e) {
                    console.warn("SchemaForm: Failed to get file path:", e);
                }
            }

            const extension = file.name.split('.').pop().toLowerCase();
            let headers = [];

            if (extension === 'ags') {
                // AGS files are handled primarily via file path on backend
                return;
            } else if (extension === 'csv') {
                Papa.parse(file, {
                    header: true,
                    skipEmptyLines: true,
                    complete: (results) => {
                        console.log("Papa Parse Results (Full):", results);
                        if (results.meta && results.meta.fields) {
                            setFileColumns(results.meta.fields);
                        } else if (results.data && results.data.length > 0) {
                            setFileColumns(Object.keys(results.data[0]));
                        }

                        // Store the actual data for the backend
                        if (results.data && results.data.length > 0) {
                            setFormData(prev => ({ ...prev, raw_data: results.data }));
                        }
                    },
                    error: (err) => {
                        setUploadError("Failed to parse CSV file: " + err.message);
                    }
                });
            } else if (['xlsx', 'xls'].includes(extension)) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const data = new Uint8Array(e.target.result);
                        const workbook = XLSX.read(data, { type: 'array' });
                        const firstSheetName = workbook.SheetNames[0];
                        const worksheet = workbook.Sheets[firstSheetName];
                        const jsonData = XLSX.utils.sheet_to_json(worksheet); // No header:1 to get objects

                        if (jsonData && jsonData.length > 0) {
                            setFileColumns(Object.keys(jsonData[0]));
                            setFormData(prev => ({ ...prev, raw_data: jsonData }));
                        }
                    } catch (err) {
                        setUploadError("Failed to parse Excel file: " + err.message);
                    }
                };
                reader.readAsArrayBuffer(file);
            } else {
                setUploadError("Unsupported file type. Please upload .csv, .xlsx, or .xls");
            }
        } catch (err) {
            setUploadError("Error reading file: " + err.message);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // Final Validation Check
        const errors = {};
        let hasErrors = false;

        normalizedInputs.forEach(baseInput => {
            const override = overrides[functionName]?.[baseInput.name] || {};
            const input = { ...baseInput, ...override };

            if (input.validationRegex && formData[input.name]) {
                try {
                    const regex = new RegExp(input.validationRegex);
                    if (!regex.test(String(formData[input.name]))) {
                        errors[input.name] = 'Invalid format';
                        hasErrors = true;
                    }
                } catch (e) { }
            }
        });

        if (hasErrors) {
            setValidationErrors(errors);
            return;
        }

        console.log("SchemaForm handleSubmit - formData:", formData);
        onCalculate(formData);
    };

    const isDev = import.meta.env.DEV || Boolean(window.electronAPI?.isDev);

    if (!schema) return <div className="text-gray-400">Select a function to configure parameters.</div>;

    return (

        <>
            <Card className="w-full relative shadow-sm">
                <div className="flex flex-wrap items-center justify-between border-b border-border pb-4 mb-6 gap-3">
                    <div className="min-w-0 flex-1">
                        <h2 className="text-xl font-bold text-text-main flex items-center gap-2.5 truncate">
                            <span className="truncate">{functionName || "Calculation Analysis"}</span>
                            {isDev && isEditMode && (
                                <span className="text-[10px] font-mono font-semibold bg-primary/15 text-primary border border-primary/30 px-2 py-0.5 rounded-full uppercase shrink-0">
                                    Dev Edit Mode
                                </span>
                            )}
                        </h2>
                        <p className="text-xs text-text-muted mt-1">Configure geotechnical parameters and execute validated analysis.</p>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                        {isDev && (
                            <button
                                type="button"
                                onClick={() => setIsEditMode(!isEditMode)}
                                className={`flex items-center gap-1.5 text-xs font-medium transition-colors px-2.5 py-1.5 border border-border rounded ${isEditMode ? 'bg-primary text-white shadow-sm' : 'text-text-muted hover:bg-secondary/10'}`}
                                title="Toggle Schema Customization Mode (Dev only)"
                            >
                                {isEditMode ? <Check size={14} /> : <Edit2 size={14} />}
                                <span>{isEditMode ? 'Done Editing' : 'Customize Form'}</span>
                            </button>
                        )}
                        <button
                            type="button"
                            onClick={() => setShowDocs(true)}
                            className="text-text-muted hover:text-primary border border-border hover:border-primary/40 bg-surface px-3 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-1.5 shadow-sm"
                            title="View Calculation Guide & Formulation"
                        >
                            <Book size={14} className="text-primary" />
                            <span>Guide & Theory</span>
                        </button>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {normalizedInputs.map((baseInput) => {
                            // Apply Overrides
                            const override = overrides[functionName]?.[baseInput.name] || {};
                            const input = { ...baseInput, ...override };

                            const isMultiColumn = override.displayType === 'column_multi_select' || (!override.displayType && (input.name === 'parameters' || input.name === 'plot_parameters' || input.name === 'properties' || (fileColumns.length > 0 && (input.name === 'columns' || input.name.toLowerCase().includes('parameters')))));
                            const isSingleColumn = override.displayType === 'column_select' || (!override.displayType && (input.type === 'column_select' || input.name === 'soiltypecolumn' || input.name === 'depth_column' || input.name === 'qc_column' || input.name.toLowerCase().endsWith('_column') || input.name.toLowerCase().endsWith('_col') || input.name.toLowerCase().includes('soiltype')));
                            const isDropdown = override.displayType === 'dropdown' || (override.allowedOptions && override.allowedOptions.length > 0);

                            // Helper for Edit Mode Wrapper
                            const wrapperClass = `relative ${isEditMode ? 'border border-dashed border-primary/20 rounded-md p-2' : ''}`;
                            const editOverlay = isEditMode ? (
                                <div
                                    className="absolute inset-0 z-10 cursor-pointer"
                                    onClick={() => setEditingField(input)}
                                    title="Click to Edit"
                                />
                            ) : null;

                            // Helper for Label with Actions
                            const renderLabel = () => (
                                <div className="flex items-center gap-1.5 mb-1 group/label">
                                    <label className="text-sm text-text-muted flex items-center gap-1 cursor-default">
                                        {input.label || input.name}
                                        {input.required && <span className="text-primary font-bold">*</span>}
                                        {input.unit && <span className="text-text-muted text-xs font-normal">({input.unit})</span>}
                                    </label>

                                    {input.description && (
                                        <div className="relative group/tooltip">
                                            <HelpCircle size={12} className="text-text-muted cursor-help" />
                                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2 bg-surface border border-border rounded shadow-xl text-xs text-text-main opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all z-50 pointer-events-none">
                                                <div dangerouslySetInnerHTML={{ __html: input.description }} />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            );

                            // Handle Enums or Select Options
                            if (input.enum || input.options || input.type === 'select') {
                                const options = input.enum || input.options || [];
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <select
                                                value={formData[input.name] || ''}
                                                onChange={(e) => handleChange(input.name, e.target.value)}
                                                className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full"
                                                required={input.required}
                                                disabled={isEditMode}
                                            >
                                                {options.map(opt => (
                                                    <option key={opt} value={opt}>{opt}</option>
                                                ))}
                                            </select>
                                        </div>
                                    </div>
                                );
                            }

                            if (input.type === 'file') {
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <div className="flex flex-col gap-2">
                                                <input
                                                    type="file"
                                                    accept={input.accept || ".csv,.xlsx,.xls"}
                                                    onChange={(e) => handleFileUpload(input.name, e.target.files[0])}
                                                    className="block w-full text-sm text-text-muted
                                                    file:mr-4 file:py-2 file:px-4
                                                    file:rounded file:border-0
                                                    file:text-sm file:font-semibold
                                                    file:bg-primary/10 file:text-primary
                                                    hover:file:bg-primary/20
                                                    cursor-pointer"
                                                    disabled={isEditMode}
                                                />
                                                {uploadError && <span className="text-xs text-red-500">{uploadError}</span>}
                                            </div>
                                        </div>
                                    </div>
                                );
                            } else if (isMultiColumn && fileColumns.length > 0) {
                                return (
                                    <div key={input.name} className={`${wrapperClass} md:col-span-2`}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <ParameterChipsSelector
                                                name={input.name}
                                                value={formData[input.name]}
                                                availableColumns={fileColumns}
                                                onChange={(val) => handleChange(input.name, val)}
                                                required={input.required}
                                                disabled={isEditMode}
                                                placeholder={input.placeholder || input.description}
                                            />
                                            {validationErrors[input.name] && (
                                                <span className="text-xs text-red-500 mt-1">{validationErrors[input.name]}</span>
                                            )}
                                        </div>
                                    </div>
                                );
                            } else if (isSingleColumn && fileColumns.length > 0) {
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <ColumnSelectDropdown
                                                name={input.name}
                                                value={formData[input.name]}
                                                availableColumns={fileColumns}
                                                onChange={(val) => handleChange(input.name, val)}
                                                required={input.required}
                                                disabled={isEditMode}
                                                placeholder={input.placeholder || input.description}
                                            />
                                            {validationErrors[input.name] && (
                                                <span className="text-xs text-red-500 mt-1">{validationErrors[input.name]}</span>
                                            )}
                                        </div>
                                    </div>
                                );
                            } else if (isDropdown) {
                                const optionsList = override.allowedOptions
                                    ? override.allowedOptions.split(',').map(s => s.trim()).filter(Boolean)
                                    : (input.enum || []);
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <select
                                                value={formData[input.name] !== undefined ? String(formData[input.name]) : ''}
                                                onChange={(e) => handleChange(input.name, e.target.value)}
                                                className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full text-sm"
                                                required={input.required}
                                                disabled={isEditMode}
                                            >
                                                <option value="">Select option...</option>
                                                {optionsList.map(opt => (
                                                    <option key={opt} value={opt}>{opt}</option>
                                                ))}
                                            </select>
                                            {validationErrors[input.name] && (
                                                <span className="text-xs text-red-500 mt-1">{validationErrors[input.name]}</span>
                                            )}
                                        </div>
                                    </div>
                                );
                            } else if (input.type === 'column_select') {
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <select
                                                value={formData[input.name] || ''}
                                                onChange={(e) => handleChange(input.name, e.target.value)}
                                                className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                                                disabled={fileColumns.length === 0 || isEditMode}
                                            >
                                                <option value="">Select a column...</option>
                                                {fileColumns.map(col => (
                                                    <option key={col} value={col}>{col}</option>
                                                ))}
                                            </select>
                                            {fileColumns.length === 0 && <span className="text-xs text-text-muted mt-1">Upload a file or select SoilProfile to see columns</span>}
                                        </div>
                                    </div>
                                );
                            } else if (input.type === 'object_select') {
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-1.5 mb-1 group/label">
                                                    <label className="text-sm text-text-muted flex items-center gap-1 cursor-default">
                                                        {input.label || input.name}
                                                        {input.required && <span className="text-primary font-bold">*</span>}
                                                    </label>

                                                    {input.description && (
                                                        <div className="relative group/tooltip">
                                                            <HelpCircle size={12} className="text-text-muted cursor-help" />
                                                            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2 bg-surface border border-border rounded shadow-xl text-xs text-text-main opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all z-50 pointer-events-none">
                                                                <div dangerouslySetInnerHTML={{ __html: input.description }} />
                                                            </div>
                                                        </div>
                                                    )}

                                                    <button
                                                        type="button"
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            e.stopPropagation();
                                                            setEditingField(input);
                                                        }}
                                                        className={`p-0.5 rounded hover:bg-primary/10 text-text-muted hover:text-primary transition-all ${isEditMode ? 'opacity-100' : 'opacity-0'} group-hover/label:opacity-100`}
                                                        title="Edit Field"
                                                    >
                                                        <Edit2 size={10} />
                                                    </button>
                                                </div>

                                                {input.objectType === 'SoilProfile' && (
                                                    <button
                                                        type="button"
                                                        onClick={() => setIsProfileModalOpen(true)}
                                                        className="text-xs text-primary hover:underline flex items-center gap-1"
                                                        disabled={isEditMode}
                                                    >
                                                        <Settings size={12} /> Manage
                                                    </button>
                                                )}
                                            </div>
                                            <ObjectSelector
                                                objectType={input.objectType}
                                                value={formData[input.name] || ''}
                                                onChange={(val) => handleChange(input.name, val)}
                                                required={input.required}
                                                refreshTrigger={refreshProfiles}
                                                disabled={isEditMode}
                                            />
                                        </div>
                                    </div>
                                );
                            } else if (input.type === 'list') {
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col md:col-span-2">
                                            {renderLabel()}
                                            <textarea
                                                value={formData[input.name] || ''}
                                                onChange={(e) => handleChange(input.name, e.target.value)}
                                                placeholder={input.description || 'Enter values separated by commas or new lines...'}
                                                className="bg-background border border-border rounded px-3 py-2 text-text-main font-mono text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full min-h-[80px]"
                                                required={input.required}
                                                disabled={isEditMode}
                                            />
                                            <span className="text-[10px] text-text-muted mt-1">Example: 10, 20, 30.5</span>
                                        </div>
                                    </div>
                                );
                            } else if (input.type === 'boolean') {
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <select
                                                value={String(formData[input.name] ?? false)}
                                                onChange={(e) => handleChange(input.name, e.target.value === 'true')}
                                                className="bg-background border border-border rounded px-3 py-2 text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all w-full"
                                                required={input.required}
                                                disabled={isEditMode}
                                            >
                                                <option value="true">True</option>
                                                <option value="false">False</option>
                                            </select>
                                        </div>
                                    </div>
                                );
                            } else {
                                return (
                                    <div key={input.name} className={wrapperClass}>
                                        {editOverlay}
                                        <div className="flex flex-col">
                                            {renderLabel()}
                                            <Input
                                                type={input.type === 'number' || input.type === 'float' ? 'number' : 'text'}
                                                step="any"
                                                min={input.min !== undefined ? input.min : (input.minimum !== undefined ? input.minimum : undefined)}
                                                max={input.max !== undefined ? input.max : (input.maximum !== undefined ? input.maximum : undefined)}
                                                value={formData[input.name] !== undefined ? formData[input.name] : ''}
                                                onChange={(e) => handleChange(input.name, e.target.value, input.validationRegex)}
                                                placeholder={input.placeholder || input.description || ''}
                                                required={input.required}
                                                disabled={isEditMode}
                                                className={validationErrors[input.name] ? "border-red-500 focus:border-red-500 focus:ring-red-500" : ""}
                                            />
                                            {validationErrors[input.name] && (
                                                <span className="text-xs text-red-500 mt-1">{validationErrors[input.name]}</span>
                                            )}
                                        </div>
                                    </div>
                                );
                            }
                        })}
                    </div>

                    <div className="flex justify-end pt-4 border-t border-border mt-6">
                        <Button type="submit" variant="primary" disabled={isLoading}>
                            {isLoading ? (
                                <div className="flex items-center gap-2">
                                    <Loader className="animate-spin" size={16} />
                                    Calculating...
                                </div>
                            ) : (
                                "Calculate"
                            )}
                        </Button>
                    </div>
                </form>
            </Card>

            {/* Documentation Modal */}
            <AnimatePresence>
                {showDocs && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-surface w-full max-w-5xl max-h-[85vh] rounded-md shadow-2xl flex flex-col border border-border overflow-hidden"
                        >
                            {/* Modal Header with Integrated Tabs and Actions */}
                            <div className="flex flex-wrap items-center justify-between px-5 py-3.5 border-b border-border bg-background shrink-0 gap-4">
                                {/* Left: Title & Icon */}
                                <div className="flex items-center gap-2.5 min-w-0">
                                    <div className="p-1.5 rounded bg-primary/10 text-primary border border-primary/20 shrink-0">
                                        <Book size={18} />
                                    </div>
                                    <div className="min-w-0">
                                        <h3 className="text-base font-bold text-text-main truncate">
                                            {functionName}
                                        </h3>
                                        <span className="text-[11px] text-text-muted">Documentation & Parameter Configuration</span>
                                    </div>
                                </div>

                                {/* Center & Right: Segmented Tabs + Header Actions */}
                                <div className="flex items-center gap-2.5 shrink-0">
                                    {/* Segmented Tab Switcher (Dev Only) */}
                                    {isDev && (
                                        <div className="flex bg-surface p-1 rounded border border-border">
                                            <button
                                                type="button"
                                                onClick={() => setActiveDocTab('guide')}
                                                className={`px-3 py-1 text-xs font-medium rounded transition-all ${
                                                    activeDocTab === 'guide'
                                                        ? 'bg-primary text-white shadow-sm'
                                                        : 'text-text-muted hover:text-text-main'
                                                }`}
                                            >
                                                User Guide
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setActiveDocTab('fields')}
                                                className={`px-3 py-1 text-xs font-medium rounded transition-all ${
                                                    activeDocTab === 'fields'
                                                        ? 'bg-primary text-white shadow-sm'
                                                        : 'text-text-muted hover:text-text-main'
                                                }`}
                                            >
                                                Field Configuration
                                            </button>
                                        </div>
                                    )}

                                    {/* Edit Guide Button (Dev Only) */}
                                    {isDev && activeDocTab === 'guide' && (
                                        <button
                                            type="button"
                                            onClick={() => {
                                                if (!isEditingDocs) {
                                                    const currentOrFallback = (editedDocs && editedDocs.trim()) || (pageDocs && pageDocs.trim()) || generateDefaultDocumentation(functionName, schema, normalizedInputs);
                                                    setEditedDocs(currentOrFallback);
                                                    setPageDocs(currentOrFallback);
                                                }
                                                setIsEditingDocs(!isEditingDocs);
                                            }}
                                            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded border transition-all ${
                                                isEditingDocs
                                                    ? 'bg-primary text-white border-primary shadow-sm'
                                                    : 'bg-surface border-border text-text-muted hover:text-text-main hover:border-primary/50'
                                            }`}
                                            title={isEditingDocs ? "Preview documentation" : "Edit documentation source"}
                                        >
                                            {isEditingDocs ? <Check size={14} /> : <Edit2 size={13} />}
                                            <span>{isEditingDocs ? 'Preview' : 'Edit Guide'}</span>
                                        </button>
                                    )}

                                    <div className="h-4 w-[1px] bg-border my-auto mx-0.5" />

                                    {/* Close Button */}
                                    <button
                                        type="button"
                                        onClick={() => setShowDocs(false)}
                                        className="p-1.5 rounded hover:bg-surface border border-transparent hover:border-border text-text-muted hover:text-text-main transition-colors"
                                        title="Close documentation (Esc)"
                                    >
                                        <X size={18} />
                                    </button>
                                </div>
                            </div>

                            <div className="flex-1 overflow-y-auto p-0 bg-surface/50">
                                {activeDocTab === 'guide' ? (
                                    <div className="p-6 h-full flex flex-col">
                                        {isEditingDocs ? (
                                            <div className="flex-1 flex flex-col gap-3">
                                                <div className="flex items-center justify-between text-xs text-text-muted">
                                                    <span>HTML / Markdown Source Editor</span>
                                                    <span className="font-mono text-[11px]">Supports standard HTML tags and typography</span>
                                                </div>
                                                <textarea
                                                    value={editedDocs}
                                                    onChange={(e) => setEditedDocs(e.target.value)}
                                                    className="w-full flex-1 min-h-[420px] p-4 bg-background border border-border rounded-md font-mono text-sm focus:outline-none focus:ring-1 focus:ring-primary text-text-main leading-relaxed"
                                                    placeholder="Enter HTML or text documentation..."
                                                />
                                                <div className="flex justify-between items-center gap-2 pt-2 border-t border-border">
                                                    <button
                                                        type="button"
                                                        onClick={() => setEditedDocs(generateDefaultDocumentation(functionName, schema, normalizedInputs))}
                                                        className="text-xs text-text-muted hover:text-primary transition-colors underline"
                                                    >
                                                        Reset to default template
                                                    </button>
                                                    <div className="flex items-center gap-2">
                                                        <Button variant="secondary" onClick={() => {
                                                            setEditedDocs(pageDocs);
                                                            setIsEditingDocs(false);
                                                        }}>Cancel</Button>
                                                        <Button variant="primary" onClick={handleSavePageDocs}>Save Guide</Button>
                                                    </div>
                                                </div>
                                            </div>
                                        ) : (
                                            <UserGuideTemplate
                                                functionName={functionName}
                                                pageDocs={pageDocs}
                                                schema={schema}
                                                normalizedInputs={normalizedInputs}
                                                overrides={overrides}
                                            />
                                        )}
                                    </div>
                                ) : (
                                    <div className="p-6 space-y-6">
                                        <div className="grid grid-cols-1 gap-4">
                                            {normalizedInputs.map(baseInput => {
                                                const override = overrides[functionName]?.[baseInput.name] || {};
                                                const input = { ...baseInput, ...override };

                                                return (
                                                    <div key={input.name} className="bg-background border border-border rounded-lg p-4 transition-all hover:border-primary/50">
                                                        <div className="flex items-start justify-between mb-4">
                                                            <div>
                                                                <h4 className="font-semibold text-text-main flex items-center gap-2">
                                                                    {input.label || input.name}
                                                                    <span className="text-xs font-mono text-text-muted bg-secondary/10 px-1.5 rounded">{input.name}</span>
                                                                </h4>
                                                                <p className="text-xs text-text-muted mt-1 max-w-xl">{input.description || "No description provided."}</p>
                                                            </div>
                                                        </div>

                                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                            {/* Validation Section */}
                                                            <div className="space-y-2">
                                                                <label className="text-xs font-medium text-text-muted uppercase tracking-wider">Validation Rule</label>
                                                                <div className="flex gap-2">
                                                                    <select
                                                                        className="bg-background border border-border rounded px-2 py-1.5 text-sm w-32 focus:outline-none focus:border-primary"
                                                                        onChange={(e) => handleSaveOverride(functionName, input.name, { ...override, validationRegex: e.target.value })}
                                                                        value={['^\\d*\\.?\\d+$', '^-?\\d+$', '^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$'].includes(input.validationRegex) ? input.validationRegex : 'custom'}
                                                                    >
                                                                        <option value="">None</option>
                                                                        <option value="^\\d*\\.?\\d+$">Positive Num</option>
                                                                        <option value="^-?\\d+$">Integer</option>
                                                                        <option value="^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$">Email</option>
                                                                        <option value="custom">Custom</option>
                                                                    </select>
                                                                    <input
                                                                        value={input.validationRegex || ''}
                                                                        onChange={(e) => handleSaveOverride(functionName, input.name, { ...override, validationRegex: e.target.value })}
                                                                        placeholder="Regex Pattern..."
                                                                        className="flex-1 bg-surface border border-border rounded px-3 py-1.5 text-sm font-mono focus:outline-none focus:border-primary"
                                                                    />
                                                                </div>
                                                            </div>

                                                            {/* Image Upload Section */}
                                                            <div className="space-y-2">
                                                                <label className="text-xs font-medium text-text-muted uppercase tracking-wider">Reference Image</label>
                                                                <div className="flex items-center gap-4">
                                                                    {input.imageUrl ? (
                                                                        <div className="relative h-12 w-12 rounded border border-border overflow-hidden group/img">
                                                                            <img src={input.imageUrl} alt="Ref" className="h-full w-full object-cover" />
                                                                            <button
                                                                                onClick={() => handleSaveOverride(functionName, input.name, { ...override, imageUrl: '' })}
                                                                                className="absolute inset-0 bg-black/50 text-white flex items-center justify-center opacity-0 group-hover/img:opacity-100 transition-opacity"
                                                                            >
                                                                                <X size={12} />
                                                                            </button>
                                                                        </div>
                                                                    ) : (
                                                                        <div className="h-12 w-12 rounded border border-dashed border-border flex items-center justify-center text-text-muted bg-surface/50">
                                                                            <Settings size={16} />
                                                                        </div>
                                                                    )}
                                                                    <label className="cursor-pointer flex items-center gap-2 text-xs font-medium text-primary hover:underline">
                                                                        Upload New
                                                                        <input
                                                                            type="file"
                                                                            className="hidden"
                                                                            accept="image/*"
                                                                            onChange={(e) => handleSchemaImageUpload(e.target.files[0], input.name)}
                                                                        />
                                                                    </label>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Soil Profile Modal */}
            <SoilProfileModal
                isOpen={isProfileModalOpen}
                onClose={() => setIsProfileModalOpen(false)}
                onSelect={(id) => {
                    // Start refreshing the list
                    setRefreshProfiles(prev => prev + 1);
                    // Find the input name for SoilProfile (usually 'soilprofile' but could be specific)
                    const soilProfileInput = normalizedInputs.find(i => i.objectType === 'SoilProfile');
                    if (soilProfileInput) {
                        handleChange(soilProfileInput.name, id);
                    }
                }}
            />

            {/* Saved Profiles List (Only for SoilProfile function) */}
            {/* Saved Profiles List (Only for SoilProfile function) */}
            {/* Saved Profiles List (Only for SoilProfile function) */}
            {functionName === 'SoilProfile' && (
                <div className="pt-6 border-t border-border">
                    <button
                        onClick={() => setShowSavedProfiles(!showSavedProfiles)}
                        className="flex items-center gap-2 text-sm font-medium text-text-muted hover:text-primary transition-colors mb-4"
                    >
                        {showSavedProfiles ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                        {showSavedProfiles ? "Hide Saved Profiles" : "Show Saved Profiles"}
                    </button>

                    {showSavedProfiles && (
                        <SavedProfilesList
                            refreshTrigger={refreshProfiles}
                            onDelete={async (id) => {
                                if (!confirm("Are you sure you want to delete this profile?")) return;
                                try {
                                    const res = await fetch(`http://127.0.0.1:8000/api/objects/SoilProfile/${id}`, { method: 'DELETE' });
                                    if (res.ok) setRefreshProfiles(prev => prev + 1);
                                } catch (e) {
                                    console.error("Failed to delete", e);
                                }
                            }}
                            onView={(id) => setViewProfileIds(id)}
                        />
                    )}
                </div>
            )}

            {/* Profile View Modal */}
            <ProfileViewModal
                isOpen={!!viewProfileId}
                profileId={viewProfileId}
                onClose={() => setViewProfileIds(null)}
            />

            {/* Schema Editor Tray */}
            <SchemaEditor
                isOpen={!!editingField}
                onClose={() => setEditingField(null)}
                field={editingField}
                onSave={handleSaveOverride}
                functionId={functionName}
            />

            {/* AI Auto-Fill Modal */}
            <AnimatePresence>
                {showAutoFillModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                        onClick={() => setShowAutoFillModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-surface border border-border rounded-xl shadow-2xl max-w-lg w-full p-5 space-y-4"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex items-center justify-between border-b border-border pb-3">
                                <div className="flex items-center gap-2">
                                    <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
                                        <Sparkles size={18} />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-sm text-text-main">AI Smart Auto-Fill</h3>
                                        <p className="text-xs text-text-muted">Paste borehole log or site notes to auto-extract parameters</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setShowAutoFillModal(false)}
                                    className="text-text-muted hover:text-text-main"
                                >
                                    <X size={16} />
                                </button>
                            </div>

                            <div className="space-y-2">
                                <textarea
                                    value={autoFillText}
                                    onChange={(e) => setAutoFillText(e.target.value)}
                                    placeholder="e.g.: SPT borehole test at depth 4.5m indicates sand layer with friction angle phi = 32 deg, unit weight gamma = 19 kN/m3 and cohesion c = 0 kPa..."
                                    rows={5}
                                    className="w-full bg-background border border-border rounded-lg p-3 text-xs text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                                />
                                {autoFillMsg && (
                                    <div className={`p-2.5 rounded-lg text-xs font-medium ${
                                        autoFillMsg.type === 'success'
                                            ? 'bg-green-500/10 text-green-500 border border-green-500/20'
                                            : autoFillMsg.type === 'warn'
                                            ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                                            : 'bg-red-500/10 text-red-500 border border-red-500/20'
                                    }`}>
                                        {autoFillMsg.text}
                                    </div>
                                )}
                            </div>

                            <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
                                <Button
                                    variant="secondary"
                                    onClick={() => setShowAutoFillModal(false)}
                                    className="text-xs py-1.5 px-3"
                                >
                                    Cancel
                                </Button>
                                <Button
                                    variant="primary"
                                    onClick={handleAutoFill}
                                    disabled={!autoFillText.trim() || isAutoFilling}
                                    className="text-xs py-1.5 px-3 flex items-center gap-1.5"
                                >
                                    {isAutoFilling ? <Loader size={14} className="animate-spin" /> : <Sparkles size={14} />}
                                    <span>Extract & Populate</span>
                                </Button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

        </>
    );
};

