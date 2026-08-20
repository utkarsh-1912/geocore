/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Card } from '../../components/ui/Card';
import { ArrowRight, Folder, FileText } from 'lucide-react';

export const DashboardGrid = ({ items, onSelect, title, description, isCategory = false }) => {
    return (
        <div className="max-w-7xl mx-auto h-full flex flex-col">
            <div className="mb-8 shrink-0">
                <h2 className="text-3xl font-bold text-text-main mb-2">{title}</h2>
                {description && <p className="text-text-muted">{description}</p>}
            </div>

            {items && items.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-4">
                    {items.map((item, index) => (
                        <motion.div
                            key={item.id || item.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            onClick={() => onSelect(item)}
                            className="cursor-pointer group"
                        >
                            <Card className="h-full hover:border-primary transition-colors duration-300 relative overflow-hidden group-hover:shadow-lg">
                                <div className="flex items-start justify-between mb-4">
                                    <div className={`p-3 rounded-lg ${isCategory ? 'bg-primary/10 text-primary' : 'bg-primary-light/10 text-primary-light'}`}>
                                        {isCategory ? <Folder size={24} /> : <FileText size={24} />}
                                    </div>
                                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-x-2 group-hover:translate-x-0">
                                        <ArrowRight size={20} className="text-primary" />
                                    </div>
                                </div>

                                <h3 className="text-xl font-semibold text-text-main mb-2 bg-gradient-to-r from-text-main to-text-main bg-[length:0%_2px] bg-no-repeat bg-left-bottom group-hover:bg-[length:100%_2px] transition-all duration-300 from-primary">
                                    {item.title}
                                </h3>

                                <p className="text-text-muted text-sm line-clamp-2">
                                    {item.description || "Access geotechnical modules and calculations."}
                                </p>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            ) : (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    className="flex-1 flex flex-col items-center justify-center p-12 min-h-[400px] text-center"
                >
                    <h3 className="text-xl font-semibold text-text-muted mb-2">No Modules Available</h3>
                    <p className="text-text-muted/70 max-w-sm">
                        This category does not have any active calculation modules yet. Please explore other categories in the sidebar.
                    </p>
                </motion.div>
            )}
        </div>
    );
};
