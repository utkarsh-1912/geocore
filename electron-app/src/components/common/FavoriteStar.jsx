/** Author: Utkarsh Gupta, License: GPL v3 */

import React, { useId } from 'react';
import { Star } from 'lucide-react';
import { useFavorites } from '@/context/FavoritesContext';

/**
 * Star in the theme's green, shaded with the brand gradient (light to primary green; follows the light/dark theme
 * through the CSS colour tokens). `filled` fills it; otherwise only the outline carries the gradient.
 */
export const GradientStar = ({ size = 15, filled = true, className = '' }) => {
    const id = `star-grad-${useId().replace(/:/g, '')}`;
    return (
        <Star size={size} className={className} stroke={`url(#${id})`} fill={filled ? `url(#${id})` : 'none'}>
            <defs>
                <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" style={{ stopColor: 'var(--color-primary-light)' }} />
                    <stop offset="100%" style={{ stopColor: 'var(--color-primary)' }} />
                </linearGradient>
            </defs>
        </Star>
    );
};

/**
 * Star toggle for a method (function id) or a folder (folderKey). Stops the click so a star on a card does not
 * also open the card. `reveal`: hidden until the parent `.group` is hovered, unless starred.
 */
export const FavoriteStar = ({ id, type = 'method', label, size = 15, reveal = false, className = '' }) => {
    const { isFavorite, toggleFavorite } = useFavorites();
    if (!id) return null;
    const on = isFavorite(id, type);
    const name = label ? ` ${label}` : '';
    return (
        <button
            type="button"
            onClick={(e) => { e.stopPropagation(); toggleFavorite(id, type); }}
            aria-pressed={on}
            aria-label={on ? `Remove${name} from favourites` : `Add${name} to favourites`}
            title={on ? 'Remove from favourites' : 'Add to favourites'}
            className={`shrink-0 rounded-md p-1 transition-all ${on
                ? 'hover:bg-primary/10'
                : `text-text-muted hover:text-primary hover:bg-surface-muted ${reveal ? 'opacity-0 group-hover:opacity-100 focus-visible:opacity-100' : ''}`} ${className}`}
        >
            {on ? <GradientStar size={size} /> : <Star size={size} />}
        </button>
    );
};

export default FavoriteStar;
