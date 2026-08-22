/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState, useEffect } from 'react';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { Input } from '../../components/ui/Input';
import { X, Upload, Plus, Trash2, Check, FileText, Loader, Eye, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { ProfileViewModal } from './ProfileViewModal';

export const SoilProfileModal = ({ isOpen, onClose, onSelect, objectType = "SoilProfile" }) => {
    const [activeTab, setActiveTab] = useState('select'); // select, create, upload
    const [profiles, setProfiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [viewProfile, setViewProfile] = useState(null); // Profile to view details

    // Select State
    const [selectedId, setSelectedId] = useState('');

    // Create State
    const [layers, setLayers] = useState([
        { depth_to: 10, soil_type: 'Clay', unit_weight: 18, total_unit_weight: 20, cohesion: 0, friction_angle: 30 }
    ]);
    const [profileName, setProfileName] = useState('');
    const [waterLevel, setWaterLevel] = useState(0);

    // Upload State
    const [uploadFile, setUploadFile] = useState(null);
    const [uploadName, setUploadName] = useState('');

    useEffect(() => {
        if (isOpen) {
            fetchProfiles();
        }
    }, [isOpen]);

    const fetchProfiles = async () => {
        setLoading(true);
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/objects/${objectType}`);
            const data = await res.json();
            setProfiles(data.objects || []);
        } catch (err) {
            console.error("Failed to fetch profiles", err);
        } finally {
            setLoading(false);
        }
    };

    const handleLayerChange = (index, field, value) => {
        const newLayers = [...layers];
        if (field === 'soil_type') {
            newLayers[index][field] = value;
        } else {
            newLayers[index][field] = parseFloat(value);
        }
        setLayers(newLayers);
    };

    const addLayer = () => {
        setLayers([...layers, { ...layers[layers.length - 1] }]);
    };

    const removeLayer = (index) => {
        if (layers.length > 1) {
            setLayers(layers.filter((_, i) => i !== index));
        }
    };

    const handleCreate = async () => {
        // Prepare data for creating formatted as per Registry expectation
        // Registry expects DataFrame columns or similar input
        // We'll rename our internal keys to standard Geocore column names
        const formattedData = layers.map((layer, idx) => {
            const depthFrom = idx === 0 ? 0 : layers[idx - 1].depth_to;
            return {
                "Depth from [m]": depthFrom,
                "Depth to [m]": layer.depth_to,
                "Soil type": layer.soil_type,
                "Unit Weight [kN/m3]": layer.unit_weight,
                "Total Unit Weight [kN/m3]": layer.total_unit_weight,
                "Cohesion [kPa]": layer.cohesion,
                "Friction Angle [deg]": layer.friction_angle
            };
        });

        const payload = {
            raw_data: formattedData,
            name: profileName || `Manual Profile ${new Date().toLocaleTimeString()}`,
            water_level: waterLevel
        };

        try {
            setLoading(true);
            const res = await fetch(`http://127.0.0.1:8000/api/objects/create?type_name=${objectType}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("Failed to create profile");

            const data = await res.json();
            onSelect(data.id);
            onClose();
        } catch (err) {
            console.error(err);
            toast.error("Error creating profile: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async () => {
        if (!uploadFile) return;

        const formData = new FormData();
        formData.append('file', uploadFile);
        // We can pass name if supported, else registry uses filename

        try {
            setLoading(true);
            const res = await fetch(`http://127.0.0.1:8000/api/objects/upload?type_name=${objectType}`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) throw new Error("Failed to upload profile");

            const data = await res.json();
            onSelect(data.id);
            onClose();
        } catch (err) {
            console.error(err);
            toast.error("Error uploading profile: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (e, id) => {
        e.stopPropagation();
        if (!confirm("Are you sure you want to delete this profile?")) return;

        try {
            const res = await fetch(`http://127.0.0.1:8000/api/objects/${objectType}/${id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                fetchProfiles();
                if (selectedId === id) setSelectedId('');
            }
        } catch (err) {
            console.error("Failed to delete", err);
        }
    };

    const handleView = (e, id) => {
        e.stopPropagation();
        setViewProfile({ id });
    };

    const handleSelectCurrent = () => {
        if (selectedId) {
            onSelect(selectedId);
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-surface w-full max-w-4xl max-h-[90vh] rounded-lg shadow-2xl flex flex-col border border-border"
            >
                <div className="flex items-center justify-between p-4 border-b border-border">
                    <h3 className="text-lg font-bold text-text-main flex items-center gap-2">
                        <FileText size={20} className="text-primary" />
                        Manage {objectType}s
                    </h3>
                    <button onClick={onClose} className="p-1 rounded-full hover:bg-background text-text-muted transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <div className="flex border-b border-border">
                    <button
                        onClick={() => setActiveTab('select')}
                        className={`px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'select' ? 'text-primary border-b-2 border-primary' : 'text-text-muted hover:text-text-main'}`}
                    >
                        Select Existing
                    </button>
                    <button
                        onClick={() => setActiveTab('create')}
                        className={`px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'create' ? 'text-primary border-b-2 border-primary' : 'text-text-muted hover:text-text-main'}`}
                    >
                        Create New
                    </button>
                    <button
                        onClick={() => setActiveTab('upload')}
                        className={`px-4 py-3 text-sm font-medium transition-colors ${activeTab === 'upload' ? 'text-primary border-b-2 border-primary' : 'text-text-muted hover:text-text-main'}`}
                    >
                        Upload File
                    </button>
                </div>

                <div className="p-6 overflow-y-auto flex-1">
                    {activeTab === 'select' && (
                        <div className="space-y-4">
                            {profiles.length === 0 ? (
                                <div className="text-center py-8 text-text-muted">
                                    No profiles found. Create one or upload a file.
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 gap-2">
                                    {profiles.map(p => (
                                        <div
                                            key={p.id}
                                            onClick={() => setSelectedId(p.id)}
                                            className={`p-3 rounded border cursor-pointer flex items-center justify-between transition-colors ${selectedId === p.id ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}`}
                                        >
                                            <div>
                                                <div className="font-medium text-text-main">{p.name}</div>
                                                <div className="text-xs text-text-muted">ID: {p.id.substring(0, 8)}...</div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={(e) => handleView(e, p.id)}
                                                    className="p-1.5 rounded hover:bg-background text-text-muted hover:text-primary transition-colors"
                                                    title="View Details"
                                                >
                                                    <Eye size={16} />
                                                </button>
                                                <button
                                                    onClick={(e) => handleDelete(e, p.id)}
                                                    className="p-1.5 rounded hover:bg-background text-text-muted hover:text-red-500 transition-colors"
                                                    title="Delete"
                                                >
                                                    <Trash2 size={16} />
                                                </button>

                                                {selectedId === p.id && <Check size={16} className="text-primary ml-2" />}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                            <div className="flex justify-end pt-4">
                                <Button onClick={handleSelectCurrent} disabled={!selectedId} variant="primary">
                                    Select Profile
                                </Button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'create' && (
                        <div className="space-y-4">
                            <div className="flex gap-4">
                                <div className="flex-1">
                                    <Input
                                        label="Profile Name"
                                        value={profileName}
                                        onChange={(e) => setProfileName(e.target.value)}
                                        placeholder="My Soil Profile"
                                    />
                                </div>
                                <div className="w-1/3">
                                    <Input
                                        label="Water Level [m]"
                                        type="number"
                                        value={waterLevel}
                                        onChange={(e) => setWaterLevel(e.target.value)}
                                    />
                                </div>
                            </div>

                            <div className="border border-border rounded overflow-hidden">
                                <table className="w-full text-sm text-left">
                                    <thead className="bg-background text-text-muted font-medium">
                                        <tr>
                                            <th className="p-2">Depth To [m]</th>
                                            <th className="p-2">Soil Type</th>
                                            <th className="p-2">Unit Wt [kN/m3]</th>
                                            <th className="p-2">Total Unit Wt</th>
                                            <th className="p-2">Cohesion [kPa]</th>
                                            <th className="p-2">Friction [deg]</th>
                                            <th className="p-2 w-10"></th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-border">
                                        {layers.map((layer, idx) => (
                                            <tr key={idx}>
                                                <td className="p-2"><input type="number" step="0.1" className="w-full bg-transparent border-none focus:ring-0 text-text-main" value={layer.depth_to} onChange={(e) => handleLayerChange(idx, 'depth_to', e.target.value)} /></td>
                                                <td className="p-2"><input type="text" className="w-full bg-transparent border-none focus:ring-0 text-text-main" value={layer.soil_type} onChange={(e) => handleLayerChange(idx, 'soil_type', e.target.value)} /></td>
                                                <td className="p-2"><input type="number" step="0.1" className="w-full bg-transparent border-none focus:ring-0 text-text-main" value={layer.unit_weight} onChange={(e) => handleLayerChange(idx, 'unit_weight', e.target.value)} /></td>
                                                <td className="p-2"><input type="number" step="0.1" className="w-full bg-transparent border-none focus:ring-0 text-text-main" value={layer.total_unit_weight} onChange={(e) => handleLayerChange(idx, 'total_unit_weight', e.target.value)} /></td>
                                                <td className="p-2"><input type="number" step="0.1" className="w-full bg-transparent border-none focus:ring-0 text-text-main" value={layer.cohesion} onChange={(e) => handleLayerChange(idx, 'cohesion', e.target.value)} /></td>
                                                <td className="p-2"><input type="number" step="0.1" className="w-full bg-transparent border-none focus:ring-0 text-text-main" value={layer.friction_angle} onChange={(e) => handleLayerChange(idx, 'friction_angle', e.target.value)} /></td>
                                                <td className="p-2 text-center">
                                                    <button onClick={() => removeLayer(idx)} className="text-red-500 hover:text-red-700">
                                                        <Trash2 size={14} />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            <Button onClick={addLayer} variant="secondary" className="w-full flex items-center justify-center gap-2">
                                <Plus size={16} /> Add Layer
                            </Button>

                            <div className="flex justify-end pt-4">
                                <Button onClick={handleCreate} variant="primary" disabled={loading}>
                                    {loading ? "Creating..." : "Create Profile"}
                                </Button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'upload' && (
                        <div className="space-y-4">
                            <div className="border-2 border-dashed border-border rounded-lg p-8 flex flex-col items-center justify-center text-center hover:border-primary transition-colors cursor-pointer"
                                onClick={() => document.getElementById('modal-file-upload').click()}
                            >
                                <Upload size={48} className="text-primary mb-4" />
                                <div className="text-lg font-medium text-text-main">
                                    {uploadFile ? uploadFile.name : "Click to select a file"}
                                </div>
                                <div className="text-sm text-text-muted mt-2">
                                    Supports .csv, .xlsx (with headers: Depth to, Unit Weight, etc.)
                                </div>
                                <input
                                    id="modal-file-upload"
                                    type="file"
                                    className="hidden"
                                    accept=".csv,.xlsx,.xls"
                                    onChange={(e) => setUploadFile(e.target.files[0])}
                                />
                            </div>

                            <div className="flex justify-end pt-4">
                                <Button onClick={handleUpload} variant="primary" disabled={!uploadFile || loading}>
                                    {loading ? "Uploading..." : "Upload & Create"}
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </motion.div>

            {/* Replaced inline view with ProfileViewModal to centralize logic and styling */}
            <ProfileViewModal
                isOpen={!!viewProfile}
                profileId={viewProfile?.id}
                onClose={() => setViewProfile(null)}
            />
        </div>
    );
};
