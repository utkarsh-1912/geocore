import React, { useState, useEffect } from 'react';
import { Button } from '../../components/ui/Button';
import { X, Loader } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const ProfileViewModal = ({ profileId, isOpen, onClose }) => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [displayLimit, setDisplayLimit] = useState(50);

    useEffect(() => {
        if (isOpen && profileId) {
            fetchProfile(profileId);
        } else {
            setProfile(null);
            setDisplayLimit(50);
        }
    }, [isOpen, profileId]);

    const fetchProfile = async (id) => {
        setLoading(true);
        try {
            const res = await fetch(`http://127.0.0.1:8000/api/objects/SoilProfile/${id}`);
            const data = await res.json();
            setProfile({ id, ...data });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-surface w-full max-w-4xl max-h-[90vh] rounded-lg shadow-2xl flex flex-col border border-border"
            >
                <div className="flex items-center justify-between p-4 border-b border-border bg-background shrink-0">
                    <div>
                        <h4 className="text-lg font-bold text-text-main flex items-center gap-2">
                            {profile?.name || 'Soil Profile'}
                        </h4>
                        <div className="text-xs text-text-muted">ID: {profileId}</div>
                    </div>
                    <button onClick={onClose} className="p-1 rounded-full hover:bg-background text-text-muted transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <div className="flex-1 overflow-auto p-0 relative min-h-[200px]">
                    {loading ? (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Loader className="animate-spin text-primary" size={32} />
                        </div>
                    ) : profile?.data && profile.data.length > 0 ? (
                        <div className="w-full">
                            <table className="w-full text-sm text-left border-collapse">
                                <thead className="bg-secondary/20 text-text-main font-semibold sticky top-0 z-10 backdrop-blur-md">
                                    <tr>
                                        {Object.keys(profile.data[0]).map(key => (
                                            <th key={key} className="p-3 border-b border-border whitespace-nowrap bg-background/95">{key}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border">
                                    {profile.data.slice(0, displayLimit).map((row, idx) => (
                                        <tr key={idx} className="hover:bg-primary/5 transition-colors">
                                            {Object.values(row).map((val, i) => (
                                                <td key={i} className="p-2 whitespace-nowrap text-text-main border-r border-border last:border-r-0">{val}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>

                            {profile.data.length > displayLimit && (
                                <div className="p-4 text-center border-t border-border bg-background sticky bottom-0">
                                    <div className="text-xs text-text-muted mb-2">
                                        Showing {displayLimit} of {profile.data.length} rows
                                    </div>
                                    <Button
                                        onClick={() => setDisplayLimit(prev => prev + 100)}
                                        variant="secondary"
                                        size="sm"
                                    >
                                        Load More
                                    </Button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="p-12 text-center text-text-muted">
                            <p>No data available for preview.</p>
                            {profile?.columns && (
                                <p className="text-xs mt-2 font-mono">Columns: {profile.columns.join(', ')}</p>
                            )}
                        </div>
                    )}
                </div>

                <div className="p-4 border-t border-border flex justify-end gap-2 shrink-0 bg-background rounded-b-lg">
                    <Button onClick={onClose} variant="primary">Close</Button>
                </div>
            </motion.div>
        </div>
    );
};
