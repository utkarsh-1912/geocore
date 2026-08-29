/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 * 
 * GeoAI Custom Geotechnical Intelligence Emblem & Logo.
 * Precision-engineered isometric stratigraphy crystal with
 * an embedded neural intelligence core and starburst apex.
 */

import React from 'react';

export const GeoAILogo = ({ size = 20, className = '', variant = 'icon', showText = false }) => {
    const emblem = (
        <svg
            width={size}
            height={size}
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={`shrink-0 ${className}`}
        >
            <defs>
                <linearGradient id="geoai-strata-top" x1="6" y1="6" x2="26" y2="16" gradientUnits="userSpaceOnUse">
                    <stop stopColor="currentColor" stopOpacity="0.9" />
                    <stop offset="1" stopColor="currentColor" stopOpacity="0.4" />
                </linearGradient>
                <linearGradient id="geoai-strata-left" x1="4" y1="14" x2="16" y2="28" gradientUnits="userSpaceOnUse">
                    <stop stopColor="currentColor" stopOpacity="0.75" />
                    <stop offset="1" stopColor="currentColor" stopOpacity="0.25" />
                </linearGradient>
                <linearGradient id="geoai-strata-right" x1="28" y1="14" x2="16" y2="28" gradientUnits="userSpaceOnUse">
                    <stop stopColor="currentColor" stopOpacity="0.5" />
                    <stop offset="1" stopColor="currentColor" stopOpacity="0.15" />
                </linearGradient>
            </defs>

            {/* Top Stratum Cap */}
            <path
                d="M16 3L27 9.5L16 16L5 9.5L16 3Z"
                fill="url(#geoai-strata-top)"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinejoin="round"
            />

            {/* Left Subsurface Facet */}
            <path
                d="M5 9.5L16 16V29L5 22.5V9.5Z"
                fill="url(#geoai-strata-left)"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinejoin="round"
            />

            {/* Right Subsurface Facet */}
            <path
                d="M27 9.5L16 16V29L27 22.5V9.5Z"
                fill="url(#geoai-strata-right)"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinejoin="round"
            />

            {/* Horizontal Geotechnical Stratigraphy Shear Bands */}
            <path
                d="M5 14L16 20.5L27 14"
                stroke="currentColor"
                strokeWidth="1.25"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeOpacity="0.8"
            />
            <path
                d="M5 18.5L16 25L27 18.5"
                stroke="currentColor"
                strokeWidth="1.25"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeOpacity="0.8"
            />

            {/* Central Neural AI Intelligence Core Spark */}
            <path
                d="M16 6.5L17.2 9.5L20.2 10.7L17.2 11.9L16 14.9L14.8 11.9L11.8 10.7L14.8 9.5L16 6.5Z"
                fill="currentColor"
                stroke="currentColor"
                strokeWidth="0.75"
                strokeLinejoin="round"
            />
        </svg>
    );

    if (variant === 'badge') {
        return (
            <div 
                className={`flex items-center justify-center rounded bg-primary/10 border border-primary/20 text-primary shrink-0 transition-all ${className}`}
                style={{ width: size, height: size }}
            >
                {React.cloneElement(emblem, {
                    width: Math.round(size * 0.65),
                    height: Math.round(size * 0.65),
                    className: 'shrink-0'
                })}
            </div>
        );
    }

    if (showText) {
        return (
            <div className={`flex items-center gap-2 ${className}`}>
                {emblem}
                <span className="font-bold tracking-tight text-text-main">
                    Geo<span className="text-primary">AI</span>
                </span>
            </div>
        );
    }

    return emblem;
};

export default GeoAILogo;
