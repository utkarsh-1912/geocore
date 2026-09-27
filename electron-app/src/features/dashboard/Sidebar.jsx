/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

import React, { useState } from 'react';
import { Activity, ChevronRight } from 'lucide-react';
import { GeoAILogo } from '../../components/common/GeoAILogo';
import { getCategoryIcon } from '../../config/categoryIcons';
import logoFull from '../../assets/logo-2.png';
import logoIcon from '../../assets/logoIcon.png';
import { IS_MAC } from '../../utils/platform';

/**
 * Tooltip for the collapsed rail. Rendered with fixed positioning so the
 * scrollable nav (overflow hidden) does not clip it.
 */
const RailTooltip = ({ tip }) => {
    if (!tip) return null;
    return (
        <div
            className="fixed z-[70] -translate-y-1/2 px-2 py-1 bg-text-main text-background text-xs font-medium rounded shadow-lg pointer-events-none whitespace-nowrap"
            style={{ top: tip.y, left: tip.x }}
        >
            {tip.label}
        </div>
    );
};

const NavItem = ({ active, collapsed, label, icon, onClick, onTip }) => {
    const showTip = (e) => {
        if (!collapsed) return;
        const r = e.currentTarget.getBoundingClientRect();
        onTip({ label, x: r.right + 8, y: r.top + r.height / 2 });
    };
    return (
        <button
            onClick={onClick}
            onMouseEnter={showTip}
            onMouseLeave={() => onTip(null)}
            onFocus={showTip}
            onBlur={() => onTip(null)}
            aria-label={collapsed ? label : undefined}
            aria-current={active ? 'page' : undefined}
            className={`relative w-full flex items-center h-9 rounded transition-colors ${active
                ? 'bg-primary/10 text-primary font-semibold'
                : 'text-text-muted hover:bg-surface-muted hover:text-text-main font-medium'
                } ${collapsed ? 'justify-center' : 'gap-3 px-3'}`}
        >
            {active && <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-r bg-primary" />}
            <span className="shrink-0 w-5 h-5 flex items-center justify-center">{icon}</span>
            {!collapsed && <span className="text-sm truncate">{label}</span>}
        </button>
    );
};

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
    const [tip, setTip] = useState(null);

    const statusStyle = backendStatus === 'online'
        ? { text: 'text-success', dot: 'bg-success', label: 'Engine ready' }
        : backendStatus === 'connecting'
            ? { text: 'text-warning', dot: 'bg-warning', label: 'Engine starting…' }
            : { text: 'text-error', dot: 'bg-error', label: 'Engine offline' };

    return (
        <aside className={`bg-surface border-r border-border flex flex-col h-full shrink-0 transition-[width] duration-300 ${collapsed ? 'w-[64px]' : 'w-60'}`}>
            {/* Part of the window title bar: draggable, and on macOS it hosts the
                traffic lights, so the logo shifts right (or hides when collapsed). */}
            <div className={`h-13 shrink-0 flex items-center border-b border-border ${IS_MAC ? 'justify-end pl-[84px] pr-3' : 'justify-center px-3'}`}
                style={{ WebkitAppRegion: 'drag' }}>
                {collapsed ? (
                    !IS_MAC && <img src={logoIcon} alt="GeoCore" className="h-8 w-8 object-contain" draggable={false} />
                ) : (
                    <img src={logoFull} alt="GeoCore" className={`${IS_MAC ? 'h-7' : 'h-9'} min-w-0 object-contain`} draggable={false} />
                )}
            </div>

            <nav className="flex-1 py-3 px-2 overflow-y-auto overflow-x-hidden no-scrollbar" onScroll={() => setTip(null)}>
                <NavItem
                    active={isGeoAIActive}
                    collapsed={collapsed}
                    label="GeoAI"
                    icon={<GeoAILogo size={18} className="text-primary" />}
                    onClick={onOpenGeoAI}
                    onTip={setTip}
                />

                {collapsed
                    ? <div className="my-3 mx-2 h-px bg-border" />
                    : <div className="px-3 pt-5 pb-1.5 text-[11px] font-semibold text-text-subtle uppercase tracking-wider">Modules</div>}

                <ul className="space-y-0.5">
                    {modules.map((module) => {
                        const Icon = getCategoryIcon(module.id);
                        return (
                            <li key={module.id}>
                                <NavItem
                                    active={!isGeoAIActive && !!selectedCategory && selectedCategory.id === module.id}
                                    collapsed={collapsed}
                                    label={module.title}
                                    icon={<Icon size={18} />}
                                    onClick={() => onSelectCategory(module)}
                                    onTip={setTip}
                                />
                            </li>
                        );
                    })}
                </ul>
            </nav>

            <div className="p-2 border-t border-border">
                <button
                    onClick={onStatusClick}
                    onMouseEnter={(e) => {
                        if (!collapsed) return;
                        const r = e.currentTarget.getBoundingClientRect();
                        setTip({ label: `System health · ${statusStyle.label}`, x: r.right + 8, y: r.top + r.height / 2 });
                    }}
                    onMouseLeave={() => setTip(null)}
                    aria-label="System health"
                    className={`group flex items-center w-full rounded hover:bg-surface-muted transition-colors ${collapsed ? 'justify-center h-10' : 'gap-3 px-3 py-2'}`}
                >
                    <span className="relative w-5 h-5 flex items-center justify-center shrink-0">
                        <Activity size={18} className={statusStyle.text} />
                        <span className={`absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full ring-2 ring-surface ${statusStyle.dot} ${backendStatus === 'offline' ? '' : 'animate-pulse'}`} />
                    </span>
                    {!collapsed && (
                        <>
                            <span className="flex flex-col text-left min-w-0 flex-1">
                                <span className="text-xs font-semibold text-text-main leading-tight">System Health</span>
                                <span className={`text-[11px] font-medium truncate ${statusStyle.text}`}>{statusStyle.label}</span>
                            </span>
                            <ChevronRight size={14} className="text-text-subtle group-hover:text-text-muted transition-colors" />
                        </>
                    )}
                </button>
            </div>

            <RailTooltip tip={collapsed ? tip : null} />
        </aside>
    );
};
