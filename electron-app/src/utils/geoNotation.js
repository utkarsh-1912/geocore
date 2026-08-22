/**
 * Author: Utkarsh Gupta
 * License: Proprietary / GeoCore
 */

/**
 * Geotechnical Parameter Notation & Mathematical Mapping Dictionary
 */
export const GEOTECHNICAL_NOTATIONS = {
  // Strength Parameters
  phi_eff: { symbol: "φ'", label: "Effective Friction Angle", math: "\\phi'", unit: "deg", category: "strength" },
  friction_angle: { symbol: "φ'", label: "Friction Angle", math: "\\phi'", unit: "deg", category: "strength" },
  FrictionAngle: { symbol: "φ'", label: "Friction Angle", math: "\\phi'", unit: "deg", category: "strength" },
  cohesion: { symbol: "c'", label: "Effective Cohesion", math: "c'", unit: "kPa", category: "strength" },
  Cohesion: { symbol: "c'", label: "Effective Cohesion", math: "c'", unit: "kPa", category: "strength" },
  cu: { symbol: "cᵤ", label: "Undrained Shear Strength", math: "c_u", unit: "kPa", category: "strength" },
  undrained_cohesion: { symbol: "cᵤ", label: "Undrained Shear Strength", math: "c_u", unit: "kPa", category: "strength" },
  UndrainedCohesion: { symbol: "cᵤ", label: "Undrained Shear Strength", math: "c_u", unit: "kPa", category: "strength" },
  su: { symbol: "sᵤ", label: "Undrained Strength", math: "s_u", unit: "kPa", category: "strength" },
  delta_eff: { symbol: "δ'", label: "Interface Friction Angle", math: "\\delta'", unit: "deg", category: "strength" },
  dilation_angle: { symbol: "ψ", label: "Dilation Angle", math: "\\psi", unit: "deg", category: "strength" },

  // Density & Weights
  gamma: { symbol: "γ", label: "Total Unit Weight", math: "\\gamma", unit: "kN/m³", category: "density" },
  unit_weight: { symbol: "γ", label: "Unit Weight", math: "\\gamma", unit: "kN/m³", category: "density" },
  UnitWeight: { symbol: "γ", label: "Unit Weight", math: "\\gamma", unit: "kN/m³", category: "density" },
  gamma_eff: { symbol: "γ'", label: "Effective (Submerged) Unit Weight", math: "\\gamma'", unit: "kN/m³", category: "density" },
  gamma_dry: { symbol: "γ_d", label: "Dry Unit Weight", math: "\\gamma_d", unit: "kN/m³", category: "density" },
  gamma_sat: { symbol: "γ_sat", label: "Saturated Unit Weight", math: "\\gamma_{sat}", unit: "kN/m³", category: "density" },
  density: { symbol: "ρ", label: "Mass Density", math: "\\rho", unit: "kg/m³", category: "density" },
  specific_gravity: { symbol: "Gₛ", label: "Specific Gravity", math: "G_s", unit: "-", category: "density" },

  // Stress & Pressure
  sigma_v: { symbol: "σᵥ", label: "Total Vertical Stress", math: "\\sigma_v", unit: "kPa", category: "stress" },
  sigma_v_eff: { symbol: "σ'ᵥ", label: "Effective Vertical Overburden", math: "\\sigma'_v", unit: "kPa", category: "stress" },
  sigma_h: { symbol: "σ_h", label: "Total Horizontal Stress", math: "\\sigma_h", unit: "kPa", category: "stress" },
  sigma_h_eff: { symbol: "σ'_h", label: "Effective Horizontal Stress", math: "\\sigma'_h", unit: "kPa", category: "stress" },
  pore_pressure: { symbol: "u", label: "Pore Water Pressure", math: "u", unit: "kPa", category: "stress" },
  u0: { symbol: "u₀", label: "Hydrostatic Pore Pressure", math: "u_0", unit: "kPa", category: "stress" },
  k0: { symbol: "K₀", label: "At-Rest Earth Pressure Coeff.", math: "K_0", unit: "-", category: "stress" },
  ka: { symbol: "Kₐ", label: "Active Earth Pressure Coeff.", math: "K_a", unit: "-", category: "stress" },
  kp: { symbol: "Kₚ", label: "Passive Earth Pressure Coeff.", math: "K_p", unit: "-", category: "stress" },

  // Dynamic & Stiffness
  g_max: { symbol: "Gₘₐₓ", label: "Small-Strain Shear Modulus", math: "G_{max}", unit: "MPa", category: "stiffness" },
  Gmax: { symbol: "Gₘₐₓ", label: "Small-Strain Shear Modulus", math: "G_{max}", unit: "MPa", category: "stiffness" },
  vs: { symbol: "Vₛ", label: "Shear Wave Velocity", math: "V_s", unit: "m/s", category: "dynamics" },
  Vs: { symbol: "Vₛ", label: "Shear Wave Velocity", math: "V_s", unit: "m/s", category: "dynamics" },
  vp: { symbol: "Vₚ", label: "Compression Wave Velocity", math: "V_p", unit: "m/s", category: "dynamics" },
  e_modulus: { symbol: "E", label: "Young's Modulus", math: "E", unit: "MPa", category: "stiffness" },
  poisson_ratio: { symbol: "ν", label: "Poisson's Ratio", math: "\\nu", unit: "-", category: "stiffness" },
  damping_ratio: { symbol: "D", label: "Damping Ratio", math: "D", unit: "%", category: "dynamics" },

  // Geometry & Depths
  depth: { symbol: "z", label: "Depth below GL", math: "z", unit: "m", category: "geometry" },
  Depth: { symbol: "z", label: "Depth", math: "z", unit: "m", category: "geometry" },
  depth_from: { symbol: "z_top", label: "Top Depth", math: "z_{top}", unit: "m", category: "geometry" },
  depth_to: { symbol: "z_bot", label: "Bottom Depth", math: "z_{bot}", unit: "m", category: "geometry" },
  width: { symbol: "B", label: "Footing / Foundation Width", math: "B", unit: "m", category: "geometry" },
  length: { symbol: "L", label: "Footing Length", math: "L", unit: "m", category: "geometry" },
  diameter: { symbol: "D", label: "Pile / Foundation Diameter", math: "D", unit: "m", category: "geometry" },
  embedment: { symbol: "D_f", label: "Embedment Depth", math: "D_f", unit: "m", category: "geometry" },
  thickness: { symbol: "t", label: "Wall / Layer Thickness", math: "t", unit: "m", category: "geometry" },

  // Site Investigation & In-Situ
  qc: { symbol: "q_c", label: "Cone Tip Resistance", math: "q_c", unit: "MPa", category: "insitu" },
  qt: { symbol: "q_t", label: "Corrected Cone Resistance", math: "q_t", unit: "MPa", category: "insitu" },
  fs: { symbol: "f_s", label: "Sleeve Friction", math: "f_s", unit: "kPa", category: "insitu" },
  rf: { symbol: "R_f", label: "Friction Ratio", math: "R_f", unit: "%", category: "insitu" },
  n60: { symbol: "N₆₀", label: "SPT N-value (60% Energy)", math: "N_{60}", unit: "blows/0.3m", category: "insitu" },
  spt_n: { symbol: "N", label: "SPT Uncorrected Blowcount", math: "N", unit: "blows/0.3m", category: "insitu" },
  N: { symbol: "N", label: "SPT Blowcount", math: "N", unit: "blows/0.3m", category: "insitu" },
  ic: { symbol: "I_c", label: "Soil Behavior Type Index", math: "I_c", unit: "-", category: "insitu" },

  // Volumetric & Index
  void_ratio: { symbol: "e", label: "Void Ratio", math: "e", unit: "-", category: "index" },
  porosity: { symbol: "n", label: "Porosity", math: "n", unit: "-", category: "index" },
  water_content: { symbol: "w", label: "Water / Moisture Content", math: "w", unit: "%", category: "index" },
  saturation: { symbol: "S_r", label: "Degree of Saturation", math: "S_r", unit: "%", category: "index" },
  plasticity_index: { symbol: "PI", label: "Plasticity Index", math: "PI", unit: "%", category: "index" },
  liquid_limit: { symbol: "LL", label: "Liquid Limit", math: "LL", unit: "%", category: "index" },
  relative_density: { symbol: "D_r", label: "Relative Density", math: "D_r", unit: "%", category: "index" }
};

/**
 * Get formatted geotechnical notation for a parameter key
 */
export function getParameterNotation(paramKey, fallbackLabel) {
  if (!paramKey) return null;
  const key = String(paramKey).trim();
  const normalizedKey = key.toLowerCase().replace(/[^a-z0-9_]/g, '');

  if (GEOTECHNICAL_NOTATIONS[key]) {
    return GEOTECHNICAL_NOTATIONS[key];
  }
  if (GEOTECHNICAL_NOTATIONS[normalizedKey]) {
    return GEOTECHNICAL_NOTATIONS[normalizedKey];
  }

  // Subscript heuristic for numbered variables (e.g. z1, B2, q_ult)
  if (key.includes('_')) {
    const [base, sub] = key.split('_');
    return { symbol: `${base}_${sub}`, label: fallbackLabel || key, unit: '', category: 'general' };
  }

  return null;
}
