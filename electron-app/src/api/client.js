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

    // Diagnostics for the System Health panel; latencyMs is the round trip seen by the app.
    healthDetails: async () => {
        const started = performance.now();
        const response = await fetchWithTimeout('/health/details', { timeout: 5000 });
        const data = await handleResponse(response);
        return { ...data, latencyMs: Math.round(performance.now() - started) };
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

    // Groundhog's validated min/max per {function: {parameter}}; static for the app's lifetime.
    getFieldBounds: async () => {
        const response = await fetchWithTimeout('/api/schema/bounds', { timeout: 10000 });
        return handleResponse(response);
    },

    // Audit trail of every calculation run through /api/execute (any calculator, not just GeoAI chat).
    getCalculationHistory: async (limit = 50) => {
        const response = await fetchWithTimeout(`/api/calculation-history?limit=${limit}`, { timeout: 5000 });
        return handleResponse(response);
    },

    clearCalculationHistory: async () => {
        const response = await fetchWithTimeout('/api/calculation-history', { method: 'DELETE', timeout: 5000 });
        return handleResponse(response);
    },

    // Mark (or unmark) one audit-trail entry as checked. note is optional.
    reviewCalculationHistoryEntry: async (entryId, reviewed = true, note = undefined) => {
        const response = await fetchWithTimeout(`/api/calculation-history/${entryId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reviewed, note }),
            timeout: 5000
        });
        return handleResponse(response);
    },

    // GeoAI
    geoaiChat: async (prompt, context, history = []) => {
        const response = await fetchWithTimeout('/api/geoai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, context, history }),
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

    geoaiChatStream: async (prompt, context = {}, history = [], signal = undefined) => {
        const response = await fetch(`${API_BASE}/api/geoai/chat?stream=true`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, context, history }),
            signal,
        });
        if (!response.ok) {
            throw new Error(`GeoAI stream request failed: ${response.status}`);
        }
        return response;
    },

    geoaiListTools: async () => {
        const response = await fetchWithTimeout('/api/geoai/tools', { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiStatus: async () => {
        const response = await fetchWithTimeout('/api/geoai/status', { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiListModels: async () => {
        const response = await fetchWithTimeout('/api/geoai/models', { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiDownloadModel: async (modelId = 'qwen3-1.7b', setActive = true) => {
        const response = await fetchWithTimeout('/api/geoai/models/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: modelId, set_active: setActive })
        });
        return handleResponse(response);
    },

    geoaiGetDownloadStatus: async () => {
        const response = await fetchWithTimeout('/api/geoai/models/download/status', { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiSelectModel: async (modelPath, provider = 'llama_cpp') => {
        const response = await fetchWithTimeout('/api/geoai/models/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_path: modelPath, provider })
        });
        return handleResponse(response);
    },

    geoaiAutoLinkModels: async () => {
        const response = await fetchWithTimeout('/api/geoai/models/autolink', {
            method: 'POST'
        });
        return handleResponse(response);
    },

    geoaiGetMemory: async () => {
        const response = await fetchWithTimeout('/api/geoai/memory', { timeout: 5000 });
        return handleResponse(response);
    },

    geoaiUnloadModel: async () => {
        const response = await fetchWithTimeout('/api/geoai/unload', {
            method: 'POST'
        });
        return handleResponse(response);
    },

    geoaiCancel: async () => {
        const response = await fetchWithTimeout('/api/geoai/cancel', {
            method: 'POST',
            timeout: 5000
        });
        return handleResponse(response);
    },

    geoaiWarmup: async () => {
        const response = await fetchWithTimeout('/api/geoai/warmup', {
            method: 'POST',
            timeout: 5000
        });
        return handleResponse(response);
    },

    // Deterministic explanation of one result (method, standard, formula, substituted values).
    // No model call, fast — safe to call right after a calculation completes.
    geoaiExplain: async (function_id, args, results) => {
        const response = await fetchWithTimeout('/api/geoai/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function_id, args, results }),
            timeout: 5000
        });
        return handleResponse(response);
    },

    // Short plain-language narration of the same explanation, from the local model. Call this
    // separately (and don't block on it) — it can take a few seconds on a cold or CPU-bound model.
    geoaiExplainNarrate: async (function_id, args, results, signal = undefined) => {
        const response = await fetch(`${API_BASE}/api/geoai/explain/narrate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ function_id, args, results }),
            signal
        });
        return handleResponse(response);
    },

    // Project groundwater level [m below ground level]; null = not recorded.
    geoaiGetGroundwater: async () => {
        const response = await fetchWithTimeout('/api/geoai/project/groundwater');
        return handleResponse(response);
    },

    geoaiSetGroundwater: async (depthM) => {
        const response = await fetchWithTimeout('/api/geoai/project/groundwater', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ groundwater_depth_m: depthM, unit: 'm' })
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
    // Object creation/upload runs the same Groundhog registry path (and warm-up wait) as
    // /api/execute, so it gets the same generous timeout instead of the 30s default - a raw
    // fetch with no timeout used to hang on "Uploading..." until the OS killed the idle
    // connection (~5 min) before surfacing any error.
    createObject: async (objectType, data) => {
        const response = await fetchWithTimeout(`/api/objects/create?type_name=${objectType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            timeout: EXECUTE_TIMEOUT
        });
        return handleResponse(response);
    },
    // dataKind: 'cpt' | 'soil_profile' - what the uploaded table holds (recorded with the object).
    uploadObjectFile: async (objectType, file, dataKind = null) => {
        const formData = new FormData();
        formData.append('file', file);
        const kindParam = dataKind ? `&data_kind=${encodeURIComponent(dataKind)}` : '';
        const response = await fetchWithTimeout(`/api/objects/upload?type_name=${objectType}${kindParam}`, {
            method: 'POST',
            body: formData,
            timeout: EXECUTE_TIMEOUT
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
