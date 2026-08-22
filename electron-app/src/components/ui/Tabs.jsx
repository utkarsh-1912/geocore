/** Author: Utkarsh Gupta, License: GPL v3 */
import React from 'react';
import { motion } from 'framer-motion';

export function Tabs({ tabs = [], activeTab, onChange, className = '' }) {
  return (
    <div className={`flex border-b border-border ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`relative flex items-center gap-2 px-4 py-2 text-sm font-medium transition-colors focus:outline-none ${
            activeTab === tab.id ? 'text-primary' : 'text-text-muted hover:text-text-main'
          }`}
        >
          {tab.icon && <span>{tab.icon}</span>}
          {tab.label}
          {activeTab === tab.id && (
            <motion.div
              layoutId="activeTabIndicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
              initial={false}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            />
          )}
        </button>
      ))}
    </div>
  );
}

export function TabPanel({ children, className = '' }) {
  return (
    <div className={`py-4 ${className}`}>
      {children}
    </div>
  );
}
