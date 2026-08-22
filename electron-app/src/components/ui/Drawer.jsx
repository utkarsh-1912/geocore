/** Author: Utkarsh Gupta, License: GPL v3 */
import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';

export function Drawer({
  isOpen,
  onClose,
  side = 'right',
  title,
  width = '384px',
  children,
  className = ''
}) {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (typeof document === 'undefined') return null;

  const variants = {
    right: { initial: { x: '100%' }, animate: { x: 0 }, exit: { x: '100%' } },
    left: { initial: { x: '-100%' }, animate: { x: 0 }, exit: { x: '-100%' } },
    bottom: { initial: { y: '100%' }, animate: { y: 0 }, exit: { y: '100%' } }
  };

  const getPositionClasses = () => {
    switch (side) {
      case 'left': return 'left-0 top-0 bottom-0 border-r';
      case 'bottom': return 'bottom-0 left-0 right-0 border-t';
      case 'right': default: return 'right-0 top-0 bottom-0 border-l';
    }
  };

  const style = side === 'bottom' ? { height: width } : { width };

  return createPortal(
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
          />
          <motion.div
            initial={variants[side].initial}
            animate={variants[side].animate}
            exit={variants[side].exit}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            style={style}
            className={`absolute flex flex-col bg-surface border-border shadow-2xl ${getPositionClasses()} ${className}`}
          >
            {title && (
              <div className="flex items-center justify-between border-b border-border px-4 py-3">
                <h2 className="text-lg font-semibold text-text-main">{title}</h2>
                <button
                  onClick={onClose}
                  className="rounded-md p-1 text-text-muted hover:bg-background hover:text-text-main focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <X size={20} />
                </button>
              </div>
            )}
            <div className="flex-1 overflow-y-auto p-4 text-text-main">
              {children}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>,
    document.body
  );
}
