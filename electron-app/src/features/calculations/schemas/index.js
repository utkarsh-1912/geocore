/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

import { generalSchemas } from './general';
import { plottingSchemas } from './plotting';
import { pipelineSchemas } from './pipelines';
import { constitutiveSchemas } from './constitutive';
import { eurocodeSchemas } from './eurocode';
import { soilDynamicsSchemas } from './soildynamics';
import { excavationsSchemas } from './excavations';
import { consolidationSchemas } from './consolidation';

import { shallowFoundationsSchemas } from './shallowfoundations';
import { settlementSchemas } from './settlement';
import { validationSchemas } from './validation';
import { agsSchemas } from './ags';
import { parameterMappingSchemas } from './parameter_mapping';
import { classificationSchemas } from './classification';
import { correlationsSchemas } from './correlations';
import { insituTestsSchemas } from './insitutests';
import { labTestingSchemas } from './labtesting';
import { deepFoundationsSchemas } from './deepfoundations';

import { siteInvestigationSchemas } from './siteinvestigation';

import { lateralSchemas } from './lateral';

import { cavityExpansionSchemas } from './cavity_expansion';

// Combine all schemas
const allSchemas = {
    ...generalSchemas,
    ...plottingSchemas,
    ...pipelineSchemas,
    ...constitutiveSchemas,
    ...eurocodeSchemas,
    ...soilDynamicsSchemas,
    ...excavationsSchemas,
    ...consolidationSchemas,
    ...shallowFoundationsSchemas,
    ...settlementSchemas,
    ...validationSchemas,
    ...agsSchemas,
    ...parameterMappingSchemas,
    ...classificationSchemas,
    ...correlationsSchemas,
    ...insituTestsSchemas,
    ...labTestingSchemas,
    ...deepFoundationsSchemas,
    ...siteInvestigationSchemas,
    ...lateralSchemas,
    ...cavityExpansionSchemas
};

// Default schema for unknown functions
const defaultSchema = {
    inputs: [
        { name: "depth", type: "float", unit: "m", default: 10, description: "Depth below ground surface" },
        { name: "gamma", type: "float", unit: "kN/m3", default: 18, description: "Unit weight of soil" }
    ]
};

export const getSchema = (functionId) => {
    console.log("getSchema called for:", functionId);
    console.log("Available schemas:", Object.keys(allSchemas));
    const schema = allSchemas[functionId] || defaultSchema;
    console.log("Returned schema:", schema);
    return schema;
};
