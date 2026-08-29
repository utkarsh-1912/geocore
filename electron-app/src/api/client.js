/** Author: Utkarsh Gupta, License: GPL v3 */

const API_BASE = 'http://127.0.0.1:8000';
const DEFAULT_TIMEOUT = 30000;
const EXECUTE_TIMEOUT = 120000;

async function fetchWithTimeout(resource, options = {}) {
    const { timeout = DEFAULT_TIMEOUT } = options;
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    const response = await fetch(`${API_BASE}${resource}`, {
        ...options,
        signal: controller.signal
    });
    clearTimeout(id);
    return response;
}

async function handleResponse(response) {
    if (!response.ok) {
        let errData;
        try {
            errData = await response.json();
        } catch (e) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        let errorMsg = 'An error occurred';
        let errorDetails = null;

        if (typeof errData.detail === 'string') {
            errorMsg = errData.detail;
        } else if (errData.detail && typeof errData.detail === 'object') {
            errorMsg = errData.detail.error || errData.detail.message || JSON.stringify(errData.detail);
            errorDetails = errData.detail.details;
        } else if (errData.error) {
            errorMsg = typeof errData.error === 'string' ? errData.error : JSON.stringify(errData.error);
            errorDetails = errData.details;
        }

        const customError = new Error(errorMsg);
        if (errorDetails) customError.details = errorDetails;
        throw customError;
    }
    
    // For DELETE or empty responses
    if (response.status === 204 || response.headers.get('content-length') === '0') {
        return null;
    }
    
    return await response.json();
}

export const api = {
    // Health Check
    health: async () => {
        const response = await fetchWithTimeout('/health', { timeout: 5000 });
        if (!response.ok) throw new Error('Health check failed');
        return true;
    },

    // Execution
    execute: async (moduleId, functionId, args) => {
        const response = await fetchWithTimeout('/api/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ moduleId, functionId, args }),
            timeout: EXECUTE_TIMEOUT
        });
        const results = await handleResponse(response);
        if (results && results.error) {
            const customError = new Error(typeof results.error === 'string' ? results.error : JSON.stringify(results.error));
            if (results.details) customError.details = results.details;
            throw customError;
        }
        return results;
    },

    // GeoAI
    geoaiChat: async (prompt, context) => {
        const response = await fetchWithTimeout('/api/geoai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, context }),
            timeout: 60000 // Slightly longer for AI
        });
        return handleResponse(response);
    },

    geoaiAutofill: async (raw_text, function_id) => {
        const response = await fetchWithTimeout('/api/geoai/autofill', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ raw_text, function_id })
        });
        return handleResponse(response);
    },

    geoaiChatStream: async (prompt, context = {}) => {
        const response = await fetch(`${API_BASE}/api/geoai/chat?stream=true`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, context }),
        });
        if (!response.ok) {
            throw new Error(`GeoAI stream request failed: ${response.status}`);
        }
        return response;
    },

    geoaiStatus: async () => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/status`, { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiListModels: async () => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/models`, { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiDownloadModel: async (modelId = 'qwen2.5-1.5b-instruct', setActive = true) => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/models/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId, set_active: setActive })
        });
        return handleResponse(response);
    },

    geoaiGetDownloadStatus: async () => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/models/download/status`, { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiSelectModel: async (modelPath, provider = 'llama_cpp') => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/models/select`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_path: modelPath, provider })
        });
        return handleResponse(response);
    },

    geoaiAutoLinkModels: async () => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/models/autolink`, {
            method: 'POST'
        });
        return handleResponse(response);
    },

    geoaiGetMemory: async () => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/memory`, { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiUnloadModel: async () => {
        const response = await fetchWithTimeout(`${API_BASE}/api/geoai/unload`, {
            method: 'POST'
        });
        return handleResponse(response);
    },

    // Schema Overrides
    getSchemaOverrides: async () => {
        const response = await fetchWithTimeout('/api/schema/overrides');
        return handleResponse(response);
    },

    saveSchemaOverride: async (functionId, fieldName, metadata) => {
        const response = await fetchWithTimeout('/api/schema/override', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ functionId, fieldName, metadata })
        });
        return handleResponse(response);
    },
    
    // Uploads
    uploadAsset: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetchWithTimeout('/api/assets/upload', {
            method: 'POST',
            body: formData
        });
        return handleResponse(response);
    },

    // Soil Profiles (As requested by the prompt endpoints)
    listSoilProfiles: async () => {
        const response = await fetchWithTimeout('/api/soilprofiles');
        return handleResponse(response);
    },
    getSoilProfile: async (id) => {
        const response = await fetchWithTimeout(`/api/soilprofiles/${id}`);
        return handleResponse(response);
    },
    createSoilProfile: async (data) => {
        const response = await fetchWithTimeout('/api/soilprofiles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return handleResponse(response);
    },
    deleteSoilProfile: async (id) => {
        const response = await fetchWithTimeout(`/api/soilprofiles/${id}`, {
            method: 'DELETE'
        });
        return handleResponse(response);
    },

    // Calculation Grids (As requested by the prompt endpoints)
    listCalculationGrids: async () => {
        const response = await fetchWithTimeout('/api/calculationgrids');
        return handleResponse(response);
    },
    getCalculationGrid: async (id) => {
        const response = await fetchWithTimeout(`/api/calculationgrids/${id}`);
        return handleResponse(response);
    },
    createCalculationGrid: async (data) => {
        const response = await fetchWithTimeout('/api/calculationgrids', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return handleResponse(response);
    },
    deleteCalculationGrid: async (id) => {
        const response = await fetchWithTimeout(`/api/calculationgrids/${id}`, {
            method: 'DELETE'
        });
        return handleResponse(response);
    },
    
    // Generic Object APIs (Found in source)
    listObjects: async (objectType) => {
        const response = await fetchWithTimeout(`/api/objects/${objectType}`);
        return handleResponse(response);
    },
    getObject: async (objectType, id) => {
        const response = await fetchWithTimeout(`/api/objects/${objectType}/${id}`);
        return handleResponse(response);
    },
    createObject: async (objectType, data) => {
        const response = await fetchWithTimeout(`/api/objects/create?type_name=${objectType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return handleResponse(response);
    },
    uploadObjectFile: async (objectType, file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetchWithTimeout(`/api/objects/upload?type_name=${objectType}`, {
            method: 'POST',
            body: formData
        });
        return handleResponse(response);
    },
    deleteObject: async (objectType, id) => {
        const response = await fetchWithTimeout(`/api/objects/${objectType}/${id}`, {
            method: 'DELETE'
        });
        return handleResponse(response);
    }
};
