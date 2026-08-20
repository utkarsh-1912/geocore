/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import React from 'react';
import { motion } from 'framer-motion';

export const Preloader = ({ status = "Initializing..." }) => {
    return (
        <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-background text-text-main"
        >
            <div className="relative">
                {/* Logo container with pulse effect */}
                <motion.div
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    className="mb-8 relative z-10"
                >
                    <img src="/logo-2.png" alt="Geocore" className="w-80 h-32 object-contain" />
                </motion.div>

                {/* Background glow behind logo */}
                <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full scale-150 z-0"></div>
            </div>

            <p className="text-text-muted mb-8 text-sm uppercase tracking-widest">Groundhog Analysis Engine</p>

            {/* Loading Bar */}
            <div className="w-64 h-1 bg-secondary/20 rounded-full overflow-hidden relative">
                <motion.div
                    className="absolute top-0 bottom-0 left-0 bg-primary"
                    initial={{ width: "0%" }}
                    animate={{ width: "100%" }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                        repeatType: "reverse"
                    }}
                />
            </div>

            <motion.p
                key={status} // Animate when status changes
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 text-xs font-mono text-text-muted"
            >
                {status}
            </motion.p>
        </motion.div>
    );
};
