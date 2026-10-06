/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 */

export const GEOTECHNICAL_MODULES = [
    {
        id: 'general',
        title: 'General and utility functions',
        description: 'Soil profiles, grids, plotting, and parameter mapping.',
        items: [ // Sub-modules
            {
                id: 'soil_profiles',
                title: 'Soil profiles and grids',
                functions: [
                    { id: 'SoilProfile', title: 'SoilProfile' },
                    { id: 'CalculationGrid', title: 'CalculationGrid' }
                ]
            },
            {
                id: 'plotting',
                title: 'Plotting',
                functions: [
                    { id: 'LogPlot', title: 'LogPlot' },
                    { id: 'LogPlotMatplotlib', title: 'LogPlotMatplotlib' },
                    { id: 'plot_with_log', title: 'Multi-Trace Log Plot' }
                ]
            },
            {
                id: 'ags_conversion',
                title: 'AGS Conversion',
                functions: [
                    { id: 'AGSConverter', title: 'AGSConverter' },
                    { id: 'AGSConverter_convert_ags_group', title: 'Convert AGS Group to Table' }
                ]
            },
            {
                id: 'parameter_mapping',
                title: 'Parameter Mapping',
                functions: [
                    { id: 'get_projected_point', title: 'Project Point onto Line' },
                    { id: 'latlon_distance', title: 'Distance from Lat/Lon Coordinates' },
                    { id: 'map_depth_properties', title: 'Map Layer Properties to Depths' },
                    { id: 'offsets_api', title: 'Offset from Point to Line' },
                    { id: 'merge_two_dicts', title: 'Merge Two Dictionaries' },
                    { id: 'reverse_dict', title: 'Reverse Dictionary Keys/Values' }
                ]
            },
            {
                id: 'validation',
                title: 'Validation',
                functions: [
                    { id: 'check_layer_overlap', title: 'Check Layer Overlap' },
                    { id: 'validate_boolean', title: 'Validate Boolean Input' },
                    { id: 'validate_float', title: 'Validate Float Input' },
                    { id: 'validate_integer', title: 'Validate Integer Input' },
                    { id: 'validate_list', title: 'Validate Numeric List' },
                    { id: 'validate_string', title: 'Validate String Input' }
                ]
            }
        ]
    },
    {
        id: 'site_investigation',
        title: 'Site investigation',
        description: 'Soil classification, correlations, and in-situ/lab testing.',
        items: [
            {
                id: 'classification_phase',
                title: 'Classification: Phase relations',
                functions: [
                    { id: 'bulkunitweight', title: 'Bulk Unit Weight (from Gs, e, Sr)' },
                    { id: 'bulkunitweight_dryunitweight', title: 'Bulk Unit Weight (from Dry Unit Weight)' },
                    { id: 'density_unitweight', title: 'Unit Weight to Density' },
                    { id: 'dryunitweight_watercontent', title: 'Dry Unit Weight (from Water Content)' },
                    { id: 'porosity_voidratio', title: 'Porosity (from Void Ratio)' },
                    { id: 'relative_density', title: 'Relative Density (from Void Ratio)' },
                    { id: 'saturation_watercontent', title: 'Degree of Saturation (from Water Content)' },
                    { id: 'unitweight_density', title: 'Density to Unit Weight' },
                    { id: 'unitweight_watercontent_saturated', title: 'Saturated Unit Weight (from Water Content)' },
                    { id: 'voidratio_bulkunitweight', title: 'Void Ratio (from Bulk Unit Weight)' },
                    { id: 'voidratio_drydensity', title: 'Void Ratio (from Dry Density)' },
                    { id: 'voidratio_porosity', title: 'Void Ratio (from Porosity)' },
                    { id: 'voidratio_watercontent', title: 'Void Ratio (from Water Content)' },
                    { id: 'watercontent_voidratio', title: 'Water Content (from Void Ratio)' }
                ]
            },
            {
                id: 'classification_categories',
                title: 'Classification: Classes & categories',
                functions: [
                    { id: 'relativedensity_categories', title: 'Relative Density Classification' },
                    { id: 'samplequality_voidratio_lunne', title: 'Lunne Sample Quality (Void Ratio Change)' },
                    { id: 'su_categories', title: 'Undrained Shear Strength Classification' },
                    { id: 'uscs_categories', title: 'USCS Soil Type Descriptions' }
                ]
            },
            {
                id: 'correlations_all',
                title: 'Correlations: All soil types',
                functions: [
                    { id: 'acousticimpedance_bulkunitweight_chen', title: 'Chen Acoustic Impedance–Porosity Correlation' },
                    { id: 'k0_frictionangle_mesri', title: 'Mesri K0 (Normally/Overconsolidated Soils)' },
                    { id: 'shearwavevelocity_compressionindex_cha', title: 'Cha Vs–Compression Index Correlation' }
                ]
            },
            {
                id: 'correlations_cohesive',
                title: 'Correlations: Cohesive soils',
                functions: [
                    { id: 'compressionindex_watercontent_koppula', title: 'Koppula (1981) Compression Index' },
                    { id: 'cv_liquidlimit_usnavy', title: 'US Navy Cv from Liquid Limit' },
                    { id: 'frictionangle_plasticityindex', title: 'Drained Friction Angle (from Plasticity Index)' },
                    { id: 'gmax_plasticityocr_andersen', title: 'Andersen Gmax (Plasticity & OCR)' },
                    { id: 'icl_scl_burland', title: 'Burland (1990) Intrinsic & Sedimentation Compression Lines' },
                    { id: 'k0_plasticity_kenney', title: 'Kenney K0 (from Plasticity, Clay)' }
                ]
            },
            {
                id: 'correlations_cohesionless',
                title: 'Correlations: Cohesionless soils',
                functions: [
                    { id: 'gmax_sand_hardinblack', title: 'Hardin & Black (1968) Gmax for Sand' },
                    { id: 'hssmall_parameters_sand', title: 'HS Small Parameters (from Relative Density)' },
                    { id: 'permeability_d10_hazen', title: 'Hazen Permeability (from D10)' },
                    { id: 'stress_dilatancy_bolton', title: 'Bolton Stress–Dilatancy Relation' }
                ]
            },
            {
                id: 'insitu_pcpt_class',
                title: 'In-situ: PCPT processing class',
                functions: [
                    { id: 'PCPTProcessing', title: 'PCPTProcessing' }
                ]
            },
            {
                id: 'insitu_pcpt_functions',
                title: 'In-situ: PCPT functions',
                functions: [
                    { id: 'behaviourindex_pcpt_nonnormalised', title: 'Non-Normalised Soil Behaviour Index' },
                    { id: 'behaviourindex_pcpt_robertsonwride', title: 'Robertson & Wride (1998) Soil Behaviour Index' },
                    { id: 'clippingdepths_qc1N_tianlehane', title: 'Tian & Lehane (2025) Layer Clipping Depths' },
                    { id: 'coneresistance_ocsand_baldi', title: 'Baldi Cone Resistance (Overconsolidated Sand)' },
                    { id: 'constrainedmodulus_pcpt_robertson', title: 'Robertson Constrained Modulus (CPT)' },
                    { id: 'dissipation_test_teh', title: 'Teh & Houlsby (1991) Dissipation Curve' },
                    { id: 'drainedsecantmodulus_sand_bellotti', title: 'Bellotti Drained Secant Modulus (Sand)' },
                    { id: 'frictionangle_overburden_kleven', title: 'Kleven (1986) Friction Angle Chart' },
                    { id: 'frictionangle_sand_kulhawymayne', title: 'Kulhawy & Mayne Friction Angle (Sand, CPT)' },
                    { id: 'gmax_clay_maynerix', title: 'Mayne & Rix (1993) Gmax for Clay' },
                    { id: 'gmax_cpt_puechen', title: 'Puechen Gmax (CPT)' },
                    { id: 'gmax_sand_rixstokoe', title: 'Rix & Stokoe Gmax (Sand, CPT)' },
                    { id: 'gmax_voidratio_maynerix', title: 'Mayne & Rix Gmax (from Void Ratio)' },
                    { id: 'ic_soilclass_robertson', title: 'Robertson & Wride Soil Classification (Ic)' },
                    { id: 'k0_sand_mayne', title: 'Mayne K0 (Clean Sand, CPT)' },
                    { id: 'ocr_cpt_lunne', title: 'Lunne OCR (CPT, Clay)' },
                    { id: 'pcpt_normalisations', title: 'PCPT Normalisation & Correction' },
                    { id: 'relativedensity_ncsand_baldi', title: 'Baldi Relative Density (NC Sand)' },
                    { id: 'relativedensity_ocsand_baldi', title: 'Baldi Relative Density (OC Sand)' },
                    { id: 'relativedensity_sand_jamiolkowski', title: 'Jamiolkowski Relative Density (Sand, CPT)' },
                    { id: 'sensitivity_frictionratio_lunne', title: 'Rad & Lunne (1986) Sensitivity (Friction Ratio)' },
                    { id: 'soilclass_robertson', title: 'Robertson & Wride Soil Classification' },
                    { id: 'soiltype_vs_longodonohue', title: 'Long & Donohue Soil Type (Vs, CPT)' },
                    { id: 'undrainedshearstrength_clay_radlunne', title: 'Rad & Lunne Undrained Shear Strength (Net qt)' },
                    { id: 'unitweight_mayne', title: 'Mayne Total Unit Weight (CPT)' },
                    { id: 'vs_cpt_andrus', title: 'Andrus Shear Wave Velocity (CPT)' },
                    { id: 'vs_cpt_hegazymayne', title: 'Hegazy & Mayne Shear Wave Velocity (CPT)' },
                    { id: 'vs_cpt_longdonohue', title: 'Long & Donohue Shear Wave Velocity (CPT)' },
                    { id: 'vs_cpt_mcgannetal', title: 'McGann et al. Shear Wave Velocity (CPT)' },
                    { id: 'vs_cpt_tonniandsimonini', title: 'Tonni & Simonini Shear Wave Velocity (CPT)' },
                    { id: 'vs_cpt_wrideetal', title: 'Wride et al. Shear Wave Velocity (CPT)' },
                    { id: 'vs_cptd50_karrayetal', title: 'Karray et al. Shear Wave Velocity (CPT, D50)' },
                    { id: 'vs_ic_robertsoncabal', title: 'Robertson & Cabal Shear Wave Velocity (Ic)' },
                    { id: 'vs_stressdependent_stuyts', title: 'Stuyts (2024) Stress-Dependent Shear Wave Velocity' }
                ]
            },
            {
                id: 'insitu_spt_class',
                title: 'In-situ: SPT processing class',
                functions: [
                    { id: 'SPTProcessing', title: 'SPTProcessing' }
                ]
            },
            {
                id: 'insitu_spt_functions',
                title: 'In-situ: SPT corrections & correlations',
                functions: [
                    { id: 'frictionangle_spt_PHT', title: 'Peck, Hanson & Thornburn (1974) Friction Angle' },
                    { id: 'frictionangle_spt_kulhawymayne', title: 'Kulhawy & Mayne Friction Angle (SPT)' },
                    { id: 'overburdencorrection_spt_ISO', title: 'ISO Overburden Correction (SPT N)' },
                    { id: 'overburdencorrection_spt_liaowhitman', title: 'Liao & Whitman Overburden Correction (SPT N)' },
                    { id: 'relativedensity_spt_kulhawymayne', title: 'Kulhawy & Mayne Relative Density (SPT)' },
                    { id: 'relativedensityclass_spt_terzaghipeck', title: 'Terzaghi & Peck Relative Density Class (SPT)' },
                    { id: 'spt_N60_correction', title: 'SPT N60 Energy Correction' },
                    { id: 'undrainedshearstrength_spt_salgado', title: 'Salgado Undrained Shear Strength (SPT)' },
                    { id: 'undrainedshearstrengthclass_spt_terzaghipeck', title: 'Terzaghi & Peck Strength Class (SPT)' },
                    { id: 'youngsmodulus_spt_AASHTO', title: 'AASHTO Young\'s Modulus (SPT)' }
                ]
            },
            {
                id: 'lab_sampleprep',
                title: 'Laboratory: Sample preparation',
                functions: [
                    { id: 'undercompaction_cohesionless_ladd', title: 'Ladd Undercompaction (Sample Preparation)' }
                ]
            },
            {
                id: 'lab_indextests',
                title: 'Laboratory: Index tests',
                functions: [
                    { id: 'PlasticityChart', title: 'PlasticityChart' },
                    { id: 'PSDChart', title: 'PSDChart' }
                ]
            },
            {
                id: 'lab_compressibility',
                title: 'Laboratory: Compressibility',
                functions: [
                    { id: 'logtimemethod', title: 'Log-Time Method (Coefficient of Consolidation)' },
                    { id: 'roottimemethod', title: 'Root-Time Method (Coefficient of Consolidation)' }
                ]
            }
        ]
    },
    {
        id: 'piles',
        title: 'Pile calculations',
        description: 'Axial capacity, settlements, lateral behaviour, and more.',
        items: [
            {
                id: 'unit_skin_friction',
                title: 'Unit skin friction',
                functions: [
                    { id: 'API_unit_shaft_friction_clay', title: 'API (Clay)' },
                    { id: 'API_unit_shaft_friction_sand_rp2geo', title: 'API RP2 GEO (Sand)' },
                    { id: 'unitskinfriction_clay_almhamre', title: 'Alm & Hamre (Clay)' },
                    { id: 'unitskinfriction_sand_almhamre', title: 'Alm & Hamre (Sand)' }
                ]
            },
            {
                id: 'unit_end_bearing',
                title: 'Unit end bearing',
                functions: [
                    { id: 'API_unit_end_bearing_clay', title: 'API (Clay)' },
                    { id: 'API_unit_end_bearing_sand_rp2geo', title: 'API RP2 GEO (Sand)' },
                    { id: 'unitendbearing_clay_almhamre', title: 'Alm & Hamre (Clay)' },
                    { id: 'unitendbearing_sand_almhamre', title: 'Alm & Hamre (Sand)' }
                ]
            },
            {
                id: 'axial_capacity',
                title: 'Axial capacity calculations',
                functions: [
                    { id: 'AxCapCalculation', title: 'Axial Capacity (AxCap)' }
                ]
            },
            {
                id: 'de_beer',
                title: 'De Beer and Eurocode 7 calculations',
                functions: [
                    { id: 'DeBeerCalculation', title: 'De Beer Calculation' }
                ]
            },
            {
                id: 'koppejan',
                title: 'Koppejan pile resistance',
                functions: [
                    { id: 'KoppejanCalculation', title: 'Koppejan Calculation' }
                ]
            },
            {
                id: 'lcpc',
                title: 'LCPC pile resistance',
                functions: [
                    { id: 'LCPC_Calculation', title: 'LCPC Calculation' }
                ]
            },
            {
                id: 'pile_settlement',
                title: 'Pile settlement',
                functions: [
                    { id: 'PileSettlementCurves', title: 'Pile Settlement Curves' }
                ]
            },
            {
                id: 'lateral_behaviour',
                title: 'Pile lateral behaviour',
                functions: [
                    { id: 'pilegroupeffect_reesevanimpe', title: 'Pile Group Effect (Reese & Van Impe)' },
                    { id: 'reinforced_circularsection_inertia', title: 'Reinforced Circular Section Inertia' }
                ]
            },
            {
                id: 'cavity_expansion',
                title: 'Cavity expansion methods',
                functions: [
                    { id: 'expansion_cylinder_tresca', title: 'Cylinder Expansion (Tresca)' },
                    { id: 'expansion_tresca_thicksphere', title: 'Thick Sphere Expansion (Tresca)' },
                    { id: 'stress_cylinder_elastic_isotropic', title: 'Elastic Cylinder Stress (Isotropic)' }
                ]
            },
            {
                id: 'negative_friction',
                title: 'Negative skin friction',
                functions: [
                    { id: 'negativeskinfriction_pilegroup_zeevaertdebeer', title: 'Zeevaert & De Beer (Pile Group)' }
                ]
            },
            {
                id: 'pile_testing',
                title: 'Pile testing functionality',
                functions: [
                    { id: 'piletest_chinkondler', title: 'Chin-Kondler Extrapolation' }
                ]
            }
        ]
    },
    {
        id: 'shallow',
        title: 'Shallow foundations',
        description: 'Stress distribution, capacity, and settlement analysis.',
        icon: 'Square',
        items: [
            {
                id: 'stress_dist',
                title: 'Stress distributions',
                functions: [
                    { id: 'stresses_circle', title: 'Circular Footing Stress' },
                    { id: 'stresses_lineload_retainingwall', title: 'Line Load Stress (Retaining Wall)' },
                    { id: 'stresses_pointload', title: 'Point Load Stress' },
                    { id: 'stresses_rectangle', title: 'Rectangular Footing Stress' },
                    { id: 'stresses_stripload', title: 'Strip Load Stress' },
                    { id: 'stresses_stripload_retainingwall', title: 'Strip Load Stress (Retaining Wall)' }
                ]
            },
            {
                id: 'shallow_capacity',
                title: 'Shallow foundation capacity',
                functions: [
                    { id: 'shallow_foundation_capacity_undrained', title: 'Undrained Capacity Analysis' },
                    { id: 'shallow_foundation_capacity_drained', title: 'Drained Capacity Analysis' },
                    { id: 'effectivearea_circle_api', title: 'Effective Area (Circular)' },
                    { id: 'effectivearea_rectangle_api', title: 'Effective Area (Rectangular)' },
                    { id: 'envelope_drained_api', title: 'Envelope (Drained)' },
                    { id: 'envelope_undrained_api', title: 'Envelope (Undrained)' },
                    { id: 'failuremechanism_prandtl', title: 'Failure Mechanism (Prandtl)' },
                    { id: 'ngamma_frictionangle_davisbooker', title: 'N_gamma (Davis & Booker)' },
                    { id: 'ngamma_frictionangle_meyerhof', title: 'N_gamma (Meyerhof)' },
                    { id: 'ngamma_frictionangle_vesic', title: 'N_gamma (Vesic)' },
                    { id: 'nq_frictionangle_sand', title: 'N_q (Sand)' },
                    { id: 'slidingcapacity_drained_api', title: 'Sliding Capacity (Drained)' },
                    { id: 'slidingcapacity_undrained_api', title: 'Sliding Capacity (Undrained)' },
                    { id: 'verticalcapacity_drained_api', title: 'Vertical Capacity (Drained)' },
                    { id: 'verticalcapacity_undrained_api', title: 'Vertical Capacity (Undrained)' }
                ]
            },
            {
                id: 'shallow_settlement',
                title: 'Settlement',
                functions: [
                    { id: 'settlement_calculation', title: 'Settlement Calculation (Profile)' },
                    { id: 'consolidationsettlement_mv', title: 'Consolidation Settlement (mv)' },
                    { id: 'primaryconsolidationsettlement_nc', title: 'Primary Settlement (NC)' },
                    { id: 'primaryconsolidationsettlement_oc', title: 'Primary Settlement (OC)' }
                ]
            }
        ]
    },

    {
        id: 'consolidation',
        title: 'Consolidation functions',
        description: 'Groundwater flow and pore pressure dissipation.',
        items: [
            {
                id: 'groundwater',
                title: 'Pumping tests',
                functions: [
                    { id: 'hydraulicconductivity_unconfinedaquifer', title: 'Hydraulic Conductivity (Unconfined Aquifer)' }
                ]
            },
            {
                id: 'pore_pressure',
                title: 'One-dimensional consolidation',
                functions: [
                    { id: 'consolidation_calculation', title: 'Consolidation Calculation (Numerical)' },
                    { id: 'consolidation_degree', title: 'Degree of Consolidation' },
                    { id: 'pore_pressure_fourier', title: 'Excess Pore Pressure (Fourier)' }
                ]
            }
        ]
    },
    {
        id: 'excavations',
        title: 'Excavations',
        description: 'Earth pressure coefficients and Soilmix analysis.',
        items: [
            {
                id: 'earth_pressure',
                title: 'Earth pressure coefficients',
                functions: [
                    { id: 'earthpressurecoefficients_frictionangle', title: 'Earth Pressure (Friction Angle)' },
                    { id: 'earthpressurecoefficients_poncelet', title: 'Earth Pressure (Poncelet)' },
                    { id: 'earthpressurecoefficients_rankine', title: 'Earth Pressure (Rankine)' }
                ]
            },
            {
                id: 'soilmix',
                title: 'Soilmix',
                functions: [
                    { id: 'bendingstiffness_soilmix_method1', title: 'Bending Stiffness (Method 1)' },
                    { id: 'bendingstiffness_soilmix_method2', title: 'Bending Stiffness (Method 2)' }
                ]
            }
        ]
    },
    {
        id: 'dynamics',
        title: 'Soil dynamics',
        description: 'Liquefaction, cyclic behaviour, and dynamic properties.',
        items: [
            {
                id: 'liquefaction',
                title: 'Liquefaction',
                functions: [
                    { id: 'cyclicstressratio_moss', title: 'Moss (2006) Cyclic Stress Ratio' },
                    { id: 'cyclicstressratio_youd', title: 'Youd (2001) Cyclic Stress Ratio' },
                    { id: 'liquefaction_robertsonfear', title: 'Robertson & Fear (1995) Liquefaction' },
                    { id: 'liquefactionprobability_moss', title: 'Moss (2006) Liquefaction Probability' },
                    { id: 'liquefactionprobability_saye', title: 'Saye (2017) Liquefaction Probability' }
                ]
            },
            {
                id: 'cyclic_behaviour',
                title: 'Cyclic behaviour',
                functions: [
                    { id: 'cycliccontours_dssclay_andersen', title: 'AC Cyclic Contours (DSS Clay)' },
                    { id: 'cycliccontours_triaxialclay_andersen', title: 'AC Cyclic Contours (Triaxial Clay)' },
                    { id: 'cyclicstrength_dsssand_relativedensity', title: 'AC Cyclic Strength (DSS Sand - Dr)' },
                    { id: 'cyclicstrength_dsssand_watercontent', title: 'AC Cyclic Strength (DSS Sand - w)' },
                    { id: 'plotcycliccontours_dssclay_andersen', title: 'Plot Cyclic Contours (DSS Clay)' },
                    { id: 'plotcycliccontours_triaxialclay_andersen', title: 'Plot Cyclic Contours (Triaxial Clay)' },
                    { id: 'plotporepressureaccumulation_dssclay_andersen', title: 'Plot Pore Pressure (DSS Clay)' },
                    { id: 'plotporepressureaccumulation_dsssand_andersen', title: 'Plot Pore Pressure (DSS Sand)' },
                    { id: 'plotporepressureaccumulation_triaxialclay_andersen', title: 'Plot Pore Pressure (Triaxial Clay)' },
                    { id: 'plotstrainaccumulation_dssclay_andersen', title: 'Plot Strain Accum. (DSS Clay)' },
                    { id: 'plotstrainaccumulation_dsssand_andersen', title: 'Plot Strain Accum. (DSS Sand)' },
                    { id: 'plotstrainaccumulation_triaxialclay_andersen', title: 'Plot Strain Accum. (Triaxial Clay)' },
                    { id: 'porepressureaccumulation_dssclay_andersen', title: 'Pore Pressure Accum. (DSS Clay)' },
                    { id: 'porepressureaccumulation_triaxialclay_andersen', title: 'Pore Pressure Accum. (Triaxial Clay)' },
                    { id: 'strainaccumulation_dssclay_andersen', title: 'Strain Accum. (DSS Clay)' },
                    { id: 'strainaccumulation_dsssand_andersen', title: 'Strain Accum. (DSS Sand)' },
                    { id: 'strainaccumulation_triaxialclay_andersen', title: 'Strain Accum. (Triaxial Clay)' }
                ]
            },
            {
                id: 'dynamic_props',
                title: 'Dynamic soil property correlations',
                functions: [
                    { id: 'dampingratio_sandgravel_seed', title: 'Seed & Idriss (1970) Damping Ratio' },
                    { id: 'gmax_shearwavevelocity', title: 'Gmax from Shear Wave Velocity' },
                    { id: 'modulusreduction_darendeli', title: 'Darendeli (2001) Modulus Reduction' },
                    { id: 'modulusreduction_plasticity_ishibashi', title: 'Ishibashi & Zhang (1993) Modulus Reduction' }
                ]
            },
            {
                id: 'cpt_liquefaction',
                title: 'CPT Liquefaction',
                functions: [
                    { id: 'Qtn_cs_boulanger_idriss_2014', title: 'B&I (2014) Qtn,cs' },
                    { id: 'Qtn_cs_idriss_boulanger_2008', title: 'I&B (2008) Qtn,cs' },
                    { id: 'Qtn_cs_robertson_cabal_2022', title: 'R&C (2022) Qtn,cs' },
                    { id: 'Qtn_cs_robertson_wride_1998', title: 'R&W (1998) Qtn,cs' },
                    { id: 'crr_boulanger_idriss_2014', title: 'B&I (2014) CRR' },
                    { id: 'crr_idriss_boulanger_2008', title: 'I&B (2008) CRR' },
                    { id: 'crr_robertson_cabal_2022', title: 'R&C (2022) CRR' },
                    { id: 'crr_robertson_wride_1998', title: 'R&W (1998) CRR' },
                    { id: 'csr_boulanger_idriss_2014', title: 'B&I (2014) CSR' },
                    { id: 'csr_idriss_boulanger_2008', title: 'I&B (2008) CSR' },
                    { id: 'csr_robertson_cabal_2022', title: 'R&C (2022) CSR' },
                    { id: 'csr_robertson_wride_1998', title: 'R&W (1998) CSR' },
                    { id: 'fos_liquefaction', title: 'Factor of Safety (Liquefaction)' },
                    { id: 'liquefaction_strains_zhang', title: 'Zhang (2002) Liquefaction Strains' }
                ]
            }
        ]
    },
    {
        id: 'eurocode7',
        title: 'EuroCode7',
        description: 'Parameter selection and partial factor selection.',
        items: [
            {
                id: 'parameter_selection',
                title: 'Parameter selection',
                functions: [
                    { id: 'parameter_selection_constant_value', title: 'Characteristic Value (Constant)' },
                    { id: 'parameter_selection_linear_trend', title: 'Characteristic Value (Linear Trend)' }
                ]
            },
            {
                id: 'partial_factors',
                title: 'Partial factor selection',
                functions: [
                    { id: 'eurocode7_factors', title: 'Eurocode 7 STR/GEO Partial Factors' }
                ]
            }
        ]
    },
    {
        id: 'indian_standards',
        title: 'Indian Standards (BIS)',
        description: 'IS 6403, IS 1498, IS 2131, IS 1892, IS 1904, IS 2950 and IS 2720 calculations.',
        items: [
            {
                id: 'bis_foundations',
                title: 'Foundations (IS 6403, IS 1904, IS 2950)',
                functions: [
                    { id: 'bearing_capacity_is6403', title: 'IS 6403 Bearing Capacity (Shallow Foundation)' },
                    { id: 'permissible_settlement_is1904', title: 'IS 1904 Permissible Settlement' },
                    { id: 'stability_check_is1904', title: 'IS 1904 Sliding / Overturning Check' },
                    { id: 'raft_rigidity_is2950', title: 'IS 2950 Raft Rigidity (Rigid / Flexible)' }
                ]
            },
            {
                id: 'bis_investigation',
                title: 'Site investigation (IS 1892, IS 2131, IS 1498)',
                functions: [
                    { id: 'investigation_depth_is1892', title: 'IS 1892 Depth of Investigation' },
                    { id: 'borehole_layout_is1892', title: 'IS 1892 Borehole Disposition' },
                    { id: 'spt_correction_is2131', title: 'IS 2131 SPT N Corrections' },
                    { id: 'classify_soil_is1498', title: 'IS 1498 Soil Classification' }
                ]
            },
            {
                id: 'bis_lab',
                title: 'Laboratory tests (IS 2720)',
                functions: [
                    { id: 'specific_gravity_is2720', title: 'IS 2720-3 Specific Gravity' },
                    { id: 'liquid_limit_one_point_is2720', title: 'IS 2720-5 One-Point Liquid Limit' },
                    { id: 'flow_index_is2720', title: 'IS 2720-5 Flow Index' },
                    { id: 'consistency_indices_is2720', title: 'IS 2720-5 Consistency Indices' },
                    { id: 'permeability_constant_head_is2720', title: 'IS 2720-17 Constant Head Permeability' },
                    { id: 'permeability_falling_head_is2720', title: 'IS 2720-17 Falling Head Permeability' }
                ]
            }
        ]
    },
    {
        id: 'constitutive',
        title: 'Constitutive models',
        description: 'Models for cohesionless, cohesive, and rock materials.',
        items: [
            {
                id: 'model_general',
                title: 'General',
                functions: [
                    { id: 'mohrcoulomb_triaxial_compression', title: 'Mohr-Coulomb Triaxial Compression' },
                    { id: 'mohrcoulomb_triaxial_extension', title: 'Mohr-Coulomb Triaxial Extension' }
                ]
            },
            {
                id: 'cohesionless',
                title: 'Cohesionless materials',
                functions: [
                    { id: 'hardening_soil_drained_triaxial', title: 'Hardening Soil (Drained Triaxial)' }
                ]
            },
            { id: 'cohesive', title: 'Cohesive', functions: [] },
            { id: 'rock', title: 'Rock', functions: [] }
        ]
    },
    {
        id: 'pipelines',
        title: 'Pipelines and cables',
        description: 'Stability analysis for pipelines and cables.',
        items: [
            {
                id: 'pipeline_stability',
                title: 'Pipeline and cable stability',
                functions: [
                    { id: 'contactwidth', title: 'Contact Width' },
                    { id: 'embedment_drained', title: 'Embedment (Drained)' },
                    { id: 'embedment_undrained_method1', title: 'Embedment (Undrained Method 1)' },
                    { id: 'embedment_undrained_method2', title: 'Embedment (Undrained Method 2)' },
                    { id: 'lay_touchdown_factor', title: 'Lay Touchdown Factor' },
                    { id: 'penetratedarea', title: 'Penetrated Area' }
                ]
            }
        ]
    }
];
