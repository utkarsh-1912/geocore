/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const siteInvestigationSchemas = {
    relativedensity_categories: {
        inputs: [
            {
                name: 'relative_density',
                label: 'Relative Density',
                type: 'float',
                required: true,
                description: 'Relative density of cohesionless material (D_r) [-] - Suggested range: 0.0 <= relative_density <= 1.0',
                unit: '-'
            },
        ]
    },
    samplequality_voidratio_lunne: {
        inputs: [
            {
                name: 'voidratio',
                label: 'Voidratio',
                type: 'float',
                required: true,
                description: 'Initial void ratio (e_0) [-] - Suggested range: 0.3 <= voidratio <= 3.0',
                unit: '-'
            },
            {
                name: 'voidratio_change',
                label: 'Voidratio Change',
                type: 'float',
                required: true,
                description: 'Change in void ratio when consolidating to in-situ stress (\Delta e) [-] - Suggested range: -1 <= voidratio <= 1',
                unit: '-'
            },
            {
                name: 'ocr',
                label: 'Ocr',
                type: 'float',
                required: true,
                description: 'Overconsolidation ratio (\text{OCR}) [-] - Suggested range: 1 <= voidratio <= 4.0',
                unit: '-'
            },
        ]
    },
    su_categories: {
        inputs: [
            {
                name: 'undrained_shear_strength',
                label: 'Undrained Shear Strength',
                type: 'float',
                required: true,
                description: 'Undrained shear strength of the cohesive sample (S_u) [kPa] - Suggested range: 0.0 <= undrained_shear_strength <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'standard',
                label: 'Standard',
                type: 'string',
                defaultValue: 'BS 5930:2015',
                description: 'Standard used for the classification (optional, default= \'BS 5930:2015\') - Options: (\'BS 5930:2015\', \'ASTM D-2488\')'
            },
        ]
    },
    uscs_categories: {
        inputs: [
            {
                name: 'symbol',
                label: 'Symbol',
                type: 'string',
                required: true,
                description: 'Two character symbol for the soil type according to USCS'
            },
        ]
    },
    bulkunitweight: {
        inputs: [
            {
                name: 'saturation',
                label: 'Saturation',
                type: 'float',
                required: true,
                description: 'Saturation of the sample, ratio of volume of water to volume of voids (S) [-] - Suggested range: 0.0 <= saturation <= 1.0',
                unit: '-'
            },
            {
                name: 'voidratio',
                label: 'Voidratio',
                type: 'float',
                required: true,
                description: 'Void ratio, ratio of volume of voids to volume of solids (e) [-] - Suggested range: 0.0 <= voidratio <= 4.0',
                unit: '-'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity of solid particles (G_s) [-] - Suggested range: 1.0 <= specific_gravity <= 3.0 (optional, default= 2.65)',
                unit: '-'
            },
            {
                name: 'unitweight_water',
                label: 'Unitweight Water',
                type: 'float',
                defaultValue: 10.0,
                description: 'Unit weight of water (\gamma_w) [kN/m3] - Suggested range: 9.0 <= unitweight_water <= 11.0 (optional, default= 10.0)',
                unit: 'kN/m3'
            },
        ]
    },
    bulkunitweight_dryunitweight: {
        inputs: [
            {
                name: 'dryunitweight',
                label: 'Dryunitweight',
                type: 'float',
                required: true,
                description: 'Dry unit weight, ratio of weight of solids to total volume (\gamma_d) [kN/m3] - Suggested range: 1.0 <= dryunitweight <= 15.0',
                unit: 'kN/m3'
            },
            {
                name: 'watercontent',
                label: 'Watercontent',
                type: 'float',
                required: true,
                description: 'Water content, ratio of weight of water to weight of solids (w) [-] - Suggested range: 0.0 <= watercontent <= 4.0',
                unit: '-'
            },
            {
                name: 'unitweight_water',
                label: 'Unitweight Water',
                type: 'float',
                defaultValue: 10.0,
                description: 'Unit weight of water (\gamma_w) [kN/m3] - Suggested range: 9.0 <= unitweight_water <= 11.0 (optional, default= 10.0)',
                unit: 'kN/m3'
            },
        ]
    },
    density_unitweight: {
        inputs: [
            {
                name: 'gamma',
                label: 'Gamma',
                type: 'float',
                required: true,
                description: 'Unit weight (\gamma) [kN/m3] - Suggested range: 0.0 <= gamma <= 30.0',
                unit: 'kN/m3'
            },
            {
                name: 'g',
                label: 'G',
                type: 'float',
                defaultValue: 9.81,
                description: 'Acceleration of gravity (g) [m/s2] - Suggested range: 9.7 <= g <= 10.0 (optional, default= 9.81)',
                unit: 'm/s2'
            },
        ]
    },
    dryunitweight_watercontent: {
        inputs: [
            {
                name: 'watercontent',
                label: 'Watercontent',
                type: 'float',
                required: true,
                description: 'Water content of the sample, ratio of weight of water to weight of solids (w) [-] - Suggested range: 0.0 <= watercontent <= 4.0',
                unit: '-'
            },
            {
                name: 'bulkunitweight',
                label: 'Bulkunitweight',
                type: 'float',
                required: true,
                description: 'Bulk unit weight of the sample (\gamma) [kN/m3] - Suggested range: 10.0 <= bulkunitweight <= 25.0',
                unit: 'kN/m3'
            },
        ]
    },
    porosity_voidratio: {
        inputs: [
            {
                name: 'voidratio',
                label: 'Voidratio',
                type: 'float',
                required: true,
                description: 'Void ratio defined as the ratio of volume of voids to volume of solids (e) [-] - Suggested range: 0.0 <= voidratio <= 5.0',
                unit: '-'
            },
        ]
    },
    relative_density: {
        inputs: [
            {
                name: 'void_ratio',
                label: 'Void Ratio',
                type: 'float',
                required: true,
                description: 'Void ratio of the sample (e) [-] - Suggested range: 0.0 <= void_ratio <= 5.0',
                unit: '-'
            },
            {
                name: 'e_min',
                label: 'E Min',
                type: 'float',
                required: true,
                description: 'Void ratio at the minimum density (e_{min}) [-] - Suggested range: 0.0 <= e_min <= 5.0',
                unit: '-'
            },
            {
                name: 'e_max',
                label: 'E Max',
                type: 'float',
                required: true,
                description: 'Void ratio at the maximum density (e_{max}) [-] - Suggested range: 0.0 <= e_max <= 5.0',
                unit: '-'
            },
        ]
    },
    saturation_watercontent: {
        inputs: [
            {
                name: 'water_content',
                label: 'Water Content',
                type: 'float',
                required: true,
                description: 'Water content of the soil defined as the ratio of weight of water to weight of solids (w) [-] - Suggested range: 0.0 <= water_content <= 4.0',
                unit: '-'
            },
            {
                name: 'voidratio',
                label: 'Voidratio',
                type: 'float',
                required: true,
                description: 'Ratio of volume of voids to volume of solids (e) [-] - Suggested range: 0.0 <= voidratio <= 4.0',
                unit: '-'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity of the soil grains (G_s) [-] - Suggested range: 1.0 <= specific_gravity <= 3.0 (optional, default= 2.65)',
                unit: '-'
            },
        ]
    },
    unitweight_density: {
        inputs: [
            {
                name: 'density',
                label: 'Density',
                type: 'float',
                required: true,
                description: 'Density of the sample (\rho) [kg/m3] - Suggested range: 0.0 <= density <= 3000.0',
                unit: 'kg/m3'
            },
            {
                name: 'g',
                label: 'G',
                type: 'float',
                defaultValue: 9.81,
                description: 'Acceleration due to gravity (g) [m/s2] - Suggested range: 9.7 <= g <= 11.0 (optional, default= 9.81)',
                unit: 'm/s2'
            },
        ]
    },
    unitweight_watercontent_saturated: {
        inputs: [
            {
                name: 'water_content',
                label: 'Water Content',
                type: 'float',
                required: true,
                description: 'Water content of the sample (w) [-] - Suggested range: 0.0 <= water_content <= 2.0',
                unit: '-'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity of the soil (G_s) [-] - Suggested range: 2.5 <= specific_gravity <= 2.8 (optional, default= 2.65)',
                unit: '-'
            },
            {
                name: 'gamma_w',
                label: 'Gamma W',
                type: 'float',
                defaultValue: 10.0,
                description: 'Unit weight of water (\gamma_w) [kN/m3] - Suggested range: 9.5 <= gamma_w <= 10.5 (optional, default= 10.0)',
                unit: 'kN/m3'
            },
        ]
    },
    voidratio_bulkunitweight: {
        inputs: [
            {
                name: 'bulkunitweight',
                label: 'Bulkunitweight',
                type: 'float',
                required: true,
                description: 'The bulk unit weight of the soil (ratio of weight of water and solids to volume) (\gamma) [kN/m3] - Suggested range: 10.0 <= bulkunitweight <= 25.0',
                unit: 'kN/m3'
            },
            {
                name: 'saturation',
                label: 'Saturation',
                type: 'float',
                defaultValue: 1.0,
                description: 'Saturation of the soil as a number between 0 (dry) and fully saturated (1) (S) [-] - Suggested range: 0.0 <= saturation <= 1.0 (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity or the ratio of the weight of soil solids to the weight of an equal volume of water (G_s) [-] - Suggested range: 2.4 <= specific_gravity <= 2.9 (optional, default= 2.65)',
                unit: '-'
            },
            {
                name: 'unitweight_water',
                label: 'Unitweight Water',
                type: 'float',
                defaultValue: 10.0,
                description: 'Unit weight of water (\gamma_w) [kN/m3] - Suggested range: 9.0 <= unitweight_water <= 11.0 (optional, default= 10.0)',
                unit: 'kN/m3'
            },
        ]
    },
    voidratio_drydensity: {
        inputs: [
            {
                name: 'dry_density',
                label: 'Dry Density',
                type: 'float',
                required: true,
                description: 'Dry density of the sample (\rho_d) [kg/m3] - Suggested range: 1000.0 <= dry_density <= 2000.0',
                unit: 'kg/m3'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity (G_s) [-] - Suggested range: 2.4 <= specific_gravity <= 2.9 (optional, default= 2.65)',
                unit: '-'
            },
            {
                name: 'water_density',
                label: 'Water Density',
                type: 'float',
                defaultValue: 1000.0,
                description: 'Density of water (\rho_w) [kg/m3] - Suggested range: 900.0 <= water_density <= 1100.0 (optional, default= 1000.0)',
                unit: 'kg/m3'
            },
        ]
    },
    voidratio_porosity: {
        inputs: [
            {
                name: 'porosity',
                label: 'Porosity',
                type: 'float',
                required: true,
                description: 'Porosity of the sample defined as the ratio of volume of voids to total volume (n) [-] - Suggested range: 0.0 <= porosity <= 1.0',
                unit: '-'
            },
        ]
    },
    voidratio_watercontent: {
        inputs: [
            {
                name: 'water_content',
                label: 'Water Content',
                type: 'float',
                required: true,
                description: 'Water content of the sample (w) [-] - Suggested range: 0.0 <= water_content <= 2.0',
                unit: '-'
            },
            {
                name: 'saturation',
                label: 'Saturation',
                type: 'float',
                defaultValue: 1.0,
                description: 'Saturation of the sample (S) [-] - Suggested range: 0.0 <= saturation <= 1.0 (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity of the sample (G_s) [-] - Suggested range: 2.3 <= specific_gravity <= 3.0 (optional, default= 2.65)',
                unit: '-'
            },
        ]
    },
    watercontent_voidratio: {
        inputs: [
            {
                name: 'voidratio',
                label: 'Voidratio',
                type: 'float',
                required: true,
                description: 'Void ratio of the sample (e) [-] - Suggested range: voidratio >= 0.0',
                unit: '-'
            },
            {
                name: 'saturation',
                label: 'Saturation',
                type: 'float',
                defaultValue: 1.0,
                description: 'Saturation of the sample (S) [-] - Suggested range: 0.0 <= saturation <= 1.0 (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity (G_s) [-] - Suggested range: 2.4 <= specific_gravity <= 3.0 (optional, default= 2.65)',
                unit: '-'
            },
        ]
    },
    gmax_sand_hardinblack: {
        inputs: [
            {
                name: 'sigma_m0',
                label: 'Sigma M0',
                type: 'float',
                required: true,
                description: 'Mean effective stress (p^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_m0 <= 500.0',
                unit: 'kPa'
            },
            {
                name: 'void_ratio',
                label: 'Void Ratio',
                type: 'float',
                required: true,
                description: 'In-situ void ratio of the sand (e_0) [-] - Suggested range: 0.0 <= void_ratio <= 4.0',
                unit: '-'
            },
            {
                name: 'coefficient_B',
                label: 'Coefficient B',
                type: 'float',
                defaultValue: 875.0,
                description: 'Calibration coefficient (B) [-] (optional, default= 875.0)',
                unit: '-'
            },
            {
                name: 'pref',
                label: 'Pref',
                type: 'float',
                defaultValue: 100.0,
                description: 'Reference pressure (p_{ref}^{\prime}) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
        ]
    },
    hssmall_parameters_sand: {
        inputs: [
            {
                name: 'relative_density',
                label: 'Relative Density',
                type: 'float',
                required: true,
                description: 'Relative density of sand (D_r) [pct] - Suggested range: 10.0 <= relative_density <= 100.0',
                unit: 'pct'
            },
        ]
    },
    permeability_d10_hazen: {
        inputs: [
            {
                name: 'grain_size',
                label: 'Grain Size',
                type: 'float',
                required: true,
                description: 'Grain size for which 10% of the particles are finer (D_{10}) [mm] - Suggested range: 0.01 <= grain_size <= 2.0',
                unit: 'mm'
            },
            {
                name: 'coefficient_C',
                label: 'Coefficient C',
                type: 'float',
                defaultValue: 0.01,
                description: 'Calibration coefficient containing the effect of the shape of pore channels (C_{10)) [-] (optional, default= 0.01)',
                unit: '-'
            },
        ]
    },
    stress_dilatancy_bolton: {
        inputs: [
            {
                name: 'relative_density',
                label: 'Relative Density',
                type: 'float',
                required: true,
                description: 'Relative density of the material (D_{r)) [-] - Suggested range: 0.1 <= relative_density <= 1.0',
                unit: '-'
            },
            {
                name: 'p_eff',
                label: 'P Eff',
                type: 'float',
                required: true,
                description: 'Effective pressure (p_{eff)^{\prime}) [kPa] - Suggested range: 20 <= p_eff <= 10000. In the discussion following the paper publication, a remark was made that using a minimum value of 150kPa for the effective pressure is prudent.',
                unit: 'kPa'
            },
            {
                name: 'Q',
                label: 'Q',
                type: 'float',
                defaultValue: 10,
                description: 'First calibration factor in the equation for relative dilatancy index (Q) (optional: Default = 10 for quartz and feldspar sands, See Table 2 in Bolton\'s paper for other grain types)- Suggested range: 5 <= Q <= 10'
            },
            {
                name: 'R',
                label: 'R',
                type: 'float',
                defaultValue: 1,
                description: 'Second calibration factor in the equation for relative dilatancy index (R) (optional: Default = 1)'
            },
            {
                name: 'stress_condition',
                label: 'Stress Condition',
                type: 'string',
                defaultValue: 'triaxial strain',
                description: 'Assumed stress condition: Choose between ``\'triaxial strain\'`` and ``\'plane strain\'``'
            },
        ]
    },
    compressionindex_watercontent_koppula: {
        inputs: [
            {
                name: 'water_content',
                label: 'Water Content',
                type: 'float',
                required: true,
                description: 'In-situ natural water content of the clay (w_n) [-] - Suggested range: 0.0 <= water_content <= 4.0',
                unit: '-'
            },
            {
                name: 'cc_cr_ratio',
                label: 'Cc Cr Ratio',
                type: 'float',
                defaultValue: 7.5,
                description: 'Ratio of compression index and recompression index (C_r / C_c) [-] - Suggested range: 5.0 <= cc_cr_ratio <= 10.0 (optional, default= 7.5)',
                unit: '-'
            },
        ]
    },
    cv_liquidlimit_usnavy: {
        inputs: [
            {
                name: 'liquid_limit',
                label: 'Liquid Limit',
                type: 'float',
                required: true,
                description: 'Liquid limit of the clay (LL) [pct] - Suggested range: 20.0 <= liquid_limit <= 160.0',
                unit: 'pct'
            },
            {
                name: 'trend',
                label: 'Trend',
                type: 'string',
                defaultValue: 'NC',
                description: 'Choice of trend, choose between trends for remoulded, NC and OC clay (optional, default= \'NC\') - Options: (\'Remoulded\', \'NC\', \'OC\')'
            },
        ]
    },
    frictionangle_plasticityindex: {
        inputs: [
            {
                name: 'plasticity_index',
                label: 'Plasticity Index',
                type: 'float',
                required: true,
                description: 'Plasticity index of the clay as determined from Atterberg limit tests (PI) [pct] - Suggested range: 5.0 <= plasticity_index <= 1000.0',
                unit: 'pct'
            },
        ]
    },
    gmax_plasticityocr_andersen: {
        inputs: [
            {
                name: 'pi',
                label: 'Pi',
                type: 'float',
                required: true,
                description: 'Plasticity index (difference between liquid limit and plastic limit) (PI) [pct] - Suggested range: 0.0 <= PI <= 160.0',
                unit: 'pct'
            },
            {
                name: 'ocr',
                label: 'Ocr',
                type: 'float',
                required: true,
                description: 'Overconsolidation ratio of the clay (OCR) [-] - Suggested range: 1.0 <= OCR <= 40.0',
                unit: '-'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] - Suggested range: 90.0 <= atmospheric_pressure <= 110.0 (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 30.0,
                description: 'First calibration coefficient (:math:``) [-] (optional, default= 30.0)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 75.0,
                description: 'Second calibration coefficient (:math:``) [-] (optional, default= 75.0)',
                unit: '-'
            },
            {
                name: 'coefficient_3',
                label: 'Coefficient 3',
                type: 'float',
                defaultValue: 0.03,
                description: 'Third calibration coefficient (:math:``) [-] (optional, default= 0.03)',
                unit: '-'
            },
            {
                name: 'coefficient_4',
                label: 'Coefficient 4',
                type: 'float',
                defaultValue: 0.5,
                description: 'Fourth calibration coefficient (exponent for OCR) (:math:``) [-] (optional, default= 0.5)',
                unit: '-'
            },
            {
                name: 'coefficient_5',
                label: 'Coefficient 5',
                type: 'float',
                defaultValue: 0.9,
                description: 'Fifth calibration coefficient (exponent for sigma_ref) (:math:``) [-] (optional, default= 0.9)',
                unit: '-'
            },
        ]
    },
    k0_plasticity_kenney: {
        inputs: [
            {
                name: 'pi',
                label: 'Pi',
                type: 'float',
                required: true,
                description: 'Plasticity index (\text{PI}) [pct] - Suggested range: 5 <= PI <= 80',
                unit: 'pct'
            },
            {
                name: 'ocr',
                label: 'Ocr',
                type: 'float',
                defaultValue: 1,
                description: 'Overconsolidation ratio (\text{OCR}) [-] (optional, default= 1, suggested range: 1 <= OCR < 30)',
                unit: '-'
            },
            {
                name: 'coeff_1',
                label: 'Coeff 1',
                type: 'float',
                defaultValue: 0.19,
                description: 'First calibration coefficient (optional, default=0.19)'
            },
            {
                name: 'coeff_2',
                label: 'Coeff 2',
                type: 'float',
                defaultValue: 0.233,
                description: 'Second calibration coefficient (optional, default=0.233)'
            },
            {
                name: 'coeff_3',
                label: 'Coeff 3',
                type: 'float',
                defaultValue: -281,
                description: 'First calibration coefficient (optional, default=-281)'
            },
            {
                name: 'coeff_4',
                label: 'Coeff 4',
                type: 'float',
                defaultValue: 1.85,
                description: 'Second calibration coefficient (optional, default=1.85)'
            },
        ]
    },
    acousticimpedance_bulkunitweight_chen: {
        inputs: [
            {
                name: 'bulkunitweight',
                label: 'Bulkunitweight',
                type: 'float',
                required: true,
                description: 'Bulk (total) unit weight (\gamma) [kN/m3] - Suggested range: 12.0 <= bulkunitweight <= 22.0',
                unit: 'kN/m3'
            },
            {
                name: 'specific_gravity',
                label: 'Specific Gravity',
                type: 'float',
                defaultValue: 2.65,
                description: 'Specific gravity of the soil (G_s) [-] - Suggested range: 1.0 <= specific_gravity <= 3.0 (optional, default= 2.65)',
                unit: '-'
            },
            {
                name: 'saturation',
                label: 'Saturation',
                type: 'float',
                defaultValue: 1.0,
                description: 'Saturation of the soil (fully saturated for offshore soils) (S) [-] - Suggested range: 0.0 <= saturation <= 1.0 (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'gamma_w',
                label: 'Gamma W',
                type: 'float',
                defaultValue: 10.0,
                description: 'Unit weight of water (\gamma_w) [kN/m3] - Suggested range: 9.5 <= gamma_w <= 10.5 (optional, default= 10.0)',
                unit: 'kN/m3'
            },
            {
                name: 'calibration_factor_4',
                label: 'Calibration Factor 4',
                type: 'float',
                defaultValue: 0.0001315,
                description: 'Calibration factor on the fourth order term (:math:``) [-] (optional, default= 0.0001315)',
                unit: '-'
            },
            {
                name: 'calibration_factor_3',
                label: 'Calibration Factor 3',
                type: 'float',
                defaultValue: -0.03776,
                description: 'Calibration factor on the third order term (:math:``) [-] (optional, default= -0.03776)',
                unit: '-'
            },
            {
                name: 'calibration_factor_2',
                label: 'Calibration Factor 2',
                type: 'float',
                defaultValue: 4.201,
                description: 'Calibration factor on the second order term (:math:``) [-] (optional, default= 4.201)',
                unit: '-'
            },
            {
                name: 'calibration_factor_1',
                label: 'Calibration Factor 1',
                type: 'float',
                defaultValue: -245.0,
                description: 'Calibration factor on the first order term (:math:``) [-] (optional, default= -245.0)',
                unit: '-'
            },
            {
                name: 'calibration_factor_0',
                label: 'Calibration Factor 0',
                type: 'float',
                defaultValue: 8603.0,
                description: 'Calibration factor on the zero order term (:math:``) [-] (optional, default= 8603.0)',
                unit: '-'
            },
        ]
    },
    k0_frictionangle_mesri: {
        inputs: [
            {
                name: 'phi_cs',
                label: 'Phi Cs',
                type: 'float',
                required: true,
                description: 'Critical state friction angle (\varphi_{cs}^{\prime}) [deg] - Suggested range: 0.01 <= grain_size <= 2.0',
                unit: 'deg'
            },
            {
                name: 'ocr',
                label: 'Ocr',
                type: 'float',
                defaultValue: 1,
                description: 'Overconsolidation ratio (\text{OCR}) [-] (optional, default= 1, suggested range: 1 <= OCR < 30)',
                unit: '-'
            },
        ]
    },
    shearwavevelocity_compressionindex_cha: {
        inputs: [
            {
                name: 'Cc',
                label: 'Cc',
                type: 'float',
                required: true,
                description: 'Compression index (C_c) [-] - Suggested range: 0.005 <= Cc <= 1.2',
                unit: '-'
            },
            {
                name: 'sigma_eff_particle_motion',
                label: 'Sigma Eff Particle Motion',
                type: 'float',
                required: true,
                description: 'Effective stress in the direction of particle motion (\sigma_{\perp}^{\prime}) [kPa] - Suggested range: 10 <= sigma_eff_particle_motion <= 1200',
                unit: 'kPa'
            },
            {
                name: 'sigma_eff_wave_propagation',
                label: 'Sigma Eff Wave Propagation',
                type: 'float',
                required: true,
                description: 'Effective stress in the direction of wave propagation (\sigma_{\parallel}^{\prime}) [kPa] - Suggested range: 10 <= sigma_eff_wave_propagation <= 1200',
                unit: 'kPa'
            },
            {
                name: 'alpha',
                label: 'Alpha',
                type: 'float',
                description: 'Custom alpha-factor in the power law (\alpha) [-] - Suggested range: 5 <= alpha <= 1000 (optional, default=``np.nan``)',
                unit: '-'
            },
            {
                name: 'beta',
                label: 'Beta',
                type: 'float',
                description: 'Custom beta-factor in the power law (\beta) [-] - Suggested range: 0.0 <= beta <= 0.6 (optional, default= ´´np.nan´´)',
                unit: '-'
            },
            {
                name: 'calibration_factor_alpha_1',
                label: 'Calibration Factor Alpha 1',
                type: 'float',
                defaultValue: 13.5,
                description: 'First calibration factor for alpha [-] (optional, default= 13.5)',
                unit: '-'
            },
            {
                name: 'calibration_factor_alpha_2',
                label: 'Calibration Factor Alpha 2',
                type: 'float',
                defaultValue: -0.63,
                description: 'Second calibration factor for alpha [-] (optional, default= 0.63)',
                unit: '-'
            },
            {
                name: 'calibration_factor_beta_1',
                label: 'Calibration Factor Beta 1',
                type: 'float',
                defaultValue: 0.17,
                description: 'First calibration factor for beta [-] (optional, default= 0.17)',
                unit: '-'
            },
            {
                name: 'calibration_factor_beta_2',
                label: 'Calibration Factor Beta 2',
                type: 'float',
                defaultValue: 0.43,
                description: 'First calibration factor for alpha [-] (optional, default= 0.43)',
                unit: '-'
            },
        ]
    },
    behaviourindex_pcpt_nonnormalised: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'Rf',
                label: 'Rf',
                type: 'float',
                required: true,
                description: 'Friction rato (R_f) [pct] - Suggested range: 0.1 <= Rf <= 10.0',
                unit: 'pct'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] - Suggested range: 90.0 <= atmospheric_pressure <= 110.0 (optional, default= 100.0)',
                unit: 'kPa'
            },
        ]
    },
    behaviourindex_pcpt_robertsonwride: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Corrected cone resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'fs',
                label: 'Fs',
                type: 'float',
                required: true,
                description: 'Sleeve friction (f_s) [MPa] - Suggested range: fs >= 0.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo',
                label: 'Sigma Vo',
                type: 'float',
                required: true,
                description: 'Total vertical stress (\sigma_{vo}) [kPa] - Suggested range: sigma_vo >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 9.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (used for normalisation) (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'ic_min',
                label: 'Ic Min',
                type: 'float',
                defaultValue: 1.0,
                description: 'Minimum value for soil behaviour type index used in the optimisation routine (I_{c,min}) [-] (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'ic_max',
                label: 'Ic Max',
                type: 'float',
                defaultValue: 4.0,
                description: 'Maximum value for soil behaviour type index used in the optimisation routine (I_{c,max}) [-] (optional, default= 4.0)',
                unit: '-'
            },
            {
                name: 'zhang_multiplier_1',
                label: 'Zhang Multiplier 1',
                type: 'float',
                defaultValue: 0.381,
                description: 'First multiplier in the equation for exponent n (:math:``) [-] (optional, default= 0.381)',
                unit: '-'
            },
            {
                name: 'zhang_multiplier_2',
                label: 'Zhang Multiplier 2',
                type: 'float',
                defaultValue: 0.05,
                description: 'Second multiplier in the equation for exponent n (:math:``) [-] (optional, default= 0.05)',
                unit: '-'
            },
            {
                name: 'zhang_subtraction',
                label: 'Zhang Subtraction',
                type: 'float',
                defaultValue: 0.15,
                description: 'Term subtracted in the equation for exponent n (:math:``) [-] (optional, default= 0.15)',
                unit: '-'
            },
            {
                name: 'robertsonwride_coefficient1',
                label: 'Robertsonwride Coefficient1',
                type: 'float',
                defaultValue: 3.47,
                description: 'First coefficient in the equation by Robertson and Wride (:math:``) [-] (optional, default= 3.47)',
                unit: '-'
            },
            {
                name: 'robertsonwride_coefficient2',
                label: 'Robertsonwride Coefficient2',
                type: 'float',
                defaultValue: 1.22,
                description: 'Second coefficient in the equation by Robertson and Wride (:math:``) [-] (optional, default= 1.22)',
                unit: '-'
            },
            {
                name: 'cn_capping',
                label: 'Cn Capping',
                type: 'float',
                defaultValue: 1.7
            },
        ]
    },
    clippingdepths_qc1N_tianlehane: {
        inputs: [
            {
                name: 'qc1NW',
                label: 'Qc1Nw',
                type: 'float',
                required: true,
                description: 'Steady-state normalised cone resistance in the weaker layer (q_{c1N,W}) [-] - Suggested range: 0.0 <= qc1NW <= 1000.0',
                unit: '-'
            },
            {
                name: 'qc1NS',
                label: 'Qc1Ns',
                type: 'float',
                required: true,
                description: 'Steady-state normalised cone resistance in the stronger layer (q_{c1N,S}) [-] - Suggested range: 0.0 <= qc1NS <= 1000.0',
                unit: '-'
            },
            {
                name: 'cone_diameter',
                label: 'Cone Diameter',
                type: 'float',
                defaultValue: 0.03568,
                description: 'Cone diameter (d_c) [m] - Suggested range: 0.001 <= cone_diameter <= 1000.0 (optional, default=0.03568 for a 10cm2 cone)',
                unit: 'm'
            },
            {
                name: 'tolerance',
                label: 'Tolerance',
                type: 'float',
                defaultValue: 0.05,
                description: 'Defines the multiplier to detect which data needs to be clipped [-] - Suggested range: 0.001 <= tolerance <= 0.999 (optional, default=0.05)',
                unit: '-'
            },
        ]
    },
    coneresistance_ocsand_baldi: {
        inputs: [
            {
                name: 'dr',
                label: 'Dr',
                type: 'float',
                required: true,
                description: 'Relative density (D_r) [-] - Suggested range: 0.0 <= dr <= 1.0',
                unit: '-'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'k0',
                label: 'K0',
                type: 'float',
                required: true,
                description: 'Coefficient of lateral earth pressure (K_o) [-] - Suggested range: 0.3 <= k0 <= 5.0',
                unit: '-'
            },
            {
                name: 'coefficient_0',
                label: 'Coefficient 0',
                type: 'float',
                defaultValue: 181.0,
                description: 'Coefficient C0 (C_0) [-] (optional, default= 181.0)',
                unit: '-'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 0.55,
                description: 'Coefficient C1 (C_1) [-] (optional, default= 0.55)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 2.61,
                description: 'Coefficient C2 (C_2) [-] (optional, default= 2.61)',
                unit: '-'
            },
        ]
    },
    constrainedmodulus_pcpt_robertson: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Corrected cone tip resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'ic',
                label: 'Ic',
                type: 'float',
                required: true,
                description: 'Soil behaviour type index (I_c) [-] - Suggested range: 1.0 <= ic <= 5.0',
                unit: '-'
            },
            {
                name: 'sigma_vo',
                label: 'Sigma Vo',
                type: 'float',
                required: true,
                description: 'Total vertical stress (\sigma_{vo}) [kPa] - Suggested range: 0.0 <= sigma_vo <= 2000.0',
                unit: 'kPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'coefficient1',
                label: 'Coefficient1',
                type: 'float',
                defaultValue: 0.0188,
                description: 'First calibration coefficient (default=0.0188)'
            },
            {
                name: 'coefficient2',
                label: 'Coefficient2',
                type: 'float',
                defaultValue: 0.55,
                description: 'Second calibration coefficient (default=0.55)'
            },
            {
                name: 'coefficient3',
                label: 'Coefficient3',
                type: 'float',
                defaultValue: 1.68,
                description: 'Third calibration coefficient (default=1.68)'
            },
            {
                name: 'qt_pivot',
                label: 'Qt Pivot',
                type: 'float',
                defaultValue: 14,
                description: 'Value of Q_t when the formula for \alpha_M changes (default=14)'
            },
        ]
    },
    dissipation_test_teh: {
        inputs: [
            {
                name: 'ch',
                label: 'Ch',
                type: 'float',
                required: true,
                description: 'Horizontal coefficient of consolidation (c_h) [m2/yr] - Suggested range: 0.0 <= ch <= 100.0',
                unit: 'm2/yr'
            },
            {
                name: 'shearmodulus',
                label: 'Shearmodulus',
                type: 'float',
                required: true,
                description: 'Shear modulus of the soil (G) [kPa] - Suggested range: 0.0 <= shearmodulus <= 500000.0',
                unit: 'kPa'
            },
            {
                name: 'undrained_shear_strength',
                label: 'Undrained Shear Strength',
                type: 'float',
                required: true,
                description: 'Undrained shear strength (S_u) [kPa] - Suggested range: 1.0 <= undrained_shear_strength <= 500.0',
                unit: 'kPa'
            },
            {
                name: 'u_initial',
                label: 'U Initial',
                type: 'float',
                required: true,
                description: 'Initial excess pore pressure (\Delta u_i) [kPa] - Suggested range: 0.0 <= u_initial <= 2000.0',
                unit: 'kPa'
            },
            {
                name: 'cone_area',
                label: 'Cone Area',
                type: 'float',
                defaultValue: 10.0,
                description: 'Cone area (\pi a^2) [cm2] - Suggested range: 2.0 <= cone_area <= 15.0 (optional, default= 10.0)',
                unit: 'cm2'
            },
            {
                name: 'sensor_location',
                label: 'Sensor Location',
                type: 'string',
                defaultValue: 'u2',
                description: 'Location of the pore pressure sensor (optional, default= \'u2\') - Options: (\'u1\', \' u2\')'
            },
        ]
    },
    drainedsecantmodulus_sand_bellotti: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 50.0 <= sigma_vo_eff <= 300.0',
                unit: 'kPa'
            },
            {
                name: 'K0',
                label: 'K0',
                type: 'float',
                required: true,
                description: 'Coefficient of lateral earth pressure at rest (K_0) [-] - Suggested range: 0.5 <= K0 <= 2.0',
                unit: '-'
            },
            {
                name: 'sandtype',
                label: 'Sandtype',
                type: 'string',
                required: true,
                description: 'Type of sand - Options: ("NC", "Aged NC", "OC")'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] - Suggested range: 90.0 <= atmospheric_pressure <= 110.0 (optional, default= 100.0)',
                unit: 'kPa'
            },
        ]
    },
    frictionangle_overburden_kleven: {
        inputs: [
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Effective vertical stress (\sigma \prime _{vo}) [kPa]  - Suggested range: 10.0<=sigma_vo_eff<=800.0',
                unit: 'kPa'
            },
            {
                name: 'relative_density',
                label: 'Relative Density',
                type: 'float',
                required: true,
                description: 'Relative density of sand (D_r) [Percent]  - Suggested range: 40.0<=relative_density<=100.0',
                unit: 'Percent'
            },
            {
                name: 'Ko',
                label: 'Ko',
                type: 'float',
                defaultValue: 0.5,
                description: 'Coefficient of lateral earth pressure at rest (K_o) [-] (optional, default=0.5) - Suggested range: 0.3<=Ko<=2.0',
                unit: '-'
            },
            {
                name: 'max_friction_angle',
                label: 'Max Friction Angle',
                type: 'float',
                defaultValue: 45.0,
                description: 'The maximum allowable effective friction angle (\phi \prime _{max}) [deg] (optional, default=45.0)',
                unit: 'deg'
            },
        ]
    },
    frictionangle_sand_kulhawymayne: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Total cone resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure used for normalisation (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 17.6,
                description: 'First calibration coefficient (:math:``) [-] (optional, default= 17.6)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 11.0,
                description: 'Second calibration coefficient (:math:``) [-] (optional, default= 11.0)',
                unit: '-'
            },
        ]
    },
    gmax_clay_maynerix: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 2.78,
                description: 'Multiplier in the equation (:math:``) [-] (optional, default= 2.78)',
                unit: '-'
            },
            {
                name: 'exponent',
                label: 'Exponent',
                type: 'float',
                defaultValue: 1.335,
                description: 'Exponent in the equation (:math:``) [-] (optional, default= 1.335)',
                unit: '-'
            },
        ]
    },
    gmax_cpt_puechen: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 70.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'Bq',
                label: 'Bq',
                type: 'float',
                required: true,
                description: 'Pore pressure ratio (B_q) [-] - Suggested range: -0.2 <= Bq <= 0.5',
                unit: '-'
            },
            {
                name: 'coefficient_b',
                label: 'Coefficient B',
                type: 'float',
                defaultValue: 1.0,
                description: 'Calibration coefficient b (b) [-] (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'coefficient_Bq',
                label: 'Coefficient Bq',
                type: 'float',
                defaultValue: 4.0,
                description: 'Multiplier on Bq (:math:``) [-] (optional, default= 4.0)',
                unit: '-'
            },
            {
                name: 'multiplier_qc',
                label: 'Multiplier Qc',
                type: 'float',
                defaultValue: 1.634,
                description: 'Multiplier applied on qc (:math:``) [-] (optional, default= 1.634)',
                unit: '-'
            },
            {
                name: 'exponent_1',
                label: 'Exponent 1',
                type: 'float',
                defaultValue: 0.25,
                description: 'Exponent on qc (:math:``) [-] (optional, default= 0.25)',
                unit: '-'
            },
            {
                name: 'exponent_2',
                label: 'Exponent 2',
                type: 'float',
                defaultValue: 0.375,
                description: 'Exponent on vertical effective stress (:math:``) [-] (optional, default= 0.375)',
                unit: '-'
            },
            {
                name: 'Bq_min',
                label: 'Bq Min',
                type: 'float',
                defaultValue: 0,
                description: 'Minimum value of Bq. If Bq is lower than this value, the minimum will be used for the calculation [-] (optional, default= 0)',
                unit: '-'
            },
            {
                name: 'Bq_max',
                label: 'Bq Max',
                type: 'float',
                defaultValue: 0.5,
                description: 'Maximum value of Bq. If Bq is higher than this value, the maximum will be used for the calculation [-] (optional, default= 0.5)',
                unit: '-'
            },
        ]
    },
    gmax_sand_rixstokoe: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 1634.0,
                description: 'Multiplier in the correlation equation (:math:``) [-] (optional, default= 1634.0)',
                unit: '-'
            },
            {
                name: 'qc_exponent',
                label: 'Qc Exponent',
                type: 'float',
                defaultValue: 0.25,
                description: 'Exponent applied on the cone tip resistance (:math:``) [-] (optional, default= 0.25)',
                unit: '-'
            },
            {
                name: 'stress_exponent',
                label: 'Stress Exponent',
                type: 'float',
                defaultValue: 0.375,
                description: 'Exponent applied on the vertical effective stress (:math:``) [-] (optional, default= 0.375)',
                unit: '-'
            },
        ]
    },
    gmax_voidratio_maynerix: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.1 <= qc <= 10.0',
                unit: 'MPa'
            },
            {
                name: 'void_ratio',
                label: 'Void Ratio',
                type: 'float',
                required: true,
                description: 'Void ratio of the clay determined from index tests or CPT-based correlations (e_0) [-] - Suggested range: 0.2 <= void_ratio <= 10.0',
                unit: '-'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] - Suggested range: 90.0 <= atmospheric_pressure <= 110.0 (optional, default= 1.0)',
                unit: 'kPa'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 99.5,
                description: 'First calibration coefficient (:math:``) [-] (optional, default= 99.5)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 0.305,
                description: 'Second  calibration coefficient (:math:``) [-] (optional, default= 0.305)',
                unit: '-'
            },
            {
                name: 'coefficient_3',
                label: 'Coefficient 3',
                type: 'float',
                defaultValue: 0.695,
                description: 'Third calibration coefficient (:math:``) [-] (optional, default= 0.695)',
                unit: '-'
            },
            {
                name: 'coefficient_4',
                label: 'Coefficient 4',
                type: 'float',
                defaultValue: 1.13,
                description: 'Fourth calibration coefficient (:math:``) [-] (optional, default= 1.13)',
                unit: '-'
            },
        ]
    },
    ic_soilclass_robertson: {
        inputs: [
            {
                name: 'ic',
                label: 'Ic',
                type: 'float',
                required: true,
                description: 'Soil behaviour type index (I_c) [-] - Suggested range: 1.0 <= ic <= 5.0',
                unit: '-'
            },
        ]
    },
    k0_sand_mayne: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Total cone resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'ocr',
                label: 'Ocr',
                type: 'float',
                required: true,
                description: 'Overconsolidation ratio (OCR) [-] - Suggested range: 1.0 <= ocr <= 20.0',
                unit: '-'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] - Suggested range: 90.0 <= atmospheric_pressure <= 110.0 (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 0.192,
                description: 'Multiplier in equation (:math:``) [-] (optional, default= 0.192)',
                unit: '-'
            },
            {
                name: 'exponent_1',
                label: 'Exponent 1',
                type: 'float',
                defaultValue: 0.22,
                description: 'First exponent in equation (:math:``) [-] (optional, default= 0.22)',
                unit: '-'
            },
            {
                name: 'exponent_2',
                label: 'Exponent 2',
                type: 'float',
                defaultValue: 0.31,
                description: 'Second exponent in equation (:math:``) [-] (optional, default= 0.31)',
                unit: '-'
            },
            {
                name: 'exponent_3',
                label: 'Exponent 3',
                type: 'float',
                defaultValue: 0.27,
                description: 'Third exponent in equation (:math:``) [-] (optional, default= 0.27)',
                unit: '-'
            },
            {
                name: 'friction_angle',
                label: 'Friction Angle',
                type: 'float',
                defaultValue: 32.0,
                description: 'Effective friction angle of the sand (\varphi^{\prime}) [deg] - Suggested range: 25.0 <= friction_angle <= 45.0 (optional, default= 32.0)',
                unit: 'deg'
            },
        ]
    },
    ocr_cpt_lunne: {
        inputs: [
            {
                name: 'Qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Normalised cone resistance (Q_t) [-] - Suggested range: 2.0 <= Qt <= 34.0',
                unit: '-'
            },
            {
                name: 'Bq',
                label: 'Bq',
                type: 'float',
                description: 'Pore pressure ratio (B_q) [-] - Suggested range: 0.0 <= Bq <= 1.4 (optional, default=None)',
                unit: '-'
            },
        ]
    },
    pcpt_normalisations: {
        inputs: [
            {
                name: 'measured_qc',
                label: 'Measured Qc',
                type: 'float',
                required: true,
                description: 'Measured cone resistance (q_c^*) [MPa] - Suggested range: 0.0 <= measured_qc <= 150.0',
                unit: 'MPa'
            },
            {
                name: 'measured_fs',
                label: 'Measured Fs',
                type: 'float',
                required: true,
                description: 'Measured sleeve friction (f_s^*) [MPa] - Suggested range: 0.0 <= measured_fs <= 10.0',
                unit: 'MPa'
            },
            {
                name: 'measured_u2',
                label: 'Measured U2',
                type: 'float',
                required: true,
                description: 'Pore pressure measured at the shoulder (u_2^*) [MPa] - Suggested range: -10.0 <= measured_u2 <= 10.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_tot',
                label: 'Sigma Vo Tot',
                type: 'float',
                required: true,
                description: 'Total vertical stress (\sigma_{vo}) [kPa] - Suggested range: sigma_vo_tot >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Effective vertical stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'depth',
                label: 'Depth',
                type: 'float',
                required: true,
                description: 'Depth below surface (for saturated soils) where measurement is taken. For onshore tests, use the depth below the watertable. (z) [m] - Suggested range: depth >= 0.0',
                unit: 'm'
            },
            {
                name: 'cone_area_ratio',
                label: 'Cone Area Ratio',
                type: 'float',
                required: true,
                description: 'Ratio between the cone rod area and the maximum cone area (a) [-] - Suggested range: 0.0 <= cone_area_ratio <= 1.0',
                unit: '-'
            },
            {
                name: 'start_depth',
                label: 'Start Depth',
                type: 'float',
                defaultValue: 0.0,
                description: 'Start depth of the test, specify this for a downhole test. Leave at zero for a test starting from surface (d) [m] - Suggested range: start_depth >= 0.0 (optional, default= 0.0)',
                unit: 'm'
            },
            {
                name: 'unitweight_water',
                label: 'Unitweight Water',
                type: 'float',
                defaultValue: 10.25,
                description: 'Unit weight of water, default is for seawater (\gamma_w) [kN/m3] - Suggested range: 9.0 <= unitweight_water <= 11.0 (optional, default= 10.25)',
                unit: 'kN/m3'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100,
                description: 'Atmospheric pressure (used for normalisation) (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'ic_min',
                label: 'Ic Min',
                type: 'float',
                defaultValue: 1.0,
                description: 'Minimum value for soil behaviour type index used in the optimisation routine (I_{c,min}) [-] (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'ic_max',
                label: 'Ic Max',
                type: 'float',
                defaultValue: 4.0,
                description: 'Maximum value for soil behaviour type index used in the optimisation routine (I_{c,max}) [-] (optional, default= 4.0)',
                unit: '-'
            },
            {
                name: 'zhang_multiplier_1',
                label: 'Zhang Multiplier 1',
                type: 'float',
                defaultValue: 0.381,
                description: 'First multiplier in the equation for exponent n (:math:``) [-] (optional, default= 0.381)',
                unit: '-'
            },
            {
                name: 'zhang_multiplier_2',
                label: 'Zhang Multiplier 2',
                type: 'float',
                defaultValue: 0.05,
                description: 'Second multiplier in the equation for exponent n (:math:``) [-] (optional, default= 0.05)',
                unit: '-'
            },
            {
                name: 'zhang_subtraction',
                label: 'Zhang Subtraction',
                type: 'float',
                defaultValue: 0.15,
                description: 'Term subtracted in the equation for exponent n (:math:``) [-] (optional, default= 0.15)',
                unit: '-'
            },
            {
                name: 'robertsonwride_coefficient1',
                label: 'Robertsonwride Coefficient1',
                type: 'float',
                defaultValue: 3.47,
                description: 'First coefficient in the equation by Robertson and Wride (:math:``) [-] (optional, default= 3.47)',
                unit: '-'
            },
            {
                name: 'robertsonwride_coefficient2',
                label: 'Robertsonwride Coefficient2',
                type: 'float',
                defaultValue: 1.22,
                description: 'Second coefficient in the equation by Robertson and Wride (:math:``) [-] (optional, default= 1.22)',
                unit: '-'
            },
            {
                name: 'cn_capping',
                label: 'Cn Capping',
                type: 'float',
                defaultValue: 1.7
            },
        ]
    },
    relativedensity_ncsand_baldi: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tipe resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'coefficient_0',
                label: 'Coefficient 0',
                type: 'float',
                defaultValue: 157.0,
                description: 'Coefficient C0 (C_0) [-] (optional, default= 157.0)',
                unit: '-'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 0.55,
                description: 'Coefficient C1 (C_1) [-] (optional, default= 0.55)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 2.41,
                description: 'Coefficient C2 (C_2) [-] (optional, default= 2.41)',
                unit: '-'
            },
        ]
    },
    relativedensity_ocsand_baldi: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'k0',
                label: 'K0',
                type: 'float',
                required: true,
                description: 'Coefficient of lateral earth pressure (K_o) [-] - Suggested range: 0.3 <= k0 <= 5.0',
                unit: '-'
            },
            {
                name: 'coefficient_0',
                label: 'Coefficient 0',
                type: 'float',
                defaultValue: 181.0,
                description: 'Coefficient C0 (C_0) [-] (optional, default= 181.0)',
                unit: '-'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 0.55,
                description: 'Coefficient C1 (C_1) [-] (optional, default= 0.55)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 2.61,
                description: 'Coefficient C2 (C_2) [-] (optional, default= 2.61)',
                unit: '-'
            },
        ]
    },
    relativedensity_sand_jamiolkowski: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 50.0 <= sigma_vo_eff <= 400.0',
                unit: 'kPa'
            },
            {
                name: 'k0',
                label: 'K0',
                type: 'float',
                required: true,
                description: 'Coefficient of lateral earth pressure (K_o) [-] - Suggested range: 0.4 <= k0 <= 1.5',
                unit: '-'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure used for normalisation (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 2.96,
                description: 'First calibration coefficient (:math:``) [-] (optional, default= 2.96)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 24.94,
                description: 'Second calibration coefficient (:math:``) [-] (optional, default= 24.94)',
                unit: '-'
            },
            {
                name: 'coefficient_3',
                label: 'Coefficient 3',
                type: 'float',
                defaultValue: 0.46,
                description: 'Third calibration coefficient (:math:``) [-] (optional, default= 0.46)',
                unit: '-'
            },
            {
                name: 'coefficient_4',
                label: 'Coefficient 4',
                type: 'float',
                defaultValue: -1.87,
                description: 'Fourth calibration coefficient (:math:``) [-] (optional, default= -1.87)',
                unit: '-'
            },
            {
                name: 'coefficient_5',
                label: 'Coefficient 5',
                type: 'float',
                defaultValue: 2.32,
                description: 'Fifth calibration coefficient (:math:``) [-] (optional, default= 2.32)',
                unit: '-'
            },
        ]
    },
    sensitivity_frictionratio_lunne: {
        inputs: [
            {
                name: 'Rf',
                label: 'Rf',
                type: 'float',
                required: true,
                description: 'Friction ratio (R_f = f_t / q_t) [percent] - Suggested range: 0.5 <= Rf <= 2.2',
                unit: 'percent'
            },
        ]
    },
    soilclass_robertson: {
        inputs: [
            {
                name: 'ic_class_number',
                label: 'Ic Class Number',
                type: 'float',
                required: true,
                description: 'Soil behaviour type index class number (I_c) [-] - Suggested range: ic = 1 to 9',
                unit: '-'
            },
        ]
    },
    soiltype_vs_longodonohue: {
        inputs: [
            {
                name: 'Vs',
                label: 'Vs',
                type: 'float',
                required: true,
                description: 'Shear wave velocity (V_s) [m/s] - Suggested range: 0.0 <= Vs <= 600.0',
                unit: 'm/s'
            },
            {
                name: 'Qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Normalised cone resistance (Q_t) [-] - Suggested range: 0.0 <= Qt <= 200.0',
                unit: '-'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
        ]
    },
    undrainedshearstrength_clay_radlunne: {
        inputs: [
            {
                name: 'qnet',
                label: 'Qnet',
                type: 'float',
                required: true,
                description: 'Net cone resistance (corrected for area ratio and total stress at the depth of the cone) (q_{net}) [MPa] - Suggested range: 0.0 <= qnet <= 120.0',
                unit: 'MPa'
            },
            {
                name: 'Nk',
                label: 'Nk',
                type: 'float',
                required: true,
                description: 'Empirical factor (N_k) [-] - Suggested range: 8.0 <= Nk <= 30.0',
                unit: '-'
            },
        ]
    },
    unitweight_mayne: {
        inputs: [
            {
                name: 'ft',
                label: 'Ft',
                type: 'float',
                required: true,
                description: 'Total sleeve friction (f_t) [MPa] - Suggested range: 0.0 <= ft <= 10.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 500.0',
                unit: 'kPa'
            },
            {
                name: 'unitweight_water',
                label: 'Unitweight Water',
                type: 'float',
                defaultValue: 10.25,
                description: 'Unit weight of water (\gamma_w) [kN/m3] - Suggested range: 9.0 <= unitweight_water <= 11.0 (optional, default= 10.25)',
                unit: 'kN/m3'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 1.95,
                description: 'First coefficient in the calibrated equation (:math:``) [-] (optional, default= 1.95)',
                unit: '-'
            },
            {
                name: 'exponent_1',
                label: 'Exponent 1',
                type: 'float',
                defaultValue: 0.06,
                description: 'First exponent in the calibrated equation (:math:``) [-] (optional, default= 0.06)',
                unit: '-'
            },
            {
                name: 'exponent_2',
                label: 'Exponent 2',
                type: 'float',
                defaultValue: 0.06,
                description: 'Second exponent in the calibrated equation (:math:``) [-] (optional, default= 0.06)',
                unit: '-'
            },
        ]
    },
    vs_cpt_andrus: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Corrected cone tip resistance (note that formula is based on qt in kPa) (q_t) [MPa] - Suggested range: 0.0 <= qt <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'depth',
                label: 'Depth',
                type: 'float',
                required: true,
                description: 'Depth below mudline (z) [m] - Suggested range: 0.0 <= depth <= 100.0',
                unit: 'm'
            },
            {
                name: 'ic',
                label: 'Ic',
                type: 'float',
                required: true,
                description: 'Soil behaviour type index (I_c) [-] - Suggested range: 1.0 <= ic <= 5.0',
                unit: '-'
            },
            {
                name: 'SF',
                label: 'Sf',
                type: 'float',
                defaultValue: 1.0,
                description: 'Scaling factor. In case of Holocene soils, this is an age scaling factor (SF, ASF) [-] - Suggested range: 1.0 <= SF <= 3.0 (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'age',
                label: 'Age',
                type: 'string',
                defaultValue: 'Holocene',
                description: 'Age of soils (optional, default= \'Holocene\') - Options: (\'Holocene\', \'Pleistocene\', \'Tertiary\')'
            },
            {
                name: 'holocene_multiplier',
                label: 'Holocene Multiplier',
                type: 'float',
                defaultValue: 2.27,
                description: 'Multiplier on holocene equation (:math:``) [-] (optional, default= 2.27)',
                unit: '-'
            },
            {
                name: 'holocene_qt_exponent',
                label: 'Holocene Qt Exponent',
                type: 'float',
                defaultValue: 0.412,
                description: 'Exponent on qt in holocene equation (:math:``) [-] (optional, default= 0.412)',
                unit: '-'
            },
            {
                name: 'holocene_ic_exponent',
                label: 'Holocene Ic Exponent',
                type: 'float',
                defaultValue: 0.989,
                description: 'Exponent on Ic in holocene equation (:math:``) [-] (optional, default= 0.989)',
                unit: '-'
            },
            {
                name: 'holocene_z_exponent',
                label: 'Holocene Z Exponent',
                type: 'float',
                defaultValue: 0.033,
                description: 'Exponent on depth in holocene equation (:math:``) [-] (optional, default= 0.033)',
                unit: '-'
            },
            {
                name: 'pleistocene_multiplier',
                label: 'Pleistocene Multiplier',
                type: 'float',
                defaultValue: 2.62,
                description: 'Multiplier on pleistocene equation (:math:``) [-] (optional, default= 2.62)',
                unit: '-'
            },
            {
                name: 'pleistocene_qt_exponent',
                label: 'Pleistocene Qt Exponent',
                type: 'float',
                defaultValue: 0.395,
                description: 'Exponent on qt in pleistocene equation (:math:``) [-] (optional, default= 0.395)',
                unit: '-'
            },
            {
                name: 'pleistocene_ic_exponent',
                label: 'Pleistocene Ic Exponent',
                type: 'float',
                defaultValue: 0.912,
                description: 'Exponent on Ic in pleistocene equation (:math:``) [-] (optional, default= 0.912)',
                unit: '-'
            },
            {
                name: 'pleistocene_z_exponent',
                label: 'Pleistocene Z Exponent',
                type: 'float',
                defaultValue: 0.124,
                description: 'Exponent on depth in pleistocene equation (:math:``) [-] (optional, default= 0.124)',
                unit: '-'
            },
            {
                name: 'tertiary_multiplier',
                label: 'Tertiary Multiplier',
                type: 'float',
                defaultValue: 13.0,
                description: 'Multiplier on tertiary equation (:math:``) [-] (optional, default= 13.0)',
                unit: '-'
            },
            {
                name: 'tertiary_qt_exponent',
                label: 'Tertiary Qt Exponent',
                type: 'float',
                defaultValue: 0.382,
                description: 'Exponent on qt in tertiary equation (:math:``) [-] (optional, default= 0.382)',
                unit: '-'
            },
            {
                name: 'tertiary_z_exponent',
                label: 'Tertiary Z Exponent',
                type: 'float',
                defaultValue: 0.099,
                description: 'Exponent on depth in tertiary equation (:math:``) [-] (optional, default= 0.099)',
                unit: '-'
            },
        ]
    },
    vs_cpt_hegazymayne: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Corrected cone tip resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'fs',
                label: 'Fs',
                type: 'float',
                required: true,
                description: 'Sleeve friction (f_s) [MPa] - Suggested range: 0.0 <= fs <= 10.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'sigma_vo',
                label: 'Sigma Vo',
                type: 'float',
                required: true,
                description: 'Vertical total stress (\sigma_{vo}) [kPa] - Suggested range: 0.0 <= sigma_vo <= 2000.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'zhang',
                label: 'Zhang',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean determining whether the Zhang exponent (default groundhog implementation) needs to be used (optional, default= True)'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 0.0831,
                description: 'Multiplier in Equation 6 (:math:``) [-] (optional, default= 0.0831)',
                unit: '-'
            },
            {
                name: 'exponent_stress',
                label: 'Exponent Stress',
                type: 'float',
                defaultValue: 0.25,
                description: 'Exponent on the normalised stresses (:math:``) [-] (optional, default= 0.25)',
                unit: '-'
            },
            {
                name: 'multiplier_ic',
                label: 'Multiplier Ic',
                type: 'float',
                defaultValue: 1.786,
                description: 'Multiplier on soil behaviour type index (:math:``) [-] (optional, default= 1.786)',
                unit: '-'
            },
        ]
    },
    vs_cpt_longdonohue: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Corrected cone resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 2.0',
                unit: 'MPa'
            },
            {
                name: 'u2',
                label: 'U2',
                type: 'float',
                required: true,
                description: 'Pore pressure at the shoulder (u_2) [MPa] - Suggested range: -1.0 <= u2 <= 1.0',
                unit: 'MPa'
            },
            {
                name: 'u0',
                label: 'U0',
                type: 'float',
                required: true,
                description: 'Hydrostatic pressure (u_0) [kPa] - Suggested range: 0.0 <= u0 <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'Bq',
                label: 'Bq',
                type: 'float',
                required: true,
                description: 'Pore pressure ratio (B_q) [-] - Suggested range: -0.6 <= Bq <= 1.4',
                unit: '-'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 1.961,
                description: 'Multiplier in expression for Vs (:math:``) [-] (optional, default= 1.961)',
                unit: '-'
            },
            {
                name: 'exponent_qt',
                label: 'Exponent Qt',
                type: 'float',
                defaultValue: 0.579,
                description: 'Exponent on qt (:math:``) [-] (optional, default= 0.579)',
                unit: '-'
            },
            {
                name: 'exponent_Bq',
                label: 'Exponent Bq',
                type: 'float',
                defaultValue: 1.202,
                description: 'Exponent on 1 + Bq (:math:``) [-] (optional, default= 1.202)',
                unit: '-'
            },
        ]
    },
    vs_cpt_mcgannetal: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Corrected cone tip resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'fs',
                label: 'Fs',
                type: 'float',
                required: true,
                description: 'Sleeve friction (f_s) [MPa] - Suggested range: 0.0 <= fs <= 10.0',
                unit: 'MPa'
            },
            {
                name: 'depth',
                label: 'Depth',
                type: 'float',
                required: true,
                description: 'Depth below ground surface (z) [m] - Suggested range: 0.0 <= depth <= 100.0',
                unit: 'm'
            },
            {
                name: 'coefficient1_general',
                label: 'Coefficient1 General',
                type: 'float',
                defaultValue: 18.4,
                description: 'First calibration coefficient in general equation (:math:``) [-] (optional, default= 18.4)',
                unit: '-'
            },
            {
                name: 'coefficient2_general',
                label: 'Coefficient2 General',
                type: 'float',
                defaultValue: 0.144,
                description: 'Second calibration coefficient in general equation (:math:``) [-] (optional, default= 0.144)',
                unit: '-'
            },
            {
                name: 'coefficient3_general',
                label: 'Coefficient3 General',
                type: 'float',
                defaultValue: 0.083,
                description: 'Third calibration coefficient in general equation (:math:``) [-] (optional, default= 0.083)',
                unit: '-'
            },
            {
                name: 'coefficient4_general',
                label: 'Coefficient4 General',
                type: 'float',
                defaultValue: 0.278,
                description: 'Fourth calibration coefficient in general equation (:math:``) [-] (optional, default= 0.278)',
                unit: '-'
            },
            {
                name: 'coefficient1_loess',
                label: 'Coefficient1 Loess',
                type: 'float',
                defaultValue: 103.6,
                description: 'First calibration coefficient in loess equation (:math:``) [-] (optional, default= 103.6)',
                unit: '-'
            },
            {
                name: 'coefficient2_loess',
                label: 'Coefficient2 Loess',
                type: 'float',
                defaultValue: 0.0074,
                description: 'Second calibration coefficient in loess equation (:math:``) [-] (optional, default= 0.0074)',
                unit: '-'
            },
            {
                name: 'coefficient3_loess',
                label: 'Coefficient3 Loess',
                type: 'float',
                defaultValue: 0.13,
                description: 'Third calibration coefficient in loess equation (:math:``) [-] (optional, default= 0.13)',
                unit: '-'
            },
            {
                name: 'coefficient4_loess',
                label: 'Coefficient4 Loess',
                type: 'float',
                defaultValue: 0.253,
                description: 'Fourth calibration coefficient in loess equation (:math:``) [-] (optional, default= 0.253)',
                unit: '-'
            },
            {
                name: 'loess',
                label: 'Loess',
                type: 'boolean',
                defaultValue: false,
                description: 'Boolean determining whether the loess equation needs to be used (optional, default= False)'
            },
        ]
    },
    vs_cpt_tonniandsimonini: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Corrected cone tip resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'ic',
                label: 'Ic',
                type: 'float',
                required: true,
                description: 'Soil behaviour type index (I_c) [-] - Suggested range: 1.0 <= ic <= 5.0',
                unit: '-'
            },
            {
                name: 'sigma_vo',
                label: 'Sigma Vo',
                type: 'float',
                required: true,
                description: 'Total vertical stress (\sigma_{vo}) [kPa] - Suggested range: 0.0 <= sigma_vo <= 2000.0',
                unit: 'kPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 0.8,
                description: 'Multiplier on Ic in Equation 12 (:math:``) [-] (optional, default= 0.8)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 1.17,
                description: 'Value after minus sign in Equation 12 (:math:``) [-] (optional, default= 1.17)',
                unit: '-'
            },
        ]
    },
    vs_cpt_wrideetal: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 103.2,
                description: 'Multiplier on corrected cone resistance (Y) [-] - Suggested range: 95.6 <= multiplier <= 110.8 (optional, default= 103.2)',
                unit: '-'
            },
            {
                name: 'exponent_qc1',
                label: 'Exponent Qc1',
                type: 'float',
                defaultValue: 0.25,
                description: 'Exponent on stress-corrected cone resistance (:math:``) [-] - Suggested range: 0.23 <= exponent_qc1 <= 0.25 (optional, default= 0.25)',
                unit: '-'
            },
        ]
    },
    vs_cptd50_karrayetal: {
        inputs: [
            {
                name: 'qc',
                label: 'Qc',
                type: 'float',
                required: true,
                description: 'Cone tip resistance (q_c) [MPa] - Suggested range: 0.0 <= qc <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'd50',
                label: 'D50',
                type: 'float',
                required: true,
                description: 'Median grain size (d_{50}) [mm] - Suggested range: 0.1 <= d50 <= 10.0',
                unit: 'mm'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'exponent_vs1',
                label: 'Exponent Vs1',
                type: 'float',
                defaultValue: 0.25,
                description: 'Exponent on stresses in Vs1 formula (:math:``) [-] (optional, default= 0.25)',
                unit: '-'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 125.5,
                description: 'Multiplier in Equation 15 (:math:``) [-] (optional, default= 125.5)',
                unit: '-'
            },
            {
                name: 'exponent_qc1',
                label: 'Exponent Qc1',
                type: 'float',
                defaultValue: 0.25,
                description: 'Exponent on qc1 in Equation 15 (:math:``) [-] (optional, default= 0.25)',
                unit: '-'
            },
            {
                name: 'exponent_d50',
                label: 'Exponent D50',
                type: 'float',
                defaultValue: 0.115,
                description: 'Exponent on median grain size in Equation 15 (:math:``) [-] (optional, default= 0.115)',
                unit: '-'
            },
        ]
    },
    vs_ic_robertsoncabal: {
        inputs: [
            {
                name: 'qt',
                label: 'Qt',
                type: 'float',
                required: true,
                description: 'Total cone resistance (q_t) [MPa] - Suggested range: 0.0 <= qt <= 100.0',
                unit: 'MPa'
            },
            {
                name: 'ic',
                label: 'Ic',
                type: 'float',
                required: true,
                description: 'Soil behaviour type index according to Robertson and Wride (I_c) [-] - Suggested range: 1.0 <= ic <= 4.0',
                unit: '-'
            },
            {
                name: 'sigma_vo',
                label: 'Sigma Vo',
                type: 'float',
                required: true,
                description: 'Total vertical stress (sigma_{vo}) [kPa] - Suggested range: 0.0 <= sigma_vo <= 800.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'gamma',
                label: 'Gamma',
                type: 'float',
                defaultValue: 19,
                description: 'Bulk unit weight (\gamma) [kN/m3] - Suggested range: 12.0 <= gamma <= 22.0',
                unit: 'kN/m3'
            },
            {
                name: 'g',
                label: 'G',
                type: 'float',
                defaultValue: 9.81,
                description: 'Acceleration due to gravity (g) [m/s2] - Suggested range: 9.7 <= g <= 10.2 (optional, default= 9.81)',
                unit: 'm/s2'
            },
            {
                name: 'exponent',
                label: 'Exponent',
                type: 'float',
                defaultValue: 0.5,
                description: 'Exponent in equation for shear wave velocity (:math:``) [-] (optional, default= 0.5)',
                unit: '-'
            },
            {
                name: 'calibration_coefficient_1',
                label: 'Calibration Coefficient 1',
                type: 'float',
                defaultValue: 0.55,
                description: 'First calibration coefficient in equation for alpha_s (:math:``) [-] (optional, default= 0.55)',
                unit: '-'
            },
            {
                name: 'calibration_coefficient_2',
                label: 'Calibration Coefficient 2',
                type: 'float',
                defaultValue: 1.68,
                description: 'Second calibration coefficient in equation for alpha_s (:math:``) [-] (optional, default= 1.68)',
                unit: '-'
            },
        ]
    },
    vs_stressdependent_stuyts: {
        inputs: [
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 50.0 <= sigma_vo_eff <= 800.0',
                unit: 'kPa'
            },
            {
                name: 'ic',
                label: 'Ic',
                type: 'float',
                required: true,
                description: 'Soil behaviour type index (I_c) [-] - Suggested range: 1.0 <= ic <= 4.0',
                unit: '-'
            },
            {
                name: 'a0',
                label: 'A0',
                type: 'float',
                defaultValue: 2.075,
                description: 'Calibration coefficient 0 (a_0) [-] - Suggested range: 1.7 <= a0 <= 2.5 (optional, default= 2.075)',
                unit: '-'
            },
            {
                name: 'a1',
                label: 'A1',
                type: 'float',
                defaultValue: -0.213,
                description: 'Calibration coefficient 1 (a_1) [-] - Suggested range: -0.5 <= a1 <= -0.05 (optional, default= -0.213)',
                unit: '-'
            },
            {
                name: 'a2',
                label: 'A2',
                type: 'float',
                defaultValue: 0.77,
                description: 'Calibration coefficient 2 (a_2) [-] - Suggested range: 0.5 <= a2 <= 1.0 (optional, default= 0.77)',
                unit: '-'
            },
            {
                name: 'a3',
                label: 'A3',
                type: 'float',
                defaultValue: -0.25,
                description: 'Calibration coefficient 3 (a_3) [-] - Suggested range: -0.5 <= a3 <= -0.1 (optional, default= -0.25)',
                unit: '-'
            },
        ]
    },
    InsituTestProcessing: {
        inputs: [
            { name: 'title', label: 'Analysis Title', type: 'string', defaultValue: 'InsituTestProcessing', required: true, description: 'Enter a title for this analysis' },
            {
                name: 'title',
                label: 'Title',
                type: 'float',
                required: true
            },
            {
                name: 'waterunitweight',
                label: 'Waterunitweight',
                type: 'float',
                defaultValue: 10.25
            },
        ]
    },
    PCPTProcessing: {
        inputs: [
            { name: 'title', label: 'Analysis Title', type: 'string', defaultValue: 'PCPTProcessing', required: true, description: 'Enter a title for this analysis' },
            {
                name: 'title',
                label: 'Title',
                type: 'float',
                required: true
            },
            {
                name: 'waterunitweight',
                label: 'Waterunitweight',
                type: 'float',
                defaultValue: 10.25
            },
        ]
    },
    plot_combined_longitudinal_profile: {
        inputs: [
            {
                name: 'cpts',
                label: 'Cpts',
                type: 'list',
                defaultValue: [],
                description: 'List with PCPTProcessing objects to be plotted'
            },
            {
                name: 'profiles',
                label: 'Profiles',
                type: 'list',
                defaultValue: [],
                description: 'List with SoilProfile objects for which a log needs to be plotted'
            },
            {
                name: 'latlon',
                label: 'Latlon',
                type: 'boolean',
                defaultValue: false,
                description: 'Boolean determining whether latitude and longitude are used or easting and northing in m (default=False for easting and northing in m)'
            },
            {
                name: 'option',
                label: 'Option',
                type: 'string',
                defaultValue: 'name',
                description: 'Determines whether CPT names (``option=\'name\'``) or tuples with coordinates (``option=\'coords\'``) are used for the ``start`` and ``end`` arguments'
            },
            {
                name: 'start',
                label: 'Start',
                type: 'string',
                description: 'CPT name for the starting point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in ``cpts``.'
            },
            {
                name: 'end',
                label: 'End',
                type: 'string',
                description: 'CPT name for the end point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in ``cpts``.'
            },
            {
                name: 'band',
                label: 'Band',
                type: 'float',
                defaultValue: 1000,
                description: 'Offset from the line connecting start and end points in which CPT are considered for plotting (default=1000m)'
            },
            {
                name: 'extend_profile',
                label: 'Extend Profile',
                type: 'boolean',
                defaultValue: false,
                description: 'Boolean determining whether the profile needs to be extended beyond the start and end points (default=False)'
            },
            {
                name: 'plotmap',
                label: 'Plotmap',
                type: 'boolean',
                defaultValue: false,
                description: 'Boolean determining whether a map of locations needs to be plotted next to the profile (default=False)'
            },
            {
                name: 'fillcolordict',
                label: 'Fillcolordict',
                type: 'string',
                defaultValue: {"SAND": "yellow", "CLAY": "brown", "SILT": "green", "ROCK": "grey"},
                description: 'Dictionary with fill colours (default yellow for \'SAND\', brown from \'CLAY\' and grey for \'ROCK\')'
            },
            {
                name: 'uniformcolor',
                label: 'Uniformcolor',
                type: 'string',
                description: 'Uniform color to use for all CPT traces (default=None for different color for each trace)'
            },
            {
                name: 'opacity',
                label: 'Opacity',
                type: 'float',
                defaultValue: 1,
                description: 'Opacity of the layers (default = 1 for non-transparent behaviour)'
            },
            {
                name: 'logwidth',
                label: 'Logwidth',
                type: 'float',
                defaultValue: 1,
                description: 'Width of the soil logs as an absolute value (default = 1)'
            },
            {
                name: 'prop',
                label: 'Prop',
                type: 'string',
                defaultValue: 'qc [MPa]',
                description: 'Selected property for plotting (default=\'qc [MPa]\')',
                unit: 'MPa'
            },
            {
                name: 'distance_unit',
                label: 'Distance Unit',
                type: 'string',
                defaultValue: 'm',
                description: 'Unit for coordinates and elevation (default=\'m\')'
            },
            {
                name: 'scale_factor',
                label: 'Scale Factor',
                type: 'float',
                defaultValue: 0.001,
                description: 'Scale factor for the property (default=0.001)'
            },
            {
                name: 'showfig',
                label: 'Showfig',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean determining whether the figure is shown (default=True)'
            },
            {
                name: 'xaxis_layout',
                label: 'Xaxis Layout',
                type: 'string',
                description: 'Dictionary with layout for the xaxis (default=None)'
            },
            {
                name: 'yaxis_layout',
                label: 'Yaxis Layout',
                type: 'string',
                description: 'Dictionary with layout for the xaxis (default=None)'
            },
            {
                name: 'general_layout',
                label: 'General Layout',
                type: 'string',
                description: 'Dictionary with general layout options (default=None)'
            },
            {
                name: 'legend_layout',
                label: 'Legend Layout',
                type: 'string',
                description: 'Dictionary with legend layout options (default=None)'
            },
            {
                name: 'show_annotations',
                label: 'Show Annotations',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean determining whether annotations need to be shown (default=True)'
            },
        ]
    },
    plot_longitudinal_profile: {
        inputs: [
            {
                name: 'cpts',
                label: 'Cpts',
                type: 'list',
                defaultValue: [],
                description: 'List with PCPTProcessing objects to be plotted'
            },
            {
                name: 'latlon',
                label: 'Latlon',
                type: 'boolean',
                defaultValue: false,
                description: 'Boolean determining whether latitude and longitude are used or easting and northing in m (default=False for easting and northing in m)'
            },
            {
                name: 'option',
                label: 'Option',
                type: 'string',
                defaultValue: 'name',
                description: 'Determines whether CPT names (``option=\'name\'``) or tuples with coordinates (``option=\'coords\'``) are used for the ``start`` and ``end`` arguments'
            },
            {
                name: 'start',
                label: 'Start',
                type: 'string',
                description: 'CPT name for the starting point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in ``cpts``.'
            },
            {
                name: 'end',
                label: 'End',
                type: 'string',
                description: 'CPT name for the end point or tuple of coordinates. If a CPT name is used, the selected CPT must be contained in ``cpts``.'
            },
            {
                name: 'band',
                label: 'Band',
                type: 'float',
                defaultValue: 1000,
                description: 'Offset from the line connecting start and end points in which CPT are considered for plotting (default=1000m)'
            },
            {
                name: 'extend_profile',
                label: 'Extend Profile',
                type: 'boolean',
                defaultValue: false,
                description: 'Boolean determining whether the profile needs to be extended beyond the start and end points (default=False)'
            },
            {
                name: 'plotmap',
                label: 'Plotmap',
                type: 'boolean',
                defaultValue: false,
                description: 'Boolean determining whether a map of locations needs to be plotted next to the profile (default=False)'
            },
            {
                name: 'uniformcolor',
                label: 'Uniformcolor',
                type: 'string',
                description: 'Uniform color to use for all CPT traces (default=None for different color for each trace)'
            },
            {
                name: 'prop',
                label: 'Prop',
                type: 'string',
                defaultValue: 'qc [MPa]',
                description: 'Selected property for plotting (default=\'qc [MPa]\')',
                unit: 'MPa'
            },
            {
                name: 'distance_unit',
                label: 'Distance Unit',
                type: 'string',
                defaultValue: 'm',
                description: 'Unit for coordinates and elevation (default=\'m\')'
            },
            {
                name: 'scale_factor',
                label: 'Scale Factor',
                type: 'float',
                defaultValue: 0.001,
                description: 'Scale factor for the property (default=0.001)'
            },
            {
                name: 'showfig',
                label: 'Showfig',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean determining whether the figure is shown (default=True)'
            },
            {
                name: 'xaxis_layout',
                label: 'Xaxis Layout',
                type: 'string',
                description: 'Dictionary with layout for the xaxis (default=None)'
            },
            {
                name: 'yaxis_layout',
                label: 'Yaxis Layout',
                type: 'string',
                description: 'Dictionary with layout for the xaxis (default=None)'
            },
            {
                name: 'general_layout',
                label: 'General Layout',
                type: 'string',
                description: 'Dictionary with general layout options (default=None)'
            },
            {
                name: 'legend_layout',
                label: 'Legend Layout',
                type: 'string',
                description: 'Dictionary with legend layout options (default=None)'
            },
            {
                name: 'show_annotations',
                label: 'Show Annotations',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean determining whether annotations need to be shown (default=True)'
            },
            {
                name: 'mapbox_zoom',
                label: 'Mapbox Zoom',
                type: 'float',
                defaultValue: 10,
                description: 'Zoom factor for map (if plotted, default=10)'
            },
        ]
    },
    read_ags: {
        inputs: [
            {
                name: 'file_path',
                label: 'File Path',
                type: 'float',
                required: true,
                description: 'Path (absolute or relative to the ags file)'
            },
            {
                name: 'groupname',
                label: 'Groupname',
                type: 'string',
                required: true,
                description: 'Name of the AGS group exactly as it is written in the AGS file'
            },
            {
                name: 'combine_headers',
                label: 'Combine Headers',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean determining whether the units are included in the header or not'
            },
            {
                name: 'includes_type',
                label: 'Includes Type',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean determining whether a TYPE is included with the data'
            },
        ]
    },
    frictionangle_spt_PHT: {
        inputs: [
            {
                name: 'N1_60',
                label: 'N1 60',
                type: 'float',
                required: true,
                description: 'Corrected SPT N value (\left( N_1 \right)_{60}) [-] - Suggested range: 0.0 <= N1_60 <= 60.0',
                unit: '-'
            },
            {
                name: 'intercept',
                label: 'Intercept',
                type: 'float',
                defaultValue: 27.1,
                description: 'Intercept at N=0 (-) [deg] - Suggested range: 23.0 <= intercept <= 35.0 (optional, default= 27.1)',
                unit: 'deg'
            },
            {
                name: 'multiplier',
                label: 'Multiplier',
                type: 'float',
                defaultValue: 0.3,
                description: 'Multiplier on linear term (-) [deg/blow] - Suggested range: 0.1 <= multiplier <= 0.7 (optional, default= 0.3)',
                unit: 'deg/blow'
            },
            {
                name: 'multiplier_quadratic',
                label: 'Multiplier Quadratic',
                type: 'float',
                defaultValue: 0.00054,
                description: 'Multiplier on the quadratic term (-) [deg/blow^2] - Suggested range: 0.0001 <= multiplier_quadratic <= 0.001 (optional, default= 0.00054)',
                unit: 'deg/blow^2'
            },
        ]
    },
    frictionangle_spt_kulhawymayne: {
        inputs: [
            {
                name: 'N',
                label: 'N',
                type: 'float',
                required: true,
                description: 'SPT N number (N) [-] - Suggested range: 0.0 <= N <= 60.0',
                unit: '-'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{vo}^{\prime}) [kPa] - Suggested range: 0.0 <= sigma_vo_eff <= 1000.0',
                unit: 'kPa'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] - Suggested range: 90.0 <= atmospheric_pressure <= 110.0 (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'coefficient_1',
                label: 'Coefficient 1',
                type: 'float',
                defaultValue: 12.2,
                description: 'First calibration coefficient (:math:``) [-] (optional, default= 12.2)',
                unit: '-'
            },
            {
                name: 'coefficient_2',
                label: 'Coefficient 2',
                type: 'float',
                defaultValue: 20.3,
                description: 'Second  calibration coefficient (:math:``) [-] (optional, default= 20.3)',
                unit: '-'
            },
            {
                name: 'coefficient_3',
                label: 'Coefficient 3',
                type: 'float',
                defaultValue: 0.34,
                description: 'Third calibration coefficient (:math:``) [-] (optional, default= 0.34)',
                unit: '-'
            },
        ]
    },
    overburdencorrection_spt_ISO: {
        inputs: [
            {
                name: 'N',
                label: 'N',
                type: 'float',
                required: true,
                description: 'Uncorrected or corrected SPT N number (N or N_{60}) [-] - Suggested range: 0.0 <= N <= 60.0',
                unit: '-'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Vertical effective stress (\sigma_{v0}^{\prime}) [kPa] - Suggested range: 25.0 <= sigma_vo_eff <= 400.0',
                unit: 'kPa'
            },
            {
                name: 'granular',
                label: 'Granular',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean defining whether the soil is granular or not. If the soil is not granular, the correction factor is taken equal to 1'
            },
        ]
    },
    overburdencorrection_spt_liaowhitman: {
        inputs: [
            {
                name: 'N',
                label: 'N',
                type: 'float',
                required: true,
                description: 'Field value of SPT N number (N) or corrected value N_{60} [-] - Suggested range: N >= 0.0',
                unit: '-'
            },
            {
                name: 'sigma_vo_eff',
                label: 'Sigma Vo Eff',
                type: 'float',
                required: true,
                description: 'Effective overburden pressure (\sigma_{vo}^{\prime}) [kPa] - Suggested range: sigma_vo_eff >= 0.0',
                unit: 'kPa'
            },
            {
                name: 'granular',
                label: 'Granular',
                type: 'boolean',
                defaultValue: true,
                description: 'Boolean defining whether the soil behaves in a granular or not. If the behaviour is not granular, the correction factor is taken equal to 1.'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] (optional, default= 100.0)',
                unit: 'kPa'
            },
        ]
    },
    relativedensity_spt_kulhawymayne: {
        inputs: [
            {
                name: 'N1_60',
                label: 'N1 60',
                type: 'float',
                required: true,
                description: 'SPT number corrected for overburden stress and energy ((N_1)_{60}) [-] - Suggested range: 0.0 <= N_1_60 <= 100.0',
                unit: '-'
            },
            {
                name: 'd_50',
                label: 'D 50',
                type: 'float',
                required: true,
                description: 'Median grain size (d_{50}) [mm] - Suggested range: 0.002 <= d_50 <= 20.0',
                unit: 'mm'
            },
            {
                name: 'calibration_factor_1',
                label: 'Calibration Factor 1',
                type: 'float',
                defaultValue: 60.0,
                description: 'First calibration factor (:math:``) [-] (optional, default= 60.0)',
                unit: '-'
            },
            {
                name: 'calibration_factor_2',
                label: 'Calibration Factor 2',
                type: 'float',
                defaultValue: 25.0,
                description: 'Second calibration factor (:math:``) [-] (optional, default= 25.0)',
                unit: '-'
            },
            {
                name: 'time_since_deposition',
                label: 'Time Since Deposition',
                type: 'float',
                defaultValue: 1.0,
                description: 'Time since deposition (t) [years] - Suggested range: time_since_deposition >= 1.0 (optional, default= 1.0)',
                unit: 'years'
            },
            {
                name: 'ocr',
                label: 'Ocr',
                type: 'float',
                defaultValue: 1.0,
                description: 'Overconsolidation ratio (OCR) [-] - Suggested range: 1.0 <= ocr <= 50.0 (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'ca_override',
                label: 'Ca Override',
                type: 'float',
                description: 'Direct specification of factor CA (C_A) [-] - Suggested range: ca_override >= 1.0 (optional, default= np.nan)',
                unit: '-'
            },
            {
                name: 'cocr_override',
                label: 'Cocr Override',
                type: 'float',
                description: 'Direct specification of factor COCR (C_{OCR}) [-] - Suggested range: cocr_override >= 1.0 (optional, default= np.nan)',
                unit: '-'
            },
        ]
    },
    relativedensityclass_spt_terzaghipeck: {
        inputs: [
            {
                name: 'N',
                label: 'N',
                type: 'float',
                required: true,
                description: 'Uncorrected SPT N number (N) [-] - Suggested range: 0.0 <= N <= 60.0',
                unit: '-'
            },
        ]
    },
    spt_N60_correction: {
        inputs: [
            {
                name: 'N',
                label: 'N',
                type: 'float',
                required: true,
                description: 'Field value of SPT N number (N) [-] - Suggested range: N >= 0.0',
                unit: '-'
            },
            {
                name: 'borehole_diameter',
                label: 'Borehole Diameter',
                type: 'float',
                required: true,
                description: 'Diameter of the borehole (D) [mm] - Suggested range: 60.0 <= borehole_diameter <= 200.0',
                unit: 'mm'
            },
            {
                name: 'rod_length',
                label: 'Rod Length',
                type: 'float',
                required: true,
                description: 'Length of rods connecting hammer with sampler (L) [m] - Suggested range: rod_length >= 0.0',
                unit: 'm'
            },
            {
                name: 'country',
                label: 'Country',
                type: 'float',
                required: true,
                description: 'Country where SPT test is executed - Options: (\'Japan\', \'United States\', \'Argentina\', \'China\', \'Other\'). If \'Other\' is chosen, an override for \eta_H should be specified'
            },
            {
                name: 'hammertype',
                label: 'Hammertype',
                type: 'string',
                required: true,
                description: 'Type of hammer used - Options: (\'Donut\', \'Safety\')'
            },
            {
                name: 'hammerrelease',
                label: 'Hammerrelease',
                type: 'float',
                required: true,
                description: 'Release mechanism for the hammer - Options: (\'Free fall\', \'Rope and pulley\')'
            },
            {
                name: 'samplertype',
                label: 'Samplertype',
                type: 'string',
                defaultValue: 'Standard sampler',
                description: 'Type of sampler used (optional, default= \'Standard sampler\') - Options: (\'Standard sampler\', \'With liner for dense sand and clay\', \'With liner for loose sand\')'
            },
            {
                name: 'eta_H',
                label: 'Eta H',
                type: 'float',
                description: 'Correction factor for hammer efficiency (\eta_H) [pct] - Suggested range: 0.0 <= eta_H <= 100.0 (optional, default= np.nan)',
                unit: 'pct'
            },
            {
                name: 'eta_B',
                label: 'Eta B',
                type: 'float',
                description: 'Correction factor for borehole diameter (\eta_B) [-] - Suggested range: 1.0 <= eta_B <= 1.2 (optional, default= np.nan)',
                unit: '-'
            },
            {
                name: 'eta_S',
                label: 'Eta S',
                type: 'float',
                description: 'Correction factor for sampler type (\eta_S) [-] - Suggested range: 0.8 <= eta_S <= 1.0 (optional, default= np.nan)',
                unit: '-'
            },
            {
                name: 'eta_R',
                label: 'Eta R',
                type: 'float',
                description: 'Correction factor for rod length (\eta_R) [-] - Suggested range: 0.75 <= eta_R <= 1.0 (optional, default= np.nan)',
                unit: '-'
            },
        ]
    },
    undrainedshearstrength_spt_salgado: {
        inputs: [
            {
                name: 'pi',
                label: 'Pi',
                type: 'float',
                required: true,
                description: 'Plasticity index (difference between liquid and plastic limit) (PI) [pct] - Suggested range: 15.0 <= plasticity_index <= 60.0',
                unit: 'pct'
            },
            {
                name: 'N_60',
                label: 'N 60',
                type: 'float',
                required: true,
                description: 'SPT number corrected to 60% energy ratio (N_{60}) [-] - Suggested range: 0.0 <= N_60 <= 100.0',
                unit: '-'
            },
            {
                name: 'atmospheric_pressure',
                label: 'Atmospheric Pressure',
                type: 'float',
                defaultValue: 100.0,
                description: 'Atmospheric pressure (P_a) [kPa] - Suggested range: 90.0 <= atmospheric_pressure <= 110.0 (optional, default= 100.0)',
                unit: 'kPa'
            },
            {
                name: 'alpha_prime_override',
                label: 'Alpha Prime Override',
                type: 'float',
                description: 'Override for direct specification of the alpha prime factor (\alpha^{\prime}) [-] - Suggested range: alpha_prime_override >= 0.0 (optional, default= np.nan)',
                unit: '-'
            },
        ]
    },
    undrainedshearstrengthclass_spt_terzaghipeck: {
        inputs: [
            {
                name: 'N',
                label: 'N',
                type: 'float',
                required: true,
                description: 'Uncorrected SPT N number (N) [-] - Suggested range: 0.0 <= N <= 60.0',
                unit: '-'
            },
        ]
    },
    youngsmodulus_spt_AASHTO: {
        inputs: [
            {
                name: 'N1_60',
                label: 'N1 60',
                type: 'float',
                required: true,
                description: 'Corrected SPT N number (\left( N_1 \right)_{60}) [-] - Suggested range: 0.0 <= N1_60 <= 60.0',
                unit: '-'
            },
            {
                name: 'soiltype',
                label: 'Soiltype',
                type: 'string',
                required: true,
                description: 'Soil type - Options: ("Silts", "Clean sands", "Coarse sands", "Gravels")'
            },
            {
                name: 'multiplier_silts',
                label: 'Multiplier Silts',
                type: 'float',
                defaultValue: 0.4,
                description: 'Multiplier on the silty soils (-) [-] (optional, default= 0.4)',
                unit: '-'
            },
            {
                name: 'multiplier_cleansand',
                label: 'Multiplier Cleansand',
                type: 'float',
                defaultValue: 0.7,
                description: 'Multiplier on the clean find sands (-) [-] (optional, default= 0.7)',
                unit: '-'
            },
            {
                name: 'multiplier_coarsesand',
                label: 'Multiplier Coarsesand',
                type: 'float',
                defaultValue: 1.0,
                description: 'Multiplier on the coarse sands (-) [-] (optional, default= 1.0)',
                unit: '-'
            },
            {
                name: 'multiplier_gravel',
                label: 'Multiplier Gravel',
                type: 'float',
                defaultValue: 1.1,
                description: 'Multiplier on the gravels (-) [-] (optional, default= 1.1)',
                unit: '-'
            },
        ]
    },
    SPTProcessing: {
        inputs: [
            { name: 'title', label: 'Analysis Title', type: 'string', defaultValue: 'SPTProcessing', required: true, description: 'Enter a title for this analysis' },
            {
                name: 'title',
                label: 'Title',
                type: 'float',
                required: true
            },
            {
                name: 'waterunitweight',
                label: 'Waterunitweight',
                type: 'float',
                defaultValue: 10
            },
        ]
    },
    logtimemethod: {
        inputs: [
            {
                name: 'times',
                label: 'Times',
                type: 'float',
                required: true,
                description: 'Array with time values in seconds, increasing from 0s at the start of the test'
            },
            {
                name: 'settlements',
                label: 'Settlements',
                type: 'float',
                required: true,
                description: 'Array with settlement values, increasing from 0 at the origin. The units are not important as only the time for 90% consolidation is determined.'
            },
            {
                name: 'drainagelength',
                label: 'Drainagelength',
                type: 'float',
                required: true,
                description: 'Drainage length for the consolidation (H_{dr}) [m] - Suggested range: drainagelength > 0',
                unit: 'm'
            },
            {
                name: 'initialguess_override',
                label: 'Initialguess Override',
                type: 'float',
                description: 'Override for the initial guess for \sqrt{t_{100}}, default=np.nan'
            },
            {
                name: 'ignore_warnings',
                label: 'Ignore Warnings',
                type: 'boolean',
                defaultValue: true
            },
            {
                name: 'showfig',
                label: 'Showfig',
                type: 'boolean',
                defaultValue: true
            },
        ]
    },
    roottimemethod: {
        inputs: [
            {
                name: 'times',
                label: 'Times',
                type: 'float',
                required: true,
                description: 'Array with time values in seconds, increasing from 0s at the start of the test'
            },
            {
                name: 'settlements',
                label: 'Settlements',
                type: 'float',
                required: true,
                description: 'Array with settlement values, increasing from 0 at the origin. The units are not important as only the time for 90% consolidation is determined.'
            },
            {
                name: 'drainagelength',
                label: 'Drainagelength',
                type: 'float',
                required: true,
                description: 'Drainage length for the consolidation (H_{dr}) [m] - Suggested range: drainagelength > 0',
                unit: 'm'
            },
            {
                name: 'initialguess_override',
                label: 'Initialguess Override',
                type: 'float',
                description: 'Override for the initial guess for \sqrt{t_{90}}, default=np.nan'
            },
            {
                name: 'xrange',
                label: 'Xrange',
                type: 'string',
                defaultValue: '(0, 100)'
            },
            {
                name: 'showfig',
                label: 'Showfig',
                type: 'boolean',
                defaultValue: true
            },
        ]
    },
    selectpoints: {
        inputs: [
            {
                name: 'nopoints',
                label: 'Nopoints',
                type: 'float',
                required: true
            },
            {
                name: 'timeout',
                label: 'Timeout',
                type: 'float',
                defaultValue: 60
            },
        ]
    },
    PSDChart: {
        inputs: [
            {
                name: 'plot_title',
                label: 'Plot Title',
                type: 'string'
            },
            {
                name: 'marginsettings',
                label: 'Marginsettings',
                type: 'string',
                defaultValue: {"l": 0, "r": 0, "b": 100, "t": 100, "pad": 0}
            },
            {
                name: 'legendsettings',
                label: 'Legendsettings',
                type: 'string',
                defaultValue: {"x": 0.1, "y": 0.9}
            },
        ]
    },
    PlasticityChart: {
        inputs: [
            {
                name: 'plot_height',
                label: 'Plot Height',
                type: 'float',
                defaultValue: 500
            },
            {
                name: 'plot_width',
                label: 'Plot Width',
                type: 'float',
                defaultValue: 800
            },
            {
                name: 'plot_title',
                label: 'Plot Title',
                type: 'string'
            },
        ]
    },
    undercompaction_cohesionless_ladd: {
        inputs: [
            {
                name: 'sample_height',
                label: 'Sample Height',
                type: 'float',
                required: true,
                description: 'Total height of the sample (H_0) [m] - Suggested range: 0.0 <= sample_height <= 1.0',
                unit: 'm'
            },
            {
                name: 'no_layers',
                label: 'No Layers',
                type: 'float',
                required: true,
                description: 'Number of layers for the sample (N) [-] - Suggested range: 1.0 <= no_layers <= 10.0',
                unit: '-'
            },
            {
                name: 'undercompaction_deepest',
                label: 'Undercompaction Deepest',
                type: 'float',
                required: true,
                description: 'Chosen undercompaction degree of the deepest layer (U_1) [pct] - Suggested range: 0.0 <= undercompaction_deepest <= 10.0',
                unit: 'pct'
            },
            {
                name: 'undercompaction_shallowest',
                label: 'Undercompaction Shallowest',
                type: 'float',
                defaultValue: 0,
                description: 'Chosen undercompaction degree of the shallowest layer (U_N) [pct] (default=0pct) - Suggested range: 0.0 <= undercompaction_deepest <= 10.0',
                unit: 'pct'
            },
        ]
    },
};
