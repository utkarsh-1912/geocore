/**
 * Author: Utkarsh Gupta
 * License: GPL v2
 */

export const SOIL_PROFILE_DOCS = `
<div class="space-y-4">
    <div class="p-4 bg-primary/5 rounded-lg border border-primary/20">
        <code class="text-sm font-mono text-primary">class groundhog.general.soilprofile.SoilProfile(*args, **kwargs)</code>
        <p class="mt-2 text-text-muted">A SoilProfile object is a Pandas dataframe with specific functionality for geotechnical calculations. There is a column syntax requirement in which the columns with the top and bottom depth need to be defined for each layer. By default ‘Depth from [m]’ and ‘Depth to [m]’ are expected but this can be customised.</p>
    </div>

    <h3 class="text-lg font-bold text-text-main mt-6">Methods</h3>

    <div class="pl-4 border-l-2 border-border space-y-6">
        <div>
            <code class="text-sm font-mono font-bold text-text-main">__init__(*args, **kwargs)</code>
            <p class="text-sm text-text-muted mt-1">Overrides the init method of a dataframe to check the correctness of the layering and to set the depth column names.</p>
        </div>

        <div>
            <code class="text-sm font-mono font-bold text-text-main">adjust_layertransition(currentdepth, newdepth, tolerance=0.001)</code>
            <p class="text-sm text-text-muted mt-1">Adjusts the depth of a layer transition.</p>
            <ul class="list-disc list-inside mt-2 text-sm text-text-muted pl-2">
                <li><span class="font-medium text-text-main">currentdepth</span>: Current depth of the layer transition</li>
                <li><span class="font-medium text-text-main">newdepth</span>: Desired new depth of the layer transition</li>
                <li><span class="font-medium text-text-main">tolerance</span>: Offset above and below currentdepth in which a layer transition is sought (to cope with number precision issues)</li>
            </ul>
        </div>

        <div>
             <code class="text-sm font-mono font-bold text-text-main">applyfunction(function, resultkey, outputkey, parametermapping={}, **kwargs)</code>
             <p class="text-sm text-text-muted mt-1">Applies a groundhog function to a soil profile. The function is applied to each row of the soilprofile.</p>
        </div>
        
        <!-- Add more methods here as needed from the user prompt -->
    </div>
</div>
`;

export const CALCULATION_GRID_DOCS = `
<div class="space-y-4">
    <div class="p-4 bg-primary/5 rounded-lg border border-primary/20">
        <code class="text-sm font-mono text-primary">class groundhog.general.soilprofile.CalculationGrid(soilprofile, dz, custom_nodes=None, include_layertransitions=True)</code>
        <p class="mt-2 text-text-muted">A CalculationGrid is an object which consist of a dataframe with nodes .nodes and a dataframe with elements .elements. Properties of the soil profile are mapped to the nodes and the elements to allow subsequent calculation.</p>
    </div>

    <h3 class="text-lg font-bold text-text-main mt-6">Initialization</h3>
    <div class="pl-4 border-l-2 border-border">
         <code class="text-sm font-mono font-bold text-text-main">__init__(soilprofile, dz, custom_nodes=None, include_layertransitions=True)</code>
         <p class="text-sm text-text-muted mt-1">Initializes the CalculationGrid object from a SoilProfile object.</p>
         <ul class="list-disc list-inside mt-2 text-sm text-text-muted pl-2">
            <li><span class="font-medium text-text-main">soilprofile</span>: The source SoilProfile object</li>
            <li><span class="font-medium text-text-main">dz</span>: Nodes offset</li>
            <li><span class="font-medium text-text-main">custom_nodes</span>: NumPy array with custom nodes (optional)</li>
            <li><span class="font-medium text-text-main">include_layertransitions</span>: Whether to insert nodes at layer transitions (default=True)</li>
         </ul>
    </div>
</div>
`;
