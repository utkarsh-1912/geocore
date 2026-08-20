import React, { useState, useEffect } from 'react';
import { Trash2, Eye, FileText, RefreshCw, Loader } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export const SavedProfilesList = ({ onSelect, onDelete, onView, refreshTrigger }) => {
    const [profiles, setProfiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchProfiles = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch('http://127.0.0.1:8000/api/objects/SoilProfile');
            if (!res.ok) throw new Error("Failed to fetch profiles");
            const data = await res.json();
            setProfiles(data.objects || []);
        } catch (err) {
            console.error("Failed to load profiles", err);
            setError("Failed to load profiles.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProfiles();
    }, [refreshTrigger]);

    if (loading && profiles.length === 0) {
        return <div className="p-4 text-center text-text-muted flex items-center justify-center gap-2"><Loader className="animate-spin" size={16} /> Loading profiles...</div>;
    }

    if (error) {
        return (
            <div className="p-4 border border-red-500/20 bg-red-500/10 rounded text-red-500 text-sm flex items-center justify-between">
                <span>{error}</span>
                <button onClick={fetchProfiles} className="p-1 hover:bg-red-500/20 rounded"><RefreshCw size={14} /></button>
            </div>
        );
    }

    if (profiles.length === 0) {
        return null; // Hide completely if no profiles
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-text-muted uppercase tracking-wider">Saved Profiles</h4>
                <button onClick={fetchProfiles} className="text-xs text-primary hover:underline flex items-center gap-1">
                    <RefreshCw size={12} /> Refresh
                </button>
            </div>
            <div className="grid grid-cols-1 gap-2 max-h-[300px] overflow-y-auto pr-1 custom-scrollbar">
                {profiles.map(p => (
                    <div
                        key={p.id}
                        className="p-3 bg-background border border-border rounded-lg flex items-center justify-between hover:border-primary/50 transition-colors group"
                    >
                        <div className="flex items-center gap-3 overflow-hidden">
                            <div className="p-2 bg-secondary/10 rounded text-primary">
                                <FileText size={18} />
                            </div>
                            <div className="min-w-0">
                                <div className="font-medium text-text-main truncate" title={p.name}>{p.name}</div>
                                <div className="text-xs text-text-muted truncate">ID: {p.id.substring(0, 8)}...</div>
                            </div>
                        </div>

                        <div className="flex items-center gap-1 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    console.log("View clicked for", p.id);
                                    onView(p.id);
                                }}
                                className="p-2 text-text-muted hover:text-primary hover:bg-primary/10 rounded transition-colors"
                                title="View Details"
                            >
                                <Eye size={16} />
                            </button>
                            <button
                                onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    onDelete(p.id);
                                }}
                                className="p-2 text-text-muted hover:text-red-500 hover:bg-red-500/10 rounded transition-colors"
                                title="Delete Profile"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
