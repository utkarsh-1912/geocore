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
                    { id: 'plot_with_log', title: 'plot_with_log()' }
                ]
            },
            {
                id: 'ags_conversion',
                title: 'AGS Conversion',
                functions: [
                    { id: 'AGSConverter', title: 'AGSConverter' },
                    { id: 'AGSConverter_convert_ags_group', title: 'convert_ags_group()' }
                ]
            },
            {
                id: 'parameter_mapping',
                title: 'Parameter Mapping',
                functions: [
                    { id: 'get_projected_point', title: 'get_projected_point()' },
                    { id: 'latlon_distance', title: 'latlon_distance()' },
                    { id: 'map_depth_properties', title: 'map_depth_properties()' },
                    { id: 'offsets_api', title: 'offsets()' },
                    { id: 'merge_two_dicts', title: 'merge_two_dicts()' },
                    { id: 'reverse_dict', title: 'reverse_dict()' }
                ]
            },
            {
                id: 'validation',
                title: 'Validation',
                functions: [
                    { id: 'check_layer_overlap', title: 'check_layer_overlap()' },
                    { id: 'validate_boolean', title: 'validate_boolean()' },
                    { id: 'validate_float', title: 'validate_float()' },
                    { id: 'validate_integer', title: 'validate_integer()' },
                    { id: 'validate_list', title: 'validate_list()' },
                    { id: 'validate_string', title: 'validate_string()' }
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
                    { id: 'bulkunitweight', title: 'bulkunitweight()' },
                    { id: 'bulkunitweight_dryunitweight', title: 'bulkunitweight_dryunitweight()' },
                    { id: 'density_unitweight', title: 'density_unitweight()' },
                    { id: 'dryunitweight_watercontent', title: 'dryunitweight_watercontent()' },
                    { id: 'porosity_voidratio', title: 'porosity_voidratio()' },
                    { id: 'relative_density', title: 'relative_density()' },
                    { id: 'saturation_watercontent', title: 'saturation_watercontent()' },
                    { id: 'unitweight_density', title: 'unitweight_density()' },
                    { id: 'unitweight_watercontent_saturated', title: 'unitweight_watercontent_saturated()' },
                    { id: 'voidratio_bulkunitweight', title: 'voidratio_bulkunitweight()' },
                    { id: 'voidratio_drydensity', title: 'voidratio_drydensity()' },
                    { id: 'voidratio_porosity', title: 'voidratio_porosity()' },
                    { id: 'voidratio_watercontent', title: 'voidratio_watercontent()' },
                    { id: 'watercontent_voidratio', title: 'watercontent_voidratio()' }
                ]
            },
            {
                id: 'classification_categories',
                title: 'Classification: Classes & categories',
                functions: [
                    { id: 'relativedensity_categories', title: 'relativedensity_categories()' },
                    { id: 'samplequality_voidratio_lunne', title: 'samplequality_voidratio_lunne()' },
                    { id: 'su_categories', title: 'su_categories()' },
                    { id: 'uscs_categories', title: 'uscs_categories()' }
                ]
            },
            {
                id: 'correlations_all',
                title: 'Correlations: All soil types',
                functions: [
                    { id: 'acousticimpedance_bulkunitweight_chen', title: 'acousticimpedance_bulkunitweight_chen()' },
                    { id: 'k0_frictionangle_mesri', title: 'k0_frictionangle_mesri()' },
                    { id: 'shearwavevelocity_compressionindex_cha', title: 'shearwavevelocity_compressionindex_cha()' }
                ]
            },
            {
                id: 'correlations_cohesive',
                title: 'Correlations: Cohesive soils',
                functions: [
                    { id: 'compressionindex_watercontent_koppula', title: 'compressionindex_watercontent_koppula()' },
                    { id: 'cv_liquidlimit_usnavy', title: 'cv_liquidlimit_usnavy()' },
                    { id: 'frictionangle_plasticityindex', title: 'frictionangle_plasticityindex()' },
                    { id: 'gmax_plasticityocr_andersen', title: 'gmax_plasticityocr_andersen()' },
                    { id: 'k0_plasticity_kenney', title: 'k0_plasticity_kenney()' }
                ]
            },
            {
                id: 'correlations_cohesionless',
                title: 'Correlations: Cohesionless soils',
                functions: [
                    { id: 'gmax_sand_hardinblack', title: 'gmax_sand_hardinblack()' },
                    { id: 'hssmall_parameters_sand', title: 'hssmall_parameters_sand()' },
                    { id: 'permeability_d10_hazen', title: 'permeability_d10_hazen()' },
                    { id: 'stress_dilatancy_bolton', title: 'stress_dilatancy_bolton()' }
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
                    { id: 'behaviourindex_pcpt_nonnormalised', title: 'behaviourindex_pcpt_nonnormalised()' },
                    { id: 'behaviourindex_pcpt_robertsonwride', title: 'behaviourindex_pcpt_robertsonwride()' },
                    { id: 'clippingdepths_qc1N_tianlehane', title: 'clippingdepths_qc1N_tianlehane()' },
                    { id: 'coneresistance_ocsand_baldi', title: 'coneresistance_ocsand_baldi()' },
                    { id: 'constrainedmodulus_pcpt_robertson', title: 'constrainedmodulus_pcpt_robertson()' },
                    { id: 'dissipation_test_teh', title: 'dissipation_test_teh()' },
                    { id: 'drainedsecantmodulus_sand_bellotti', title: 'drainedsecantmodulus_sand_bellotti()' },
                    { id: 'frictionangle_overburden_kleven', title: 'frictionangle_overburden_kleven()' },
                    { id: 'frictionangle_sand_kulhawymayne', title: 'frictionangle_sand_kulhawymayne()' },
                    { id: 'gmax_clay_maynerix', title: 'gmax_clay_maynerix()' },
                    { id: 'gmax_cpt_puechen', title: 'gmax_cpt_puechen()' },
                    { id: 'gmax_sand_rixstokoe', title: 'gmax_sand_rixstokoe()' },
                    { id: 'gmax_voidratio_maynerix', title: 'gmax_voidratio_maynerix()' },
                    { id: 'ic_soilclass_robertson', title: 'ic_soilclass_robertson()' },
                    { id: 'k0_sand_mayne', title: 'k0_sand_mayne()' },
                    { id: 'ocr_cpt_lunne', title: 'ocr_cpt_lunne()' },
                    { id: 'pcpt_normalisations', title: 'pcpt_normalisations()' },
                    { id: 'relativedensity_ncsand_baldi', title: 'relativedensity_ncsand_baldi()' },
                    { id: 'relativedensity_ocsand_baldi', title: 'relativedensity_ocsand_baldi()' },
                    { id: 'relativedensity_sand_jamiolkowski', title: 'relativedensity_sand_jamiolkowski()' },
                    { id: 'sensitivity_frictionratio_lunne', title: 'sensitivity_frictionratio_lunne()' },
                    { id: 'soilclass_robertson', title: 'soilclass_robertson()' },
                    { id: 'soiltype_vs_longodonohue', title: 'soiltype_vs_longodonohue()' },
                    { id: 'undrainedshearstrength_clay_radlunne', title: 'undrainedshearstrength_clay_radlunne()' },
                    { id: 'unitweight_mayne', title: 'unitweight_mayne()' },
                    { id: 'vs_cpt_andrus', title: 'vs_cpt_andrus()' },
                    { id: 'vs_cpt_hegazymayne', title: 'vs_cpt_hegazymayne()' },
                    { id: 'vs_cpt_longdonohue', title: 'vs_cpt_longdonohue()' },
                    { id: 'vs_cpt_mcgannetal', title: 'vs_cpt_mcgannetal()' },
                    { id: 'vs_cpt_tonniandsimonini', title: 'vs_cpt_tonniandsimonini()' },
                    { id: 'vs_cpt_wrideetal', title: 'vs_cpt_wrideetal()' },
                    { id: 'vs_cptd50_karrayetal', title: 'vs_cptd50_karrayetal()' },
                    { id: 'vs_ic_robertsoncabal', title: 'vs_ic_robertsoncabal()' },
                    { id: 'vs_stressdependent_stuyts', title: 'vs_stressdependent_stuyts()' }
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
                    { id: 'frictionangle_spt_PHT', title: 'frictionangle_spt_PHT()' },
                    { id: 'frictionangle_spt_kulhawymayne', title: 'frictionangle_spt_kulhawymayne()' },
                    { id: 'overburdencorrection_spt_ISO', title: 'overburdencorrection_spt_ISO()' },
                    { id: 'overburdencorrection_spt_liaowhitman', title: 'overburdencorrection_spt_liaowhitman()' },
                    { id: 'relativedensity_spt_kulhawymayne', title: 'relativedensity_spt_kulhawymayne()' },
                    { id: 'relativedensityclass_spt_terzaghipeck', title: 'relativedensityclass_spt_terzaghipeck()' },
                    { id: 'spt_N60_correction', title: 'spt_N60_correction()' },
                    { id: 'undrainedshearstrength_spt_salgado', title: 'undrainedshearstrength_spt_salgado()' },
                    { id: 'undrainedshearstrengthclass_spt_terzaghipeck', title: 'undrainedshearstrengthclass_spt_terzaghipeck()' },
                    { id: 'youngsmodulus_spt_AASHTO', title: 'youngsmodulus_spt_AASHTO()' }
                ]
            },
            {
                id: 'lab_sampleprep',
                title: 'Laboratory: Sample preparation',
                functions: [
                    { id: 'undercompaction_cohesionless_ladd', title: 'undercompaction_cohesionless_ladd()' }
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
                    { id: 'logtimemethod', title: 'logtimemethod()' },
                    { id: 'roottimemethod', title: 'roottimemethod()' }
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
                    { id: 'parameter_selection_constant_value', title: 'constant_value()' },
                    { id: 'parameter_selection_linear_trend', title: 'linear_trend()' }
                ]
            },
            {
                id: 'partial_factors',
                title: 'Partial factor selection',
                functions: [
                    { id: 'eurocode7_factors', title: 'Eurocode7_factoring_STR_GEO' }
                ]
            }
        ]
    },
    {
        id: 'constitutive',
        title: 'Constitutive models',
        description: 'Models for cohesionless, cohesive, and rock materials.',
        items: [
            { id: 'model_general', title: 'General', functions: [] },
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
