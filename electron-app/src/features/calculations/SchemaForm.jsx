/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React, { useState, useEffect } from 'react';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { HelpCircle, X, Book, Loader, Settings, ChevronDown, ChevronRight, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import * as XLSX from 'xlsx';
import Papa from 'papaparse';
import { SoilProfileModal } from './SoilProfileModal';
import { SavedProfilesList } from './SavedProfilesList';
import { ProfileViewModal } from './ProfileViewModal';
import SchemaEditor from './SchemaEditor';
import { Edit2, Save } from 'lucide-react';


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
                <option value={value}>[Current/Restored] ID: {value.substring(0, 8)}...</option>
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

    // Fetch Overrides and Page Docs on Mount/Update
    useEffect(() => {
        fetch('http://localhost:8000/api/schema/overrides')
            .then(res => res.json())
            .then(data => {
                console.log("Loaded schema overrides:", data);
                setOverrides(data);

                // Initialize Page Docs
                const customDocs = data[functionName]?._page_docs?.description;
                const defaultDocs = schema?.documentation || '';
                setPageDocs(customDocs || defaultDocs);
                setEditedDocs(customDocs || defaultDocs);
            })
            .catch(err => console.error("Failed to load schema overrides:", err));
    }, [functionName, schema]);

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

    if (!schema) return <div className="text-gray-400">Select a function to configure parameters.</div>;

    return (

        <>
            <Card className="w-full relative">
                <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
                    <h3 className="font-semibold text-text-main flex items-center gap-2">
                        Input Parameters
                        {isEditMode && <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full">Editing Mode</span>}
                    </h3>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setIsEditMode(!isEditMode)}
                            className={`flex items-center gap-2 text-sm font-medium transition-colors px-3 py-1.5 border border-border rounded-md ${isEditMode ? 'bg-primary text-white shadow-md' : 'text-text-muted hover:bg-secondary/10'}`}
                            title="Toggle Edit Mode"
                        >
                            {isEditMode ? <Check size={16} /> : <Edit2 size={16} />}
                        </button>
                        <button
                            onClick={() => setShowDocs(true)}
                            className="text-primary hover:text-primary/80 transition-colors flex items-center gap-2 text-sm font-medium"
                            title="View Documentation"
                        >
                            <Book size={16} />
                            Documentation
                        </button>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {normalizedInputs.map((baseInput) => {
                            // Apply Overrides
                            const override = overrides[functionName]?.[baseInput.name] || {};
                            const input = { ...baseInput, ...override };

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
                                            {fileColumns.length === 0 && <span className="text-xs text-text-muted mt-1">Upload a file to see columns</span>}
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
                                                value={formData[input.name] || ''}
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
                            className="bg-surface w-full max-w-5xl max-h-[85vh] rounded-lg shadow-2xl flex flex-col border border-border"
                        >
                            <div className="flex items-center justify-between p-4 border-b border-border bg-background shrink-0">
                                <h3 className="text-lg font-bold text-text-main flex items-center gap-2">
                                    <Book size={20} className="text-primary" />
                                    {functionName} Configuration
                                </h3>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => setShowDocs(false)}
                                        className="p-1 rounded-full hover:bg-background text-text-muted transition-colors"
                                    >
                                        <X size={20} />
                                    </button>
                                </div>
                            </div>

                            <Tabs
                                tabs={[
                                    { id: 'guide', label: 'User Guide' },
                                    { id: 'fields', label: 'Field Configuration' }
                                ]}
                                activeTab={activeDocTab}
                                onChange={setActiveDocTab}
                            />

                            <div className="flex-1 overflow-y-auto p-0 bg-surface/50">
                                {activeDocTab === 'guide' ? (
                                    <div className="p-6 h-full flex flex-col">
                                        <div className="flex justify-end mb-4">
                                            <button
                                                onClick={() => setIsEditingDocs(!isEditingDocs)}
                                                className={`p-1.5 rounded-full flex items-center gap-2 text-sm transition-colors ${isEditingDocs ? 'bg-primary text-white' : 'text-text-muted hover:bg-secondary/10'}`}
                                            >
                                                {isEditingDocs ? <Check size={16} /> : <Edit2 size={16} />}
                                            </button>
                                        </div>
                                        {isEditingDocs ? (
                                            <div className="flex-1 flex flex-col gap-2">
                                                <textarea
                                                    value={editedDocs}
                                                    onChange={(e) => setEditedDocs(e.target.value)}
                                                    className="w-full flex-1 min-h-[400px] p-4 bg-background border border-border rounded font-mono text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                                                    placeholder="Enter HTML or text documentation..."
                                                />
                                                <div className="flex justify-end gap-2">
                                                    <Button variant="secondary" onClick={() => {
                                                        setEditedDocs(pageDocs);
                                                        setIsEditingDocs(false);
                                                    }}>Cancel</Button>
                                                    <Button variant="primary" onClick={handleSavePageDocs}>Save Guide</Button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="prose dark:prose-invert max-w-none">
                                                <div dangerouslySetInnerHTML={{ __html: pageDocs }} />
                                            </div>
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

        </>
    );
};

