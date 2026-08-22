/**
 * Author: Utkarsh Gupta
 * License: Proprietary / GeoCore
 */

import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, ArrowRightLeft } from 'lucide-react';

/**
 * Compatible unit groups and conversion rates relative to standard base SI unit
 */
const UNIT_GROUPS = {
  // Pressure / Stress (Base: kPa)
  kPa: { base: 'kPa', units: { kPa: 1, MPa: 0.001, bar: 0.01, ksf: 0.0208854, psf: 20.8854, Pa: 1000 } },
  MPa: { base: 'kPa', units: { kPa: 1, MPa: 0.001, bar: 0.01, ksf: 0.0208854, psf: 20.8854, Pa: 1000 } },
  psf: { base: 'kPa', units: { kPa: 1, MPa: 0.001, bar: 0.01, ksf: 0.0208854, psf: 20.8854, Pa: 1000 } },
  ksf: { base: 'kPa', units: { kPa: 1, MPa: 0.001, bar: 0.01, ksf: 0.0208854, psf: 20.8854, Pa: 1000 } },

  // Length / Depth (Base: m)
  m: { base: 'm', units: { m: 1, ft: 3.28084, in: 39.3701, mm: 1000, cm: 100 } },
  ft: { base: 'm', units: { m: 1, ft: 3.28084, in: 39.3701, mm: 1000, cm: 100 } },
  mm: { base: 'm', units: { m: 1, ft: 3.28084, in: 39.3701, mm: 1000, cm: 100 } },

  // Unit Weight (Base: kN/m³)
  'kN/m³': { base: 'kN/m³', units: { 'kN/m³': 1, 'kN_m3': 1, 'pcf': 6.36588, 'g/cm³': 0.101972, 'kg/m³': 101.972 } },
  'kN_m3': { base: 'kN/m³', units: { 'kN/m³': 1, 'kN_m3': 1, 'pcf': 6.36588, 'g/cm³': 0.101972, 'kg/m³': 101.972 } },
  'pcf': { base: 'kN/m³', units: { 'kN/m³': 1, 'kN_m3': 1, 'pcf': 6.36588, 'g/cm³': 0.101972, 'kg/m³': 101.972 } },

  // Angles (Base: deg)
  deg: { base: 'deg', units: { deg: 1, rad: 0.0174533 } },
  rad: { base: 'deg', units: { deg: 1, rad: 0.0174533 } },

  // Velocity (Base: m/s)
  'm/s': { base: 'm/s', units: { 'm/s': 1, 'ft/s': 3.28084, 'km/h': 3.6 } }
};

export const UnitBadge = ({ unit, currentValue, onConvertValue, className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const popoverRef = useRef(null);

  if (!unit || unit === '-' || unit === '') {
    return null;
  }

  const cleanUnit = unit.replace(/[\[\]]/g, '').trim();
  const group = UNIT_GROUPS[cleanUnit] || UNIT_GROUPS[cleanUnit.toLowerCase()];

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleUnitSelect = (targetUnit) => {
    if (!group || targetUnit === cleanUnit || !onConvertValue) {
      setIsOpen(false);
      return;
    }

    const val = parseFloat(currentValue);
    if (!isNaN(val)) {
      // Convert to base unit then to target unit
      const currentRate = group.units[cleanUnit] || 1;
      const targetRate = group.units[targetUnit] || 1;
      const baseValue = val / currentRate;
      const convertedValue = baseValue * targetRate;
      
      // Round to 4 decimal places cleanly
      const rounded = Math.round(convertedValue * 10000) / 10000;
      onConvertValue(rounded, targetUnit);
    }
    setIsOpen(false);
  };

  return (
    <div className={`relative inline-block ${className}`} ref={popoverRef}>
      <button
        type="button"
        onClick={() => group && setIsOpen(!isOpen)}
        className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[11px] font-mono rounded border transition-all ${
          group
            ? 'bg-secondary/10 hover:bg-primary/15 border-border hover:border-primary/40 text-text-muted hover:text-primary cursor-pointer'
            : 'bg-secondary/5 border-transparent text-text-muted cursor-default'
        }`}
        title={group ? 'Click for instant unit conversion' : ''}
      >
        <span>[{unit}]</span>
        {group && <ChevronDown size={10} className="text-text-muted opacity-70" />}
      </button>

      {isOpen && group && (
        <div className="absolute right-0 top-full mt-1 z-50 w-36 bg-surface border border-border rounded-md shadow-xl p-1 text-xs">
          <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-text-muted border-b border-border flex items-center gap-1">
            <ArrowRightLeft size={10} className="text-primary" />
            <span>Convert Unit</span>
          </div>
          <div className="space-y-0.5 mt-1 max-h-40 overflow-y-auto">
            {Object.keys(group.units).map((u) => (
              <button
                key={u}
                type="button"
                onClick={() => handleUnitSelect(u)}
                className={`w-full text-left px-2 py-1 rounded flex items-center justify-between font-mono text-[11px] transition-colors ${
                  u === cleanUnit
                    ? 'bg-primary text-white font-bold'
                    : 'text-text-main hover:bg-primary/10 hover:text-primary'
                }`}
              >
                <span>{u}</span>
                {u === cleanUnit && <span className="text-[9px]">Active</span>}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
