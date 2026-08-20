/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React from 'react';
import { Layers, Box, Shovel, FileText, Activity, Droplets, Database, Ruler, Zap, Anchor } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

const CategoryIcon = ({ id }) => {
    const icons = {
        'general': Database,
        'site_investigation': SearchIcon, // defined below
        'piles': Box,
        'shallow': Components,
        'consolidation': Droplets,
        'excavations': Shovel,
        'dynamics': Activity,
        'standards': Ruler,
        'constitutive': Layers,
        'pipelines': Anchor
    };

    // Fallback icon
    const Icon = icons[id] || FileText;
    return <Icon size={20} />;
};

// Helper icons if not in lucide imports
const SearchIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /></svg>
);
const Components = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5.5 8.5 9 12l-3.5 3.5L2 12l3.5-3.5Z" /><path d="m12 2 3.5 3.5L12 9 8.5 5.5 12 2Z" /><path d="m18.5 8.5 3.5 3.5-3.5 3.5L15 12l3.5-3.5Z" /><path d="m12 15 3.5 3.5L12 22l-3.5-3.5L12 15Z" /></svg>
);


export const Sidebar = ({ modules, onSelectCategory, selectedCategory, collapsed, backendStatus, onStatusClick }) => {
    return (
        <div className={`bg-surface border-r border-border flex flex-col h-full transition-all duration-300 ${collapsed ? 'w-[70px]' : 'w-64'}`}>
            <div className="h-13 flex items-center justify-center border-b border-border p-2">
                {collapsed ? (
                    <img src="/logoIcon.png" alt="GeoCore" className="h-8 w-8 object-contain" />
                ) : (
                    <img src="/logo-2.png" alt="GeoCore" className="h-10 object-contain" />
                )}
            </div>

            <div className="flex-1 py-4 overflow-y-auto overflow-x-hidden">
                {!collapsed && <div className="px-4 mb-2 text-xs font-semibold text-text-muted uppercase tracking-wider">Modules</div>}

                <ul className="space-y-1">
                    {modules.map((module) => (
                        <li key={module.id}>
                            <button
                                onClick={() => onSelectCategory(module)}
                                title={collapsed ? module.title : ''}
                                className={`w-full flex items-center py-3 transition-colors relative group ${selectedCategory && selectedCategory.id === module.id
                                    ? 'bg-primary/10 text-primary border-r-2 border-primary'
                                    : 'text-text-muted hover:bg-background hover:text-text-main'
                                    } ${collapsed ? 'justify-center px-0' : 'justify-start px-4'}`}
                            >
                                <div className={`${collapsed ? '' : 'mr-3'} shrink-0`}>
                                    <CategoryIcon id={module.id} />
                                </div>

                                {!collapsed && (
                                    <span className="text-sm font-medium truncate">{module.title}</span>
                                )}

                                {/* Hover Tooltip for collapsed state */}
                                {collapsed && (
                                    <div className="absolute left-full ml-2 px-2 py-1 bg-text-main text-background text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
                                        {module.title}
                                    </div>
                                )}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="p-2 border-t border-border">
                <button
                    onClick={onStatusClick}
                    className={`flex items-center w-full hover:bg-background rounded-lg transition-all ${collapsed ? 'justify-center p-2' : 'px-2 py-2'}`}
                >
                    <div className={`flex items-center gap-3 ${collapsed ? '' : 'w-full'}`}>
                        <div className="relative flex items-center justify-center">
                            <Activity size={20} className={backendStatus === 'online' ? 'text-primary' : 'text-red-500'} />
                            <span className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border-2 border-surface ${backendStatus === 'online' ? 'bg-primary' : 'bg-red-500'} ${backendStatus === 'online' ? 'animate-pulse' : ''}`} />
                        </div>
                        {!collapsed && (
                            <div className="flex flex-col text-left">
                                <span className="text-xs font-bold text-text-main leading-tight">System Status</span>
                                <span className={`text-[10px] uppercase font-bold tracking-wider ${backendStatus === 'online' ? 'text-primary' : 'text-red-500'}`}>
                                    {backendStatus === 'online' ? 'Online' : 'Offline'}
                                </span>
                            </div>
                        )}
                    </div>
                </button>
            </div>
        </div>
    );
};
