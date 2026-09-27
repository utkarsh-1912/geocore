/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React from 'react';
import { Layers, Box, Shovel, FileText, Activity, Droplets, Database, Ruler, Anchor, ChevronRight } from 'lucide-react';
import { GeoAILogo } from '../../components/common/GeoAILogo';
import logoFull from '../../assets/logo-2.png';
import logoIcon from '../../assets/logoIcon.png';

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
    return <Icon size={18} />;
};

// Helper icons if not in lucide imports
const SearchIcon = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /></svg>
);
const Components = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5.5 8.5 9 12l-3.5 3.5L2 12l3.5-3.5Z" /><path d="m12 2 3.5 3.5L12 9 8.5 5.5 12 2Z" /><path d="m18.5 8.5 3.5 3.5-3.5 3.5L15 12l3.5-3.5Z" /><path d="m12 15 3.5 3.5L12 22l-3.5-3.5L12 15Z" /></svg>
);


const NavItem = ({ active, collapsed, label, icon, onClick }) => (
    <button
        onClick={onClick}
        title={collapsed ? label : undefined}
        aria-current={active ? 'page' : undefined}
        className={`w-full flex items-center h-10 rounded-lg transition-colors relative group ${active
            ? 'bg-primary/10 text-primary font-semibold'
            : 'text-text-muted hover:bg-surface-muted hover:text-text-main font-medium'
            } ${collapsed ? 'justify-center px-0' : 'justify-start px-3 gap-3'}`}
    >
        {active && !collapsed && (
            <span className="absolute left-0 top-2 bottom-2 w-[3px] rounded-r-full bg-primary" />
        )}
        <span className="shrink-0 flex items-center justify-center">{icon}</span>

        {!collapsed && <span className="text-sm truncate">{label}</span>}

        {/* Hover tooltip for collapsed state */}
        {collapsed && (
            <span className="absolute left-full ml-3 px-2 py-1 bg-text-main text-background text-xs font-medium rounded-md shadow-pop opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                {label}
            </span>
        )}
    </button>
);

export const Sidebar = ({
    modules,
    onSelectCategory,
    selectedCategory,
    collapsed,
    backendStatus,
    onStatusClick,
    onOpenGeoAI,
    isGeoAIActive
}) => {
    const statusStyle = backendStatus === 'online'
        ? { text: 'text-success', dot: 'bg-success', label: 'Engine ready' }
        : backendStatus === 'connecting'
            ? { text: 'text-warning', dot: 'bg-warning', label: 'Engine starting…' }
            : { text: 'text-error', dot: 'bg-error', label: 'Engine offline' };

    return (
        <aside className={`bg-surface border-r border-border flex flex-col h-full transition-[width] duration-300 ${collapsed ? 'w-[68px]' : 'w-64'}`}>
            <div className="h-13 shrink-0 flex items-center justify-center border-b border-border px-3">
                {collapsed ? (
                    <img src={logoIcon} alt="GeoCore" className="h-8 w-8 object-contain" />
                ) : (
                    <img src={logoFull} alt="GeoCore" className="h-9 object-contain" />
                )}
            </div>

            <nav className="flex-1 py-3 px-2.5 overflow-y-auto overflow-x-hidden no-scrollbar">
                <NavItem
                    active={isGeoAIActive}
                    collapsed={collapsed}
                    label="GeoAI"
                    icon={<GeoAILogo size={20} className="text-primary" />}
                    onClick={onOpenGeoAI}
                />

                {collapsed
                    ? <div className="my-3 mx-2 h-px bg-border" />
                    : <div className="px-3 pt-5 pb-2 text-[11px] font-semibold text-text-subtle uppercase tracking-wider">Modules</div>}

                <ul className="space-y-0.5">
                    {modules.map((module) => (
                        <li key={module.id}>
                            <NavItem
                                active={!!selectedCategory && selectedCategory.id === module.id}
                                collapsed={collapsed}
                                label={module.title}
                                icon={<CategoryIcon id={module.id} />}
                                onClick={() => onSelectCategory(module)}
                            />
                        </li>
                    ))}
                </ul>
            </nav>

            <div className="p-2.5 border-t border-border">
                <button
                    onClick={onStatusClick}
                    title="System health"
                    className={`group flex items-center w-full rounded-lg hover:bg-surface-muted transition-colors ${collapsed ? 'justify-center h-10' : 'gap-3 px-3 py-2'}`}
                >
                    <span className="relative flex items-center justify-center shrink-0">
                        <Activity size={18} className={statusStyle.text} />
                        <span className={`absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full ring-2 ring-surface ${statusStyle.dot} ${backendStatus === 'offline' ? '' : 'animate-pulse'}`} />
                    </span>
                    {!collapsed && (
                        <>
                            <span className="flex flex-col text-left min-w-0 flex-1">
                                <span className="text-xs font-semibold text-text-main leading-tight">System health</span>
                                <span className={`text-[11px] font-medium truncate ${statusStyle.text}`}>{statusStyle.label}</span>
                            </span>
                            <ChevronRight size={14} className="text-text-subtle group-hover:text-text-muted transition-colors" />
                        </>
                    )}
                </button>
            </div>
        </aside>
    );
};
